import os

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
