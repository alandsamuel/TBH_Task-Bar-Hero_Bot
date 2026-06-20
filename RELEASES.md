# Releases & builds

How to build **Helper** locally and publish GitHub releases.

Workflow file: [.github/workflows/release.yml](.github/workflows/release.yml)

---

## Changelog

### v0.0.1-alpha.4 (unreleased)

- **Feature toggles** — each stash step (`open_chest`, `auto_fill`, `stash_all`, `close_stash`) and periodic action (`stash_all`, `sort`) now has its own enable/disable checkbox on the **Run & Test** tab. Disabled steps are skipped automatically.
- **Timing & Jitter rework** — all timeout defaults capped at 5s max. Tab renamed from "Timing" to "Timing & Jitter". "Save settings now" button moved to the top of the tab.
- **Tab renaming** — `Screen` → `Region & Scale`, `Run` → `Run & Test`, all scrollable.
- **Constants file** — `utils/constants.py` extracted all magic numbers and defaults from inline code.
- **opencode integration** — added `opencode.json` with project rules and commands; updated `AGENTS.md` with entry flow, diagnostics module, circular import note, process title, and PyInstaller spec info.

---

## Local build (on your PC)

Requirements: Windows, Python 3.10+

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --name Helper --add-data "resources;resources" --add-data "assets;assets" main.py
```

Output:

- Folder: `dist/Helper/`
- Executable: `dist/Helper/Helper.exe`

The folder includes bundled `resources/` and `assets/`. Zip the whole `Helper` folder if you want to share it manually.

Do **not** commit `dist/`, `build/`, or `.exe` files to git.

---

## Automated releases (GitHub Actions)

The **Release** workflow runs when you push a version tag (`v*`, e.g. `v1.0.0`).

It builds the Windows executable, zips `dist/Helper/`, and creates a GitHub Release with **Helper-Windows.zip** attached.

```bash
git checkout main
git pull
git tag v1.0.0
git push origin v1.0.0
```

Replace `v1.0.0` with your actual version each time. Open **Releases** on GitHub to download the zip.

### Release checklist

- [ ] Changes pushed to `main`
- [ ] Tag name starts with `v` (e.g. `v1.0.0`)
- [ ] **Release** workflow finished successfully
- [ ] **Helper-Windows.zip** appears on the release page
- [ ] Smoke-test: unzip and run `Helper.exe` on Windows

---

## Troubleshooting

| Problem | What to try |
|--------|-------------|
| Release has no zip | Tag must be `v*` (e.g. `v1.0.0`), not `1.0.0` |
| Workflow did not run | Confirm the tag was pushed: `git push origin v1.0.0` |
| Exe won't start | Run from the unzipped `Helper` folder (not only the `.exe` moved alone) |

---

## Quick reference

| Goal | Command / action |
|------|------------------|
| Run from source | `python main.py` |
| Build locally | `pyinstaller --name Helper --add-data "resources;resources" --add-data "assets;assets" main.py` |
| New release | `git tag v1.0.0 && git push origin v1.0.0` |
