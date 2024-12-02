#!/usr/bin/env bash
set -euo pipefail

# Ensure correct cwd, for example: ~/Projects/Tauon
cd "$(dirname "$0")"

export PYTHONPATH=".":"${PYTHONPATH-}"

python -m venv .venv
# Windows: .\.venv\Scripts\activate
source .venv/bin/activate

tauonmb "$@"
