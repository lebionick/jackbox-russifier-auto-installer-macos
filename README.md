# jackbox-russifier-auto-installer-macos
This is just simple script with simple instructions to simplify installation process of Whatif russifiers for Jackbox party pack games on Steam for Macos 

## Prerequisites:
1. You ought to have macos device with installed Steam and some Jackbox Party Packs you want russifiers to apply.  
2. You ought to download russifiers from website: https://dl.whatif.one/ : log in into steam in a browser and follow the instructions to download russifiers for macos (steam versions).
3. Place all archives with russifiers into one folder, later you will be needed to pass this path to script.

## Installation:
1. you need to have macos console package manager `brew` installed.
2. (optional) unarchiving is done using `unar` tool, script will attempt to install it if it is not present, however you might want to install it by yourself using `brew install unar`.
3. recommended way is to use `uv` to resolve and install dependencies and create `python` venv, so to install you need:
    1. `cd <repo root>`
    2. `brew install pipx`
    3. `pipx ensurepath`
    4. `pipx install uv`
    5. open new tab in terminal or manually "re-source", e.g. `source ~/.zshrc` (depending on your shell)
    6. `uv sync`

## Launching:
just call (replacing <> with actual value): `uv run jackbox-auto-russifier -i <path to folder where all archived russifiers are placed>`  
Add `--dry-run` to command to inspect what it does without replacing game files.
  
**Alternatively** if you are using different tool to create venv (or using host env), enter this env and launch command without `uv run`.  

## After patching
You are free to delete directory with this repo entirely, virtual environment will also be deleted (however `brew`, `pipx` and `unar` will remain).   
However Steam now does not allow to launch games without updates if any, so from time to time, Party Packs will be updated, meaning replacing russified files with original ones, breaking their purpose. For this case I recommend to keep this tool and archives. To reduce disk usage you can delete `unarchived` folder.