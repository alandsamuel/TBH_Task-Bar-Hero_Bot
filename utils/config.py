import random
from pathlib import Path
from tkinter import BooleanVar, DoubleVar, IntVar, StringVar

from yaml import dump, safe_load

from utils.constants import (
    DEFAULT_BETWEEN_CLICKS_MAX,
    DEFAULT_BETWEEN_CLICKS_MIN,
    DEFAULT_CLICK_OFFSET_MAX,
    DEFAULT_CLICK_OFFSET_MIN,
    DEFAULT_COMBINE_WAIT_MAX,
    DEFAULT_COMBINE_WAIT_MIN,
    DEFAULT_INTERVAL_MAX,
    DEFAULT_INTERVAL_MIN,
    DEFAULT_LOOP_MAX,
    DEFAULT_LOOP_MIN,
    DEFAULT_MS_SPREAD,
    DEFAULT_SECONDS_SPREAD,
    DEFAULT_STEP_WAIT_MAX,
    DEFAULT_STEP_WAIT_MIN,
    DEFAULT_WINDOW_SCALE,
    MAX_TIMEOUT,
    WINDOW_SCALES,
)
from utils.global_variables import BASE_DIR, CONFIG_PATH
_SCALE_SUFFIX = {
    "1": "",
    "1.25": "_1-25",
    "1.5": "_1-50",
    "2": "_2",
}
_SCALE_SUFFIXES = tuple(_SCALE_SUFFIX.values())


def _template_path(relative_path: str) -> str:
    return str((BASE_DIR / relative_path).resolve())


def _legacy_ms_range(raw_value, default_spread=DEFAULT_MS_SPREAD):
    """Parse legacy config values stored in milliseconds."""
    if isinstance(raw_value, dict):
        return int(raw_value["min"]), int(raw_value["max"])
    value = int(raw_value)
    spread = max(50, int(value * default_spread))
    return max(0, value - spread), value + spread


def _seconds_range(raw_value, default_spread=DEFAULT_SECONDS_SPREAD):
    if isinstance(raw_value, dict):
        return float(raw_value["min"]), float(raw_value["max"])
    value = float(raw_value)
    spread = max(0.05, value * default_spread)
    return max(0.0, round(value - spread, 2)), round(value + spread, 2)


def _offset_range(raw_config):
    if raw_config is None:
        return DEFAULT_CLICK_OFFSET_MIN, DEFAULT_CLICK_OFFSET_MAX
    if isinstance(raw_config, dict):
        return int(raw_config["min"]), int(raw_config["max"])
    value = int(raw_config)
    return -value, value


def _migrate_timing(section, old_key, new_key, default_min, default_max):
    """Upgrade legacy *_ms keys to second-based min/max dicts."""
    if new_key in section:
        min_s, max_s = _seconds_range(section[new_key])
    elif old_key in section:
        min_ms, max_ms = _legacy_ms_range(section[old_key])
        min_s, max_s = round(min_ms / 1000, 2), round(max_ms / 1000, 2)
    else:
        min_s, max_s = default_min, default_max
    section[new_key] = {"min": min_s, "max": max_s}
    section.pop(old_key, None)


def _normalize_config(config):
    """Upgrade older config.yml shapes to min/max ranges."""
    _migrate_timing(config["timeouts"], "loop_ms", "loop", DEFAULT_LOOP_MIN, DEFAULT_LOOP_MAX)
    if "step_wait" not in config["timeouts"]:
        config["timeouts"]["step_wait"] = {"min": DEFAULT_STEP_WAIT_MIN, "max": DEFAULT_STEP_WAIT_MAX}
    else:
        min_s, max_s = _seconds_range(config["timeouts"]["step_wait"])
        max_s = min(max_s, MAX_TIMEOUT)
        min_s = min(min_s, max_s)
        config["timeouts"]["step_wait"] = {"min": min_s, "max": max_s}

    after_click = config["timeouts"]["after_click"]
    if not isinstance(after_click, dict):
        min_s, max_s = _seconds_range(after_click)
        config["timeouts"]["after_click"] = {"min": min_s, "max": max_s}

    _migrate_timing(config["combine_flow"], "wait_ms", "wait", DEFAULT_COMBINE_WAIT_MIN, DEFAULT_COMBINE_WAIT_MAX)

    periodic = config["periodic_stash_sort"]
    _migrate_timing(periodic, "interval_ms", "interval", DEFAULT_INTERVAL_MIN, DEFAULT_INTERVAL_MAX)
    _migrate_timing(periodic, "between_clicks_ms", "between_clicks", DEFAULT_BETWEEN_CLICKS_MIN, DEFAULT_BETWEEN_CLICKS_MAX)
    interval = periodic["interval"]
    interval["max"] = min(interval["max"], MAX_TIMEOUT)
    interval["min"] = min(interval["min"], interval["max"])

    if "randomization" not in config:
        config["randomization"] = {}
    offset_min, offset_max = _offset_range(config["randomization"].get("click_offset_px"))
    config["randomization"]["click_offset_px"] = {"min": offset_min, "max": offset_max}

    scale = str(config.get("window_scale", DEFAULT_WINDOW_SCALE))
    config["window_scale"] = scale if scale in _SCALE_SUFFIX else DEFAULT_WINDOW_SCALE

    return config


def base_template_name(filename: str) -> str:
    """Strip scale suffix so config stores e.g. auto_fill.png, not auto_fill_1-25.png."""
    path = Path(filename)
    stem = path.stem
    for scale_suffix in _SCALE_SUFFIXES:
        if scale_suffix and stem.endswith(scale_suffix):
            return f"{stem[: -len(scale_suffix)]}{path.suffix}"
    return path.name


def _load_template_basename(relative_path: str) -> str:
    return base_template_name(Path(relative_path).name)


def _load_config():
    with open(CONFIG_PATH, encoding="utf-8") as config_file:
        return _normalize_config(safe_load(config_file))


config = _load_config()

dict = {
    "search_region": {
        "x": IntVar(value=config["search_region"]["x"]),
        "y": IntVar(value=config["search_region"]["y"]),
        "width": IntVar(value=config["search_region"]["width"]),
        "height": IntVar(value=config["search_region"]["height"]),
    },
    "matching": {
        "threshold": DoubleVar(value=config["matching"]["threshold"]),
    },
    "timeouts": {
        "loop": {
            "min": DoubleVar(value=config["timeouts"]["loop"]["min"]),
            "max": DoubleVar(value=config["timeouts"]["loop"]["max"]),
        },
        "after_click": {
            "min": DoubleVar(value=config["timeouts"]["after_click"]["min"]),
            "max": DoubleVar(value=config["timeouts"]["after_click"]["max"]),
        },
        "step_wait": {
            "min": DoubleVar(value=config["timeouts"]["step_wait"]["min"]),
            "max": DoubleVar(value=config["timeouts"]["step_wait"]["max"]),
        },
    },
    "combine_flow": {
        "wait": {
            "min": DoubleVar(value=config["combine_flow"]["wait"]["min"]),
            "max": DoubleVar(value=config["combine_flow"]["wait"]["max"]),
        },
        "template": StringVar(value=_load_template_basename(config["combine_flow"]["template"])),
        "back_template": StringVar(
            value=_load_template_basename(config["combine_flow"]["back_template"])
        ),
    },
    "periodic_stash_sort": {
        "interval": {
            "min": DoubleVar(value=config["periodic_stash_sort"]["interval"]["min"]),
            "max": DoubleVar(value=config["periodic_stash_sort"]["interval"]["max"]),
        },
        "between_clicks": {
            "min": DoubleVar(value=config["periodic_stash_sort"]["between_clicks"]["min"]),
            "max": DoubleVar(value=config["periodic_stash_sort"]["between_clicks"]["max"]),
        },
        "stash_template": StringVar(
            value=_load_template_basename(config["periodic_stash_sort"]["stash_template"])
        ),
        "sort_template": StringVar(
            value=_load_template_basename(config["periodic_stash_sort"]["sort_template"])
        ),
        "stash_enabled": BooleanVar(value=config["periodic_stash_sort"].get("stash_enabled", True)),
        "sort_enabled": BooleanVar(value=config["periodic_stash_sort"].get("sort_enabled", True)),
    },
    "randomization": {
        "click_offset_px": {
            "min": IntVar(value=config["randomization"]["click_offset_px"]["min"]),
            "max": IntVar(value=config["randomization"]["click_offset_px"]["max"]),
        },
    },
    "chest_check": [
        {
            "name": entry["name"],
            "template": StringVar(value=_load_template_basename(entry["template"])),
        }
        for entry in config["chest_check"]["templates"]
    ],
    "steps": [
        {
            "name": step["name"],
            "enabled": BooleanVar(value=step.get("enabled", True)),
            **(
                {"template": StringVar(value=_load_template_basename(step["template"]))}
                if "template" in step
                else {}
            ),
        }
        for step in config["steps"]
    ],
    "features": {
        "main_loop": BooleanVar(value=config.get("features", {}).get("main_loop", True)),
        "periodic_stash_sort": BooleanVar(value=config.get("features", {}).get("periodic_stash_sort", True)),
    },
    "log_lvl": StringVar(value=config.get("log_lvl", "INFO")),
    "window_scale": StringVar(value=config["window_scale"]),
}


def scaled_template_name(filename: str, scale: str | None = None) -> str:
    """Apply window scale suffix: 1 → no suffix, 1.25 → _1-25, 1.5 → _1-50, 2 → _2."""
    base = base_template_name(filename)
    path = Path(base)
    scale_key = scale if scale is not None else dict["window_scale"].get()
    suffix = _SCALE_SUFFIX.get(str(scale_key), "")
    return f"{path.stem}{suffix}{path.suffix}"


def _resolved_template(filename: str) -> str:
    name = Path(filename).name
    return _template_path(f"assets/{name}")


def template_path_for(variable) -> str:
    from wrappers.logging_wrapper import debug, warning

    base = base_template_name(variable.get())
    scaled = scaled_template_name(base)
    path = _resolved_template(scaled)
    if Path(path).is_file():
        debug(f"Template: {Path(path).name} (scale {dict['window_scale'].get()})")
        return path
    if scaled != base:
        warning(
            f"Scaled template missing: {scaled} (scale {dict['window_scale'].get()}), "
            f"trying base {base}"
        )
        path = _resolved_template(base)
    if not Path(path).is_file():
        raise FileNotFoundError(f"Template not found: {scaled} or {base}")
    return path


def chest_check_entries():
    return [
        {"name": entry["name"], "template": template_path_for(entry["template"])}
        for entry in dict["chest_check"]
    ]


def step_entries():
    steps = []
    for step in dict["steps"]:
        item = {"name": step["name"], "enabled": step["enabled"].get()}
        if "template" in step:
            item["template"] = template_path_for(step["template"])
        steps.append(item)
    return steps


def save_data():
    data = {
        "search_region": {
            "x": dict["search_region"]["x"].get(),
            "y": dict["search_region"]["y"].get(),
            "width": dict["search_region"]["width"].get(),
            "height": dict["search_region"]["height"].get(),
        },
        "matching": {
            "threshold": dict["matching"]["threshold"].get(),
        },
        "timeouts": {
            "loop": {
                "min": dict["timeouts"]["loop"]["min"].get(),
                "max": dict["timeouts"]["loop"]["max"].get(),
            },
            "after_click": {
                "min": dict["timeouts"]["after_click"]["min"].get(),
                "max": dict["timeouts"]["after_click"]["max"].get(),
            },
            "step_wait": {
                "min": dict["timeouts"]["step_wait"]["min"].get(),
                "max": dict["timeouts"]["step_wait"]["max"].get(),
            },
        },
        "combine_flow": {
            "wait": {
                "min": dict["combine_flow"]["wait"]["min"].get(),
                "max": dict["combine_flow"]["wait"]["max"].get(),
            },
            "template": f"assets/{base_template_name(dict['combine_flow']['template'].get())}",
            "back_template": f"assets/{base_template_name(dict['combine_flow']['back_template'].get())}",
        },
        "periodic_stash_sort": {
            "interval": {
                "min": dict["periodic_stash_sort"]["interval"]["min"].get(),
                "max": dict["periodic_stash_sort"]["interval"]["max"].get(),
            },
            "between_clicks": {
                "min": dict["periodic_stash_sort"]["between_clicks"]["min"].get(),
                "max": dict["periodic_stash_sort"]["between_clicks"]["max"].get(),
            },
            "stash_template": f"assets/{base_template_name(dict['periodic_stash_sort']['stash_template'].get())}",
            "sort_template": f"assets/{base_template_name(dict['periodic_stash_sort']['sort_template'].get())}",
            "stash_enabled": dict["periodic_stash_sort"]["stash_enabled"].get(),
            "sort_enabled": dict["periodic_stash_sort"]["sort_enabled"].get(),
        },
        "randomization": {
            "click_offset_px": {
                "min": dict["randomization"]["click_offset_px"]["min"].get(),
                "max": dict["randomization"]["click_offset_px"]["max"].get(),
            },
        },
        "chest_check": {
            "templates": [
                {
                    "name": entry["name"],
                    "template": f"assets/{base_template_name(entry['template'].get())}",
                }
                for entry in dict["chest_check"]
            ],
        },
        "steps": [
            {
                "name": step["name"],
                "enabled": step["enabled"].get(),
                **(
                    {"template": f"assets/{base_template_name(step['template'].get())}"}
                    if "template" in step
                    else {}
                ),
            }
            for step in dict["steps"]
        ],
        "features": {
            "main_loop": dict["features"]["main_loop"].get(),
            "periodic_stash_sort": dict["features"]["periodic_stash_sort"].get(),
        },
        "log_lvl": dict["log_lvl"].get(),
        "window_scale": dict["window_scale"].get(),
    }

    with open(CONFIG_PATH, "w", encoding="utf-8") as yaml_file:
        dump(data, yaml_file, sort_keys=False)


def random_timeout(range_dict):
    low = float(range_dict["min"].get() if hasattr(range_dict["min"], "get") else range_dict["min"])
    high = float(range_dict["max"].get() if hasattr(range_dict["max"], "get") else range_dict["max"])
    if low > high:
        low, high = high, low
    return round(random.uniform(low, high), 2)


def random_delay_ms(range_dict):
    return int(random_timeout(range_dict) * 1000)


def random_click_offset():
    offset = dict["randomization"]["click_offset_px"]
    low = int(offset["min"].get())
    high = int(offset["max"].get())
    if low > high:
        low, high = high, low
    return random.randint(low, high), random.randint(low, high)
