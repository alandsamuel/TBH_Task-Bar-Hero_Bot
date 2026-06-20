import sys
from pathlib import Path

# ── Window scale ──
WINDOW_SCALES = ("1", "1.25", "1.5", "2")
DEFAULT_WINDOW_SCALE = "1"

# ── Default timing values (seconds) ──
DEFAULT_LOOP_MIN = 1.2
DEFAULT_LOOP_MAX = 1.8

DEFAULT_STEP_WAIT_MIN = 3.0
DEFAULT_STEP_WAIT_MAX = 5.0

DEFAULT_COMBINE_WAIT_MIN = 2.5
DEFAULT_COMBINE_WAIT_MAX = 3.5

DEFAULT_INTERVAL_MIN = 3.0
DEFAULT_INTERVAL_MAX = 5.0

DEFAULT_BETWEEN_CLICKS_MIN = 0.2
DEFAULT_BETWEEN_CLICKS_MAX = 0.6

# ── Hard timeout cap (seconds) ──
MAX_TIMEOUT = 5.0

# ── Spread defaults for single-value → range conversions ──
DEFAULT_SECONDS_SPREAD = 0.2
DEFAULT_MS_SPREAD = 0.15

# ── Click offset defaults (pixels) ──
DEFAULT_CLICK_OFFSET_MIN = -6
DEFAULT_CLICK_OFFSET_MAX = 6

# ── GUI overlay ──
MIN_REGION_SIZE = 20
OVERLAY_ALPHA = 0.25

# ── Diagnostics status colors ──
STATUS_COLORS = {
    "PASS": "#1a7f37",
    "WARN": "#9a6700",
    "FAIL": "#cf222e",
}
