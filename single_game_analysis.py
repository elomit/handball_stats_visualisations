from os import makedirs
from os.path import basename, isdir

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
from timeline_analysis import full_game_analysis_new, seconds_per_attack  # noqa: E402

"""
This script used the json file from the Handballfreunde Statistik App.
Execute with python single_game_analysis.py.
Analysis can then be found in the output folder.
"""

# TODO create input folder and parse every file in it
def main():
    # Import data from json and parse it for further analysis.
    # the raw file is kept to embed it into the pdf, so the report can be recalculated from the pdf
    with open(PATH, "rb") as json_file:
        content = json_file.read()
    data = parse_json(content.decode("utf-8"))

    normal_game_analysis(data, [(basename(PATH), content)])


def normal_game_analysis(data: pd.DataFrame, source_files: list[tuple[str, bytes]]):
    """Create the analyses and the pdf, source_files are the json files (name, content) the data was parsed from,
    they are embedded into the pdf."""

    # here and not in main(), so the output folder also exists for multiple_game_analysis.py and reparse_pdf.py
    if not isdir(OUTPUT_DIR):
        makedirs(OUTPUT_DIR)

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
    analysis.add_analysis(analyze_shots_overall(data))
    analysis.add_analysis(analyze_shots(data))
    analysis.add_analysis(analyze_keeper(data))

    # Create pdf
    try:
        pdf_path = create_pdf(analysis, PDF_FILE_PATH, source_files)
        print(f'Created PDF report at {pdf_path}')
    except Exception as e:
        print(f'Error while creating PDF: {e}')


if __name__ == '__main__':
    main()
