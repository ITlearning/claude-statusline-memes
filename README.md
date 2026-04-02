# claude-statusline-memes

[한국어](#korean) | [English](#english)

---

<a name="korean"></a>
## 한국어

Claude Code 프롬프트 입력창 아래에 표시되는 statusline 플러그인.
모델명, rate limit (5h/7d), 컨텍스트 사용량, 그리고 시간대별 한국어 개발자 밈을 보여줍니다.

### 미리보기

시간대별로 다른 밈이 표시됩니다:

```
# 🌅 아침 (6~9시)
claude-sonnet-4-6 │ 5h ██░░░ 42% │ 7d █░░░░ 18% │ Ctx ██░░░░ 31% │ 🌅 오늘은 진짜 클린코드 쓴다! │ ⎇ main

# ☀️ 오전 (9~12시)
claude-sonnet-4-6 │ 5h ███░░ 58% │ 7d ██░░░ 35% │ Ctx ███░░░ 52% │ ☀️ 뇌가 돌아가는 황금 시간대! │ ⎇ feature/login

# 🌞 오후 (12~18시)
claude-sonnet-4-6 │ 5h ████░ 80% 23m │ 7d ██░░░ 40% │ Ctx ████░░ 71% │ 🌞 작동은 하는데 이유는 모름... │ ⎇ main

# 🌆 저녁 (18~21시)
claude-sonnet-4-6 │ 5h █████ 95% 4m │ 7d ███░░ 61% │ Ctx █████░ 88% │ 🌆 딱 이것만 하고 퇴근 (3번째) │ ⎇ hotfix

# 🌃 야간 (21시~)
claude-sonnet-4-6 │ 5h ░░░░░  0% │ 7d ██░░░ 32% │ Ctx ██░░░░ 38% │ 🌃 오늘 중으로 라고 했지 몇 시까지라고 안 했잖아! │ ⎇ main
```

20% 확률로 AI 밈도 등장:

```
claude-sonnet-4-6 │ 5h ███░░ 55% │ 7d ██░░░ 28% │ Ctx ██░░░░ 44% │ ☀️ "간단히 수정해줘" → 파일 12개 변경됨 │ ⎇ main
claude-sonnet-4-6 │ 5h ██░░░ 43% │ 7d █░░░░ 19% │ Ctx ███░░░ 50% │ 🌞 코드 리뷰어: Claude, 작성자: Claude, 나: 구경 중 │ ⎇ dev
claude-sonnet-4-6 │ 5h ░░░░░  8% │ 7d ██░░░ 36% │ Ctx █░░░░░ 22% │ 🌃 context window 날아가기 3, 2, 1... │ ⎇ main
```

### 설치

**직접 설치:**

```bash
/plugin install ITlearning/claude-statusline-memes
```

**마켓플레이스로 설치:**

```bash
/plugin marketplace add ITlearning/claude-statusline-memes
/plugin install claude-statusline-memes@ITlearning
```

설치 후 Claude Code를 재시작하면 첫 세션에서 자동으로 설정됩니다.

> 이미 다른 statusline을 사용 중이라면, `/setup-statusline` 커맨드를 실행해서 교체 여부를 결정할 수 있어요.

### 설정

`~/.claude/statusline-meme-config.json` 파일을 만들어 커스터마이즈:

```json
{
  "interval_minutes": 5,
  "custom_messages": [
    "여기에 커스텀 메시지 추가"
  ]
}
```

- `interval_minutes`: 밈이 바뀌는 주기 (기본값: 5분)
- `custom_messages`: 풀에 추가할 커스텀 메시지

### 표시 항목

| 항목 | 설명 |
|------|------|
| 모델명 | 현재 Claude 모델 |
| `5h ████░ 80%` | 5시간 rate limit 사용량 + 리셋 카운트다운 |
| `7d ██░░░ 40%` | 7일 rate limit 사용량 + 리셋 카운트다운 |
| `Ctx ███░░░ 52%` | 컨텍스트 윈도우 사용량 |
| 밈 | 시간대별 한국어 개발자 유머 |
| `⎇ branch` | 현재 git 브랜치 |

사용량에 따라 초록 → 노랑 → 빨강으로 색상이 바뀝니다.

### 커스터마이즈 스킬

설치 후 Claude Code에서 다음 커맨드로 statusline을 입맛대로 바꿀 수 있습니다:

| 커맨드 | 설명 |
|--------|------|
| `/customize-colors` | 5h, 7d, Ctx 색상 변경 기준 조정 (전체 또는 항목별) |
| `/customize-layout` | 표시 항목 순서 변경 / 숨기기 |
| `/setup-statusline` | statusline 재설정 |

---

<a name="english"></a>
## English

A Claude Code statusline plugin that displays below the prompt input.
Shows model name, rate limits (5h/7d), context window usage, and time-based Korean developer humor.

### Preview

Different memes appear based on the time of day:

```
# 🌅 Morning (6–9am)
claude-sonnet-4-6 │ 5h ██░░░ 42% │ 7d █░░░░ 18% │ Ctx ██░░░░ 31% │ 🌅 오늘은 진짜 클린코드 쓴다! │ ⎇ main

# ☀️ Late morning (9am–12pm)
claude-sonnet-4-6 │ 5h ███░░ 58% │ 7d ██░░░ 35% │ Ctx ███░░░ 52% │ ☀️ 뇌가 돌아가는 황금 시간대! │ ⎇ feature/login

# 🌞 Afternoon (12–6pm)
claude-sonnet-4-6 │ 5h ████░ 80% 23m │ 7d ██░░░ 40% │ Ctx ████░░ 71% │ 🌞 작동은 하는데 이유는 모름... │ ⎇ main

# 🌆 Evening (6–9pm)
claude-sonnet-4-6 │ 5h █████ 95% 4m │ 7d ███░░ 61% │ Ctx █████░ 88% │ 🌆 딱 이것만 하고 퇴근 (3번째) │ ⎇ hotfix

# 🌃 Night (9pm+)
claude-sonnet-4-6 │ 5h ░░░░░  0% │ 7d ██░░░ 32% │ Ctx ██░░░░ 38% │ 🌃 오늘 중으로 라고 했지 몇 시까지라고 안 했잖아! │ ⎇ main
```

20% chance of AI memes:

```
claude-sonnet-4-6 │ 5h ███░░ 55% │ 7d ██░░░ 28% │ Ctx ██░░░░ 44% │ ☀️ "간단히 수정해줘" → 파일 12개 변경됨 │ ⎇ main
claude-sonnet-4-6 │ 5h ██░░░ 43% │ 7d █░░░░ 19% │ Ctx ███░░░ 50% │ 🌞 코드 리뷰어: Claude, 작성자: Claude, 나: 구경 중 │ ⎇ dev
claude-sonnet-4-6 │ 5h ░░░░░  8% │ 7d ██░░░ 36% │ Ctx █░░░░░ 22% │ 🌃 context window 날아가기 3, 2, 1... │ ⎇ main
```

### Install

**Direct install:**

```bash
/plugin install ITlearning/claude-statusline-memes
```

**Via marketplace:**

```bash
/plugin marketplace add ITlearning/claude-statusline-memes
/plugin install claude-statusline-memes@ITlearning
```

After install, restart Claude Code. The statusline configures itself automatically on first session start.

> If you already have a statusline configured, run `/setup-statusline` to manage the transition.

### Configuration

Create `~/.claude/statusline-meme-config.json` to customize:

```json
{
  "interval_minutes": 5,
  "custom_messages": [
    "Add your custom messages here"
  ]
}
```

- `interval_minutes`: How often the meme rotates (default: 5)
- `custom_messages`: Your own messages mixed into the pool

### What it shows

| Section | Description |
|---------|-------------|
| Model | Current Claude model name |
| `5h ████░ 80%` | 5-hour rate limit usage with reset countdown |
| `7d ██░░░ 40%` | 7-day rate limit usage with reset countdown |
| `Ctx ███░░░ 52%` | Context window usage |
| Meme | Time-based Korean developer humor |
| `⎇ branch` | Current git branch |

Colors shift green → yellow → red as usage increases.

### Customization Skills

After install, use these commands in Claude Code to customize:

| Command | Description |
|---------|-------------|
| `/customize-colors` | Adjust warning/danger thresholds for 5h, 7d, Ctx — globally or per-metric |
| `/customize-layout` | Reorder or hide statusline elements |
| `/setup-statusline` | Reconfigure the statusline |

## License

MIT
