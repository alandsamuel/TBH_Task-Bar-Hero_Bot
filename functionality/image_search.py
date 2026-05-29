from pathlib import Path

import cv2 as cv
import numpy as np
from PIL import ImageGrab

from wrappers.logging_wrapper import debug


def find_template(region, template_path, threshold=0.7):
    """
    Search for a template image inside a screen region.

    region: (x, y, width, height) in screen coordinates
    Returns (center_x, center_y, score) or None if not found.
    """
    region_x, region_y, width, height = region
    bbox = (region_x, region_y, region_x + width, region_y + height)

    screenshot = ImageGrab.grab(bbox=bbox)
    screenshot_cv = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2BGR)

    template = cv.imread(str(template_path))
    if template is None:
        raise FileNotFoundError(f"Template not found or unreadable: {template_path}")

    template_h, template_w = template.shape[:2]
    if screenshot_cv.shape[0] < template_h or screenshot_cv.shape[1] < template_w:
        debug(
            f"Region too small for template {Path(template_path).name}: "
            f"{screenshot_cv.shape[1]}x{screenshot_cv.shape[0]} vs {template_w}x{template_h}"
        )
        return None

    result = cv.matchTemplate(screenshot_cv, template, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(result)

    debug(
        f"Template {Path(template_path).name} best score {max_val:.3f} at {max_loc}"
    )

    if max_val < threshold:
        return None

    match_x, match_y = max_loc
    center_x = region_x + match_x + template_w // 2
    center_y = region_y + match_y + template_h // 2
    return center_x, center_y, float(max_val)
