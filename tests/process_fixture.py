"""Controlled POSIX failure fixture; never an emulated GPU/simulator result."""
import os
from pathlib import Path
import signal
import sys
import time

mode, marker = sys.argv[1:3]
if mode in ['fork-wait', 'fork-exit']:
    child = os.fork()
    if child == 0:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        Path(marker).write_text(str(os.getpid()))
        while True:
            time.sleep(0.01)
    while not Path(marker).exists():
        time.sleep(0.005)
    if mode == 'fork-exit':
        os._exit(0)
    while True:
        time.sleep(0.01)
elif mode == 'flood':
    while True:
        os.write(1, b'x' * 65536)
elif mode == 'cancel-runner':
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
    from process_runner import atomic_json, execute
    result = execute([sys.executable, __file__, 'fork-wait', marker],
        cwd=Path(marker).parent, log_path=marker + '.log', timeout=20, grace=0.05)
    atomic_json(marker + '.result.json', result)
else:
    raise SystemExit('unknown fixture mode')
