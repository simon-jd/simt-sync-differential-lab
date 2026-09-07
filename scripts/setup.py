#!/usr/bin/env python3
"""Fetch the locked upstream and apply only the lab's focused changes."""
import json
import argparse
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / 'upstream.lock.json').read_text())
parser = argparse.ArgumentParser()
parser.add_argument('--baseline', action='store_true', help='omit the two model fixes')
args = parser.parse_args()
source = ROOT / ('vendor/vortex-baseline' if args.baseline else 'vendor/vortex')
if not (source / '.git').exists():
    source.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', str(source)], check=True)
    subprocess.run(['git', '-C', str(source), 'remote', 'add', 'origin', lock['repository']], check=True)
    subprocess.run(['git', '-C', str(source), 'fetch', '--depth=1', 'origin', lock['commit']], check=True)
    subprocess.run(['git', '-C', str(source), 'checkout', '--detach', 'FETCH_HEAD'], check=True)
actual = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
if actual != lock['commit']:
    raise SystemExit('refusing to replace a different Vortex revision')
locked_modules = [(line.split()[0], line.split()[1]) for line in lock['submodules']]
if any((source / path).is_symlink() for _, path in locked_modules):
    # Existing local baseline builds may share immutable third-party checkouts.
    # Git refuses to update symlink submodules; verify every locked revision instead.
    if not args.baseline:
        raise SystemExit('dependency aliases are permitted only for a baseline replay')
    for expected, path in locked_modules:
        actual = subprocess.check_output(['git', '-C', str(source / path), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != expected:
            raise SystemExit(f'shared dependency revision differs: {path}')
else:
    subprocess.run(['git', '-C', str(source), 'submodule', 'update', '--init', '--recursive', '--depth=1'], check=True)
for patch in sorted((ROOT / 'patches').glob('*.patch')):
    if args.baseline and patch.name.startswith(('0001-', '0002-')):
        applied = subprocess.run(['git', '-C', str(source), 'apply', '--reverse', '--check', str(patch)], capture_output=True)
        if applied.returncode == 0:
            raise SystemExit('baseline already contains a model repair; refusing to mislabel it')
        continue
    applied = subprocess.run(['git', '-C', str(source), 'apply', '--reverse', '--check', str(patch)], capture_output=True)
    if applied.returncode != 0:
        subprocess.run(['git', '-C', str(source), 'apply', '--check', str(patch)], check=True)
        subprocess.run(['git', '-C', str(source), 'apply', str(patch)], check=True)
for path in (ROOT / 'overlays').rglob('*'):
    if path.is_file():
        target = source / path.relative_to(ROOT / 'overlays')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
print('Pinned source and focused patches prepared.')
