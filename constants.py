import os

MISSED_SHOTS_FIELDS = ['Block', 'Verworfen', 'Gehalten']
SCORED_SHOTS_FIELDS = ["Tor"]
SHOT_FIELDS = ["Tor", "Gehalten", "Verworfen", "Block"]
GOALIE_SHOTS_FIELDS = ["Tor", "Gehalten", "Verworfen"]

NAME = "" # hier filename (einzelnes Spiel) oder Ordnername (mehrere Spiele) eintragen
CURRENT_DIR = os.getcwd()
PATH = rf"{CURRENT_DIR}/input/{NAME}.json"
OUTPUT_DIR = CURRENT_DIR + "/output/"
PPT_FILE_PATH = rf"{OUTPUT_DIR}/{NAME}.ppt"
PDF_FILE_PATH = rf"{OUTPUT_DIR}/{NAME}.pdf"
TITLE_IMG_PATH = rf"{CURRENT_DIR}/woran-hat-es-gelegen-winner.png"
MULTIPLE_GAMES_FOLDER_PATH = rf"{CURRENT_DIR}/input/{NAME}"
POSITION_MAPPING = {
    "LA": "Linksaußen",
    "RA": "Rechtsaußen",
    "KM": "Kreis",
    "L": "Halblinks",
    "R": "Halbrechts",
    "M": "Mitte",
    "RL": "Rückraum Links",
    "RM": "Rückraum Mitte",
    "RR": "Rückraum Rechts",
    "K": "Konter",
    "7M": "7M"
}
