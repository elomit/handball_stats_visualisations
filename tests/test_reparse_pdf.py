"""
Tests that the json input embedded into the pdf report can be read back unchanged by reparse_pdf.py.
Execute from the project folder with python -m unittest
"""

import json
import os
import tempfile
import unittest

from PIL import Image

from Analysis import Analysis
from pdf_creation import create_pdf
from reparse_pdf import read_source_files


def mock_game(opponent: str) -> tuple[str, bytes]:
    """Made up game file (name, content) in the format of the Handballfreunde Statistik App,
    with non ascii characters, so the test notices if the file is not embedded byte for byte."""

    game = {
        "own_team": "Handballfreunde",
        "enemy_team": opponent,
        "actions": [
            {"timestamp": 40, "type": "Tor", "location": "RL", "own_team": True,
             "player": {"number": 7, "player_name": "Spieler Ä", "position": "RL"}, "x": "50", "y": "40"},
            {"timestamp": 75, "type": "Gehalten", "location": "LA", "own_team": False,
             "player": None, "x": None, "y": None},
        ],
    }
    return f"game_{opponent}.json", json.dumps(game, ensure_ascii=False).encode("utf-8")


class ReparsePdfTest(unittest.TestCase):

    def assert_input_survives_pdf(self, source_files: list[tuple[str, bytes]]):
        """Create and save a pdf with the input embedded, reparse it and compare with the input."""

        with tempfile.TemporaryDirectory() as temp_dir:
            title_image = os.path.join(temp_dir, "title.png")
            Image.new("RGB", (40, 30), "white").save(title_image)
            pdf_path = create_pdf(Analysis(title_image), os.path.join(temp_dir, "report.pdf"), source_files)

            self.assertEqual(read_source_files(pdf_path), source_files)

    def test_single_input(self):
        self.assert_input_survives_pdf([mock_game("Gegner")])

    def test_multiple_inputs(self):
        self.assert_input_survives_pdf([mock_game("A"), mock_game("B"), mock_game("C")])


if __name__ == '__main__':
    unittest.main()
