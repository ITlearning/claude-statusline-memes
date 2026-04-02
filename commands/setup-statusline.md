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
     import json, sys, os, tempfile
     settings_path = os.path.expanduser('~/.claude/settings.json')
     script_path = sys.argv[1]
     with open(settings_path) as f: data = json.load(f)
     data['statusLine'] = {"type": "command", "command": script_path}
     tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(settings_path))
     try:
         with os.fdopen(tmp_fd, 'w') as f: json.dump(data, f, indent=2)
         os.replace(tmp_path, settings_path)
     except Exception:
         os.unlink(tmp_path)
         raise
     print("✅ 설정 완료! 다음 세션부터 새 statusline이 표시됩니다.")
     PYEOF
     ```
   - If user says no: leave settings unchanged and confirm no changes made.
3. If no conflict output: confirm "✅ claude-statusline-memes statusline이 설정되었습니다!"
