from typing import Any

from pptx import Presentation
from pptx.util import Inches

from constants import TITLE_IMG_PATH


def add_image_to_ppt(img_path, ppt, left=1, top=1, width=8, height=5):
    slide_layout = ppt.slide_layouts[5]
    slide = ppt.slides.add_slide(slide_layout)
    slide.shapes.add_picture(img_path, left=Inches(left), top=Inches(top), width=Inches(width), height=Inches(height))


def create_ppt(images: dict[str, Any]):
    ppt = Presentation()

    # Title Slide
    add_image_to_ppt(TITLE_IMG_PATH, ppt, 2, 0, 6, 7)

    # TODO add table of contents

    add_images_to_ppt(images, ppt)

    return ppt


def add_images_to_ppt(images: dict[str, Any], ppt: Presentation):
    for element in images.values():
        if type(element) is dict:
            return add_images_to_ppt(element, ppt)
        elif type(element) is list:
            for image in element:
                add_image_to_ppt(image, ppt)
        elif type(element) is str:
            add_image_to_ppt(element, ppt)
        else:
            print("Error: " + str(type(element)) + " is not an expected type.")
            return

    return
