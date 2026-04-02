---
name: switch-statusline
description: 등록된 statusline 플러그인 목록을 보여주고, 사용자가 선택한 플러그인으로 활성 statusLine을 전환합니다
---

`~/.claude/statusline-registry.json`에 등록된 statusline 플러그인 목록을 읽고, 사용자가 원하는 플러그인으로 `~/.claude/settings.json`의 statusLine command를 전환해줍니다.

## Step 1 — 레지스트리 읽기

`~/.claude/statusline-registry.json` 파일을 읽습니다.

파일이 없거나, 파일은 있지만 `statuslines` 배열이 비어 있으면 아래 메시지를 출력하고 종료합니다:

> "등록된 statusline이 없습니다. 다른 statusline 플러그인을 설치하면 자동으로 등록됩니다."

레지스트리 형식:
```json
{
  "statuslines": [
    { "name": "claude-statusline-memes", "command": "/path/to/statusline.py" },
    { "name": "other-plugin", "command": "/path/to/other.sh" }
  ]
}
```

## Step 2 — 현재 활성 statusLine 읽기

`~/.claude/settings.json`을 읽고 `statusLine.command` 값을 확인합니다.

settings.json 예시:
```json
{
  "statusLine": {
    "command": "/Users/tabber/claude-statusline-memes/scripts/statusline.py"
  }
}
```

`statusLine.command`가 없으면 현재 활성 항목 없음으로 간주합니다.

## Step 3 — 목록 표시 및 분기

레지스트리에 등록된 statusline 개수에 따라 분기합니다.

### 1개뿐인 경우:

현재 활성 command와 비교하여:
- 이미 활성 상태라면:
  > "현재 1개만 등록되어 있으며, 이미 활성화되어 있습니다: **{name}**"
- 아직 활성화되지 않은 경우에는 Step 4로 바로 진행합니다 (선택 없이 해당 항목을 적용).

### 2개 이상인 경우:

번호 목록으로 표시합니다. 현재 활성 항목에는 `[현재 활성]` 표시를 붙입니다.

예시:
> "등록된 statusline 목록입니다:
>
> 1. claude-statusline-memes [현재 활성]
> 2. other-plugin
>
> 전환할 번호를 입력해주세요 (취소하려면 Enter 또는 0):"

사용자가 0이나 빈 입력을 하면:
> "취소했습니다. 변경사항 없음."
으로 종료합니다.

사용자가 현재 활성 항목과 동일한 번호를 선택하면:
> "{name}은(는) 이미 활성화되어 있습니다. 변경사항 없음."
으로 종료합니다.

유효하지 않은 번호(범위 초과 등)를 입력하면 다시 묻습니다.

## Step 4 — settings.json 업데이트 (atomic write)

선택된 항목의 `command` 값으로 `~/.claude/settings.json`의 `statusLine.command`를 업데이트합니다.

아래 Python 코드를 실행합니다 (atomic write: tempfile + os.replace):

```python
import json, os, tempfile

settings_path = os.path.expanduser("~/.claude/settings.json")
new_command = "/선택된/command/경로"  # 선택한 항목의 command로 교체

# settings.json 읽기 (없으면 빈 dict)
if os.path.exists(settings_path):
    with open(settings_path, "r") as f:
        settings = json.load(f)
else:
    settings = {}

# statusLine.command 업데이트
if "statusLine" not in settings:
    settings["statusLine"] = {}
settings["statusLine"]["command"] = new_command

# atomic write: 같은 디렉터리에 임시 파일 생성 후 교체
dir_ = os.path.dirname(settings_path)
with tempfile.NamedTemporaryFile("w", dir=dir_, delete=False, suffix=".tmp") as tf:
    json.dump(settings, tf, ensure_ascii=False, indent=2)
    tmp_path = tf.name

os.replace(tmp_path, settings_path)
print("완료")
```

실제 실행 시 `new_command`를 선택된 항목의 `command` 값으로 대입하여 실행합니다.

에러 발생 시 에러 메시지를 그대로 사용자에게 보여주고 종료합니다.

## Step 5 — 완료 메시지

성공 시:

> "완료! 활성 statusline을 **{name}** 으로 전환했습니다.
> 다음 Claude Code 세션부터 적용됩니다."

---

**참고:**
- `statusline-registry.json`이 존재하지 않는 경우와 `statuslines` 배열이 빈 경우 모두 동일하게 처리합니다.
- `settings.json`의 다른 키는 절대 수정하지 않습니다. 오직 `statusLine.command`만 변경합니다.
- atomic write를 사용하는 이유는 쓰기 도중 충돌로 파일이 손상되는 것을 방지하기 위해서입니다.
