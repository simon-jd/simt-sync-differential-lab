#!/usr/bin/env python3
"""Pack and revalidate the full completion run; never replace original evidence."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import tempfile
ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'results/completion/evidence'
RUN_ID = 'completion-20260906'

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def pack():
    ARCHIVE.mkdir(parents=True, exist_ok=False)
    files = {}
    names = {}
    for name, folder in sources().items():
        require((folder / 'result.json').is_file(), 'missing run: ' + name)
        names[name] = str(folder.relative_to(ROOT))
        for source in sorted(folder.iterdir()):
            if source.is_symlink() or not source.is_file():
                continue
            if FILTER and source.name not in FILTER:
                continue
            data = source.read_bytes()
            target = ARCHIVE / name / source.name
            if source.suffix != '.json':
                data = gzip.compress(data, mtime=0)
                target = target.with_name(target.name + '.gz')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            files[str(target.relative_to(ARCHIVE))] = sha(data)
    (ARCHIVE / 'index.json').write_text(json.dumps(dict(schema_version=1, runs=list(names), local_sources=names, files=files), indent=2) + '\n')

def unpack(destination):
    index = json.loads((ARCHIVE / 'index.json').read_text())
    for name, expected in index['files'].items():
        source = ARCHIVE / name
        require(source.resolve().is_relative_to(ARCHIVE.resolve()), 'invalid archive path')
        data = source.read_bytes()
        require(sha(data) == expected, 'changed evidence: ' + name)
        target = destination / name
        if source.suffix == '.gz':
            target = target.with_suffix('')
            data = gzip.decompress(data)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    require(set(index['runs']) == set(sources()), 'incomplete execution population')
    return {name: json.loads((destination / name / 'result.json').read_text()) for name in index['runs']}
FILTER = None

def sources():
    return {f'{RUN_ID}-{version}-{label}-{driver}': ROOT / 'artifacts/runs' / f'{RUN_ID}-{version}-{label}-{driver}' for version in ['baseline','fixed'] for label in ['slot','generation'] for driver in ['simx','rtlsim']} | {f'{RUN_ID}-{version}-unit-{seed}': ROOT / 'artifacts/runs' / f'{RUN_ID}-{version}-unit-{seed}' for version, seeds in [('baseline',[1]),('fixed',[1,42,2026])] for seed in seeds}

def verify():
    from review_evidence import verify as differential
    result = differential(ARCHIVE, RUN_ID + '-')
    require('8 passed, 637 deselected' in (ROOT / 'results/completion/canonical-regression.log').read_text(), 'canonical regression missing')
    log = (ROOT / 'results/completion/yosys.log').read_text()
    require('Found and reported 0 problems.' in log and 'End of script.' in log, 'synthesis incomplete')
    rtl = gzip.decompress((ROOT / 'results/completion/barrier.v.gz').read_bytes())
    expected = (ROOT / 'results/completion/barrier.sha256').read_text().split()[0]
    require(sha(rtl) == expected, 'synthesized input differs')
    result.update(canonical_passes=8, structural_synthesis='passed')
    return result

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['pack','verify']);args=parser.parse_args()
    if args.action == 'pack':pack()
    print(json.dumps(verify(),indent=2))
