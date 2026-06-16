#!/usr/bin/env bash
# Novel Suite — unified local verification (Linux/macOS/CI parity with final-verify.ps1)
# Usage: bash platforms/final-verify.sh [--changed-only] [--skip-pytest] [--skip-markdown]

set -euo pipefail

CHANGED_ONLY=0
SKIP_PYTEST=0
SKIP_MARKDOWN=0
BASE_REF="HEAD"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --changed-only) CHANGED_ONLY=1; shift ;;
    --skip-pytest) SKIP_PYTEST=1; shift ;;
    --skip-markdown) SKIP_MARKDOWN=1; shift ;;
    --base-ref) BASE_REF="${2:?}"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

failures=()

echo "== Novel Suite Final Verification =="
echo "Repo: $REPO_ROOT"

echo ""
echo "-- Changed files (git) --"
mapfile -t changed_tracked < <(git diff --name-only --diff-filter=ACMRTUXB "$BASE_REF" -- 2>/dev/null || true)
mapfile -t changed_untracked < <(git ls-files --others --exclude-standard 2>/dev/null || true)
changed_all=()
while IFS= read -r line; do
  [[ -n "$line" ]] && changed_all+=("$line")
done < <(printf '%s\n' "${changed_tracked[@]}" "${changed_untracked[@]}" | sort -u)
if [[ ${#changed_all[@]} -eq 0 ]]; then
  echo "(none vs $BASE_REF)"
else
  printf '  %s\n' "${changed_all[@]}"
fi

if [[ $SKIP_PYTEST -eq 0 ]]; then
  echo ""
  echo "-- pytest (-m 'not ffmpeg') --"
  python3 -m pytest -m "not ffmpeg" -q || failures+=("pytest failed")
else
  echo "(pytest skipped)"
fi

echo ""
echo "-- pyright --"
if [[ $CHANGED_ONLY -eq 1 ]]; then
  py_files=()
  for f in "${changed_all[@]}"; do
    [[ "$f" == *.py ]] && py_files+=("$f")
  done
  if [[ ${#py_files[@]} -eq 0 ]]; then
    echo "(ChangedOnly: no .py changes — skip pyright)"
  else
    npx --yes pyright -p pyrightconfig.json "${py_files[@]}" || failures+=("pyright failed")
  fi
else
  npx --yes pyright -p pyrightconfig.json || failures+=("pyright failed")
fi

if [[ $SKIP_MARKDOWN -eq 0 ]] && [[ -f .markdownlint-cli2.jsonc ]]; then
  echo ""
  echo "-- markdownlint-cli2 (CI-aligned globs + intel/radar) --"
  npx --yes markdownlint-cli2 \
    "cursor-novel-writer/**/*.md" \
    "cursor-novel-video/**/*.md" \
    "docs/**/*.md" \
    "intel/**/*.md" \
    "skills/**/*.md" \
    ".cursor/rules/**/*.mdc" \
    "novels/README.md" \
    "*.md" || failures+=("markdownlint failed")

  echo ""
  echo "-- intel radar generator contract (pytest) --"
  python3 -m pytest tests/test_intel_radar_markdown.py -q || failures+=("intel radar markdown contract failed")
elif [[ $SKIP_MARKDOWN -eq 1 ]]; then
  echo "(markdownlint skipped)"
else
  echo "(no .markdownlint-cli2.jsonc — skip markdownlint)"
fi

echo ""
echo "== Final Verification Summary =="
if [[ ${#failures[@]} -gt 0 ]]; then
  echo "FAILED:"
  printf '  - %s\n' "${failures[@]}"
  exit 1
fi

echo "OK: all checks passed."
exit 0
