#!/usr/bin/env bash
set -euo pipefail

# Ensure correct cwd, for example: ~/Projects/Tauon
cd "$(dirname "$0")"

export PYTHONPATH=".":"${PYTHONPATH-}"


python -m venv .venv
# Windows: .\.venv\Scripts\activate
source .venv/bin/activate
#pip install -r requirements_windows.txt
pip install build
python -m compile_translations
python -m build --wheel
#python -m installer --destdir=".venv" dist/*.whl
pip install --prefix ".venv" dist/*.whl --force-reinstall

printf All done! Run "./run.sh" to launch Tauon.

tauonmb "$@"
