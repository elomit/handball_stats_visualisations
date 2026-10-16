from os import makedirs
from os.path import isdir

import matplotlib
import pandas as pd

# headless backend, images are only saved to files (also avoids conflicts with a GUI like kivy)
matplotlib.use("Agg")

from Analysis import Analysis  # noqa: E402
from constants import PATH, OUTPUT_DIR, TITLE_IMG_PATH, PDF_FILE_PATH, POSITION_MAPPING  # noqa: E402
from field_analysis import mistake_field_analysis  # noqa: E402
from parsing import parse_json  # noqa: E402
from pdf_creation import create_pdf  # noqa: E402
from shot_analysis import analyze_keeper, analyze_shots, analyze_shots_overall  # noqa: E402
from table_analysis import player_position_summary_table  # noqa: E402
from timeline_analysis import full_game_analysis_new, seconds_per_attack  # noqa: E402

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
    # Normal shot analysis table not needed since the pitch-plot displays that information better
    # analysis.add_analysis(game_analysis_table(data, POSITION_MAPPING))
    # Mistake table not needed since the pitch-plot displays that information better
    # analysis.add_analysis(mistake_analysis_table(data, POSITION_MAPPING))
    analysis.add_analysis(mistake_field_analysis(data, POSITION_MAPPING))
    analysis.add_analysis(seconds_per_attack(data))
    analysis.add_analysis(player_position_summary_table(data))
    analysis.add_analysis(analyze_shots_overall(data))
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
