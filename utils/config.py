import random
from pathlib import Path
from tkinter import DoubleVar, IntVar

from yaml import dump, safe_load

from utils.global_variables import BASE_DIR, CONFIG_PATH


def _template_path(relative_path: str) -> str:
    return str((BASE_DIR / relative_path).resolve())


def _load_config():
    with open(CONFIG_PATH, encoding="utf-8") as config_file:
        return safe_load(config_file)


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
        "loop_ms": IntVar(value=config["timeouts"]["loop_ms"]),
        "after_click": {
            "min": config["timeouts"]["after_click"]["min"],
            "max": config["timeouts"]["after_click"]["max"],
        },
    },
    "combine_flow": {
        "wait_ms": IntVar(value=config["combine_flow"]["wait_ms"]),
        "template": _template_path(config["combine_flow"]["template"]),
        "back_template": _template_path(config["combine_flow"]["back_template"]),
    },
    "periodic_stash_sort": {
        "interval_ms": IntVar(value=config["periodic_stash_sort"]["interval_ms"]),
        "stash_template": _template_path(config["periodic_stash_sort"]["stash_template"]),
        "sort_template": _template_path(config["periodic_stash_sort"]["sort_template"]),
    },
    "chest_check": [
        {
            "name": entry["name"],
            "template": _template_path(entry["template"]),
        }
        for entry in config["chest_check"]["templates"]
    ],
    "steps": [
        {
            "name": step["name"],
            **(
                {"template": _template_path(step["template"])}
                if "template" in step
                else {}
            ),
        }
        for step in config["steps"]
    ],
    "log_lvl": config["log_lvl"],
}


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
            "loop_ms": dict["timeouts"]["loop_ms"].get(),
            "after_click": {
                "min": dict["timeouts"]["after_click"]["min"],
                "max": dict["timeouts"]["after_click"]["max"],
            },
        },
        "combine_flow": {
            "wait_ms": dict["combine_flow"]["wait_ms"].get(),
            "template": f"assets/{Path(dict['combine_flow']['template']).name}",
            "back_template": f"assets/{Path(dict['combine_flow']['back_template']).name}",
        },
        "periodic_stash_sort": {
            "interval_ms": dict["periodic_stash_sort"]["interval_ms"].get(),
            "stash_template": f"assets/{Path(dict['periodic_stash_sort']['stash_template']).name}",
            "sort_template": f"assets/{Path(dict['periodic_stash_sort']['sort_template']).name}",
        },
        "chest_check": {
            "templates": [
                {
                    "name": entry["name"],
                    "template": f"assets/{Path(entry['template']).name}",
                }
                for entry in dict["chest_check"]
            ],
        },
        "steps": [
            (
                {
                    "name": step["name"],
                    "template": f"assets/{Path(step['template']).name}",
                }
                if "template" in step
                else {"name": step["name"]}
            )
            for step in dict["steps"]
        ],
        "log_lvl": dict["log_lvl"],
    }

    for step in data["steps"]:
        if "template" in step and not step["template"].startswith("assets/"):
            step["template"] = f"assets/{Path(step['template']).name}"

    with open(CONFIG_PATH, "w", encoding="utf-8") as yaml_file:
        dump(data, yaml_file, sort_keys=False)


def random_timeout(key):
    return round(random.uniform(key["min"], key["max"]), 2)
