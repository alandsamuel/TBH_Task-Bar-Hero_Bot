from pathlib import Path
from tkinter import Tk

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "resources" / "config.yml"

root = Tk()
continue_stash = False
current_step_index = 0
status_message = "Idle"
status_label = None
combine_check_pending = False
