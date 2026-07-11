"""This module creates a pdf report based on the analysis graphs."""

import os
from typing import Tuple
from fpdf import FPDF
from PIL import Image
from Analysis import Analysis


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

    _add_analysis_to_pdf(pdf, report)

    if pdf.page_no() == 0:
        pdf.add_page()
        pdf.set_font('helvetica', size=12)
        pdf.cell(0, 10, 'No analysis content was available.', ln=True)

    pdf.output(output_file_path)
    return output_file_path


def _add_analysis_to_pdf(pdf: FPDF, analysis: Analysis) -> None:
    """Helper function to add graphs to pdf report."""

    # add graph to analysis
    if analysis.image_path:
        image_path = analysis.image_path
        if os.path.isfile(image_path):
            pdf.add_page()
            page_width = pdf.w
            page_height = pdf.h
            img_width, img_height = _fit_image_size(image_path, page_width - 30, page_height - 30)

            x = (page_width - img_width) / 2
            y = (page_height - img_height) / 2
            pdf.image(image_path, x=x, y=y, w=img_width, h=img_height)

    for child in analysis.sub_analyses:
        _add_analysis_to_pdf(pdf, child)


def _fit_image_size(image_path: str, max_width: float, max_height: float) -> Tuple[float, float]:
    """Helper function to fit images in the pdf."""

    with Image.open(image_path) as img:
        img_w, img_h = img.size

    ratio = min(max_width / img_w, max_height / img_h, 1.0)
    return img_w * ratio, img_h * ratio
