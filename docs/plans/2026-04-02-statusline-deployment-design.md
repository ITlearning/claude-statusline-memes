# claude-statusline-memes Deployment Design

## Overview

Package the existing `~/.claude/statusline-command.sh` Python script as a Claude Code plugin and publish it to GitHub with self-hosted marketplace support.

## Goals

- GitHub 레포에 플러그인으로 배포
- 직접 설치(`/plugin install tabber/claude-statusline-memes`) 지원
- 마켓플레이스 추가 후 설치(`/plugin marketplace add tabber/claude-statusline-memes`) 지원
- 설치 시 statusLine 자동 설정, 충돌 시 사용자에게 확인

## Repository Structure

```
claude-statusline-memes/
├── .claude-plugin/
│   ├── plugin.json          # Plugin metadata
│   └── marketplace.json     # Marketplace catalog (self-hosted)
├── hooks/
│   ├── hooks.json           # SessionStart hook declaration
│   └── setup.sh             # Setup detection & configuration script
├── scripts/
│   └── statusline.py        # Statusline command script
├── config/
│   └── default-config.json  # Default meme config
├── commands/
│   └── setup-statusline.md  # /setup-statusline slash command
├── README.md
└── LICENSE
```

## Setup Flow

### SessionStart Hook (`hooks/setup.sh`)

1. Read `~/.claude/settings.json`
2. Check `statusLine` field:
   - **Not set** → auto-write `{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/statusline.py"}`, output success message
   - **Already this plugin** → no-op
   - **Different command exists** → output conflict message to stdout (injected as session context → Claude relays "앗! 이미 사용하고 있는 statusline이 있어요. 지우고 설치할까요?")

### `/setup-statusline` Command

Manual re-run of setup for reconfiguration at any time. Claude runs `setup.sh` interactively and handles the conflict prompt.

## Marketplace Design

Same repo serves as both plugin and marketplace (same pattern as `swift-study-skills`):

- **Direct install**: `/plugin install tabber/claude-statusline-memes`
- **Via marketplace**: `/plugin marketplace add tabber/claude-statusline-memes` then `/plugin install claude-statusline-memes@tabber`

`marketplace.json` in `.claude-plugin/` lists the plugin pointing to `./` as source.

## Files to Create

| File | Source |
|------|--------|
| `scripts/statusline.py` | Extracted from `~/.claude/statusline-command.sh` |
| `config/default-config.json` | From `~/.claude/statusline-meme-config.json` |
| `.claude-plugin/plugin.json` | New |
| `.claude-plugin/marketplace.json` | New |
| `hooks/hooks.json` | New |
| `hooks/setup.sh` | New |
| `commands/setup-statusline.md` | New |
| `README.md` | New |
| `LICENSE` | New (MIT) |
