#!/usr/bin/env python3
"""Package selected real executions; preserve original bytes and provenance."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'results/evidence'
out.mkdir(parents=True, exist_ok=True)
names = [f'{prefix}-{case}-{driver}'
         for prefix in ['replay2-baseline', 'fixed']
         for case in ['slot', 'generation'] for driver in ['simx', 'rtlsim']]
names += [f'rtl-unit-seed-{seed}' for seed in [1, 42, 2026]]
reproductions = ['replay2-baseline-unit'] + [p.name for p in sorted((ROOT / 'artifacts/runs').glob('packaged-*'))]
for name in names + reproductions:
    shutil.copytree(ROOT / 'artifacts/runs' / name, out / name, dirs_exist_ok=True)
shutil.copyfile(ROOT / 'artifacts/setup/canonical-regression.log', out / 'canonical-regression.log')
shutil.copyfile(ROOT / 'artifacts/synthesis/yosys.log', out / 'yosys.log')
shutil.copyfile(ROOT / 'artifacts/synthesis/barrier.v', out / 'synthesized-input.v')
files = [p for name in names + reproductions for p in (out / name).iterdir() if p.is_file()]
files += [out / n for n in ['canonical-regression.log', 'baseline-unit.log', 'yosys.log', 'synthesized-input.v']]
index = dict(schema_version=1, primary_runs=names, reproduction_runs=reproductions, files={
    str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(files)})
(out / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
print(f'Exported {len(names)} runs and {len(files)} auditable files')
