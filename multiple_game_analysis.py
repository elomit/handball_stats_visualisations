import os
import pandas as pd

from Analysis import Analysis
from constants import TITLE_IMG_PATH, PPT_FILE_PATH, PDF_FILE_PATH, MULTIPLE_GAMES_FOLDER_PATH, POSITION_MAPPING, CORRECT_PLAYER_NAMES
from parsing import parse_json
from ppt_creation import create_ppt
from pdf_creation import ppt_to_pdf
from shot_analysis import analyze_keeper, analyze_shots
from table_analysis import game_analysis_table
from timeline_analysis import full_game_analysis_new


def merge_game_data(path_to_folder):
    """Read all JSON files in the folder and merge them into one dataframe."""

    all_data = pd.DataFrame()
    for filename in os.listdir(path_to_folder):
        if filename.endswith(".json"):
            full_path = os.path.join(path_to_folder, filename)
            with open(full_path) as json_data:
                data = parse_json(json_data.read())
                json_data.close()
                all_data = pd.concat([data, all_data], ignore_index=True)
    
    return all_data


def main():
    """Generate multiple game analysis."""
    
    all_data = merge_game_data(MULTIPLE_GAMES_FOLDER_PATH)

    # rename position to be more readable
    all_data["location"] = all_data["location"].replace(POSITION_MAPPING)

    # correct names
    all_data.player_name = all_data.player_name.replace(CORRECT_PLAYER_NAMES)

    # Create Analyses
    analysis = Analysis(TITLE_IMG_PATH,6,7, 0.25, 2)
    analysis.add_analysis(full_game_analysis_new(all_data))
    analysis.add_analysis(game_analysis_table(all_data,POSITION_MAPPING))
    analysis.add_analysis(analyze_shots(all_data))
    analysis.add_analysis(analyze_keeper(all_data))

    # Create ppt
    ppt = create_ppt(analysis)

    try:
        ppt.save(PPT_FILE_PATH)
    except PermissionError:
        print("Kollege! Mach die PowerPoint zu, es zieht! Dann nochmal probieren bitte (-_-)")
        os.system("TASKKILL /F /IM powerpnt.exe")


    try:
        ppt_to_pdf(PPT_FILE_PATH, PDF_FILE_PATH)
        print(f'PDF wurde erstellt in {PDF_FILE_PATH}.')
    except:
        print('PDF muss noch erstellt werden.')


if __name__ == '__main__':
    main()