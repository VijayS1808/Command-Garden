#!/usr/bin/env bash
set -euo pipefail
if [ "$(id -u)" -eq 0 ]; then
  echo 'Run this installer as your normal desktop user, without sudo.'
  exit 1
fi
if ! /usr/bin/python3 -c 'from PyQt5.QtWidgets import QApplication' 2>/dev/null; then
  echo 'Install the desktop dependency first:'
  echo '  sudo apt update && sudo apt install python3-pyqt5 fonts-noto-color-emoji'
  echo 'Then run: bash install.sh'
  exit 1
fi
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_dir="$HOME/.local/share/command-garden-app"
mkdir -p "$install_dir" "$HOME/.local/bin" "$HOME/.local/share/applications"
for file in app.py store.py icon.svg README.md; do
  if [ "$source_dir" != "$install_dir" ]; then cp -- "$source_dir/$file" "$install_dir/$file"; fi
done
/usr/bin/python3 - "$install_dir" <<'PY'
import sys, shlex
from pathlib import Path
root = Path(sys.argv[1]); home = Path.home()
launcher = home/'.local/bin/command-garden'
launcher.write_text('#!/bin/sh\nexec /usr/bin/python3 '+shlex.quote(str(root/'app.py'))+' "$@"\n')
launcher.chmod(0o755)
def quote(s):
    return '"'+str(s).replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')+'"'
(home/'.local/share/applications/command-garden.desktop').write_text(
    '[Desktop Entry]\nType=Application\nName=Command Garden\nComment=Local commands, scripts, notes and images\n'
    'Exec='+quote(launcher)+'\nIcon='+str(root/'icon.svg')+'\nTerminal=false\nCategories=Utility;Development;\nStartupNotify=true\n')
PY
echo 'Installed! Search for Command Garden in your application menu.'
echo 'Or launch with: ~/.local/bin/command-garden'
