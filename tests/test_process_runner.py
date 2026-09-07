import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from process_runner import atomic_json, execute, exclusive_directory


@unittest.skipUnless(os.name == 'posix', 'POSIX process groups and file locks')
class ProcessContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.marker = self.root / 'child.pid'
        self.fixture = ROOT / 'tests/process_fixture.py'

    def run_fixture(self, mode, **kwargs):
        options = dict(timeout=1, grace=0.05)
        options.update(kwargs)
        return execute([sys.executable, str(self.fixture), mode, str(self.marker)],
                       cwd=self.root, log_path=self.root / 'stdout.log', **options)

    def assert_child_stopped(self):
        pid = int(self.marker.read_text())
        deadline = time.monotonic() + 1
        while time.monotonic() < deadline:
            stat = Path(f'/proc/{pid}/stat')
            if not stat.exists() or stat.read_text().split()[2] == 'Z':
                return  # A zombie cannot consume CPU or write more artifacts.
            time.sleep(0.01)
        os.kill(pid, signal.SIGKILL)
        self.fail('descendant remained runnable after executor returned')

    def test_cancellation_during_cleanup_is_not_lost(self):
        from unittest.mock import patch
        import process_runner
        original = process_runner._stop_group
        def signal_after_cleanup(proc, grace):
            result = original(proc, grace)
            os.kill(os.getpid(), signal.SIGTERM)
            return result
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(process_runner, '_stop_group', side_effect=signal_after_cleanup):
                result = execute([sys.executable, '-c', 'print("done")'],
                    cwd=temporary, log_path=Path(temporary) / 'log', timeout=3)
        self.assertEqual(result['status'], 'cancelled')
        self.assertEqual(result['cancellation_signal'], signal.SIGTERM)

    def test_completed_preserves_bytes_and_exit_status(self):
        result = execute([sys.executable, '-c', 'import os; os.write(1,b"hello\\x00"); raise SystemExit(7)'],
            cwd=self.root, log_path=self.root / 'out', timeout=1)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['exit_code'], 7)
        self.assertEqual((self.root / 'out').read_bytes(), b'hello\0')

    def test_launch_error_is_a_terminal_outcome(self):
        result = execute(['/definitely/missing-executable'], cwd=self.root,
                         log_path=self.root / 'out', timeout=1)
        self.assertEqual(result['status'], 'launch_error')
        self.assertIsNone(result['exit_code'])

    def test_timeout_kills_descendant_after_leader_exits(self):
        result = self.run_fixture('fork-wait', timeout=0.3)
        self.assertEqual(result['status'], 'timeout')
        self.assertTrue(result['cleanup_sigkill'])
        self.assert_child_stopped()

    def test_successful_leader_cannot_leave_background_work(self):
        result = self.run_fixture('fork-exit')
        self.assertEqual(result['status'], 'descendant_leak')
        self.assertEqual(result['exit_code'], 0)
        self.assert_child_stopped()

    def test_output_budget_is_a_hard_file_limit(self):
        result = self.run_fixture('flood', max_output_bytes=4096)
        self.assertEqual(result['status'], 'output_limit')
        self.assertEqual((self.root / 'stdout.log').stat().st_size, 4096)
        self.assertGreater(result['observed_output_bytes'], 4096)

    def test_sigterm_cancels_and_persists_a_complete_outcome(self):
        proc = subprocess.Popen([sys.executable, str(self.fixture), 'cancel-runner', str(self.marker)])
        try:
            until = time.monotonic() + 3
            while not self.marker.exists() and time.monotonic() < until:
                time.sleep(0.01)
            self.assertTrue(self.marker.exists())
            proc.send_signal(signal.SIGTERM)
            self.assertEqual(proc.wait(timeout=3), 0)
            result = json.loads(Path(str(self.marker) + '.result.json').read_text())
            self.assertEqual(result['status'], 'cancelled')
            self.assertEqual(result['cancellation_signal'], signal.SIGTERM)
            self.assert_child_stopped()
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()

    def test_rejects_nonfinite_execution_budget(self):
        for timeout in [0, -1, float('nan'), float('inf')]:
            with self.assertRaises(ValueError):
                execute(['unused'], cwd=self.root, log_path=self.root / 'out', timeout=timeout)

    def test_atomic_json_rejects_nan_without_replacing_previous_result(self):
        target = self.root / 'result.json'
        atomic_json(target, {'status': 'old'})
        with self.assertRaises(ValueError):
            atomic_json(target, {'bad': float('nan')})
        self.assertEqual(json.loads(target.read_text()), {'status': 'old'})
        self.assertEqual(list(self.root.glob('.result.json-*')), [])

    def test_readers_never_observe_partial_json(self):
        target = self.root / 'result.json'
        atomic_json(target, {'generation': 0, 'padding': 'x' * 8192})
        stop = threading.Event()
        failures = []
        def read():
            while not stop.is_set():
                try:
                    self.assertEqual(len(json.loads(target.read_text())['padding']), 8192)
                except Exception as error:
                    failures.append(str(error))
        reader = threading.Thread(target=read)
        reader.start()
        try:
            for generation in range(1, 20):
                atomic_json(target, {'generation': generation, 'padding': 'x' * 8192})
        finally:
            stop.set()
            reader.join()
        self.assertEqual(failures, [])

    def test_shared_directory_admission_is_exclusive(self):
        with exclusive_directory(self.root):
            with self.assertRaises(BlockingIOError):
                with exclusive_directory(self.root):
                    self.fail('two executors admitted')
        with exclusive_directory(self.root):
            pass


if __name__ == '__main__':
    unittest.main()
