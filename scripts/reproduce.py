#!/usr/bin/env python3
"""Run both model versions, preserving expected failures as failures."""
from pathlib import Path
import sys
from run_case import ROOT, run

prefix = sys.argv[1] if len(sys.argv) > 1 else 'reproduced'
if not prefix.replace('-', '').replace('_', '').isalnum():
    raise SystemExit('invalid output prefix')
for version, build in [('baseline', 'build-baseline32'), ('fixed', 'build32')]:
    for label, app, args in [('slot', 'bar_slot_phase', []),
                             ('generation', 'bar_generation', ['-n8', '-s1'])]:
        for driver in ['simx', 'rtlsim']:
            code = run(f'{prefix}-{version}-{label}-{driver}',
                ['env', f'LD_LIBRARY_PATH={ROOT / build / "sw/runtime"}',
                 f'VORTEX_DRIVER={driver}', f'./{app}', *args],
                ROOT / build / 'tests/regression' / app, 120)
            expected_failure = version == 'baseline' and (label, driver) in [
                ('slot', 'rtlsim'), ('generation', 'simx')]
            # Inspect status, because timeouts/infrastructure errors are not counterexamples.
            import json
            rec = json.loads((ROOT / 'artifacts/runs' /
                f'{prefix}-{version}-{label}-{driver}' / 'result.json').read_text())
            expected = 'semantic_failure' if expected_failure else 'pass'
            if rec['status'] != expected:
                raise SystemExit(f'unexpected {version}/{label}/{driver}: {rec["status"]}')
    for seed in ([1] if version == 'baseline' else [1, 42, 2026]):
        run(f'{prefix}-{version}-unit-{seed}', ['./barrier', str(seed)],
            ROOT / build / 'hw/unittest/barrier', 30)
        rec = json.loads((ROOT / 'artifacts/runs' / f'{prefix}-{version}-unit-{seed}' / 'result.json').read_text())
        if rec['status'] != ('semantic_failure' if version == 'baseline' else 'pass'):
            raise SystemExit('unexpected unit-test outcome')
print('Expected baseline counterexamples and fixed-model passes reproduced.')
