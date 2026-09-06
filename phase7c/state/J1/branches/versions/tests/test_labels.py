import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from labels import normalize_label

class LabelTests(unittest.TestCase):
    def test_label(self):
        self.assertEqual(normalize_label(' North America! '), 'north-america')
