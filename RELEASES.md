# Releases & builds

How to build **TBH Helper** locally, download CI artifacts, and publish GitHub releases.

Workflow file: [.github/workflows/build.yml](.github/workflows/build.yml)

---

## Local build (on your PC)

Requirements: Windows, Python 3.10+

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --name TBHHelper --add-data "resources;resources" --add-data "assets;assets" main.py
```

Output:

- Folder: `dist/TBHHelper/`
- Executable: `dist/TBHHelper/TBHHelper.exe`

The folder includes bundled `resources/` and `assets/`. Zip the whole `TBHHelper` folder if you want to share it manually.

Do **not** commit `dist/`, `build/`, or `.exe` files to git.

---

## Automated builds (GitHub Actions)

The workflow **Build Windows executable** runs when:

- You push to `main` or `master`
- You open a pull request to `main` or `master`
- You push a version tag (`v*`, e.g. `v1.0.0`)
- You trigger it manually (**Actions** → **Run workflow**)

Each successful run produces **TBHHelper-Windows.zip** (the full `dist/TBHHelper/` folder, zipped).

Artifacts are kept for **90 days**.

---

## Download a build (no release tag)

Use this when you just want the latest exe from CI.

1. Open the repo on GitHub → **Actions**
2. Click **Build Windows executable**
3. Open the latest **green** run
4. Scroll to **Artifacts** → download **TBHHelper-Windows**
5. Unzip → run `TBHHelper/TBHHelper.exe`

### Trigger a build manually

1. **Actions** → **Build Windows executable**
2. **Run workflow** → choose branch (usually `main`) → **Run workflow**
3. Wait for the green checkmark, then download the artifact as above

---

## Publish a GitHub Release

Use this when you want a version listed under **Releases** with the zip attached.

1. Make sure your changes are merged and pushed to `main`
2. Choose a version tag (examples: `v1.0.0`, `v1.0.1`, `v2.0.0`)
3. Create and push the tag:

```bash
git checkout main
git pull
git tag v1.0.0
git push origin v1.0.0
```

4. GitHub Actions runs the build and attaches **TBHHelper-Windows.zip** to the new release
5. Open **Releases** on GitHub to confirm the zip is there

Replace `v1.0.0` with your actual version each time.

### Release checklist

- [ ] Changes pushed to `main`
- [ ] Tag name starts with `v` (e.g. `v1.0.0`) — required for the release step
- [ ] Actions workflow finished successfully
- [ ] **TBHHelper-Windows.zip** appears on the release page
- [ ] Smoke-test: unzip and run `TBHHelper.exe` on Windows

---

## Troubleshooting

| Problem | What to try |
|--------|-------------|
| No **Artifacts** section | Build failed — open the run and read the error log |
| Release has no zip | Tag must be `v*` (e.g. `v1.0.0`), not `1.0.0` |
| Exe won't start | Run from the unzipped `TBHHelper` folder (not only the `.exe` moved alone) |
| Old build | Download latest green Actions run or push a new tag |

---

## Quick reference

| Goal | Command / action |
|------|------------------|
| Run from source | `python main.py` |
| Build locally | `pyinstaller --name TBHHelper --add-data "resources;resources" --add-data "assets;assets" main.py` |
| Latest CI zip | **Actions** → latest run → **TBHHelper-Windows** artifact |
| New release | `git tag v1.0.0 && git push origin v1.0.0` |
