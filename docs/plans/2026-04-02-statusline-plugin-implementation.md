# claude-statusline-memes Plugin Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the existing statusline script as an installable Claude Code plugin with auto-setup and self-hosted marketplace support.

**Architecture:** A single GitHub repo acts as both the plugin and its own marketplace. A SessionStart hook handles auto-configuration of `settings.json` on first run, with conflict detection for existing statusLines. The Python statusline script is copied verbatim from the existing `~/.claude/statusline-command.sh`.

**Tech Stack:** Python 3 (statusline script), Bash (setup hook), JSON (plugin/marketplace manifests), Claude Code plugin format

---

## Chunk 1: Core Scripts and Config

### Task 1: Copy statusline script

**Files:**
- Create: `scripts/statusline.py`

- [ ] **Step 1: Create scripts directory and copy the script**

```bash
mkdir -p scripts
cp ~/.claude/statusline-command.sh scripts/statusline.py
chmod +x scripts/statusline.py
```

- [ ] **Step 2: Verify it runs correctly**

```bash
echo '{"model":{"display_name":"claude-sonnet-4-6"},"rate_limits":{},"context_window":{"used_percentage":12},"workspace":{"current_dir":"'"$(pwd)"'"}}' | python3 scripts/statusline.py
```

Expected: A statusline string with model name, rate limit bars, context bar, and a meme message. No errors.

- [ ] **Step 3: Commit**

```bash
git add scripts/statusline.py
git commit -m "feat: add statusline script"
```

---

### Task 2: Default config

**Files:**
- Create: `config/default-config.json`

- [ ] **Step 1: Create config directory and default config**

```bash
mkdir -p config
```

Create `config/default-config.json`:

```json
{
  "interval_minutes": 5,
  "custom_messages": []
}
```

- [ ] **Step 2: Verify config is valid JSON**

```bash
python3 -m json.tool config/default-config.json
```

Expected: Pretty-printed JSON with no errors.

- [ ] **Step 3: Commit**

```bash
git add config/default-config.json
git commit -m "feat: add default meme config"
```

---

### Task 3: Plugin and marketplace manifests

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Create `.claude-plugin/` directory**

```bash
mkdir -p .claude-plugin
```

- [ ] **Step 2: Create `plugin.json`**

```json
{
  "name": "claude-statusline-memes",
  "version": "1.0.0",
  "description": "Claude Code statusline with Korean developer memes — shows model, rate limits, context usage, and time-based humor",
  "author": {
    "name": "tabber"
  },
  "license": "MIT",
  "keywords": ["statusline", "memes", "korean", "productivity", "rate-limits"]
}
```

- [ ] **Step 3: Create `marketplace.json`**

```json
{
  "name": "tabber",
  "owner": {
    "name": "tabber"
  },
  "metadata": {
    "description": "Claude Code statusline plugins by tabber",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "claude-statusline-memes",
      "source": "./",
      "description": "Claude Code statusline with Korean developer memes — shows model, rate limits, context usage, and time-based humor",
      "version": "1.0.0",
      "keywords": ["statusline", "memes", "korean", "productivity"]
    }
  ]
}
```

- [ ] **Step 4: Verify both files are valid JSON**

```bash
python3 -m json.tool .claude-plugin/plugin.json && python3 -m json.tool .claude-plugin/marketplace.json
```

Expected: Both files pretty-print without errors.

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/
git commit -m "feat: add plugin and marketplace manifests"
```

---

## Chunk 2: Hooks and Commands

### Task 4: SessionStart hook

**Files:**
- Create: `hooks/hooks.json`
- Create: `hooks/setup.sh`

- [ ] **Step 1: Create hooks directory**

```bash
mkdir -p hooks
```

- [ ] **Step 2: Create `hooks/hooks.json`**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/setup.sh\"",
            "async": false
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Create `hooks/setup.sh`**

The script handles 3 cases:
1. No statusLine → auto-configure
2. Already this plugin → no-op
3. Different statusLine → output conflict message for Claude to relay

```bash
#!/usr/bin/env bash
set -euo pipefail

SETTINGS="$HOME/.claude/settings.json"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
SCRIPT_PATH="${PLUGIN_ROOT}/scripts/statusline.py"

# Ensure settings.json exists
if [ ! -f "$SETTINGS" ]; then
    echo '{}' > "$SETTINGS"
fi

# Read current statusLine command (empty string if not set)
current_command=$(python3 - <<PYEOF
import json, sys
try:
    with open('$SETTINGS') as f:
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
if echo "$current_command" | grep -q "statusline.py"; then
    exit 0
fi

# Case 1: Not configured at all — auto-configure
if [ -z "$current_command" ]; then
    python3 - "$SCRIPT_PATH" <<'PYEOF'
import json, sys, os

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

with open(settings_path, 'w') as f:
    json.dump(data, f, indent=2)
PYEOF
    exit 0
fi

# Case 3: Different statusLine exists — output conflict message
echo "STATUSLINE_CONFLICT: 이미 다른 statusline이 설정되어 있습니다 (${current_command}). /setup-statusline 커맨드를 실행하면 교체할 수 있습니다."
```

- [ ] **Step 4: Make setup.sh executable**

```bash
chmod +x hooks/setup.sh
```

- [ ] **Step 5: Test Case 1 — no statusLine configured**

Back up current settings, remove statusLine, run setup, verify it writes the path.

```bash
# Back up
cp ~/.claude/settings.json /tmp/settings-backup.json

# Remove statusLine field temporarily
python3 -c "
import json
with open('/Users/tabber/.claude/settings.json') as f: d = json.load(f)
d.pop('statusLine', None)
with open('/Users/tabber/.claude/settings.json', 'w') as f: json.dump(d, f, indent=2)
"

# Run setup with CLAUDE_PLUGIN_ROOT pointing to current dir
CLAUDE_PLUGIN_ROOT="$(pwd)" bash hooks/setup.sh

# Verify statusLine was written
python3 -c "
import json
with open('/Users/tabber/.claude/settings.json') as f: d = json.load(f)
print(d.get('statusLine'))
"
```

Expected: `{'type': 'command', 'command': '<path>/scripts/statusline.py'}`

- [ ] **Step 6: Restore settings and test Case 2 — already this plugin**

```bash
# Set statusLine to this plugin
python3 -c "
import json
with open('/Users/tabber/.claude/settings.json') as f: d = json.load(f)
d['statusLine'] = {'type': 'command', 'command': '$(pwd)/scripts/statusline.py'}
with open('/Users/tabber/.claude/settings.json', 'w') as f: json.dump(d, f, indent=2)
"

# Run setup — should exit silently
CLAUDE_PLUGIN_ROOT="$(pwd)" bash hooks/setup.sh
echo "exit code: $?"
```

Expected: exit code 0, no output.

- [ ] **Step 7: Test Case 3 — different statusLine exists**

```bash
# Set statusLine to something else
python3 -c "
import json
with open('/Users/tabber/.claude/settings.json') as f: d = json.load(f)
d['statusLine'] = {'type': 'command', 'command': '/some/other/script.sh'}
with open('/Users/tabber/.claude/settings.json', 'w') as f: json.dump(d, f, indent=2)
"

CLAUDE_PLUGIN_ROOT="$(pwd)" bash hooks/setup.sh
```

Expected: Output containing "STATUSLINE_CONFLICT: 이미 다른 statusline이..."

- [ ] **Step 8: Restore original settings**

```bash
cp /tmp/settings-backup.json ~/.claude/settings.json
```

- [ ] **Step 9: Commit**

```bash
git add hooks/
git commit -m "feat: add SessionStart hook for auto-setup"
```

---

### Task 5: /setup-statusline command

**Files:**
- Create: `commands/setup-statusline.md`

The command is a Claude skill that tells Claude to run the setup script interactively, handling the conflict prompt.

- [ ] **Step 1: Create commands directory**

```bash
mkdir -p commands
```

- [ ] **Step 2: Create `commands/setup-statusline.md`**

```markdown
---
name: setup-statusline
description: Set up or reconfigure the claude-statusline-memes statusline. Run this to install, reinstall, or replace an existing statusline configuration.
---

Run the setup script to configure the statusline:

1. Run: `CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}" bash "${CLAUDE_PLUGIN_ROOT}/hooks/setup.sh"`
2. If the output contains "STATUSLINE_CONFLICT":
   - Tell the user: "앗! 이미 사용하고 있는 statusline이 있어요. 지우고 claude-statusline-memes로 설치할까요?"
   - If user says yes: run the following to replace it:
     ```bash
     python3 - "${CLAUDE_PLUGIN_ROOT}/scripts/statusline.py" <<'PYEOF'
     import json, sys, os
     settings_path = os.path.expanduser('~/.claude/settings.json')
     script_path = sys.argv[1]
     with open(settings_path) as f: data = json.load(f)
     data['statusLine'] = {"type": "command", "command": script_path}
     with open(settings_path, 'w') as f: json.dump(data, f, indent=2)
     print("✅ 설정 완료! 다음 세션부터 새 statusline이 표시됩니다.")
     PYEOF
     ```
   - If user says no: leave settings unchanged and confirm no changes made.
3. If no conflict output: confirm "✅ claude-statusline-memes statusline이 설정되었습니다!"
```

- [ ] **Step 3: Commit**

```bash
git add commands/
git commit -m "feat: add /setup-statusline command"
```

---

## Chunk 3: Documentation and GitHub

### Task 6: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

```markdown
# claude-statusline-memes

Claude Code statusline with Korean developer memes.

Shows model name, rate limits (5h/7d), context window usage, and time-based Korean developer humor in the prompt statusline.

## Preview

```
claude-sonnet-4-6 │ 5h ██░░░ 42% │ 7d █░░░░ 18% │ Ctx ██░░░░ 31% │ ☀️ 밥 먹고 나니까 전부 내 잘못인 것 같다... │ ⎇ main
```

## Install

### Direct install

```bash
/plugin install tabber/claude-statusline-memes
```

### Via marketplace

```bash
/plugin marketplace add tabber/claude-statusline-memes
/plugin install claude-statusline-memes@tabber
```

After install, restart Claude Code. The statusline configures itself automatically on first session start.

> If you already have a statusline configured, run `/setup-statusline` to manage the transition.

## Configuration

The plugin reads `~/.claude/statusline-meme-config.json`. Create this file to customize:

```json
{
  "interval_minutes": 5,
  "custom_messages": [
    "여기에 커스텀 메시지 추가"
  ]
}
```

- `interval_minutes`: How often the meme rotates (default: 5)
- `custom_messages`: Your own messages mixed into the pool

## What it shows

| Section | Description |
|---------|-------------|
| Model | Current Claude model name |
| `5h ████░ 80%` | 5-hour rate limit usage with countdown |
| `7d ██░░░ 40%` | 7-day rate limit usage with countdown |
| `Ctx ███░░░ 52%` | Context window usage |
| Meme | Time-based Korean developer humor |
| `⎇ branch` | Current git branch |

Colors: green → yellow → red as usage increases.

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README"
```

---

### Task 7: LICENSE

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: Create MIT LICENSE**

```
MIT License

Copyright (c) 2026 tabber

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Commit**

```bash
git add LICENSE
git commit -m "chore: add MIT license"
```

---

### Task 8: Create GitHub repo and push

- [ ] **Step 1: Create public GitHub repo**

```bash
gh repo create tabber/claude-statusline-memes --public --description "Claude Code statusline with Korean developer memes" --source=. --remote=origin
```

- [ ] **Step 2: Push to GitHub**

```bash
git push -u origin main
```

- [ ] **Step 3: Verify plugin structure on GitHub**

Open `https://github.com/tabber/claude-statusline-memes` and confirm:
- `.claude-plugin/plugin.json` visible
- `.claude-plugin/marketplace.json` visible
- `scripts/statusline.py` visible
- `hooks/` directory visible
- `README.md` renders correctly

- [ ] **Step 4: Test direct install**

In a new Claude Code session:

```bash
/plugin install tabber/claude-statusline-memes
```

Expected: Plugin installs, SessionStart hook runs on next session, statusline appears.

- [ ] **Step 5: Test marketplace install**

```bash
/plugin marketplace add tabber/claude-statusline-memes
/plugin install claude-statusline-memes@tabber
```

Expected: Same result as direct install.
```
