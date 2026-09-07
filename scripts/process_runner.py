# SPDX-License-Identifier: MIT OR Apache-2.0
"""POSIX experiment process lifecycle; no service scheduler or security sandbox.

Identical, dependency-free copies ship in the three independent portfolio repos.
The caller owns output-directory admission and domain-specific result validation.
"""
from contextlib import contextmanager
import fcntl
import json
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import tempfile
import threading
import time


def atomic_json(path, record):
    """Readers see the previous complete document or the new complete document."""
    path = Path(path)
    payload = (json.dumps(record, indent=2, allow_nan=False) + '\n').encode()
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def exclusive_directory(directory):
    """Fail fast if another cooperative executor owns shared build outputs."""
    with (Path(directory) / '.lab-execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _group_exists(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def _stop_group(proc, grace):
    """Escalate for the group even when its original leader already exited."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        proc.wait(timeout=1)
        return False
    until = time.monotonic() + grace
    while time.monotonic() < until:
        proc.poll()  # Reap the leader, but never use that alone as group liveness.
        if not _group_exists(proc.pid):
            return False
        time.sleep(min(0.01, max(0, until - time.monotonic())))
    escalated = False
    try:
        os.killpg(proc.pid, signal.SIGKILL)
        escalated = True
    except ProcessLookupError:
        pass
    proc.wait(timeout=1)
    return escalated


def execute(command, *, cwd, log_path, timeout, grace=0.25,
            max_output_bytes=8 * 1024 * 1024):
    """Execute argv, stream bounded logs, and return a terminal execution outcome.

    SIGINT/SIGTERM cancellation is handled when called from the main thread.
    SIGKILL, host loss and descendants deliberately creating new sessions are
    outside this process-group contract. Docker/cgroup limits remain separate.
    """
    if not command or not isinstance(command, (list, tuple)):
        raise ValueError('a nonempty argv is required')
    if not math.isfinite(timeout) or timeout <= 0 or not math.isfinite(grace) or grace < 0:
        raise ValueError('finite positive timeout and nonnegative grace required')
    if not isinstance(max_output_bytes, int) or max_output_bytes <= 0:
        raise ValueError('positive output byte limit required')
    started = time.monotonic()
    outcome = dict(status='launch_error', exit_code=None, output_bytes=0,
                   observed_output_bytes=0, output_limit_bytes=max_output_bytes,
                   process_group_id=None, cleanup_sigkill=False,
                   cancellation_signal=None)
    proc = None
    cleaned = False
    handlers = {}
    interrupted = []

    def cancel(signum, _frame):
        if not interrupted:
            interrupted.append(signum)

    if threading.current_thread() is threading.main_thread():
        for sig in [signal.SIGINT, signal.SIGTERM]:
            handlers[sig] = signal.signal(sig, cancel)
    try:
        with Path(log_path).open('wb') as log, selectors.DefaultSelector() as selector:
            try:
                proc = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
            except OSError as error:
                outcome['error'] = f'{type(error).__name__}: {error}'
            else:
                outcome.update(status='completed', process_group_id=proc.pid)
                os.set_blocking(proc.stdout.fileno(), False)
                selector.register(proc.stdout, selectors.EVENT_READ)
                while True:
                    if interrupted:
                        outcome.update(status='cancelled', cancellation_signal=interrupted[0])
                        break
                    if time.monotonic() - started >= timeout:
                        outcome['status'] = 'timeout'
                        break
                    if proc.poll() is not None and _group_exists(proc.pid):
                        outcome['status'] = 'descendant_leak'
                        break
                    for key, _ in selector.select(min(0.02, timeout)):
                        chunk = os.read(key.fd, 65536)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        outcome['observed_output_bytes'] += len(chunk)
                        remaining = max_output_bytes - outcome['output_bytes']
                        saved = chunk[:remaining]
                        log.write(saved)
                        outcome['output_bytes'] += len(saved)
                        if len(chunk) > remaining:
                            outcome['status'] = 'output_limit'
                            break
                    if outcome['status'] == 'output_limit':
                        break
                    if proc.poll() is not None and not selector.get_map():
                        break
                # Always inspect/terminate the process group, not just proc.poll().
                try:
                    outcome['cleanup_sigkill'] = _stop_group(proc, grace)
                except subprocess.TimeoutExpired:
                    outcome['status'] = 'cleanup_failure'
                cleaned = True
                outcome['exit_code'] = proc.poll()
                proc.stdout.close()
    finally:
        # Also clean up when a local I/O exception interrupts normal collection.
        try:
            if proc is not None and not cleaned:
                _stop_group(proc, grace)
        finally:
            if interrupted:
                outcome['cancellation_signal'] = interrupted[0]
                if outcome['status'] != 'cleanup_failure':
                    outcome['status'] = 'cancelled'
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
    outcome['process_elapsed_seconds'] = time.monotonic() - started
    return outcome
