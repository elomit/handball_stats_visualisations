"""
This script creates an analysis for multiple games.
"""

import os

from constants import MULTIPLE_GAMES_FOLDER_PATH
from single_game_analysis import normal_game_analysis
from parsing import parse_games


def main():
    """Generate multiple game analysis."""

    all_data, source_files = parse_games(read_game_files(MULTIPLE_GAMES_FOLDER_PATH))

    normal_game_analysis(all_data, source_files)


def read_game_files(path_to_folder: str) -> list[tuple[str, bytes]]:
    """Read all JSON files in the folder as (file name, content), sorted by name so the merge order is always the same."""

    source_files = []
    for filename in sorted(os.listdir(path_to_folder)):
        if filename.endswith(".json"):
            with open(os.path.join(path_to_folder, filename), "rb") as json_file:
                source_files.append((filename, json_file.read()))

    return source_files


if __name__ == '__main__':
    main()
