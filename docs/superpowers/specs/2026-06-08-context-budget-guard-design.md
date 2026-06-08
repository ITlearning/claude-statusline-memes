# Context Budget Guard — 설계 스펙

- **날짜**: 2026-06-08
- **작성자**: Tabber (인병윤)
- **상태**: 승인 대기 (브레인스토밍 완료, 구현 전)

## 1. 목적 & 배경

팀 Claude 사용량 문서(Confluence pageId 1592623110)의 낭비 지표 **[B] 컨텍스트 비대화** = `단일 세션 input > 500k OR msg > 200`. Tabber의 2026-06 B는 53건(대부분 `msg>200` 쪽).

근본 사실:
- 200K vs 1M은 **같은 모델(Opus 4.8), 컨텍스트 창 크기만** 다름. 토큰당 지능·품질 동일.
- 컨텍스트 창 크기 자체가 환각을 줄이진 않지만, **실제 채워 넣은 맥락이 비대해질수록** 장문 구간의 주의력·검색 정확도가 떨어져 사실 혼동(환각처럼 보임)이 늘어남.
- 따라서 목표는 "200K냐 1M이냐"가 아니라 **working context를 lean하게 유지**하는 것. 200K 기본값은 그걸 플랫폼이 강제(자동 compact)하게 만드는 수단.

**해결 목표**: working context를 자동으로 lean하게 유지하고, 컨텍스트를 넘기기 전에 상태를 자동 기록해 세션 끊기(`/clear`)를 무비용으로 만들어 토큰·메시지 두 B 트리거를 모두 억제한다.

## 2. 비목표 (Non-goals)

- 1M 모델 폐기 — 유지하고 `/model`로 필요할 때만 사용.
- 컨텍스트 임계에서 `/clear`를 **자동 실행** — Claude Code에 그런 훅 이벤트가 없고, 강제 자동화는 위험. 인지신호 + 무비용 핸드오프로 사람이 끊게 한다.
- AI 요약 핸드오프 — PreCompact 훅은 셸 명령이라 "요약"은 못 함. **사실(fact) 기록**만 박는다. (요약은 Claude Code 내장 compaction이 이미 수행.)
- SessionStart 자동 주입(checkpoint 경로 자동 알림) — 이번 범위에서 제외(수동 재개).

## 3. 설계 개요 — 4개 구성요소

### ① 기본 200K 컨텍스트
- `~/.claude/settings.json`에 `model` 필드 추가 → 기본을 200K Opus 4.8 변종으로.
- 현재 settings엔 `model` 필드 없음(세션마다 `/model`로 [1m] 선택 중). 기본값을 200K로 박는다.
- 1M은 `/model`로 대용량 작업 시에만.
- **효과**: working context가 ~200K 근처에서 자동 compact → `input>500k` 원천 불가, 맥락 품질 유지.
- ✅ **확정**(claude-code-guide 2026-06-08): 200K = `"model": "claude-opus-4-8"`(또는 `"opus"`). 1M = `"opus[1m]"` / `"claude-opus-4-8[1m]"`. `[1m]` 접미사가 1M 라우팅 신호(없으면 200K 기본, 클라이언트가 접미사 제거 후 API 호출). 1M은 Team/Enterprise에서 무료 자동 가용. 적용 후 `/status`로 확인.

### ② PreCompact 훅 → 핸드오프 기록 (신규)
- `~/.claude/settings.json`의 `hooks.PreCompact`에 command 훅 추가 → `~/.claude/hooks/precompact-checkpoint.py`.
- compact(자동·수동) **직전** 실행. stdin JSON에서 `transcript_path` / `trigger` / `cwd` / `session_id` 수신.
- `~/.claude/checkpoints/<slug>.md`에 1블록 append (slug = cwd 경로 인코딩, Claude Code projects 네이밍과 동일 방식 `/`→`-`).
- 기존 훅(PermissionRequest, SessionStart)과 공존. 현재 PreCompact 훅 없음.

**checkpoint 블록 포맷**:
```
## 2026-06-08T08:55Z · auto · /Users/tabber/ios-studio
- branch: feature/studioV3 (HEAD abc1234)
- session: 4bbef201-...
- last prompt: "<마지막 실프롬프트 200자, 노이즈/커맨드 제외>"
- transcript: /Users/tabber/.claude/projects/.../<id>.jsonl
```

**스크립트 규칙**:
- git 정보: `git -C <cwd> rev-parse --abbrev-ref HEAD` / `--short HEAD` (try/except, 실패 시 공란).
- last prompt: `transcript_path` JSONL 파싱, 마지막 진짜 user text(`<local-command`/`<command-`/`<bash-`/`<task-notification` 등 래퍼 제외) 200자 truncate.
- **절대 compact를 막지 않음**: 모든 로직 try/except, 항상 exit 0, block 출력(`{"decision":"block"}`/exit 2) 금지.
- ✅ **확정**(claude-code-guide 2026-06-08): PreCompact stdin = `{session_id, transcript_path, cwd, permission_mode, hook_event_name}`. `trigger`(manual/auto)는 stdin 보장 X — 훅 **matcher**로 구분되므로 스크립트는 `trigger` 있으면 쓰고 없으면 라벨 `compact`로 둔다. (PreCompact는 exit 2/block-JSON으로 compact를 막을 수 있으니 우리는 절대 그렇게 출력하지 않음.)

### ③ statusline 확장 (기존 스크립트)
- 대상: `/Users/tabber/claude-statusline-memes/scripts/statusline.py` (이미 `data['context_window']['used_percentage']`로 `Ctx [bar] N%` 표시 중).
- **추가 A — 예산 경고**: `used_percentage >= budget_warn_pct`(기본 80)이면 명시적 `⚠️ /clear` 큐(빨강) 추가. 200K 기본에선 이 %가 곧 200K 대비라 직관적.
- **추가 B — 메시지 수**: stdin의 `transcript_path`로 메시지 수(`user`(non-meta)+`assistant` 엔트리) 세서 `msgs N/200`(색상: ratio 기반) 표시.
  - 성능: 매 렌더(~수백ms)마다 큰 JSONL 재파싱 금지 → **mtime 캐시** `~/.claude/statusline-msgcount-cache.json` (`{transcript_path: {mtime, count}}`), mtime 변동 시에만 재계산.
  - `transcript_path` 없으면 graceful skip.
- 설정: 기존 `~/.claude/statusline-meme-config.json`에 `budget_warn_pct`(기본 80), `msg_budget`(기본 200) 키 추가.
- 모든 추가 로직 try/except로 감싼다(기존 스크립트 패턴) → 실패해도 statusline 안 깨짐.
- ✅ **확정**(claude-code-guide 2026-06-08): statusline stdin에 `transcript_path`·`session_id`·`context_window`(`used_percentage`/`context_window_size`/`total_input_tokens` 등)·`rate_limits` 포함 → msgs 카운트(추가 B) 성립.

### ④ Resume 흐름 (수동, 무비용)
- 임계 근처(statusline 경고) → ②가 이미 노트 자동 저장 → 사용자가 `/clear` → 새 세션에서 `~/.claude/checkpoints/<slug>.md`(또는 프로젝트의 기존 `docs/SESSION-CONTEXT.md`) 읽고 이어감.
- 토큰·메시지 **둘 다 리셋**. SessionStart 자동 주입은 하지 않음.

## 4. 변경 파일 목록

| 파일 | 변경 | git |
|---|---|---|
| `~/.claude/settings.json` | `model` 추가, `hooks.PreCompact` 추가 | (비추적) |
| `~/.claude/hooks/precompact-checkpoint.py` | 신규 | (비추적) |
| `~/.claude/statusline-meme-config.json` | `budget_warn_pct`/`msg_budget` 추가 | (비추적) |
| `/Users/tabber/claude-statusline-memes/scripts/statusline.py` | 예산 경고 + msgs 카운트 추가 | 추적(statusline 레포) |
| `~/.claude/checkpoints/` | 런타임 생성 | (비추적) |

## 5. B 지표 매핑

| B 트리거 | 잡는 구성요소 |
|---|---|
| `input > 500k` | ① (200K에선 도달 불가) |
| `msg > 200` | ②+④ (끊기 무비용화) + ③(msgs 카운트 인지) |
| A·C·D | 무관 |

## 6. 엣지/에러 처리
- PreCompact 훅 실패가 compact를 막으면 안 됨 → 전부 try/except, exit 0.
- statusline 추가 로직 실패가 statusline을 깨면 안 됨 → 전부 try/except(기존 패턴 준수).
- msgs 캐시는 mtime 기반, 손상 시 무시하고 재계산.
- 200K 모델 문자열이 틀리면 새 세션이 엉뚱한 모델로 뜰 수 있음 → 구현 직후 `/status`로 검증.

## 7. 검증
- **②**: `echo '{"transcript_path":"<실파일>","trigger":"manual","cwd":"<repo>","session_id":"x"}' | python3 ~/.claude/hooks/precompact-checkpoint.py` → checkpoint 파일에 블록 append 확인. 이어서 실제 `/compact`로 자동 트리거 확인.
- **③**: 높은 `context_window.used_percentage` + `transcript_path` 담은 가짜 stdin을 statusline에 흘려 → `⚠️ /clear` + `msgs N/200` 출력 확인.
- **①**: settings 적용 후 새 세션 `/status`가 200K로 뜨는지.

## 8. 미해결 항목 — 전부 확정됨 (claude-code-guide 2026-06-08)
1. ✅ 200K `model` 문자열 = `claude-opus-4-8`(접미사 없음). 1M = `[1m]` 접미사.
2. ✅ PreCompact stdin = `{session_id, transcript_path, cwd, permission_mode, hook_event_name}`; exit 2/block-JSON로 차단 가능(우리는 미사용). `trigger`는 matcher 기반.
3. ✅ statusline stdin에 `transcript_path`·`context_window`·`rate_limits` 포함 → msgs 카운트 성립.

남은 사소한 확인은 구현 중 실측으로: `permission_mode` 정확값, `trigger`가 일부 버전 stdin에 실릴 수 있는지(있으면 사용).
