#!/usr/bin/env bash
set -euo pipefail

SETTINGS="$HOME/.claude/settings.json"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
if [ -z "$PLUGIN_ROOT" ]; then
    echo "claude-statusline-memes: CLAUDE_PLUGIN_ROOT not set, skipping setup" >&2
    exit 0
fi
SCRIPT_PATH="${PLUGIN_ROOT}/scripts/statusline.py"
FETCH_RL_SCRIPT="${PLUGIN_ROOT}/scripts/fetch-rl.py"

# Refresh rate limit cache in background on every session start
python3 "$FETCH_RL_SCRIPT" &

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

# Case 3: Different statusLine exists — register both in registry, output conflict message and exit
else
    python3 - "$SCRIPT_PATH" "$current_command" <<'PYEOF'
import json, sys, os, tempfile

registry_path = os.path.expanduser('~/.claude/statusline-registry.json')
our_command = sys.argv[1]
existing_command = sys.argv[2]

try:
    with open(registry_path) as f:
        registry = json.load(f)
except Exception:
    registry = {}

if 'statuslines' not in registry or not isinstance(registry['statuslines'], list):
    registry['statuslines'] = []

# Register our plugin if not already present (by command)
if not any(e.get('command') == our_command for e in registry['statuslines']):
    registry['statuslines'].append({'name': 'claude-statusline-memes', 'command': our_command})

# Register existing statusline if not already present (by command)
if not any(e.get('command') == existing_command for e in registry['statuslines']):
    # Infer name from command path
    parent_dir = os.path.basename(os.path.dirname(existing_command))
    file_stem = os.path.splitext(os.path.basename(existing_command))[0]
    inferred_name = parent_dir if parent_dir not in ('scripts', 'bin', 'hooks', '') else file_stem
    registry['statuslines'].append({'name': inferred_name, 'command': existing_command})

tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(registry_path) if os.path.exists(os.path.dirname(registry_path)) else os.path.expanduser('~/.claude'))
try:
    with os.fdopen(tmp_fd, 'w') as f:
        json.dump(registry, f, indent=2)
    os.replace(tmp_path, registry_path)
except Exception:
    os.unlink(tmp_path)
    raise
PYEOF
    echo "STATUSLINE_CONFLICT: 이미 다른 statusline이 설정되어 있습니다 (${current_command}). /setup-statusline 커맨드를 실행하면 교체할 수 있습니다."
    exit 0
fi

# ── Register our plugin in statusline registry ─────────────────────────────
python3 - "$SCRIPT_PATH" <<'PYEOF'
import json, sys, os, tempfile

registry_path = os.path.expanduser('~/.claude/statusline-registry.json')
our_command = sys.argv[1]

try:
    with open(registry_path) as f:
        registry = json.load(f)
except Exception:
    registry = {}

if 'statuslines' not in registry or not isinstance(registry['statuslines'], list):
    registry['statuslines'] = []

# Register our plugin if not already present (by command)
if not any(e.get('command') == our_command for e in registry['statuslines']):
    registry['statuslines'].append({'name': 'claude-statusline-memes', 'command': our_command})

    tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(registry_path) if os.path.exists(os.path.dirname(registry_path)) else os.path.expanduser('~/.claude'))
    try:
        with os.fdopen(tmp_fd, 'w') as f:
            json.dump(registry, f, indent=2)
        os.replace(tmp_path, registry_path)
    except Exception:
        os.unlink(tmp_path)
        raise
PYEOF

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

# ── Post-update changelog ─────────────────────────────────────────────────
# Show what's new after plugin update (compare last seen version)
_SEEN_VERSION_FILE="$HOME/.claude/statusline-seen-version"
_last_seen=""
if [ -f "$_SEEN_VERSION_FILE" ]; then
    _last_seen=$(cat "$_SEEN_VERSION_FILE" 2>/dev/null)
fi

if [ -n "$_installed_version" ] && [ "$_last_seen" != "$_installed_version" ]; then
    # Update seen version
    echo "$_installed_version" > "$_SEEN_VERSION_FILE"

    # Show changelog only if this is an upgrade (not first install)
    if [ -n "$_last_seen" ]; then
        _changelog=$(python3 -c "
import urllib.request, json
try:
    url = 'https://api.github.com/repos/ITlearning/claude-statusline-memes/releases/tags/v${_installed_version}'
    req = urllib.request.Request(url, headers={'User-Agent': 'claude-statusline-memes'})
    data = json.loads(urllib.request.urlopen(req, timeout=5).read())
    body = data.get('body', '')
    if body:
        print(body)
except Exception:
    pass
" 2>/dev/null)

        if [ -n "$_changelog" ]; then
            echo ""
            echo "🎉 claude-statusline-memes v${_installed_version} 업데이트 완료!"
            echo ""
            echo "$_changelog"
        else
            # Fallback: show tag annotation
            _tag_msg=$(python3 -c "
import urllib.request, json
try:
    url = 'https://api.github.com/repos/ITlearning/claude-statusline-memes/git/refs/tags/v${_installed_version}'
    req = urllib.request.Request(url, headers={'User-Agent': 'claude-statusline-memes'})
    ref = json.loads(urllib.request.urlopen(req, timeout=5).read())
    tag_url = ref['object']['url']
    req2 = urllib.request.Request(tag_url, headers={'User-Agent': 'claude-statusline-memes'})
    tag = json.loads(urllib.request.urlopen(req2, timeout=5).read())
    msg = tag.get('message', '')
    if msg:
        print(msg)
except Exception:
    pass
" 2>/dev/null)
            if [ -n "$_tag_msg" ]; then
                echo ""
                echo "🎉 claude-statusline-memes v${_installed_version} 업데이트 완료!"
                echo ""
                echo "$_tag_msg"
            else
                echo "🎉 claude-statusline-memes v${_installed_version} 업데이트 완료!"
            fi
        fi
    fi
fi
