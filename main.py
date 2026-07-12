import os
from os import makedirs
from os.path import isdir

import pandas as pd

from Analysis import Analysis
from constants import PATH, OUTPUT_DIR, TITLE_IMG_PATH, PDF_FILE_PATH, POSITION_MAPPING
from parsing import parse_json
from pdf_creation import create_pdf
from shot_analysis import analyze_keeper, analyze_shots
from table_analysis import game_analysis_table
from mistakes_analysis import mistake_analysis_table
from timeline_analysis import full_game_analysis_new, seconds_per_attack

"""
This script used the json file from the Handballfreunde Statistik App.
Execute with python main.py.
Analysis can then be found in the output folder.
"""

# TODO create input folder and parse every file in it
def main():
    if not isdir(OUTPUT_DIR):
        makedirs(OUTPUT_DIR)

    # Import data from json and parse it for further analysis.
    with open(PATH, encoding="utf-8") as json_data:
        data = parse_json(json_data.read())
        json_data.close()

    normal_game_analysis(data)


def normal_game_analysis(data: pd.DataFrame):

    # rename position to be more readable
    data["location"] = data["location"].replace(POSITION_MAPPING)

    # Create Analyses
    analysis = Analysis(TITLE_IMG_PATH, 6, 7, 0.25, 2)
    analysis.add_analysis(full_game_analysis_new(data))
    analysis.add_analysis(game_analysis_table(data, POSITION_MAPPING))
    analysis.add_analysis(mistake_analysis_table(data, POSITION_MAPPING))
    analysis.add_analysis(seconds_per_attack(data))
    analysis.add_analysis(analyze_shots(data))
    analysis.add_analysis(analyze_keeper(data))

    # Create pdf
    try:
        pdf_path = create_pdf(analysis, PDF_FILE_PATH)
        print(f'Created PDF report at {pdf_path}')
    except Exception as e:
        print(f'Error while creating PDF: {e}')


if __name__ == '__main__':
    main()
