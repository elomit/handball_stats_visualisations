"""
This script creates an analysis for multiple games.
"""

import os

import pandas as pd

from constants import MULTIPLE_GAMES_FOLDER_PATH
from main import normal_game_analysis
from parsing import parse_json

def main():
    """Generate multiple game analysis."""

    all_data = merge_game_data(MULTIPLE_GAMES_FOLDER_PATH)

    normal_game_analysis(all_data)

def merge_game_data(path_to_folder):
    """Read all JSON files in the folder and merge them into one dataframe."""

    all_data = pd.DataFrame()
    for filename in os.listdir(path_to_folder):
        if filename.endswith(".json"):
            full_path = os.path.join(path_to_folder, filename)
            with open(full_path, encoding="utf-8") as json_data:
                try:
                    data = parse_json(json_data.read())
                    all_data = pd.concat([data, all_data], ignore_index=True)
                except:
                    print("filename is not a valid gamedata file")
                finally:
                    json_data.close()

    return all_data

if __name__ == '__main__':
    main()
