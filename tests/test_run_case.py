import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_case
from process_runner import exclusive_directory

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.cwd = self.root / 'build/test'
        self.cwd.mkdir(parents=True)
        source = self.root / 'source'
        subprocess.run(['git', 'init', '-q', str(source)], check=True)
        subprocess.run(['git', '-C', str(source), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-q', '--allow-empty', '-m', 'fixture'], check=True)
        (self.root / 'build/config.mk').write_text(f'VORTEX_HOME ?= {source}\n')
        self.patch = patch.object(run_case, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.temporary.cleanup)
        self.addCleanup(self.patch.stop)

    def invoke(self, command):
        run_case.run('fixture', command, self.cwd, 3)
        self.target = self.root / 'artifacts/runs/fixture'
        return json.loads((self.target / 'result.json').read_text())

    def test_launch_failure_has_terminal_record(self):
        record = self.invoke(['/definitely-not-an-executable'])
        self.assertEqual(record['status'], 'infra_failure')
        self.assertEqual(record['execution']['status'], 'launch_error')
        self.assertTrue((self.target / 'stdout.log').is_file())

    def test_stale_events_are_preserved_but_not_current_evidence(self):
        (self.cwd / 'barrier-events.csv').write_text('OLD EVENTS\n')
        record = self.invoke([sys.executable, '-c', 'print("PASSED!")'])
        self.assertEqual(record['status'], 'pass')
        self.assertNotIn('events_sha256', record)
        self.assertFalse((self.target / 'barrier-events.csv').exists())
        self.assertEqual((self.target / 'previous-barrier-events.csv').read_text(), 'OLD EVENTS\n')

    def test_shared_directory_conflict_is_explicit(self):
        with exclusive_directory(self.cwd):
            record = self.invoke([sys.executable, '-c', 'raise SystemExit(99)'])
        self.assertEqual(record['status'], 'busy')
        self.assertIsNone(record['exit_code'])

    def test_generic_failure_is_not_a_semantic_counterexample(self):
        record = self.invoke([sys.executable, '-c', 'print("FAILED!"); raise SystemExit(1)'])
        self.assertEqual(record['status'], 'infra_failure')
