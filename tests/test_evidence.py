import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_evidence import ROOT, verify

class EvidenceGates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name) / 'evidence'
        shutil.copytree(ROOT / 'results/evidence', self.folder)
        self.addCleanup(self.temp.cleanup)

    def test_changed_log_is_rejected(self):
        path = self.folder / 'fixed-generation-simx/stdout.log'
        path.write_text(path.read_text() + '\nchanged\n')
        with self.assertRaisesRegex(ValueError, 'evidence bytes changed'):
            verify(self.folder)

    def test_timeout_cannot_replace_a_semantic_counterexample(self):
        relative = 'replay2-baseline-generation-simx/result.json'
        path = self.folder / relative
        record = json.loads(path.read_text())
        record['status'] = 'timeout'
        path.write_text(json.dumps(record))
        index = json.loads((self.folder / 'index.json').read_text())
        index['files'][relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.folder / 'index.json').write_text(json.dumps(index))
        with self.assertRaisesRegex(ValueError, 'non-semantic failure'):
            verify(self.folder)

if __name__ == '__main__':
    unittest.main()
