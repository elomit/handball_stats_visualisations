from pptx import Presentation
from pptx.util import Inches

from Analysis import Analysis

def add_image_to_ppt(img_path, ppt, left=1, top=1, width=8, height=5):
    slide_layout = ppt.slide_layouts[5]
    slide = ppt.slides.add_slide(slide_layout)
    slide.shapes.add_picture(img_path, left=Inches(left), top=Inches(top), width=Inches(width), height=Inches(height))


def create_ppt(analysis: Analysis):
    ppt = Presentation()

    if analysis.image_path:
        add_image_to_ppt(analysis.image_path, ppt)

    # TODO add table of contents

    add_images_to_ppt(analysis.sub_analyses, ppt)

    return ppt


def add_images_to_ppt(analyses: list[Analysis], ppt: Presentation):
    for analysis in analyses:
        if analysis.image_path:
            add_image_to_ppt(analysis.image_path, ppt)
        if len(analysis.sub_analyses) > 0:
            add_images_to_ppt(analysis.sub_analyses, ppt)
