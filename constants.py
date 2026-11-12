import os

import matplotlib

MISSED_SHOTS_FIELDS = ['Block', 'Verworfen', 'Gehalten']
SCORED_SHOTS_FIELDS = ["Tor"]
SHOT_FIELDS = ["Tor", "Gehalten", "Verworfen", "Block"]
GOALIE_SHOTS_FIELDS = ["Tor", "Gehalten"]

# attacks (from the ball changing teams to the last action of the team): each half starts a new attack,
# the first attack of the second half counts from 30:00 (an action at exactly 30:00 still belongs to the first half)
HALF_TIME_SECONDS = 30 * 60
# if the same team has the next action after its own goal, the action of the opponent in between is missing in the data,
# the attack is estimated: a counter attack (location as in the app) took ESTIMATED_COUNTER_ATTACK_SECONDS,
# other attacks half of the time since the goal (the other half was the missing attack of the opponent)
COUNTER_ATTACK_LOCATION = "K"
ESTIMATED_COUNTER_ATTACK_SECONDS = 5
# timeline of the attacks: minutes per row
ATTACK_TIMELINE_ROW_MINUTES = 15
# seconds per attempt: the attempts are counted per step of this many seconds
ATTEMPT_DURATION_STEP_SECONDS = 5

TEAM_NAME = "Handballfreunde"
#NAME = "Hbfr Pankow_eintracht_1791072000" # hier filename (einzelnes Spiel) oder Ordnername (mehrere Spiele) eintragen
NAME = "Hbfr Pankow II_neukölln_1794009600" # hier filename (einzelnes Spiel) oder Ordnername (mehrere Spiele) eintragen
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
# target quote per position: from it on the position is green in the pitch plots, below red, keys as in POSITION_MAPPING,
# source: reports/Handball shooting quotes by level.md
# field players (amateur level): goals / all shots (saved, missed and blocked ones included)
PLAYER_TARGET_QUOTE = {"LA": 0.55, "RA": 0.55, "KM": 0.65, "L": 0.60, "R": 0.60, "M": 0.65,
                       "RL": 0.40, "RM": 0.45, "RR": 0.40, "K": 0.75, "7M": 0.70}
# keepers: saves / shots on goal (saves + goals)
KEEPER_TARGET_QUOTE = {"LA": 0.40, "RA": 0.40, "KM": 0.25, "L": 0.30, "R": 0.30, "M": 0.25,
                       "RL": 0.50, "RM": 0.45, "RR": 0.50, "K": 0.20, "7M": 0.20}
# the opponent half of the team pitch plots and the keeper pitch plots are mirrored (goal on the right),
# like on a real pitch; False: all halves face the same way (goal on the left)
MIRROR_OPPONENT = True
# the goal is 3m wide and 2m high, the shot coordinates in the goal go from 0 to 100 in both directions
GOAL_HEIGHT_RATIO = 2 / 3
