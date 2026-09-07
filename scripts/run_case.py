#!/usr/bin/env python3
"""Record a bounded real-backend run without turning infrastructure errors into passes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def run(name, command, cwd, timeout):
    target = ROOT / 'artifacts/runs' / name
    target.mkdir(parents=True, exist_ok=False)
    build = next((parent for parent in [cwd, *cwd.parents]
                  if (parent / 'config.mk').is_file()), None)
    if build is None:
        raise ValueError('run must use a configured Vortex build directory')
    source_match = re.search(r'^VORTEX_HOME\s*\?=\s*(.+)$',
                             (build / 'config.mk').read_text(), re.M)
    if not source_match:
        raise ValueError('configured source directory not found')
    source = Path(source_match.group(1).strip())
    revision = subprocess.check_output(
        ['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    diff = subprocess.check_output(['git', '-C', str(source), 'diff', 'HEAD'])
    (target / 'source.patch').write_bytes(diff)
    inputs = {}
    sources = list((ROOT / 'overlays').rglob('*'))
    for path in [cwd / 'kernel.vxbin', cwd / 'barrier', build / 'config.mk',
                 build / 'sw/VX_config.h',
                 *sorted((build / 'sw/runtime').glob('*.so')),
                 *sorted(p for p in sources if p.is_file())]:
        if path.is_file():
            inputs[str(path.relative_to(ROOT))] = sha256(path)
    started = time.time()
    status = 'infra_failure'
    with (target / 'stdout.log').open('wb') as log:
        proc = subprocess.Popen(command, cwd=cwd, stdout=log,
                                stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            code = proc.returncode
            status = 'timeout'
    elapsed = time.time() - started
    output = (target / 'stdout.log').read_text(errors='replace')
    if status != 'timeout':
        if code == 0 and re.search(r'^PASSED!$', output, re.M) and 'FAILED' not in output:
            status = 'pass'
        elif 'FAILED' in output or 'EARLY WAIT error:' in output:
            status = 'semantic_failure'
    result = dict(schema_version=1, name=name, command=command, cwd=str(cwd),
                  timeout_seconds=timeout, exit_code=code, status=status,
                  elapsed_host_seconds=elapsed, started_unix=started,
                  vortex_commit=revision, source_patch_sha256=sha256(target / 'source.patch'),
                  input_sha256=inputs, stdout_sha256=sha256(target / 'stdout.log'))
    events = cwd / 'barrier-events.csv'
    if events.is_file():
        shutil.copyfile(events, target / events.name)
        result['events_sha256'] = sha256(target / events.name)
    (target / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if status == 'pass' else 1


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
