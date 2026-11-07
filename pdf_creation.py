"""This module creates a pdf report based on the analysis graphs."""

import os
from typing import Tuple
from fpdf import FPDF
from PIL import Image, ImageColor
from Analysis import Analysis
from colors import LINK_COLOR, TEXT_COLOR, SECONDARY_TEXT_COLOR
from constants import SOURCE_FILE_DESCRIPTION, PDF_FONT_PATH, PDF_BOLD_FONT_PATH

# button that links back to the index on every page: x, y, width, height in mm
INDEX_BUTTON = (10, 10, 30, 8)
# family name of the unicode font (PDF_FONT_PATH) in the pdf
FONT = 'dejavu'
# layout of the index in mm: margin, height of the heading and the gap below it,
# line heights of the analyses (level 0) and of the players (level 1)
INDEX_MARGIN = 20
INDEX_HEADING_HEIGHT = 12
INDEX_HEADING_GAP = 4
INDEX_LINE_HEIGHTS = (8, 6.5)


def create_pdf(report: Analysis, output_file_path: str, source_files: list[tuple[str, bytes]] = ()) -> str:
    """Render analysis images into a PDF and save it to output_file_path.

    source_files are the json files (name, content) of the analysed games, they are embedded into the pdf
    (shown as attachments in most pdf viewers), so the report can be recalculated from the pdf (reparse_pdf.py).
    """

    # add .pdf if not there yet
    if not output_file_path.lower().endswith('.pdf'):
        output_file_path += '.pdf'

    # create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # L for vertical orintation, that way the imgages fit well
    pdf = FPDF('L', 'mm', 'A4')
    pdf.set_auto_page_break(auto=False)
    pdf.add_font(FONT, '', PDF_FONT_PATH)
    pdf.add_font(FONT, 'B', PDF_BOLD_FONT_PATH)

    # the pages are planned first, so the number of index pages is known before the content pages are added
    pages = [page for child in report.sub_analyses for page in _plan_pages(child)]
    levels = [level for _, _, sections in pages for _, level, _ in sections]
    index_pages = len(_index_layout(levels, pdf.h))

    # title page first, then the index from page 2 on (filled at the end, when all page numbers are known)
    _add_image_page(pdf, report.image_path)
    pdf.add_page()
    # the content pages link back to the index
    pdf.index_link = pdf.add_link(page=pdf.page_no())
    pdf.insert_toc_placeholder(_render_index, pages=index_pages)
    # the placeholder already starts the next (empty) page, the first analysis is drawn on it
    pdf.empty_page = pdf.page_no()

    # link to the page of each titled analysis, set when its section starts
    links = {}
    for image_path, titles, sections in pages:
        for key in [key for _, key in titles] + [key for _, _, key in sections]:
            if key not in links:
                links[key] = pdf.add_link()
        _add_image_page(pdf, image_path, tuple((title, links[key]) for title, key in titles))
        for title, level, key in sections:
            pdf.start_section(title, level)
            pdf.set_link(links[key], page=pdf.page_no())

    if pdf.page_no() == 0:
        pdf.add_page()
        pdf.set_font(FONT, size=12)
        pdf.cell(0, 10, 'No analysis content was available.', ln=True)

    for name, content in source_files:
        pdf.embed_file(bytes=content, basename=name, desc=SOURCE_FILE_DESCRIPTION, mime_type='application/json',
                       associated_file_relationship='Source', compress=True)

    pdf.output(output_file_path)
    return output_file_path


def _plan_pages(analysis: Analysis, level: int = 0, open_sections: tuple = (), parent_titles: tuple = ()) -> list:
    """Pages of the analysis and its sub analyses in pdf order as (image_path, titles, sections).

    The page title contains the titles of the parents too, e.g. "Wurfanalyse » player » position": titles are
    (title, analysis) of the parents and of the page, the titles of the parents link to their pages.
    Titled analyses start a section (index entry) on their page: sections are (title, level, analysis).
    An analysis without a page of its own hands its section on to its first sub analysis,
    so the index entry points to that page.
    """

    titles = parent_titles + ((analysis.title, analysis),) if analysis.title else parent_titles
    sections = open_sections + ((analysis.title, level, analysis),) if analysis.title else open_sections
    pages = []
    if analysis.image_path and os.path.isfile(analysis.image_path):
        pages.append((analysis.image_path, titles, sections))
        sections = ()

    child_level = level + 1 if analysis.title else level
    for i, child in enumerate(analysis.sub_analyses):
        pages += _plan_pages(child, child_level, sections if i == 0 else (), titles)
    return pages


def _add_image_page(pdf: FPDF, image_path: str, titles: tuple = ()) -> bool:
    """Add a page with the title at the top and the image centered below it, returns False if there is no image.

    titles are (title, link) of the parents and of this page, they are shown as "parent » ... » page".
    """

    if not image_path or not os.path.isfile(image_path):
        return False

    if getattr(pdf, 'empty_page', None) != pdf.page_no():
        pdf.add_page()
    pdf.empty_page = None
    page_width = pdf.w
    page_height = pdf.h

    # the title takes the upper part of the page, the image is centered in the rest
    top = 15
    if titles:
        _add_breadcrumb(pdf, titles)
        _add_index_button(pdf)
        top = 25

    img_width, img_height = _fit_image_size(image_path, page_width - 30, page_height - top - 15)

    x = (page_width - img_width) / 2
    y = top + (page_height - top - 15 - img_height) / 2
    pdf.image(image_path, x=x, y=y, w=img_width, h=img_height)
    return True


def _add_breadcrumb(pdf: FPDF, titles: tuple) -> None:
    """Centered page title "parent » ... » page", the parents are links (blue and underlined) to their pages.
    Long titles get a smaller font, so they don't run into the index button."""

    separator = ' » '
    text = separator.join(title for title, _ in titles)
    # same space on both sides, so the title stays centered
    button_x, _, button_width, _ = INDEX_BUTTON
    max_width = pdf.w - 2 * (button_x + button_width + 5)
    font_size = 16
    pdf.set_font(FONT, 'B', font_size)
    # the underline doesn't change the width, so the width can be measured with the normal bold font
    while pdf.get_string_width(text) > max_width and font_size > 8:
        font_size -= 0.5
        pdf.set_font(FONT, 'B', font_size)
    pdf.set_xy((pdf.w - pdf.get_string_width(text)) / 2, 10)

    for i, (title, link) in enumerate(titles):
        is_page = i == len(titles) - 1
        if i > 0:
            pdf.set_font(FONT, 'B', font_size)
            pdf.set_text_color(*_rgb(TEXT_COLOR))
            pdf.cell(pdf.get_string_width(separator), 10, separator)
        pdf.set_font(FONT, 'B' if is_page else 'BU', font_size)
        pdf.set_text_color(*_rgb(TEXT_COLOR if is_page else LINK_COLOR))
        pdf.cell(pdf.get_string_width(title), 10, title, link='' if is_page else link)


def _add_index_button(pdf: FPDF) -> None:
    """Button in the upper left corner that links back to the index."""

    x, y, width, height = INDEX_BUTTON
    pdf.set_draw_color(*_rgb(LINK_COLOR))
    pdf.set_line_width(0.4)
    pdf.rect(x, y, width, height, round_corners=True, corner_radius=2)
    pdf.set_xy(x, y)
    pdf.set_font(FONT, 'B', 10)
    pdf.set_text_color(*_rgb(LINK_COLOR))
    pdf.cell(width, height, '« Übersicht', align='C', link=pdf.index_link)


def _render_index(pdf: FPDF, outline) -> None:
    """Index with links to the pages: analyses, players below them, and the positions of a player in the same line.
    The pages for it are reserved in create_pdf with the same _index_layout."""

    pdf.set_xy(INDEX_MARGIN, INDEX_MARGIN)
    pdf.set_font(FONT, 'B', 20)
    pdf.set_text_color(*_rgb(TEXT_COLOR))
    pdf.cell(0, INDEX_HEADING_HEIGHT, 'Übersicht', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(INDEX_HEADING_GAP)

    for page_index, lines in enumerate(_index_layout([section.level for section in outline], pdf.h)):
        if page_index > 0:
            # moves on to the next reserved index page
            pdf.add_page()
            pdf.set_y(INDEX_MARGIN)
        for i, positions in lines:
            _render_index_line(pdf, outline[i], [outline[k] for k in positions])


def _index_layout(levels: list, page_height: float) -> list:
    """Lines of the index split into pages, computed only from the levels of the sections (in pdf order),
    so the number of index pages is known before the pages of the sections are added.

    A line is (i, positions) with indices into levels: section i is an analysis (level 0) or a player (level 1),
    positions are the following sections one level deeper (the positions of a player), shown in the line of the player.
    The first page starts below the heading, the following pages at the margin.
    """

    pages = [[]]
    y = INDEX_MARGIN + INDEX_HEADING_HEIGHT + INDEX_HEADING_GAP
    for i, level in enumerate(levels):
        if level > 1:
            continue
        positions = []
        if level == 1:
            for k in range(i + 1, len(levels)):
                if levels[k] <= level:
                    break
                if levels[k] == level + 1:
                    positions.append(k)

        line_height = INDEX_LINE_HEIGHTS[level]
        if y + line_height > page_height - INDEX_MARGIN:
            pages.append([])
            y = INDEX_MARGIN
        pages[-1].append((i, positions))
        y += line_height
    return pages


def _render_index_line(pdf: FPDF, section, positions: list) -> None:
    """Line of the index: title and positions as links, page number on the right."""

    line_height = INDEX_LINE_HEIGHTS[section.level]
    y = pdf.get_y()
    pdf.set_x(INDEX_MARGIN + 8 * section.level)
    pdf.set_text_color(*_rgb(LINK_COLOR))
    pdf.set_font(FONT, 'BU' if section.level == 0 else 'U', 12 if section.level == 0 else 11)
    link = pdf.add_link(page=section.page_number)
    pdf.cell(pdf.get_string_width(section.name) + 2, line_height, section.name, link=link)

    for k, position in enumerate(positions):
        if k > 0:
            # the separator is no link, so it is neither blue nor underlined
            pdf.set_font(FONT, '', 9)
            pdf.set_text_color(*_rgb(SECONDARY_TEXT_COLOR))
            pdf.cell(pdf.get_string_width(' · '), line_height, ' · ')
        pdf.set_font(FONT, 'U', 9)
        pdf.set_text_color(*_rgb(LINK_COLOR))
        pdf.cell(pdf.get_string_width(position.name), line_height, position.name,
                 link=pdf.add_link(page=position.page_number))

    pdf.set_font(FONT, 'BU' if section.level == 0 else 'U', 12 if section.level == 0 else 11)
    pdf.set_text_color(*_rgb(LINK_COLOR))
    pdf.set_xy(pdf.w - INDEX_MARGIN - 20, y)
    pdf.cell(20, line_height, str(section.page_number), align='R', link=link, new_x='LMARGIN', new_y='NEXT')


def _fit_image_size(image_path: str, max_width: float, max_height: float) -> Tuple[float, float]:
    """Helper function to fit images in the pdf."""

    with Image.open(image_path) as img:
        img_w, img_h = img.size

    ratio = min(max_width / img_w, max_height / img_h, 1.0)
    return img_w * ratio, img_h * ratio


def _rgb(color: str) -> Tuple[int, int, int]:
    """Hex color from colors.py as (r, g, b) from 0 to 255 for fpdf."""

    return ImageColor.getrgb(color)
