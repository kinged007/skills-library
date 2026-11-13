#!/usr/bin/env bash
# Install every external (referenced) skill from its original author's repo.
# Usage: scripts/install-external.sh [-g]   (needs npx, jq; run build_catalog.py first)
set -euo pipefail
cd "$(dirname "$0")/.."
jq -r '.skills[]|select(.type=="external")|"\(.source) \(.skill)"' catalog.json |
while read -r src skill; do npx skills add "$src" --skill "$skill" "$@"; done
