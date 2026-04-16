#!/usr/bin/env bash
set -euo pipefail

if [ -z "${CLAUDE_PLUGIN_ROOT:-}" ]; then
    echo "claude-statusline-memes: CLAUDE_PLUGIN_ROOT not set" >&2
    exit 1
fi

export CLAUDE_PLUGIN_ROOT

python3 - <<'PYEOF'
import json, os, tempfile

plugin_root = os.environ['CLAUDE_PLUGIN_ROOT']
script_path = os.path.join(plugin_root, 'scripts', 'statusline.py')
settings_path = os.path.expanduser('~/.claude/settings.json')
settings_dir = os.path.dirname(settings_path)

os.makedirs(settings_dir, exist_ok=True)

try:
    with open(settings_path) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        data = {}
except FileNotFoundError:
    data = {}
except Exception:
    data = {}

data['statusLine'] = {
    "type": "command",
    "command": script_path,
}

tmp_fd, tmp_path = tempfile.mkstemp(dir=settings_dir)
try:
    with os.fdopen(tmp_fd, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, settings_path)
except Exception:
    try:
        os.unlink(tmp_path)
    except Exception:
        pass
    raise

# Clean up ack file since our statusline is now active
ack_path = os.path.expanduser('~/.claude/statusline-conflict-acked.json')
try:
    os.remove(ack_path)
except FileNotFoundError:
    pass
except Exception:
    pass

print("\u2705 \uc124\uc815 \uc644\ub8cc! \ub2e4\uc74c \uc138\uc158\ubd80\ud130 \uc0c8 statusline\uc774 \ud45c\uc2dc\ub429\ub2c8\ub2e4.")
PYEOF
