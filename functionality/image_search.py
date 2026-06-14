from pathlib import Path

import cv2 as cv
import numpy as np
from PIL import ImageGrab

from wrappers.logging_wrapper import debug


def grab_region(region):
    """Capture search region as BGR numpy array."""
    region_x, region_y, width, height = region
    bbox = (region_x, region_y, region_x + width, region_y + height)
    screenshot = ImageGrab.grab(bbox=bbox)
    return cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2BGR)


def probe_template(screenshot_cv, region, template_path, threshold=0.7):
    """
    Run template match; always returns best score (for diagnostics).

    Returns dict: ok, found, score, center (x,y)|None, error|None.
    """
    region_x, region_y, _width, _height = region
    template = cv.imread(str(template_path))
    if template is None:
        return {
            "ok": False,
            "found": False,
            "score": 0.0,
            "center": None,
            "error": f"Template unreadable: {template_path}",
        }

    template_h, template_w = template.shape[:2]
    if screenshot_cv.shape[0] < template_h or screenshot_cv.shape[1] < template_w:
        return {
            "ok": False,
            "found": False,
            "score": 0.0,
            "center": None,
            "error": (
                f"Region too small for {Path(template_path).name}: "
                f"{screenshot_cv.shape[1]}x{screenshot_cv.shape[0]} vs {template_w}x{template_h}"
            ),
        }

    result = cv.matchTemplate(screenshot_cv, template, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(result)
    score = float(max_val)

    debug(
        f"Template {Path(template_path).name} best score {score:.3f} at {max_loc}"
    )

    match_x, match_y = max_loc
    center_x = region_x + match_x + template_w // 2
    center_y = region_y + match_y + template_h // 2
    found = score >= threshold

    return {
        "ok": True,
        "found": found,
        "score": score,
        "center": (center_x, center_y) if found else None,
        "error": None,
    }


def find_template(region, template_path, threshold=0.7):
    """
    Search for a template image inside a screen region.

    region: (x, y, width, height) in screen coordinates
    Returns (center_x, center_y, score) or None if not found.
    """
    screenshot_cv = grab_region(region)
    probe = probe_template(screenshot_cv, region, template_path, threshold)
    if not probe["ok"]:
        if probe["error"] and "unreadable" in probe["error"]:
            raise FileNotFoundError(probe["error"])
        debug(probe["error"])
        return None
    if not probe["found"]:
        return None

    center_x, center_y = probe["center"]
    return center_x, center_y, probe["score"]
