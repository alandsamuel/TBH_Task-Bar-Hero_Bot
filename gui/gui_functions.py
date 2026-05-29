from functools import partial
from tkinter import Canvas, Toplevel

import utils.global_variables as gv
from functionality.stash_loop import reset_stash_state, start_periodic_stash_sort, stash_loop
from utils.config import save_data
from wrappers.logging_wrapper import info


def popup_rectangle_window(button, x, y, width, height):
    window = Toplevel()
    window.resizable(False, False)
    window.attributes("-fullscreen", True)
    window.wm_attributes("-transparentcolor", window["bg"])
    canvas = Canvas(window, width=10000, height=10000)
    canvas.create_rectangle(
        x.get(),
        y.get(),
        x.get() + width.get(),
        y.get() + height.get(),
        outline="green",
        width=5,
    )
    canvas.pack()
    button.configure(
        command=partial(destroy_rectangle_window, window, button, x, y, width, height)
    )


def destroy_rectangle_window(window, button, x, y, width, height):
    window.destroy()
    button.configure(
        command=partial(popup_rectangle_window, button, x, y, width, height)
    )


def on_closing():
    save_data()
    info("GUI: Saving data")
    info("GUI: Closing")
    gv.root.destroy()


def start_stash(button):
    gv.continue_stash = True
    reset_stash_state()
    button.configure(text="Stop Stash", command=partial(stop_stash, button))
    stash_loop()
    start_periodic_stash_sort()


def stop_stash(button):
    gv.continue_stash = False
    gv.status_message = "Stopped"
    info("Process Stopped")
    if gv.status_label is not None:
        gv.status_label.configure(text=gv.status_message)
    button.configure(text="Start Stash", command=partial(start_stash, button))
