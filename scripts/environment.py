#!/usr/bin/env python3
"""Capture the build environment inside the project's experiment container."""
import hashlib
import json
from pathlib import Path
import subprocess
import platform

root = Path(__file__).resolve().parents[1]
commands = [['g++', '--version'], ['python3', '--version'], ['git', '--version'],
            ['dpkg-query', '-W', '-f=${Package}=${Version}\n']]
record = dict(schema_version=1, machine=platform.machine(),
              dockerfile_sha256=hashlib.sha256((root / 'Dockerfile').read_bytes()).hexdigest(),
              tools={})
for command in commands:
    run = subprocess.run(command, capture_output=True, text=True, check=True)
    record['tools'][' '.join(command)] = run.stdout.strip()
(root / 'results').mkdir(exist_ok=True)
(root / 'results/environment.json').write_text(json.dumps(record, indent=2) + '\n')
print('Build environment captured.')
