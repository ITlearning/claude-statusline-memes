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

# Case 2: Already configured to this plugin — fall through to version check
if echo "$current_command" | grep -q "claude-statusline-memes.*statusline\.py\|statusline\.py.*claude-statusline-memes"; then
    : # no-op

# Case 1: Not configured at all — auto-configure, then fall through to version check
elif [ -z "$current_command" ]; then
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

# Case 3: Different statusLine exists — output conflict message and exit
else
    echo "STATUSLINE_CONFLICT: 이미 다른 statusline이 설정되어 있습니다 (${current_command}). /setup-statusline 커맨드를 실행하면 교체할 수 있습니다."
    exit 0
fi

# ── Version check ──────────────────────────────────────────────────────────
_VERSION_CACHE="$HOME/.claude/statusline-version-check.json"
_VERSION_CACHE_TTL=86400  # 24 hours

_installed_version=$(python3 -c "
import json, os
try:
    path = os.path.join('$PLUGIN_ROOT', '.claude-plugin', 'plugin.json')
    print(json.load(open(path)).get('version', ''))
except Exception:
    print('')
" 2>/dev/null)

if [ -z "$_installed_version" ]; then
    exit 0
fi

_cache_fresh=$(python3 -c "
import json, time
try:
    d = json.load(open('$_VERSION_CACHE'))
    print('yes' if time.time() - d.get('checked_at', 0) < $_VERSION_CACHE_TTL else 'no')
except Exception:
    print('no')
" 2>/dev/null)

if [ "$_cache_fresh" = "yes" ]; then
    _latest_version=$(python3 -c "
import json
try:
    print(json.load(open('$_VERSION_CACHE')).get('latest', ''))
except Exception:
    print('')
" 2>/dev/null)
else
    # Fetch latest tag from GitHub
    _latest_version=$(python3 -c "
import urllib.request, json
try:
    url = 'https://api.github.com/repos/ITlearning/claude-statusline-memes/tags'
    req = urllib.request.Request(url, headers={'User-Agent': 'claude-statusline-memes'})
    tags = json.loads(urllib.request.urlopen(req, timeout=5).read())
    print(tags[0]['name'].lstrip('v') if tags else '')
except Exception:
    print('')
" 2>/dev/null)

    # Save to cache
    if [ -n "$_latest_version" ]; then
        python3 -c "
import json, time
data = {'checked_at': time.time(), 'latest': '$_latest_version'}
open('$_VERSION_CACHE', 'w').write(json.dumps(data))
" 2>/dev/null
    fi
fi

if [ -n "$_latest_version" ] && [ "$_latest_version" != "$_installed_version" ]; then
    echo "UPDATE_AVAILABLE: claude-statusline-memes v${_latest_version} 버전이 출시됐어요! (현재: v${_installed_version}) \`/plugin update claude-statusline-memes@ITlearning\` 으로 업데이트할 수 있어요."
fi
