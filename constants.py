import os

MISSED_SHOTS_FIELDS = ['Block', 'Verworfen', 'Gehalten']
SCORED_SHOTS_FIELDS = ["Tor"]
SHOT_FIELDS = ["Tor", "Gehalten", "Verworfen", "Block"]
GOALIE_SHOT_FIELDS = ["Tor", "Gehalten", "Verworfen"]

FILENAME = "Hbfr Pankow II_SCC II_1741392000" # hier filename eintragen
CURRENT_DIR = os.getcwd()
PATH = rf"{CURRENT_DIR}/input/{FILENAME}.json"
OUTPUT_DIR = CURRENT_DIR + "/output/"
PPT_FILE_PATH = rf"{OUTPUT_DIR}/{FILENAME}.ppt"
PPT_FILE_PATH_NEW = rf"{OUTPUT_DIR}/{FILENAME}_new.ppt"
PDF_FILE_PATH = rf"{OUTPUT_DIR}/{FILENAME}.pdf"
TITLE_IMG_PATH = rf"{CURRENT_DIR}/woran-hat-es-gelegen-winner.png"
