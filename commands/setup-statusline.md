---
name: setup-statusline
description: Set up or reconfigure the claude-statusline-memes statusline. Run this to install, reinstall, or replace an existing statusline configuration.
---

1. 다음 명령을 실행하세요:
   `STATUSLINE_FORCE=1 bash "${CLAUDE_PLUGIN_ROOT}/hooks/setup.sh"`
2. 출력에 `STATUSLINE_CONFLICT` 가 포함되면:
   - 사용자에게 "앗! 이미 사용하고 있는 statusline이 있어요. 지우고 claude-statusline-memes로 설치할까요?" 라고 질문
   - 사용자가 긍정("네", "yes", "ok", "덮어써", "교체" 등)으로 답하면:
     - 다음 명령을 실행: `bash "${CLAUDE_PLUGIN_ROOT}/hooks/replace-statusline.sh"`
     - 실행 후 출력을 그대로 사용자에게 보여줌
   - 사용자가 부정("아니오", "no", "취소" 등)으로 답하면:
     - 어떤 파일도 읽거나 수정하지 마세요. 오직 "알겠습니다. 변경사항 없습니다." 라고만 답해주세요.
3. 출력에 `STATUSLINE_CONFLICT` 가 없으면 "✅ claude-statusline-memes statusline이 설정되었습니다!" 라고 확인만 해주세요.

**중요: 이 슬래시 커맨드를 처리할 때 `scripts/statusline.py` 등 플러그인 내부 파일을 Read tool로 열지 마세요. 위의 명령만 실행하세요.**
