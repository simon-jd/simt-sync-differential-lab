#!/usr/bin/env python3
"""Record a bounded real-backend run without turning infrastructure errors into passes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from process_runner import atomic_json, execute, exclusive_directory

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def run(name, command, cwd, timeout):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', name):
        raise ValueError('name must be one safe path component')
    target = ROOT / 'artifacts/runs' / name
    target.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    result = dict(schema_version=1, name=name, command=command, cwd=str(cwd),
                  timeout_seconds=timeout, exit_code=None, status='infra_failure',
                  started_unix=time.time(), input_sha256={})
    (target / 'stdout.log').touch()
    try:
        build = next((parent for parent in [cwd, *cwd.parents]
                      if (parent / 'config.mk').is_file()), None)
        if build is None:
            raise ValueError('run must use a configured Vortex build directory')
        source_match = re.search(r'^VORTEX_HOME\s*\?=\s*(.+)$',
                                 (build / 'config.mk').read_text(), re.M)
        if not source_match:
            raise ValueError('configured source directory not found')
        source = Path(source_match.group(1).strip())
        result['vortex_commit'] = subprocess.check_output(
            ['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
        diff = subprocess.check_output(['git', '-C', str(source), 'diff', 'HEAD'])
        (target / 'source.patch').write_bytes(diff)
        result['source_patch_sha256'] = sha256(target / 'source.patch')
        inputs = [cwd / 'kernel.vxbin', cwd / 'barrier', build / 'config.mk',
                  build / 'sw/VX_config.h', *sorted((build / 'sw/runtime').glob('*.so')),
                  *sorted(p for p in (ROOT / 'overlays').rglob('*') if p.is_file())]
        result['input_sha256'] = {str(p.relative_to(ROOT)): sha256(p)
                                  for p in inputs if p.is_file()}
        with exclusive_directory(cwd):
            events = cwd / 'barrier-events.csv'
            if events.is_symlink():
                raise ValueError('event output must not be a symlink')
            if events.exists():
                previous = target / 'previous-barrier-events.csv'
                shutil.copyfile(events, previous)
                result['previous_events_sha256'] = sha256(previous)
                events.unlink()
            execution = execute(command, cwd=cwd, log_path=target / 'stdout.log', timeout=timeout)
            result.update(execution=execution, exit_code=execution['exit_code'])
            result['status'] = 'infra_failure' if execution['status'] == 'launch_error' else execution['status']
            output = (target / 'stdout.log').read_text(errors='replace')
            if execution['status'] == 'completed':
                result['status'] = 'infra_failure'
                passed = re.search(r'^PASSED!$', output, re.M) and 'FAILED' not in output
                kernel_failure = (re.search(r'^Found [1-9]\d* errors!$', output, re.M)
                                  and re.search(r'^FAILED!$', output, re.M))
                unit_failure = (re.search(r'^cycle=\d+ invariant=', output, re.M)
                                and re.search(r'^seed=\d+ FAILED:', output, re.M))
                if result['exit_code'] == 0 and passed:
                    result['status'] = 'pass'
                elif result['exit_code'] != 0 and (kernel_failure or unit_failure):
                    result['status'] = 'semantic_failure'
            if events.is_file() and not events.is_symlink():
                shutil.copyfile(events, target / events.name)
                result['events_sha256'] = sha256(target / events.name)
    except BlockingIOError:
        result.update(status='busy', error='another executor owns this build/test directory')
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        result.update(status='infra_failure', error=f'{type(error).__name__}: {error}')
    result['elapsed_host_seconds'] = time.monotonic() - started
    result['stdout_sha256'] = sha256(target / 'stdout.log')
    atomic_json(target / 'result.json', result)
    print(f'{name}: {result["status"]}', flush=True)
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    parser.add_argument('--cwd', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=120)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', args.name):
        parser.error('name must be a single safe path component')
    if args.timeout <= 0 or not args.command:
        parser.error('positive timeout and command are required')
    command = args.command[1:] if args.command[0] == '--' else args.command
    raise SystemExit(run(args.name, command, args.cwd.resolve(), args.timeout))
