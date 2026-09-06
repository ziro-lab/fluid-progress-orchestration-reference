import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from threshold import parse_threshold

class ThresholdTests(unittest.TestCase):
    def test_threshold(self):
        self.assertEqual(parse_threshold(' warning = 7 '), ('warning', 7))

    def test_empty_name(self):
        with self.assertRaises(ValueError):
            parse_threshold(' = 7')
