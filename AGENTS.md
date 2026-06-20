# AGENTS.md — TBH Helper

Guidance for AI agents working in this repository.

## Project summary

Windows-only Python helper for **Task Bar Hero (TBH)**. Uses **tkinter** GUI, **OpenCV** template matching, and **Win32** mouse/keyboard input to automate stash flow (open chest → auto fill → stash all → close) plus a background periodic stash/sort loop.

Entry point: `main.py` → `gui_init()` → `gv.root.mainloop()`.

### Entry flow

```
main.py
  └─ apply_process_title()        (utils/process_title.py — sets console + window title to "Helper")
  └─ gui_init()                   (gui/gui_initializer.py — sets window size, title, close handler)
      └─ stash_panel()            (gui/stash_panel.py — builds notebook tabs + footer start/stop)
  └─ gv.root.mainloop()           (tkinter event loop)
```

## Requirements

- **Windows only** (pywin32, screen capture, input simulation)
- Python 3.10+
- Dependencies in `requirements.txt`

Do not introduce cross-platform abstractions unless explicitly requested. Do not replace Win32 input with other libraries.

## Layout

```
main.py                # Entry point
gui/                   # Tkinter UI (tabs, region draw, start/stop)
functionality/         # stash_loop state machine, image_search
utils/                 # config load/save, global_variables
wrappers/              # win32api, logging
resources/config.yml   # Persisted settings (saved on app close)
assets/                # Template PNGs (base + scaled variants)
```

## Configuration

- Runtime config lives in `utils/config.py` as `dict` (Tk `IntVar` / `DoubleVar` / `StringVar` bound to GUI).
- YAML is loaded at import; `save_data()` writes GUI values back on window close.
- **Do not** add `.env` or secret handling unless asked — not used today.

### Important config concepts

| Area | Notes |
|------|--------|
| `search_region` | Screen coords for template search; set via GUI draw overlay or numeric fields |
| `window_scale` | `1`, `1.25`, `1.5`, `2` — selects scaled template suffix (`_1-25`, `_1-50`, `_2`; scale `1` = no suffix) |
| Template names in YAML/GUI | **Base names only** (e.g. `auto_fill.png`); resolve via `template_path_for()` |
| Timings | Min/max ranges in **seconds**; use `random_timeout()` / `random_delay_ms()` — avoid fixed delays for automation actions |
| `timeouts.step_wait` | Max time (random in range) to poll for one missing chest/step template; then skip to next step via `_skip_to_next_step()` |
| `log_lvl` | Applied when user clicks Start Stash (`apply_log_level()`) |

Process-facing name is **`Helper`** (`APP_DISPLAY_NAME` in `utils/global_variables.py`). Do not add "bot" to window titles, logger names, or packaged exe names.

When adding new template references, wire through `template_path_for()` so window scale works.

## GUI conventions

- Main panel: `gui/stash_panel.py` — tabbed notebook + **footer** with status and Start/Stop (always visible).
- Region draw: `gui/gui_functions.py` — use semi-transparent overlay (`-alpha`), **not** `-transparentcolor` on Windows (clicks pass through).
- Prefer help text under settings explaining what each field changes.
- Keep window resizable; avoid breaking scrollable tabs.

## Automation logic

Full diagrams and transition tables: **[docs/automation.md](docs/automation.md)**.

- Core loop: `functionality/stash_loop.py` — step index in `gv.current_step_index`, scheduled via `gv.root.after`.
- Step names are string-matched (`open_chest`, `auto_fill`, `stash_all`, …); changing step order/names requires YAML + code alignment.
- **Missing templates:** poll on `timeouts.loop` until `timeouts.step_wait` elapses (`gv.step_wait_deadline`), then `_skip_to_next_step()` advances `current_step_index` (no full loop restart). Combine-without-prompt jumps to `stash_all` in one shot; successful combine+back uses `_restart_loop()` from step 0.
- Image search: `functionality/image_search.py` — `find_template(region, path, threshold)` returns center in **screen** coordinates. Template paths via `template_path_for()` / `step_entries()` — see doc for scale suffix rules.
- Clicks: `wrappers/win32api_wrapper.py`; apply jitter via `random_click_offset()` in stash_loop, not raw center clicks.
- Periodic stash/sort: missing templates skip that click only; cycle reschedules on `periodic_stash_sort.interval`.

## Assets

Scaled templates follow naming: `{base_stem}{suffix}.png` where suffix is `""`, `_1-25`, `_1-50`, or `_2`.

If a scaled file is missing, `template_path_for()` warns and falls back to the base file.

### Template files

All templates in `assets/` have 4 variants (base, `_1-25`, `_1-50`, `_2`):
- `auto_fill.png`, `back_arrow.png`, `boss_chest_icon.png`, `chest_icon.png`, `combine.png`, `sort.png`, `stash_all.png`

`stash_all_1-25.png` is missing (only 3 variants exist for it).

## Coding standards

- **Minimal diffs** — match existing style (plain functions, no over-abstraction).
- Reuse `dict`, `gv`, existing helpers before adding new modules.
- Comments only for non-obvious behavior (Windows quirks, timing rationale).
- Do not commit secrets, `venv/`, or `.cursor/`.
- Do not create git commits or PRs unless the user asks.

## Circular import note

`utils/config.py` uses a **lazy import** inside `template_path_for()` to avoid a circular import with `wrappers.logging_wrapper` (which imports `dict` from config). Keep this pattern if you add new logging calls inside config helpers.

## Diagnostics module

`functionality/function_tester.py` provides `run_diagnostics()` — called from the **Run** tab. It tests:
1. Search region bounds
2. Screen capture (`ImageGrab.grab`)
3. Template file existence
4. Template match scores (probe vs threshold)
5. Win32 cursor position
6. Stash step config

Each check returns a `(name, status, detail)` tuple where status is `PASS`, `WARN`, or `FAIL`.

## Window/process title

`utils/process_title.py` — sets both the tkinter window title and console title to `APP_DISPLAY_NAME` ("Helper"). Uses `ctypes.windll.kernel32.SetConsoleTitleW` on Windows. Avoid changing this name — do not introduce "bot" in titles or logger names.

## PyInstaller spec files

Two `.spec` files exist:
- `main.spec` — `Analysis(['main.py'], ...)` → produces `dist/main/` (the correct entry point).
- `bot.spec` — `Analysis(['bot.py'], ...)` — legacy/stale (no `bot.py` exists in repo).

Use `main.spec` for builds. Both include `resources` and `assets` as data directories.

## Running locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Optional EXE and GitHub releases: see `RELEASES.md`. CI: `.github/workflows/release.yml`.

## Common tasks

| Task | Primary files |
|------|----------------|
| New GUI setting | `gui/stash_panel.py`, `utils/config.py`, `resources/config.yml` |
| New automation step | `functionality/stash_loop.py`, `resources/config.yml` |
| Template / scale behavior | `utils/config.py` (`template_path_for`, `scaled_template_name`) |
| Region overlay | `gui/gui_functions.py` |
| Randomization | `utils/config.py` helpers, callers in `stash_loop.py` |
| Default values / magic numbers | `utils/constants.py` — import from here, do not hardcode |

## Testing changes

- Verify imports: `python -c "import gui.stash_panel; from utils.config import template_path_for"`
- Manual test on Windows with game focused; no automated test suite in repo.
- Check console logs at INFO/DEBUG when touching template match or region draw.
