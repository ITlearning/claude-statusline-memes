#!/usr/bin/env python3
import json, sys, subprocess, os, time, random, urllib.request
from datetime import datetime

data = json.load(sys.stdin)

# Rate limit cache helpers
_RL_CACHE_PATH = os.path.expanduser('~/.claude/statusline-rl-cache.json')
_RL_API_TTL = 300  # refresh from OAuth API every 5 minutes

def _load_rl_cache():
    try:
        with open(_RL_CACHE_PATH) as f:
            return json.load(f)
    except Exception:
        return {}

def _save_rl_cache(**kwargs):
    # Merge-update: only overwrite fields that have live data (never overwrite with None)
    try:
        cache = _load_rl_cache()
        cache.update({k: v for k, v in kwargs.items() if v is not None})
        tmp = _RL_CACHE_PATH + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(cache, f)
        os.replace(tmp, _RL_CACHE_PATH)
    except Exception:
        pass

def _refresh_rl_from_api_background():
    fetch_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fetch-rl.py')
    if not os.path.exists(fetch_script):
        return
    try:
        subprocess.Popen(
            [sys.executable, fetch_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    except Exception:
        pass

# Load meme config
_config_path = os.path.expanduser('~/.claude/statusline-meme-config.json')
try:
    with open(_config_path) as _f:
        _cfg = json.load(_f)
except Exception:
    _cfg = {}
_interval_sec = int(_cfg.get('interval_minutes', 5)) * 60
_custom_messages = _cfg.get('custom_messages', [])

# Seed random based on interval — message stays fixed until next interval
random.seed(int(time.time() // _interval_sec))

# Meme cache — fetches memes.json from GitHub daily in background
_MEMES_URL = "https://raw.githubusercontent.com/ITlearning/claude-statusline-memes/main/memes.json"
_MEMES_CACHE_PATH = os.path.expanduser('~/.claude/statusline-memes-cache.json')
_MEMES_CACHE_TTL = 86400  # 24 hours


def _load_memes_cache():
    try:
        with open(_MEMES_CACHE_PATH) as _cf:
            _cache = json.load(_cf)
        if time.time() - _cache.get('fetched_at', 0) < _MEMES_CACHE_TTL:
            return _cache
        _refresh_memes_background()
        return _cache  # use stale while refreshing
    except Exception:
        _refresh_memes_background()
        return None


def _refresh_memes_background():
    _fetch_code = (
        'import json,urllib.request,time,os;'
        'url="' + _MEMES_URL + '";'
        'cache_path="' + _MEMES_CACHE_PATH + '";'
        'data=json.loads(urllib.request.urlopen(url,timeout=5).read());'
        'data["fetched_at"]=time.time();'
        'tmp=cache_path+".tmp";'
        'open(tmp,"w").write(json.dumps(data));'
        'os.replace(tmp,cache_path)'
    )
    try:
        subprocess.Popen(
            [sys.executable, '-c', _fetch_code],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    except Exception:
        pass


_memes_cache = _load_memes_cache()

# Colors
GREEN  = '\033[32m'
YELLOW = '\033[33m'
RED    = '\033[31m'
CYAN   = '\033[36m'
DIM    = '\033[2m'
RESET  = '\033[0m'

def color_for(pct):
    if pct >= 90: return RED
    if pct >= 70: return YELLOW
    return GREEN

def bar(pct, width=5):
    filled = round(pct * width / 100)
    return '█' * filled + '░' * (width - filled)

def fmt_remaining(resets_at, use_days=False):
    if resets_at is None:
        return ''
    remaining = int(resets_at) - int(time.time())
    if remaining <= 0:
        return ''
    total_minutes = remaining // 60
    h, m = divmod(total_minutes, 60)
    if use_days and h >= 24:
        d, h = divmod(h, 24)
        return f' {d}d{h}h'
    if h > 0:
        return f' {h}h{m:02d}m'
    return f' {m}m'

MAGENTA = '\033[35m'
ORANGE  = '\033[33m'
BGYELLOW= '\033[93m'
BGGREEN = '\033[92m'
BLUE    = '\033[34m'
PINK    = '\033[95m'

_AI_MEMES_FALLBACK = [
    "해결할 수 있습니다! (Claude Code를 키며)",
    "Claude한테 물어봤더니 더 헷갈림...",
    "AI가 짠 코드라 나는 모름",
    "일단 Claude한테 던져봄",
    '"이 코드 설명해줘" → Claude: "훌륭한 코드입니다!"',
    "버그 고쳐달라고 했더니 다 갈아엎음",
    "Claude: 물론이죠! 나: ...이게 맞나?",
    "AI 페어 프로그래밍 중 (AI가 다 짬)",
    "코드 리뷰어: Claude, 작성자: Claude, 나: 구경 중",
    '"간단히 수정해줘" → 파일 12개 변경됨',
    "Claude Code 없이 어떻게 살았지...",
    "프롬프트 엔지니어링이 곧 개발 실력인 시대",
    "Claude가 짠 코드를 Claude가 리뷰하는 중",
    "context window 날아가기 3, 2, 1...",
    '"이 에러 뭐야" → Claude: "좋은 질문입니다!"',
    "나: 이거 왜 됨? Claude: 사실 저도...",
    "주석 작성자: Claude. 코드 작성자: Claude. 버그 책임자: 나",
    "오늘 git log에 내 커밋이 없다...",
    "Claude가 시키는 대로 했더니 빌드 터짐",
    '"너무 잘 만들어줬다" 혼자 뿌듯해하는 중',
    "tokens: 남은 거 없음. 뇌: 남은 거 없음",
    "AI한테 설명하다가 내가 이해함",
    "이번엔 진짜 내가 짠 거임 (거짓말)",
    "Claude가 deprecated API 썼다...",
    "Claude야 운동 많이 된다.",
]
AI_MEMES = (_memes_cache.get('ai_memes') if _memes_cache else None) or _AI_MEMES_FALLBACK

def time_greeting():
    h = datetime.now().hour
    if h < 5:
        color = MAGENTA
        emoji = '🌙'
        msgs = [
            "이 시간에 코딩하는 사람은 둘 중 하나: 천재 아니면 나...",
            "버그가 밤에 더 잘 보이는 것 같다 (착각)",
            "커밋 메시지: fix",
            "아 됐다!! (5분 후 더 큰 버그 발견)",
            "스택오버플로우가 친구인 시간...",
            "자도 돼 근데 안 잘 거잖아?",
            "일단 돌아가면 된 거 아님?",
            "변수명 a, b, c로 짜고 나중에 고친다... (안 고침)",
            "에러 메시지를 읽지 않는 시간...",
            "무한루프인 줄 알았는데 그냥 느린 거였음",
            "git blame 하지 마...",
            "내가 짠 코드 내가 이해 못 함...",
        ]
    elif h < 9:
        color = ORANGE
        emoji = '🌅'
        msgs = [
            "오늘은 진짜 클린코드 쓴다!",
            "어젯밤 내가 짠 코드 다시 보는 중...",
            "커피 없이는 git push 없다!",
            "야 이거 누가 짠 거야? (내가 짰다)",
            "TODO: 오늘 안에 TODO 없애기",
            "좋은 아침!",
            "밤새 생각한 해결책: 그냥 지우면 됨",
            "오늘은 테스트 코드도 쓴다 (거짓말)",
            "지난 커밋 메시지: asdf...",
            "오늘 PR 하나만 머지하면 성공이다!",
            "기획서 다시 읽는 중...",
        ]
    elif h < 12:
        color = BGYELLOW
        emoji = '☀️'
        msgs = [
            "지금 이 순간만큼은 뭐든 할 수 있어!",
            "회의 전까지 한 기능만 더...",
            "스탠드업에서 할 말 만드는 중...",
            "뇌가 돌아가는 황금 시간대!",
            "오늘의 목표: 어제보다 조금 덜 부수기",
            "버그 잡으러 간다!",
            "이 함수 누가 300줄로 만들었어?",
            "리뷰 코멘트: nit: 변수명이...",
            "문서화 하면서 코딩? 가능한 얘기야?",
            "Ctrl+Z 40번째...",
            "타입 에러 15개... 천천히 하자",
        ]
    elif h < 18:
        color = BGGREEN
        emoji = '🌞'
        msgs = [
            "밥 먹고 나니까 전부 내 잘못인 것 같다...",
            "주석으로 덮어두면 안 보이는 거 아님?",
            "코드리뷰 == 과거의 나와 싸우기",
            "작동은 하는데 이유는 모름...",
            "이 버그 이름을 뭐라 지을까?",
            "왜 갑자기 안 되지?",
            "스택 오버플로우 답변 날짜: 2013년...",
            "작동하는 코드는 건드리지 않는다 (원칙)",
            "배포 버튼에 손이 떨린다...",
            "이 if문 한 다섯 개면 되겠지?",
            "npm install 중... (커피 마실 시간)",
        ]
    elif h < 21:
        color = PINK
        emoji = '🌆'
        msgs = [
            "딱 이것만 하고 퇴근 (3번째)",
            "이게 마지막 커밋이라고 했었다...",
            "배고프지만 빌드는 해야지!",
            "오늘 안에 머지 못 하면 내일의 내가 해결해줄 거야...",
            "저녁 먹으면서 에러 로그 읽는 중",
            "퇴근은 커밋 후에!",
            "오늘 커밋 메시지: WIP fix",
            "집에 가면서도 머릿속에서 디버깅 중...",
            "PR 설명: 이것저것 고침",
            "야 근데 이거 진짜 마지막이야!",
            "슬랙 알림 끄는 시간",
        ]
    else:
        color = BLUE
        emoji = '🌃'
        msgs = [
            "오늘 중으로 라고 했지 몇 시까지라고 안 했잖아!",
            "이쯤 되면 코드가 나를 짜고 있는 거 아닐까...",
            "자려고 누웠다가 해결책이 떠올랐다!",
            "다크모드 == 야근모드",
            "내일 아침의 나야, 미안해...",
            "졸음과의 싸움 중...",
            "커밋하고 자야지... 또 커밋하고 자야지...",
            "이 코드 이해하는 사람은 전 세계에 나 하나",
            "오늘의 교훈: 환경변수 확인 먼저",
            "git stash하고 자는 게 맞나...",
            "내일 오전 미팅 있는데...",
        ]
    # Override msgs with cached version if available
    _time_key = {0: 'late_night', 1: 'morning', 2: 'late_morning', 3: 'afternoon', 4: 'evening'}.get(
        0 if h < 5 else 1 if h < 9 else 2 if h < 12 else 3 if h < 18 else 4 if h < 21 else 5
    ) or 'night'
    if _memes_cache:
        _cached_msgs = (_memes_cache.get('time_memes') or {}).get(_time_key, {}).get('messages')
        if _cached_msgs:
            msgs = _cached_msgs
    # 20% 확률로 AI 밈 등장, 커스텀 메시지는 항상 풀에 포함
    pool = msgs + _custom_messages
    if random.random() < 0.2:
        pool = pool + AI_MEMES
    return color, f"{emoji} {random.choice(pool)}"

sep = DIM + ' │ ' + RESET
parts = []

# Model
model = (data.get('model') or {}).get('display_name', '')
if model:
    parts.append(f"{DIM}{model}{RESET}")

# Rate limits (with cache fallback) + context window (no cache — resets each session)
rl = data.get('rate_limits') or {}
fh_obj = rl.get('five_hour') or {}
sd_obj = rl.get('seven_day') or {}
fh = fh_obj.get('used_percentage')
sd = sd_obj.get('used_percentage')
ctx_pct = (data.get('context_window') or {}).get('used_percentage')

# Merge-update cache with any live rate limit data from Claude Code stdin
if fh is not None:
    _save_rl_cache(five_hour=fh_obj)
if sd is not None:
    _save_rl_cache(seven_day=sd_obj)

# Load cache for fallback; trigger API refresh if stale
_rl_cache = _load_rl_cache()
if time.time() - _rl_cache.get('api_fetched_at', 0) > _RL_API_TTL:
    _refresh_rl_from_api_background()
_cached_fh = _rl_cache.get('five_hour') or {}
_cached_sd = _rl_cache.get('seven_day') or {}

# 5h
_fh = fh if fh is not None else _cached_fh.get('used_percentage')
_fh_obj = fh_obj if fh is not None else _cached_fh
if _fh is not None:
    p = float(_fh)
    countdown = fmt_remaining(_fh_obj.get('resets_at'))
    suffix = f"{DIM}~{RESET}" if fh is None else ""
    parts.append(f"5h {color_for(p)}{bar(p)}{RESET} {color_for(p)}{p:.0f}%{suffix}{RESET}{countdown}")
else:
    parts.append(f"5h {DIM}{bar(0)}{RESET} {DIM}--%{RESET}")

# 7d
_sd = sd if sd is not None else _cached_sd.get('used_percentage')
_sd_obj = sd_obj if sd is not None else _cached_sd
if _sd is not None:
    p = float(_sd)
    countdown = fmt_remaining(_sd_obj.get('resets_at'), use_days=True)
    suffix = f"{DIM}~{RESET}" if sd is None else ""
    parts.append(f"7d {color_for(p)}{bar(p)}{RESET} {color_for(p)}{p:.0f}%{suffix}{RESET}{countdown}")
else:
    parts.append(f"7d {DIM}{bar(0)}{RESET} {DIM}--%{RESET}")

# Context window — no cache fallback (resets each session, cached value would be misleading)
if ctx_pct is not None:
    p = float(ctx_pct)
    c = color_for(p)
    parts.append(f"Ctx {c}{bar(p, 6)}{RESET} {c}{p:.0f}%{RESET}")
else:
    parts.append(f"Ctx {DIM}{bar(0, 6)}{RESET} {DIM}--%{RESET}")

# Git branch + time greeting
cwd = (data.get('workspace') or {}).get('current_dir') or data.get('cwd', '')
branch = ''
if cwd:
    try:
        branch = subprocess.check_output(
            ['git', '-C', cwd, 'symbolic-ref', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        pass

# Ralph Loop counter (inspired by oh-my-claudecode)
_ralph_state_path = os.path.join(cwd, '.claude', 'ralph-loop.local.md') if cwd else ''
if _ralph_state_path and os.path.isfile(_ralph_state_path):
    try:
        # Stale check: ignore state files older than 2 hours (abandoned sessions)
        _ralph_mtime = os.path.getmtime(_ralph_state_path)
        if time.time() - _ralph_mtime < 7200:
            with open(_ralph_state_path) as _rf:
                _ralph_raw = _rf.read()
            if _ralph_raw.startswith('---'):
                _fm_end = _ralph_raw.index('---', 3)
                _fm = _ralph_raw[3:_fm_end]
                _ralph_active = False
                _ralph_iter = 0
                _ralph_max = 0
                for _line in _fm.strip().splitlines():
                    _line = _line.strip()
                    if _line.startswith('active:'):
                        _ralph_active = _line.split(':', 1)[1].strip().lower() == 'true'
                    elif _line.startswith('iteration:'):
                        _ralph_iter = int(_line.split(':', 1)[1].strip())
                    elif _line.startswith('max_iterations:'):
                        _ralph_max = int(_line.split(':', 1)[1].strip())
                if _ralph_active:
                    # Color by progress: green → yellow → red
                    if _ralph_max > 0:
                        _ralph_pct = _ralph_iter / _ralph_max
                        if _ralph_pct >= 0.9:
                            _ralph_color = RED
                        elif _ralph_pct >= 0.7:
                            _ralph_color = YELLOW
                        else:
                            _ralph_color = GREEN
                        _ralph_txt = f"🔄 Ralph {_ralph_color}{_ralph_iter}/{_ralph_max}{RESET}"
                    else:
                        _ralph_color = GREEN if _ralph_iter < 7 else YELLOW if _ralph_iter < 15 else RED
                        _ralph_txt = f"🔄 Ralph {_ralph_color}#{_ralph_iter}{RESET}"
                    parts.append(_ralph_txt)
    except Exception as e:
        if os.environ.get('STATUSLINE_DEBUG'):
            print(f"[DEBUG] Ralph loop error: {e}", file=sys.stderr)

# Active agents indicator (SubagentStart/SubagentStop hook 기반)
_agents_state_path = os.path.expanduser('~/.claude/statusline-agents.json')
try:
    with open(_agents_state_path) as _af:
        _agents = json.load(_af).get('agents', [])
    # Filter stale agents (>2 hours)
    _agents = [a for a in _agents if time.time() - a.get('started_at', 0) < 7200]
    if _agents:
        _agent_label = "agent" if len(_agents) == 1 else "agents"
        parts.append(f"{CYAN}🤖 {len(_agents)} {_agent_label}{RESET}")
except Exception as e:
    if os.environ.get('STATUSLINE_DEBUG'):
        print(f"[DEBUG] Agents indicator error: {e}", file=sys.stderr)

t_color, t_text = time_greeting()
parts.append(f"{t_color}{t_text}{RESET}")
if branch:
    parts.append(f"{CYAN}⎇ {branch}{RESET}")

if parts:
    print(sep.join(parts))
else:
    print(f"{DIM}claude{RESET}")
