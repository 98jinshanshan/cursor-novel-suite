#!/usr/bin/env bash
# Install skills to cursor / qoder / trae-cn (project or global)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_SRC="$ROOT/skills"
GLOBAL="${GLOBAL:-0}"
AGENTS="${AGENTS:-cursor qoder trae-cn}"

install_agent() {
  local agent="$1"
  local dest_root
  case "$agent" in
    cursor)  [[ "$GLOBAL" == "1" ]] && dest_root="$HOME/.cursor/skills" || dest_root=".agents/skills" ;;
    qoder)   [[ "$GLOBAL" == "1" ]] && dest_root="$HOME/.qoder/skills" || dest_root=".qoder/skills" ;;
    trae-cn) [[ "$GLOBAL" == "1" ]] && dest_root="$HOME/.trae-cn/skills" || dest_root=".trae/skills" ;;
    *) return ;;
  esac
  mkdir -p "$dest_root"
  for skill in "$SKILLS_SRC"/*; do
    name="$(basename "$skill")"
    rm -rf "$dest_root/$name"
    cp -R "$skill" "$dest_root/$name"
    echo "Installed $name -> $dest_root ($agent)"
  done
}

for a in $AGENTS; do install_agent "$a"; done
echo "Done. Prefer: npx skills add <repo> -a cursor -a qoder -a trae-cn -y"
