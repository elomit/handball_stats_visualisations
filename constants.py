import os

import matplotlib

MISSED_SHOTS_FIELDS = ['Block', 'Verworfen', 'Gehalten']
SCORED_SHOTS_FIELDS = ["Tor"]
SHOT_FIELDS = ["Tor", "Gehalten", "Verworfen", "Block"]
GOALIE_SHOTS_FIELDS = ["Tor", "Gehalten"]

TEAM_NAME = "Handballfreunde"
NAME = "Hbfr Pankow_eintracht_1791072000" # hier filename (einzelnes Spiel) oder Ordnername (mehrere Spiele) eintragen
CURRENT_DIR = os.getcwd()
PATH = rf"{CURRENT_DIR}/input/{NAME}.json"
OUTPUT_DIR = CURRENT_DIR + "/output/"
PDF_FILE_PATH = rf"{OUTPUT_DIR}/{NAME}.pdf"
TITLE_IMG_PATH = rf"{CURRENT_DIR}/woran-hat-es-gelegen-winner.png"
MULTIPLE_GAMES_FOLDER_PATH = rf"{CURRENT_DIR}/input/{NAME}"
# pdf report (with embedded json files) that reparse_pdf.py recalculates, the new report is saved to PDF_FILE_PATH
REPARSE_PDF_PATH = rf"{CURRENT_DIR}/input/{NAME}.pdf"
# description of the json files embedded into the pdf report
SOURCE_FILE_DESCRIPTION = "Spieldaten aus der Handballfreunde Statistik App"
# unicode fonts for the texts of the pdf (the built-in fonts of fpdf2 can't show e.g. "š" in player names),
# the DejaVu fonts come with matplotlib, which uses them for the images too
PDF_FONT_PATH = os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans.ttf")
PDF_BOLD_FONT_PATH = os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans-Bold.ttf")
# the table "Quote pro Spieler" is split into columns of at most this many rows (the rows of a player stay together),
# up to QUOTE_TABLE_COLUMNS columns side by side per page, so the table stays readable for multiple games
# (with 33 rows and 3 columns a page is filled with the text at 9pt)
QUOTE_TABLE_MAX_ROWS = 33
QUOTE_TABLE_COLUMNS = 3
POSITION_MAPPING = {
    "LA": "LA",
    "RA": "RA",
    "KM": "Kreis",
    "L": "RL (6M)",
    "R": "RR (6M)",
    "M": "RM (6M)",
    "RL": "RL (9M)",
    "RM": "RM (9M)",
    "RR": "RR (9M)",
    "K": "Konter",
    "7M": "7M"
}
# quote from which shots from a position count as good (amateur level), keys as in POSITION_MAPPING
GOOD_QUOTE = {
    "LA": 0.6,
    "RA": 0.6,
    "KM": 0.65,
    "L": 0.6,
    "R": 0.6,
    "M": 0.6,
    "RL": 0.4,
    "RM": 0.4,
    "RR": 0.4,
    "K": 0.75,
    "7M": 0.7
}
# used for positions missing in GOOD_QUOTE
DEFAULT_GOOD_QUOTE = 0.5
# the opponent half of the team pitch plots and the keeper pitch plots are mirrored (goal on the right),
# like on a real pitch; False: all halves face the same way (goal on the left)
MIRROR_OPPONENT = True
# the goal is 3m wide and 2m high, the shot coordinates in the goal go from 0 to 100 in both directions
GOAL_HEIGHT_RATIO = 2 / 3
