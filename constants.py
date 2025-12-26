import os

MISSED_SHOTS_FIELDS = ['Block', 'Verworfen', 'Gehalten']
SCORED_SHOTS_FIELDS = ["Tor"]
SHOT_FIELDS = ["Tor", "Gehalten", "Verworfen", "Block"]
GOALIE_SHOTS_FIELDS = ["Tor", "Gehalten", "Verworfen"]

FILENAME = "merged" # hier filename eintragen
CURRENT_DIR = os.getcwd()
PATH = rf"{CURRENT_DIR}/input/{FILENAME}.json"
OUTPUT_DIR = CURRENT_DIR + "/output/"
PPT_FILE_PATH = rf"{OUTPUT_DIR}/{FILENAME}.ppt"
PDF_FILE_PATH = rf"{OUTPUT_DIR}/{FILENAME}.pdf"
TITLE_IMG_PATH = rf"{CURRENT_DIR}/woran-hat-es-gelegen-winner.png"
MULTIPLE_GAMES_FOLDER_PATH = rf"{CURRENT_DIR}/input/Zweite_Ergebnisse_2025"
POSITION_MAPPING = {
    "LA": "Linksaußen",
    "RA": "Rechtsaußen",
    "KM": "Kreis",
    "L": "Halblinks 6M",
    "R": "Halbrechts 6M",
    "M": "Mitte 6M",
    "RL": "Halblinks 9M",
    "RM": "Mitte 9M",
    "RR": "Halbrechts 9M",
    "K": "Konter",
    "7M": "7M"
}
CORRECT_PLAYER_NAMES = {
        'Matthias KloÃŸ' : 'Matthias Kloß',
        'Brian Mathias JÃ¤ger' :  'Brian Mathias Jäger',
        'Nenad PeÅ¡iÄ‡' : 'Nenad Pešić',
        'Axel' : 'Axel Trathnigg',
        'Robert Ã–rtel' : 'Robert Örtel',
        'Martin FlieÃŸ' : 'Martin Fließ',
        'timo' : 'unbekannter Spieler 1',
        'Franz JaÃŸ' : 'unbekannter Spieler 2',
        'Sven BaumgÃ¤rtner' : 'Sven Baumgärtner'
}
