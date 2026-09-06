import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from report import build_report

class ReportTests(unittest.TestCase):
    def test_report(self):
        self.assertEqual(build_report([{'label': 'North America!', 'version': '1.10.0'}, {'label': 'East', 'version': '1.2.0'}]), 'east: 1.2.0\nnorth-america: 1.10.0')
