#!/usr/bin/env python3
"""Reparse the saved real post-review executions; offline audit, not simulation."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def verify(root=None, prefix='review-20260906-'):
    root = root or ROOT / 'results/review/live'
    index = json.loads((root / 'index.json').read_text())
    with tempfile.TemporaryDirectory() as temporary:
        unpacked = Path(temporary)
        for name, expected in index['files'].items():
            path = root / name
            require(path.resolve().is_relative_to(root.resolve()), 'unsafe evidence path')
            data = path.read_bytes()
            require(digest(data) == expected, 'changed evidence: ' + name)
            destination = unpacked / name
            if path.suffix == '.gz':
                destination = destination.with_suffix('')
                data = gzip.decompress(data)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        records = {name: json.loads((unpacked / name / 'result.json').read_text()) for name in index['runs']}
        for name, rec in records.items():
            execution = rec['execution']
            require(execution['status'] == 'completed', 'nonterminal execution')
            require(execution['exit_code'] == rec['exit_code'], 'exit mismatch')
            require(execution['output_bytes'] == (unpacked / name / 'stdout.log').stat().st_size, 'log byte mismatch')
            require(execution['output_bytes'] <= execution['output_limit_bytes'], 'output budget violated')
        lock = json.loads((ROOT / 'upstream.lock.json').read_text())
        require(len(records) == 12, 'incomplete paired and unit replay')
        for name, rec in records.items():
            folder = unpacked / name
            require(rec['vortex_commit'] == lock['commit'], 'model revision mismatch')
            for file, field in [('stdout.log', 'stdout_sha256'), ('source.patch', 'source_patch_sha256')]:
                require(digest((folder / file).read_bytes()) == rec[field], 'output hash mismatch')
            if 'events_sha256' in rec:
                require(digest((folder / 'barrier-events.csv').read_bytes()) == rec['events_sha256'], 'events changed')
            log = (folder / 'stdout.log').read_text()
            expected_failure = name in [prefix + 'baseline-slot-rtlsim', prefix + 'baseline-generation-simx', prefix + 'baseline-unit-1']
            require(rec['status'] == ('semantic_failure' if expected_failure else 'pass'), 'differential outcome changed')
            require((rec['exit_code'] != 0) == expected_failure, 'exit status differs from expected semantics')
            require(('FAILED' in log) if expected_failure else bool(re.search(r'^PASSED!$', log, re.M)), 'missing outcome marker')
        for case in ['slot', 'generation']:
            hashes = set()
            for version in ['baseline', 'fixed']:
                for driver in ['simx', 'rtlsim']:
                    rec = records[prefix + f'{version}-{case}-{driver}']
                    hashes.update(v for k, v in rec['input_sha256'].items() if k.endswith('/kernel.vxbin'))
            require(len(hashes) == 1, 'paired kernel mismatch')
        require('slot phase errors: 256' in (unpacked / (prefix + 'baseline-slot-rtlsim') / 'stdout.log').read_text(), 'slot symptom changed')
        require('Found 18 errors!' in (unpacked / (prefix + 'baseline-generation-simx') / 'stdout.log').read_text(), 'generation symptom changed')
        totals = [0, 0, 0]
        for seed in [1, 42, 2026]:
            folder = unpacked / (prefix + f'fixed-unit-{seed}')
            match = re.search(r'seed=(\d+) cycles=(\d+) checks=(\d+) resets=(\d+)', (folder / 'stdout.log').read_text())
            require(match and int(match[1]) == seed, 'missing seed summary')
            values = list(map(int, match.groups()[1:]))
            totals = [x + y for x, y in zip(totals, values)]
            rows = list(csv.DictReader((folder / 'barrier-events.csv').open()))
            require(len(rows) == values[0], 'incomplete event stream')
            require(all(r['expected_phase'] == r['rtl_phase'] for r in rows if r['reset'] == '0'), 'phase invariant failed')
            require(sum(int(r['reset']) for r in rows) == values[2], 'reset count differs')
        require(totals == [18555, 50316, 312], 'scoreboard coverage changed')
        return {'paired_system_runs': 8, 'rtl_unit_runs': 4, 'expected_baseline_semantic_failures': 3, 'fixed_rtl_cycles': totals[0], 'fixed_invariant_checks': totals[1], 'fixed_resets': totals[2]}

if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
