"""
This script recalculates a pdf report from the json files embedded in it (e.g. after the analysis changed).
Put the pdf at REPARSE_PDF_PATH and execute with python reparse_pdf.py, the new report is saved to PDF_FILE_PATH.
Reports with one embedded file are analysed like single_game_analysis.py, reports with several like multiple_game_analysis.py.
"""

from pypdf import PdfReader

from constants import REPARSE_PDF_PATH
from single_game_analysis import normal_game_analysis
from parsing import parse_games, parse_json


def main():
    source_files = read_source_files(REPARSE_PDF_PATH)
    if not source_files:
        print(f'{REPARSE_PDF_PATH} contains no embedded json files, it can not be recalculated')
        return

    if len(source_files) == 1:
        name, content = source_files[0]
        data = parse_json(content.decode("utf-8"))
    else:
        data, source_files = parse_games(source_files)

    normal_game_analysis(data, source_files)


def read_source_files(pdf_path: str) -> list[tuple[str, bytes]]:
    """Embedded json files of the pdf as (file name, content), sorted by name like in multiple_game_analysis.py."""

    attachments = PdfReader(pdf_path).attachments
    return [(name, contents[0]) for name, contents in sorted(attachments.items()) if name.endswith(".json")]


if __name__ == '__main__':
    main()
