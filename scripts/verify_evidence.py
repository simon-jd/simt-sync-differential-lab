#!/usr/bin/env python3
"""Offline audit of immutable experiment evidence, not a new RTL simulation."""
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def verify(root=ROOT / 'results/evidence'):
    index = json.loads((root / 'index.json').read_text())
    lock = json.loads((ROOT / 'upstream.lock.json').read_text())
    for name, expected in index['files'].items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == expected,
                f'evidence bytes changed: {name}')
    runs = {}
    for name in index['primary_runs']:
        folder = root / name
        rec = json.loads((folder / 'result.json').read_text())
        for file, field in [('stdout.log', 'stdout_sha256'), ('source.patch', 'source_patch_sha256')]:
            require(hashlib.sha256((folder / file).read_bytes()).hexdigest() == rec[field], file)
        require(rec['vortex_commit'] == lock['commit'], 'wrong model revision')
        log = (folder / 'stdout.log').read_text()
        if rec['status'] == 'pass':
            require(rec['exit_code'] == 0 and re.search(r'^PASSED!$', log, re.M)
                    and 'FAILED' not in log, f'inconsistent pass: {name}')
        else:
            require(rec['status'] == 'semantic_failure' and rec['exit_code'] != 0
                    and 'FAILED!' in log, f'non-semantic failure: {name}')
        if name.startswith(('fixed-', 'replay2-')):
            for lib in ['libsimx.so', 'librtlsim.so']:
                require(any(k.endswith('/' + lib) for k in rec['input_sha256']),
                        'missing loaded model binary provenance')
        runs[name] = rec
    for case in ['slot', 'generation']:
        kernel_hashes = set()
        for prefix in ['replay2-baseline', 'fixed']:
            for driver in ['simx', 'rtlsim']:
                rec = runs[f'{prefix}-{case}-{driver}']
                faulty = prefix == 'replay2-baseline' and (case, driver) in [
                    ('slot', 'rtlsim'), ('generation', 'simx')]
                require(rec['status'] == ('semantic_failure' if faulty else 'pass'), 'wrong differential outcome')
                kernel_hashes.update(v for k, v in rec['input_sha256'].items() if k.endswith('/kernel.vxbin'))
        require(len(kernel_hashes) == 1, 'baseline/fixed kernel changed')
    require('slot phase errors: 256' in (root / 'replay2-baseline-slot-rtlsim/stdout.log').read_text(), 'missing slot symptom')
    require('Found 18 errors!' in (root / 'replay2-baseline-generation-simx/stdout.log').read_text(), 'missing generation symptom')
    totals = [0, 0, 0]
    for seed in [1, 42, 2026]:
        folder = root / f'rtl-unit-seed-{seed}'
        match = re.search(r'seed=(\d+) cycles=(\d+) checks=(\d+) resets=(\d+)', (folder / 'stdout.log').read_text())
        require(match is not None and int(match[1]) == seed, 'seed missing')
        values = list(map(int, match.groups()[1:]))
        totals = [a + b for a, b in zip(totals, values)]
        rows = list(csv.DictReader((folder / 'barrier-events.csv').open()))
        require(len(rows) == values[0], 'event coverage differs from run count')
        # CSV samples the combinational read before the active reset edge.
        require(all(r['expected_phase'] == r['rtl_phase'] for r in rows if r['reset'] == '0'), 'phase invariant violated')
        require(sum(int(r['reset']) for r in rows) == values[2], 'reset count differs')
    require(totals == [18555, 50316, 312], 'unexpected scoreboard coverage')
    require('8 passed, 637 deselected' in (root / 'canonical-regression.log').read_text(), 'canonical suite did not pass')
    synth = (root / 'yosys.log').read_text()
    require('Found and reported 0 problems.' in synth and 'End of script.' in synth,
            'incomplete synthesis/check result')
    require('cycle=8' in (root / 'baseline-unit.log').read_text(), 'baseline scoreboard counterexample missing')
    return dict(system_runs=8, rtl_cycles=totals[0], invariant_checks=totals[1], resets=totals[2], canonical_passes=8)

if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
