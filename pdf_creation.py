"""This module creates a pdf report based on the analysis graphs."""

import os
from typing import Tuple
from fpdf import FPDF
from PIL import Image, ImageColor
from Analysis import Analysis
from colors import LINK_COLOR, TEXT_COLOR, SECONDARY_TEXT_COLOR

# button that links back to the index on every page: x, y, width, height in mm
INDEX_BUTTON = (10, 10, 30, 8)


def create_pdf(report: Analysis, output_file_path: str) -> str:
    """Render analysis images into a PDF and save it to output_file_path."""

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

    # title page first, then the index on page 2 (filled at the end, when all page numbers are known)
    _add_image_page(pdf, report.image_path)
    pdf.add_page()
    # the content pages link back to the index
    pdf.index_link = pdf.add_link(page=pdf.page_no())
    pdf.insert_toc_placeholder(_render_index, allow_extra_pages=True, reset_page_indices=False)
    # the placeholder already starts the next (empty) page, the first analysis is drawn on it
    pdf.empty_page = pdf.page_no()
    for child in report.sub_analyses:
        _add_analysis_to_pdf(pdf, child)

    if pdf.page_no() == 0:
        pdf.add_page()
        pdf.set_font('helvetica', size=12)
        pdf.cell(0, 10, 'No analysis content was available.', ln=True)

    pdf.output(output_file_path)
    return output_file_path


def _add_analysis_to_pdf(pdf: FPDF, analysis: Analysis, level: int = 0, open_sections: tuple = (),
                         parent_titles: tuple = ()) -> None:
    """Helper function to add graphs to pdf report.

    Titled analyses start a section (index entry) on their page. An analysis without a page of its own
    hands its section on to its first sub analysis, so the index entry points to that page.
    The page title contains the titles of the parents too, e.g. "Wurfanalyse » player » position",
    the titles of the parents link to their pages.
    """

    # the link gets its page when the page of this analysis (or of its first sub analysis) is added
    link = pdf.add_link() if analysis.title else None
    titles = parent_titles + ((analysis.title.strip(), link),) if analysis.title else parent_titles
    sections = open_sections + ((analysis.title, level, link),) if analysis.title else open_sections
    if _add_image_page(pdf, analysis.image_path, titles):
        for title, section_level, section_link in sections:
            pdf.start_section(title, section_level)
            pdf.set_link(section_link, page=pdf.page_no())
        sections = ()

    child_level = level + 1 if analysis.title else level
    for i, child in enumerate(analysis.sub_analyses):
        _add_analysis_to_pdf(pdf, child, child_level, sections if i == 0 else (), titles)


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
    pdf.set_font('helvetica', 'B', font_size)
    # the underline doesn't change the width, so the width can be measured with the normal bold font
    while pdf.get_string_width(text) > max_width and font_size > 8:
        font_size -= 0.5
        pdf.set_font('helvetica', 'B', font_size)
    pdf.set_xy((pdf.w - pdf.get_string_width(text)) / 2, 10)

    for i, (title, link) in enumerate(titles):
        is_page = i == len(titles) - 1
        if i > 0:
            pdf.set_font('helvetica', 'B', font_size)
            pdf.set_text_color(*_rgb(TEXT_COLOR))
            pdf.cell(pdf.get_string_width(separator), 10, separator)
        pdf.set_font('helvetica', 'B' if is_page else 'BU', font_size)
        pdf.set_text_color(*_rgb(TEXT_COLOR if is_page else LINK_COLOR))
        pdf.cell(pdf.get_string_width(title), 10, title, link='' if is_page else link)


def _add_index_button(pdf: FPDF) -> None:
    """Button in the upper left corner that links back to the index."""

    x, y, width, height = INDEX_BUTTON
    pdf.set_draw_color(*_rgb(LINK_COLOR))
    pdf.set_line_width(0.4)
    pdf.rect(x, y, width, height, round_corners=True, corner_radius=2)
    pdf.set_xy(x, y)
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(*_rgb(LINK_COLOR))
    pdf.cell(width, height, '« Übersicht', align='C', link=pdf.index_link)


def _render_index(pdf: FPDF, outline) -> None:
    """Index with links to the pages: analyses, players below them, and the positions of a player in the same line."""

    margin = 20
    pdf.set_xy(margin, margin)
    pdf.set_font('helvetica', 'B', 20)
    pdf.cell(0, 12, 'Übersicht', new_x='LMARGIN', new_y='NEXT')
    pdf.set_x(margin)
    pdf.set_font('helvetica', 'I', 10)
    pdf.set_text_color(*_rgb(SECONDARY_TEXT_COLOR))
    pdf.cell(0, 6, 'Auf einen blauen Eintrag klicken, um zur Seite zu springen', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    for i, section in enumerate(outline):
        if section.level > 1:
            continue
        # positions of a player are the following sections one level deeper
        positions = []
        for sub_section in outline[i + 1:]:
            if sub_section.level <= section.level:
                break
            if sub_section.level == section.level + 1:
                positions.append(sub_section)
        if section.level == 0:
            positions = []

        line_height = 8 if section.level == 0 else 6.5
        if pdf.get_y() + line_height > pdf.h - margin:
            pdf.add_page()
            pdf.set_y(margin)

        y = pdf.get_y()
        pdf.set_x(margin + 8 * section.level)
        pdf.set_text_color(*_rgb(LINK_COLOR))
        pdf.set_font('helvetica', 'BU' if section.level == 0 else 'U', 12 if section.level == 0 else 11)
        link = pdf.add_link(page=section.page_number)
        pdf.cell(pdf.get_string_width(section.name.strip()) + 2, line_height, section.name.strip(), link=link)

        for k, position in enumerate(positions):
            if k > 0:
                # the separator is no link, so it is neither blue nor underlined
                pdf.set_font('helvetica', '', 9)
                pdf.set_text_color(*_rgb(SECONDARY_TEXT_COLOR))
                pdf.cell(pdf.get_string_width(' · '), line_height, ' · ')
            pdf.set_font('helvetica', 'U', 9)
            pdf.set_text_color(*_rgb(LINK_COLOR))
            pdf.cell(pdf.get_string_width(position.name), line_height, position.name,
                     link=pdf.add_link(page=position.page_number))

        pdf.set_font('helvetica', 'BU' if section.level == 0 else 'U', 12 if section.level == 0 else 11)
        pdf.set_text_color(*_rgb(LINK_COLOR))
        pdf.set_xy(pdf.w - margin - 20, y)
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
