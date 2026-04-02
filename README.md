# claude-statusline-memes

[한국어](#korean) | [English](#english)

---

<a name="korean"></a>
## 한국어

Claude Code 프롬프트 입력창 아래에 표시되는 statusline 플러그인.
모델명, rate limit (5h/7d), 컨텍스트 사용량, 그리고 시간대별 한국어 개발자 밈을 보여줍니다.

### 밈 기여하기

여러분이 만든 밈도 함께 써요! 참여할수록 더 풍성해집니다 🎉

- **PR**: `memes.json`에 직접 추가해서 Pull Request
- **이슈**: [GitHub Issues](https://github.com/ITlearning/claude-statusline-memes/issues)에 원하는 문구 남겨주시면 추가할게요

어떤 형식이든 환영합니다. 개발자 공감 밈, 시간대별 유머, AI 관련 드립 모두 OK!

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

### 실제 사용시 화면
<img width="782" height="94" alt="image" src="https://github.com/user-attachments/assets/96590002-d6a9-4f72-88eb-f06f5e6e4d7f" />


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

### 전체 밈 목록

<details>
<summary>전체 밈 보기 (총 134개)</summary>

#### 🌙 새벽
- 이 시간에 코딩하는 사람은 둘 중 하나: 천재 아니면 나...
- 버그가 밤에 더 잘 보이는 것 같다 (착각)
- 커밋 메시지: fix
- 아 됐다!! (5분 후 더 큰 버그 발견)
- 스택오버플로우가 친구인 시간...
- 자도 돼 근데 안 잘 거잖아?
- 일단 돌아가면 된 거 아님?
- 변수명 a, b, c로 짜고 나중에 고친다... (안 고침)
- 에러 메시지를 읽지 않는 시간...
- 무한루프인 줄 알았는데 그냥 느린 거였음
- git blame 하지 마...
- 내가 짠 코드 내가 이해 못 함...
- (코드를 보면서) 스트레스 많이 받을거야
- 빌드 터짐 괜찮아 딩딩딩~
- 커밋 날아감 괜찮아 딩딩딩~
- 에러 터짐 괜찮아 딩딩딩~
- 머지 충돌 괜찮아 딩딩딩~
- 퀸은 에러에 울지 않아 (울고 있음)
- 퀸은 빌드 실패에 굴복 안 해 (굴복함)

#### 🌅 아침
- 오늘은 진짜 클린코드 쓴다!
- 어젯밤 내가 짠 코드 다시 보는 중...
- 커피 없이는 git push 없다!
- 야 이거 누가 짠 거야? (내가 짰다)
- TODO: 오늘 안에 TODO 없애기
- 좋은 아침!
- 밤새 생각한 해결책: 그냥 지우면 됨
- 오늘은 테스트 코드도 쓴다 (거짓말)
- 지난 커밋 메시지: asdf...
- 오늘 PR 하나만 머지하면 성공이다!
- 기획서 다시 읽는 중...
- 코드 난리자베스~✨
- 오늘 코드 매끈매끈하다~
- 버그 수정이 첫번째 레슨...
- 코드 리뷰가 첫번째 레슨...
- WOW 섹시 코드... (내가 짰다)

#### ☀️ 오전
- 지금 이 순간만큼은 뭐든 할 수 있어!
- 회의 전까지 한 기능만 더...
- 스탠드업에서 할 말 만드는 중...
- 뇌가 돌아가는 황금 시간대!
- 오늘의 목표: 어제보다 조금 덜 부수기
- 버그 잡으러 간다!
- 이 함수 누가 300줄로 만들었어?
- 리뷰 코멘트: nit: 변수명이...
- 문서화 하면서 코딩? 가능한 얘기야?
- Ctrl+Z 40번째...
- 타입 에러 15개... 천천히 하자
- iOS 개발자들은 완전히 멘탈이 나가버렸습니다.
- WOW 섹시 커밋 메시지
- 테스트 코드 짜라고? 너 누군데
- 문서화 하라고? 너 누군데
- 에러 메시지 보고 허거덩거덩스...

#### 🌞 오후
- 밥 먹고 나니까 전부 내 잘못인 것 같다...
- 주석으로 덮어두면 안 보이는 거 아님?
- 코드리뷰 == 과거의 나와 싸우기
- 작동은 하는데 이유는 모름...
- 이 버그 이름을 뭐라 지을까?
- 왜 갑자기 안 되지?
- 스택 오버플로우 답변 날짜: 2013년...
- 작동하는 코드는 건드리지 않는다 (원칙)
- 배포 버튼에 손이 떨린다...
- 이 if문 한 다섯 개면 되겠지?
- npm install 중... (커피 마실 시간)
- Android 개발자들은 완전히 멘탈이 나가버렸습니다.
- 럭키비키잖아~ (빌드 성공)
- 칠 가이 모드 (코드리뷰? 나중에)
- 기술부채? 내가 그걸 모를까...
- 리팩토링 하자고? 너 누군데
- 리팩토링 후 코드 매끈매끈하다~
- 머지 GMG?
- 오늘 PR GMG?

#### 🌆 저녁
- 딱 이것만 하고 퇴근 (3번째)
- 이게 마지막 커밋이라고 했었다...
- 배고프지만 빌드는 해야지!
- 오늘 안에 머지 못 하면 내일의 내가 해결해줄 거야...
- 저녁 먹으면서 에러 로그 읽는 중
- 퇴근은 커밋 후에!
- 오늘 커밋 메시지: WIP fix
- 집에 가면서도 머릿속에서 디버깅 중...
- PR 설명: 이것저것 고침
- 야 근데 이거 진짜 마지막이야!
- 슬랙 알림 끄는 시간
- 여러분 저 했어요! 저 퇴근 못했어요! 쌰갈!
- 배포 GMG?
- 버그 고쳤음 HMH~
- 빌드 성공 HMH HMH~
- 커밋 했음 HMH
- 에러 잡음 HMH HMH
- 이 버그? 내가 그걸 모를까... (알면서 놔둠)
- 여러분 저 잡았어요! 저 에러 못잡았어요! 쌰갈!

#### 🌃 야간
- 오늘 중으로 라고 했지 몇 시까지라고 안 했잖아!
- 이쯤 되면 코드가 나를 짜고 있는 거 아닐까...
- 자려고 누웠다가 해결책이 떠올랐다!
- 다크모드 = 야근 모드
- 내일 아침의 나야, 미안해...
- 졸음과의 싸움 중...
- 커밋하고 자야지... 또 커밋하고 자야지...
- 이 코드 이해하는 사람은 전 세계에 나 하나
- 오늘의 교훈: 환경변수 확인 먼저
- git stash하고 자는 게 맞나...
- 내일 오전 미팅 있는데...
- 개발자들은 완전히 멘탈이 나가버렸습니다.
- 백엔드 개발자들은 완전히 멘탈이 나가버렸습니다.
- 칠 가이 모드 (버그? 내일의 내가 고침)
- 칠 가이 모드 (에러? 내일의 내가 봄)
- TODO 주석? 내가 그걸 모를까...
- 스택트레이스 보고 허거덩거덩스...
- 코드 리뷰 코멘트 보고 허거덩거덩스...
- WOW 섹시 에러 (처음 보는 에러)
- 이 커밋 매끈매끈하다~

#### AI 밈
- 해결할 수 있습니다! (Claude Code를 키며)
- Claude한테 물어봤더니 더 헷갈림...
- AI가 짠 코드라 나는 모름
- 일단 Claude한테 던져봄
- "이 코드 설명해줘" → Claude: "훌륭한 코드입니다!"
- 버그 고쳐달라고 했더니 다 갈아엎음
- Claude: 물론이죠! 나: ...이게 맞나?
- AI 페어 프로그래밍 중 (AI가 다 짬)
- 코드 리뷰어: Claude, 작성자: Claude, 나: 구경 중
- "간단히 수정해줘" → 파일 12개 변경됨
- Claude Code 없이 어떻게 살았지...
- 프롬프트 엔지니어링이 곧 개발 실력인 시대
- Claude가 짠 코드를 Claude가 리뷰하는 중
- context window 날아가기 3, 2, 1...
- "이 에러 뭐야" → Claude: "좋은 질문입니다!"
- 나: 이거 왜 됨? Claude: 사실 저도...
- 주석 작성자: Claude. 코드 작성자: Claude. 버그 책임자: 나
- 오늘 git log에 내 커밋이 없다...
- Claude가 시키는 대로 했더니 빌드 터짐
- "너무 잘 만들어줬다" 혼자 뿌듯해하는 중
- tokens: 남은 거 없음. 뇌: 남은 거 없음
- AI한테 설명하다가 내가 이해함
- 이번엔 진짜 내가 짠 거임 (거짓말)
- Claude가 deprecated API 썼다...
- Claude야 운동 많이 된다.

</details>

---

<a name="english"></a>
## English

A Claude Code statusline plugin that displays below the prompt input.
Shows model name, rate limits (5h/7d), context window usage, and time-based Korean developer humor.

### Contributing Memes

The more people contribute, the better the memes get! 🎉

- **PR**: Add your lines directly to `memes.json` and open a Pull Request
- **Issue**: Drop your ideas in [GitHub Issues](https://github.com/ITlearning/claude-statusline-memes/issues) and I'll add them

Developer relatable humor, time-of-day jokes, AI memes — all welcome. Any language is fine too!

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

### Full Meme List

<details>
<summary>Show all memes (134 total)</summary>

#### 🌙 Late Night
- 이 시간에 코딩하는 사람은 둘 중 하나: 천재 아니면 나...
- 버그가 밤에 더 잘 보이는 것 같다 (착각)
- 커밋 메시지: fix
- 아 됐다!! (5분 후 더 큰 버그 발견)
- 스택오버플로우가 친구인 시간...
- 자도 돼 근데 안 잘 거잖아?
- 일단 돌아가면 된 거 아님?
- 변수명 a, b, c로 짜고 나중에 고친다... (안 고침)
- 에러 메시지를 읽지 않는 시간...
- 무한루프인 줄 알았는데 그냥 느린 거였음
- git blame 하지 마...
- 내가 짠 코드 내가 이해 못 함...
- (코드를 보면서) 스트레스 많이 받을거야
- 빌드 터짐 괜찮아 딩딩딩~
- 커밋 날아감 괜찮아 딩딩딩~
- 에러 터짐 괜찮아 딩딩딩~
- 머지 충돌 괜찮아 딩딩딩~
- 퀸은 에러에 울지 않아 (울고 있음)
- 퀸은 빌드 실패에 굴복 안 해 (굴복함)

#### 🌅 Morning
- 오늘은 진짜 클린코드 쓴다!
- 어젯밤 내가 짠 코드 다시 보는 중...
- 커피 없이는 git push 없다!
- 야 이거 누가 짠 거야? (내가 짰다)
- TODO: 오늘 안에 TODO 없애기
- 좋은 아침!
- 밤새 생각한 해결책: 그냥 지우면 됨
- 오늘은 테스트 코드도 쓴다 (거짓말)
- 지난 커밋 메시지: asdf...
- 오늘 PR 하나만 머지하면 성공이다!
- 기획서 다시 읽는 중...
- 코드 난리자베스~✨
- 오늘 코드 매끈매끈하다~
- 버그 수정이 첫번째 레슨...
- 코드 리뷰가 첫번째 레슨...
- WOW 섹시 코드... (내가 짰다)

#### ☀️ Late Morning
- 지금 이 순간만큼은 뭐든 할 수 있어!
- 회의 전까지 한 기능만 더...
- 스탠드업에서 할 말 만드는 중...
- 뇌가 돌아가는 황금 시간대!
- 오늘의 목표: 어제보다 조금 덜 부수기
- 버그 잡으러 간다!
- 이 함수 누가 300줄로 만들었어?
- 리뷰 코멘트: nit: 변수명이...
- 문서화 하면서 코딩? 가능한 얘기야?
- Ctrl+Z 40번째...
- 타입 에러 15개... 천천히 하자
- iOS 개발자들은 완전히 멘탈이 나가버렸습니다.
- WOW 섹시 커밋 메시지
- 테스트 코드 짜라고? 너 누군데
- 문서화 하라고? 너 누군데
- 에러 메시지 보고 허거덩거덩스...

#### 🌞 Afternoon
- 밥 먹고 나니까 전부 내 잘못인 것 같다...
- 주석으로 덮어두면 안 보이는 거 아님?
- 코드리뷰 == 과거의 나와 싸우기
- 작동은 하는데 이유는 모름...
- 이 버그 이름을 뭐라 지을까?
- 왜 갑자기 안 되지?
- 스택 오버플로우 답변 날짜: 2013년...
- 작동하는 코드는 건드리지 않는다 (원칙)
- 배포 버튼에 손이 떨린다...
- 이 if문 한 다섯 개면 되겠지?
- npm install 중... (커피 마실 시간)
- Android 개발자들은 완전히 멘탈이 나가버렸습니다.
- 럭키비키잖아~ (빌드 성공)
- 칠 가이 모드 (코드리뷰? 나중에)
- 기술부채? 내가 그걸 모를까...
- 리팩토링 하자고? 너 누군데
- 리팩토링 후 코드 매끈매끈하다~
- 머지 GMG?
- 오늘 PR GMG?

#### 🌆 Evening
- 딱 이것만 하고 퇴근 (3번째)
- 이게 마지막 커밋이라고 했었다...
- 배고프지만 빌드는 해야지!
- 오늘 안에 머지 못 하면 내일의 내가 해결해줄 거야...
- 저녁 먹으면서 에러 로그 읽는 중
- 퇴근은 커밋 후에!
- 오늘 커밋 메시지: WIP fix
- 집에 가면서도 머릿속에서 디버깅 중...
- PR 설명: 이것저것 고침
- 야 근데 이거 진짜 마지막이야!
- 슬랙 알림 끄는 시간
- 여러분 저 했어요! 저 퇴근 못했어요! 쌰갈!
- 배포 GMG?
- 버그 고쳤음 HMH~
- 빌드 성공 HMH HMH~
- 커밋 했음 HMH
- 에러 잡음 HMH HMH
- 이 버그? 내가 그걸 모를까... (알면서 놔둠)
- 여러분 저 잡았어요! 저 에러 못잡았어요! 쌰갈!

#### 🌃 Night
- 오늘 중으로 라고 했지 몇 시까지라고 안 했잖아!
- 이쯤 되면 코드가 나를 짜고 있는 거 아닐까...
- 자려고 누웠다가 해결책이 떠올랐다!
- 다크모드 = 야근 모드
- 내일 아침의 나야, 미안해...
- 졸음과의 싸움 중...
- 커밋하고 자야지... 또 커밋하고 자야지...
- 이 코드 이해하는 사람은 전 세계에 나 하나
- 오늘의 교훈: 환경변수 확인 먼저
- git stash하고 자는 게 맞나...
- 내일 오전 미팅 있는데...
- 개발자들은 완전히 멘탈이 나가버렸습니다.
- 백엔드 개발자들은 완전히 멘탈이 나가버렸습니다.
- 칠 가이 모드 (버그? 내일의 내가 고침)
- 칠 가이 모드 (에러? 내일의 내가 봄)
- TODO 주석? 내가 그걸 모를까...
- 스택트레이스 보고 허거덩거덩스...
- 코드 리뷰 코멘트 보고 허거덩거덩스...
- WOW 섹시 에러 (처음 보는 에러)
- 이 커밋 매끈매끈하다~

#### AI Memes
- 해결할 수 있습니다! (Claude Code를 키며)
- Claude한테 물어봤더니 더 헷갈림...
- AI가 짠 코드라 나는 모름
- 일단 Claude한테 던져봄
- "이 코드 설명해줘" → Claude: "훌륭한 코드입니다!"
- 버그 고쳐달라고 했더니 다 갈아엎음
- Claude: 물론이죠! 나: ...이게 맞나?
- AI 페어 프로그래밍 중 (AI가 다 짬)
- 코드 리뷰어: Claude, 작성자: Claude, 나: 구경 중
- "간단히 수정해줘" → 파일 12개 변경됨
- Claude Code 없이 어떻게 살았지...
- 프롬프트 엔지니어링이 곧 개발 실력인 시대
- Claude가 짠 코드를 Claude가 리뷰하는 중
- context window 날아가기 3, 2, 1...
- "이 에러 뭐야" → Claude: "좋은 질문입니다!"
- 나: 이거 왜 됨? Claude: 사실 저도...
- 주석 작성자: Claude. 코드 작성자: Claude. 버그 책임자: 나
- 오늘 git log에 내 커밋이 없다...
- Claude가 시키는 대로 했더니 빌드 터짐
- "너무 잘 만들어줬다" 혼자 뿌듯해하는 중
- tokens: 남은 거 없음. 뇌: 남은 거 없음
- AI한테 설명하다가 내가 이해함
- 이번엔 진짜 내가 짠 거임 (거짓말)
- Claude가 deprecated API 썼다...
- Claude야 운동 많이 된다.

</details>

## License

MIT
