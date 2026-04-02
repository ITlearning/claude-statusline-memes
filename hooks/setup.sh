#!/usr/bin/env bash
set -euo pipefail

SETTINGS="$HOME/.claude/settings.json"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
if [ -z "$PLUGIN_ROOT" ]; then
    echo "claude-statusline-memes: CLAUDE_PLUGIN_ROOT not set, skipping setup" >&2
    exit 0
fi
SCRIPT_PATH="${PLUGIN_ROOT}/scripts/statusline.py"

# Ensure settings.json exists
if [ ! -f "$SETTINGS" ]; then
    echo '{}' > "$SETTINGS"
fi

# Read current statusLine command (empty string if not set)
current_command=$(python3 - <<PYEOF
import json, sys, os
try:
    with open(os.path.expanduser('~/.claude/settings.json')) as f:
        data = json.load(f)
    sl = data.get('statusLine', {})
    if isinstance(sl, dict):
        print(sl.get('command', ''))
    else:
        print('')
except Exception:
    print('')
PYEOF
)

# Case 2: Already configured to this plugin — no-op
if echo "$current_command" | grep -q "claude-statusline-memes.*statusline\.py\|statusline\.py.*claude-statusline-memes"; then
    exit 0
fi

# Case 1: Not configured at all — auto-configure
if [ -z "$current_command" ]; then
    python3 - "$SCRIPT_PATH" <<'PYEOF'
import json, sys, os, tempfile

settings_path = os.path.expanduser('~/.claude/settings.json')
script_path = sys.argv[1]

try:
    with open(settings_path) as f:
        data = json.load(f)
except Exception:
    data = {}

data['statusLine'] = {
    "type": "command",
    "command": script_path
}

tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(settings_path))
try:
    with os.fdopen(tmp_fd, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, settings_path)
except Exception:
    os.unlink(tmp_path)
    raise
PYEOF
    exit 0
fi

# Case 3: Different statusLine exists — output conflict message
echo "STATUSLINE_CONFLICT: 이미 다른 statusline이 설정되어 있습니다 (${current_command}). /setup-statusline 커맨드를 실행하면 교체할 수 있습니다."
