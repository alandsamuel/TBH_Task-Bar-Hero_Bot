from functools import partial
from tkinter import Button, Entry, Frame, Label

import utils.global_variables as gv
from gui.gui_functions import popup_rectangle_window, start_stash
from utils.config import dict
def stash_panel():
    panel = Frame(gv.root, padx=10, pady=10)
    panel.pack()

    Label(panel, text="Search region", font=("Segoe UI", 10, "bold")).grid(
        row=0, column=0, columnspan=4, sticky="w", pady=(0, 6)
    )

    _region_field(panel, "X", dict["search_region"]["x"], 1, 0)
    _region_field(panel, "Y", dict["search_region"]["y"], 1, 2)
    _region_field(panel, "Width", dict["search_region"]["width"], 2, 0)
    _region_field(panel, "Height", dict["search_region"]["height"], 2, 2)

    preview_button = Button(panel, text="Preview region")
    preview_button.configure(
        command=partial(
            popup_rectangle_window,
            preview_button,
            dict["search_region"]["x"],
            dict["search_region"]["y"],
            dict["search_region"]["width"],
            dict["search_region"]["height"],
        )
    )
    preview_button.grid(row=3, column=0, columnspan=4, pady=(8, 12), sticky="ew")

    Label(panel, text="Match threshold").grid(row=4, column=0, sticky="w")
    threshold_entry = _entry(panel, dict["matching"]["threshold"], width=8)
    threshold_entry.grid(row=4, column=1, sticky="w")

    Label(panel, text="Loop delay (ms)").grid(row=4, column=2, sticky="w", padx=(12, 0))
    loop_entry = _entry(panel, dict["timeouts"]["loop_ms"], width=8)
    loop_entry.grid(row=4, column=3, sticky="w")

    gv.status_label = Label(panel, text=gv.status_message, wraplength=360, justify="left")
    gv.status_label.grid(row=5, column=0, columnspan=4, sticky="w", pady=(12, 8))

    start_button = Button(panel, text="Start Stash", width=20)
    start_button.configure(command=partial(start_stash, start_button))
    start_button.grid(row=6, column=0, columnspan=4, pady=(4, 0))


def _region_field(parent, label, variable, row, column):
    Label(parent, text=label).grid(row=row, column=column, sticky="w")
    entry = _entry(parent, variable)
    entry.grid(row=row, column=column + 1, sticky="w", padx=(4, 12))


def _entry(parent, variable, width=10):
    return Entry(parent, textvariable=variable, width=width)
