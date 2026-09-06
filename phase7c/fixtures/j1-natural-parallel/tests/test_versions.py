import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from versions import sort_versions

class VersionTests(unittest.TestCase):
    def test_versions(self):
        self.assertEqual(sort_versions(['1.10.0', '1.2.0', '1.1.9']), ['1.1.9', '1.2.0', '1.10.0'])
