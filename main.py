import os
from os import makedirs
from os.path import isdir

from Analysis import Analysis
from constants import PATH, OUTPUT_DIR, TITLE_IMG_PATH, PPT_FILE_PATH
from parsing import parse_json
from ppt_creation import create_ppt
from shot_analysis import analyze_keeper, analyze_shots
from table_analysis import game_analysis_table
from timeline_analysis import full_game_analysis_new, seconds_per_attack

"""
This script used the json file from the Handballfreunde Statistik App.
Execute with python handball_stats_visualisation.py.
Analysis can then be found in the output folder.
"""

# TODO create input folder and parse every file in it
def main():
    if not isdir(OUTPUT_DIR):
        makedirs(OUTPUT_DIR)

    # Import data from json and parse it for further analysis.
    with open(PATH) as json_data:
        data = parse_json(json_data.read())
        json_data.close()

    # Create Analyses
    analysis = Analysis(TITLE_IMG_PATH,6,7, 0.25, 2)

    analysis.add_analysis(full_game_analysis_new(data))
    analysis.add_analysis(game_analysis_table(data))
    analysis.add_analysis(seconds_per_attack(data))
    analysis.add_analysis(analyze_shots(data))
    analysis.add_analysis(analyze_keeper(data))

    # Create ppt
    ppt = create_ppt(analysis)

    try:
        ppt.save(PPT_FILE_PATH)
    except PermissionError:
        print("Kollege! Mach die PowerPoint zu, es zieht! Dann nochmal probieren bitte (-_-)")
        os.system("TASKKILL /F /IM powerpnt.exe")

    # TODO platform based ppt/pdf saving


if __name__ == '__main__':
    main()
