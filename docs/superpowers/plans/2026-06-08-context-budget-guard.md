# Context Budget Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep Tabber's Claude Code working context lean (default 200K + auto-compact), auto-record a fact checkpoint before every compaction, and surface context%/message-count warnings in the statusline — so both B-metric triggers (`input>500k`, `msg>200`) are suppressed.

**Architecture:** Pure logic lives in two importable modules in the statusline repo (`scripts/context_budget.py`, `scripts/checkpoint.py`) so it's unit-testable; a thin PreCompact hook wrapper and the existing `statusline.py` just wire them in. Config in `~/.claude/`, checkpoints in `~/.claude/checkpoints/`. settings.json gets the 200K default model + the PreCompact hook.

**Tech Stack:** Python 3 (stdlib only — `unittest`, no external deps), Claude Code hooks + statusLine, JSON config.

**Repo:** All tracked code lives in `/Users/tabber/claude-statusline-memes/`. `~/.claude/settings.json`, `~/.claude/statusline-meme-config.json`, and `~/.claude/checkpoints/` are untracked runtime config/output (changed but not committed).

---

### Task 0: Feature branch

**Files:** none (git)

- [ ] **Step 1: Create a working branch in the statusline repo**

```bash
cd /Users/tabber/claude-statusline-memes
git checkout -b feat/context-budget-guard
git status   # clean tree on new branch
```

---

### Task 1: `context_budget.should_warn`

**Files:**
- Create: `/Users/tabber/claude-statusline-memes/scripts/context_budget.py`
- Test: `/Users/tabber/claude-statusline-memes/tests/test_context_budget.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_context_budget.py`:

```python
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import context_budget as cb


class TestShouldWarn(unittest.TestCase):
    def test_above_threshold(self):
        self.assertTrue(cb.should_warn(85, 80))
    def test_at_threshold(self):
        self.assertTrue(cb.should_warn(80, 80))
    def test_below_threshold(self):
        self.assertFalse(cb.should_warn(79.9, 80))
    def test_none(self):
        self.assertFalse(cb.should_warn(None, 80))
    def test_bad_value(self):
        self.assertFalse(cb.should_warn("oops", 80))


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/tabber/claude-statusline-memes && python3 tests/test_context_budget.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'context_budget'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/context_budget.py`:

```python
"""Pure helpers for the context-budget statusline additions. Stdlib only, no I/O on import."""


def should_warn(used_percentage, threshold=80.0):
    """True when context usage % is at/above threshold."""
    if used_percentage is None:
        return False
    try:
        return float(used_percentage) >= float(threshold)
    except (TypeError, ValueError):
        return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_context_budget.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/context_budget.py tests/test_context_budget.py
git commit -m "feat(budget): add should_warn for context% threshold"
```

---

### Task 2: `context_budget.count_messages` (mtime-cached)

**Files:**
- Modify: `/Users/tabber/claude-statusline-memes/scripts/context_budget.py`
- Test: `/Users/tabber/claude-statusline-memes/tests/test_context_budget.py`

- [ ] **Step 1: Write the failing tests** (append to `tests/test_context_budget.py`, before the `if __name__` line)

```python
import json, tempfile, shutil


class TestCountMessages(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.tx = os.path.join(self.dir, 'transcript.jsonl')
        self.cache = os.path.join(self.dir, 'cache.json')

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _write(self, rows):
        with open(self.tx, 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')

    def test_counts_user_and_assistant_excludes_meta(self):
        self._write([
            {"type": "user", "message": {"content": "hi"}},
            {"type": "assistant", "message": {"content": []}},
            {"type": "user", "isMeta": True, "message": {"content": "meta"}},
            {"type": "summary"},
            {"type": "user", "message": {"content": "again"}},
        ])
        self.assertEqual(cb.count_messages(self.tx, self.cache), 3)

    def test_missing_file_returns_none(self):
        self.assertIsNone(cb.count_messages(self.dir + '/nope.jsonl', self.cache))
        self.assertIsNone(cb.count_messages(None, self.cache))

    def test_uses_cache_when_mtime_unchanged(self):
        self._write([{"type": "user", "message": {"content": "hi"}}])
        first = cb.count_messages(self.tx, self.cache)
        self.assertEqual(first, 1)
        # Poison the cache value but keep mtime — cached value should be returned
        mtime = os.stat(self.tx).st_mtime
        with open(self.cache, 'w') as f:
            json.dump({self.tx: {"mtime": mtime, "count": 999}}, f)
        self.assertEqual(cb.count_messages(self.tx, self.cache), 999)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_context_budget.py -v`
Expected: FAIL — `AttributeError: module 'context_budget' has no attribute 'count_messages'`

- [ ] **Step 3: Write minimal implementation** (append to `scripts/context_budget.py`)

```python
import os
import json


def _load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_json(path, obj):
    try:
        tmp = path + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(obj, f)
        os.replace(tmp, path)
    except Exception:
        pass


def _count_in_transcript(path):
    n = 0
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            t = o.get('type')
            if t == 'assistant':
                n += 1
            elif t == 'user' and not o.get('isMeta'):
                n += 1
    return n


def count_messages(transcript_path, cache_path):
    """Count user(non-meta)+assistant messages in the transcript, cached by mtime.
    Returns None when the transcript is missing/unreadable."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    try:
        mtime = os.stat(transcript_path).st_mtime
    except OSError:
        return None
    cache = _load_json(cache_path)
    ent = cache.get(transcript_path)
    if isinstance(ent, dict) and ent.get('mtime') == mtime:
        return ent.get('count')
    try:
        count = _count_in_transcript(transcript_path)
    except Exception:
        return None
    cache[transcript_path] = {'mtime': mtime, 'count': count}
    _save_json(cache_path, cache)
    return count
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_context_budget.py -v`
Expected: PASS (8 tests total)

- [ ] **Step 5: Commit**

```bash
git add scripts/context_budget.py tests/test_context_budget.py
git commit -m "feat(budget): add mtime-cached count_messages"
```

---

### Task 3: `checkpoint.slug_for` + `checkpoint.extract_last_prompt`

**Files:**
- Create: `/Users/tabber/claude-statusline-memes/scripts/checkpoint.py`
- Test: `/Users/tabber/claude-statusline-memes/tests/test_checkpoint.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_checkpoint.py`:

```python
import os, sys, json, tempfile, shutil, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import checkpoint as ck


class TestSlug(unittest.TestCase):
    def test_path_encoded(self):
        self.assertEqual(ck.slug_for('/Users/tabber/ios-studio'), 'Users-tabber-ios-studio')
    def test_empty(self):
        self.assertEqual(ck.slug_for(''), 'unknown')


class TestExtractLastPrompt(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.tx = os.path.join(self.dir, 't.jsonl')

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _write(self, rows):
        with open(self.tx, 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')

    def test_returns_last_real_skips_noise(self):
        self._write([
            {"type": "user", "message": {"content": "first real"}},
            {"type": "user", "message": {"content": "<command-name>/clear</command-name>"}},
            {"type": "user", "isMeta": True, "message": {"content": "meta"}},
            {"type": "assistant", "message": {"content": []}},
            {"type": "user", "message": {"content": "second real"}},
            {"type": "user", "message": {"content": "<bash-stdout>x</bash-stdout>"}},
        ])
        self.assertEqual(ck.extract_last_prompt(self.tx), 'second real')

    def test_truncates(self):
        self._write([{"type": "user", "message": {"content": "x" * 500}}])
        self.assertEqual(len(ck.extract_last_prompt(self.tx, maxlen=200)), 200)

    def test_missing(self):
        self.assertEqual(ck.extract_last_prompt(None), '')
        self.assertEqual(ck.extract_last_prompt(self.dir + '/nope'), '')


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_checkpoint.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'checkpoint'`

- [ ] **Step 3: Write minimal implementation**

Create `scripts/checkpoint.py`:

```python
"""Pure-ish helpers for the PreCompact checkpoint hook. Stdlib only."""
import os
import re
import json
import subprocess

_WRAP = ('<local-command', '<command-name>', '<command-message>',
         '<bash-input>', '<bash-stdout>', '<bash-stderr>',
         '<task-notification', '[request interrupted')


def slug_for(cwd):
    return re.sub(r'[^A-Za-z0-9]+', '-', cwd or 'unknown').strip('-') or 'unknown'


def extract_last_prompt(transcript_path, maxlen=200):
    if not transcript_path or not os.path.exists(transcript_path):
        return ''
    last = ''
    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if o.get('type') != 'user' or o.get('isMeta'):
                    continue
                c = o.get('message', {}).get('content')
                txt = None
                if isinstance(c, str):
                    txt = c
                elif isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get('type') == 'text':
                            txt = b['text']
                            break
                if not txt:
                    continue
                t = txt.strip()
                if t.startswith(_WRAP):
                    continue
                last = t
    except Exception:
        return ''
    return ' '.join(last.split())[:maxlen]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_checkpoint.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/checkpoint.py tests/test_checkpoint.py
git commit -m "feat(checkpoint): add slug_for + extract_last_prompt"
```

---

### Task 4: `checkpoint.git_info` + `build_block` + `append_checkpoint` + `run`

**Files:**
- Modify: `/Users/tabber/claude-statusline-memes/scripts/checkpoint.py`
- Test: `/Users/tabber/claude-statusline-memes/tests/test_checkpoint.py`

- [ ] **Step 1: Write the failing tests** (append to `tests/test_checkpoint.py`, before `if __name__`)

```python
class TestBuildAndRun(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.cp = os.path.join(self.dir, 'checkpoints')
        self.tx = os.path.join(self.dir, 't.jsonl')
        with open(self.tx, 'w') as f:
            f.write(json.dumps({"type": "user", "message": {"content": "do the thing"}}) + '\n')

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_build_block_has_fields(self):
        block = ck.build_block('2026-06-08T08:55Z', 'auto', '/x', 'main', 'abc1234',
                               'sess1', 'hello', '/t.jsonl')
        self.assertIn('## 2026-06-08T08:55Z · auto · /x', block)
        self.assertIn('branch: main (HEAD abc1234)', block)
        self.assertIn('session: sess1', block)
        self.assertIn('last prompt: "hello"', block)
        self.assertIn('transcript: /t.jsonl', block)

    def test_run_writes_checkpoint(self):
        data = {"cwd": self.dir, "transcript_path": self.tx,
                "session_id": "s1", "trigger": "manual"}
        path = ck.run(data, '2026-06-08T09:00Z', self.cp)
        self.assertTrue(os.path.exists(path))
        body = open(path).read()
        self.assertIn('· manual · ' + self.dir, body)
        self.assertIn('last prompt: "do the thing"', body)

    def test_run_handles_non_git_cwd_and_missing_trigger(self):
        data = {"cwd": self.dir, "transcript_path": self.tx, "session_id": "s2"}
        path = ck.run(data, '2026-06-08T09:01Z', self.cp)
        body = open(path).read()
        self.assertIn('· compact · ', body)   # trigger defaulted
        # non-git dir → branch placeholder, no crash
        self.assertIn('branch: ?', body)

    def test_run_appends(self):
        data = {"cwd": self.dir, "transcript_path": self.tx, "session_id": "s3"}
        p1 = ck.run(data, '2026-06-08T09:02Z', self.cp)
        ck.run(data, '2026-06-08T09:03Z', self.cp)
        self.assertEqual(open(p1).read().count('## '), 2)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/test_checkpoint.py -v`
Expected: FAIL — `AttributeError: module 'checkpoint' has no attribute 'build_block'`

- [ ] **Step 3: Write minimal implementation** (append to `scripts/checkpoint.py`)

```python
def git_info(cwd):
    def _run(args):
        try:
            return subprocess.run(['git', '-C', cwd] + args,
                                  capture_output=True, text=True, timeout=2).stdout.strip()
        except Exception:
            return ''
    return _run(['rev-parse', '--abbrev-ref', 'HEAD']), _run(['rev-parse', '--short', 'HEAD'])


def build_block(now_iso, trigger, cwd, branch, head, session_id, last_prompt, transcript_path):
    bh = (branch or '?') + (f" (HEAD {head})" if head else "")
    return (
        f"## {now_iso} · {trigger} · {cwd}\n"
        f"- branch: {bh}\n"
        f"- session: {session_id or '?'}\n"
        f"- last prompt: \"{last_prompt}\"\n"
        f"- transcript: {transcript_path or '?'}\n\n"
    )


def append_checkpoint(checkpoints_dir, cwd, block):
    os.makedirs(checkpoints_dir, exist_ok=True)
    path = os.path.join(checkpoints_dir, slug_for(cwd) + '.md')
    with open(path, 'a') as f:
        f.write(block)
    return path


def run(data, now_iso, checkpoints_dir):
    cwd = data.get('cwd') or os.getcwd()
    transcript = data.get('transcript_path')
    branch, head = git_info(cwd)
    block = build_block(now_iso, data.get('trigger') or 'compact', cwd, branch, head,
                        data.get('session_id', ''), extract_last_prompt(transcript), transcript)
    return append_checkpoint(checkpoints_dir, cwd, block)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/test_checkpoint.py -v`
Expected: PASS (9 tests total). Note: `test_run_handles_non_git_cwd` assumes `self.dir` (a tempdir) is not a git repo; if `$TMPDIR` is unexpectedly inside a repo, branch will be non-empty — re-run in a clean tempdir.

- [ ] **Step 5: Commit**

```bash
git add scripts/checkpoint.py tests/test_checkpoint.py
git commit -m "feat(checkpoint): add git_info, build_block, append, run"
```

---

### Task 5: PreCompact hook wrapper

**Files:**
- Create: `/Users/tabber/claude-statusline-memes/scripts/precompact-checkpoint.py`

- [ ] **Step 1: Write the wrapper**

Create `scripts/precompact-checkpoint.py`:

```python
#!/usr/bin/env python3
"""Claude Code PreCompact hook: append a fact checkpoint before compaction.
NEVER blocks compaction — always exits 0, never prints a block decision."""
import sys
import os
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import checkpoint
    data = json.load(sys.stdin)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    checkpoint.run(data, now, os.path.expanduser('~/.claude/checkpoints'))
except Exception:
    pass

sys.exit(0)
```

- [ ] **Step 2: Make executable**

```bash
chmod +x /Users/tabber/claude-statusline-memes/scripts/precompact-checkpoint.py
```

- [ ] **Step 3: Manual smoke test (simulate the hook)**

```bash
cd /Users/tabber/claude-statusline-memes
printf '%s' '{"cwd":"/Users/tabber/claude-statusline-memes","transcript_path":"","session_id":"smoke1","trigger":"manual"}' \
  | scripts/precompact-checkpoint.py
echo "exit=$?"
cat ~/.claude/checkpoints/Users-tabber-claude-statusline-memes.md
```
Expected: `exit=0`; checkpoint file shows a `## … · manual · …` block with this repo's real git branch/HEAD, `last prompt: ""`, `transcript: ?`.

- [ ] **Step 4: Verify it never blocks (malformed stdin)**

```bash
printf 'not json' | scripts/precompact-checkpoint.py; echo "exit=$?"
```
Expected: `exit=0`, no traceback.

- [ ] **Step 5: Commit**

```bash
git add scripts/precompact-checkpoint.py
git commit -m "feat(hook): add PreCompact checkpoint wrapper (never blocks)"
```

---

### Task 6: Wire context budget into statusline.py

**Files:**
- Modify: `/Users/tabber/claude-statusline-memes/scripts/statusline.py` (import near top after existing imports; new parts inserted right after the existing `Ctx` block, before the `# Git branch + time greeting` line ~341)

- [ ] **Step 1: Add the import**

After the existing top imports (`import json, sys, subprocess, os, time, random, urllib.request`), add:

```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import context_budget
```

- [ ] **Step 2: Insert the budget warning + message count parts**

Find the existing context-window block that ends with:

```python
else:
    parts.append(f"Ctx {DIM}{bar(0, 6)}{RESET} {DIM}--%{RESET}")
```

Immediately AFTER it (and before `# Git branch + time greeting`), insert:

```python
# Context budget: explicit /clear cue when usage crosses the warn threshold
try:
    _warn_pct = float(_cfg.get('budget_warn_pct', 80))
    if context_budget.should_warn(ctx_pct, _warn_pct):
        parts.append(f"{RED}⚠️ /clear{RESET}")
except Exception as e:
    if os.environ.get('STATUSLINE_DEBUG'):
        print(f"[DEBUG] budget warn error: {e}", file=sys.stderr)

# Message count vs budget (msg>200 is a B trigger; transcript counted, mtime-cached)
try:
    _msg_budget = int(_cfg.get('msg_budget', 200))
    _n = context_budget.count_messages(
        data.get('transcript_path'),
        os.path.expanduser('~/.claude/statusline-msgcount-cache.json'),
    )
    if _n is not None and _msg_budget > 0:
        _ratio = _n / _msg_budget
        _mc = RED if _ratio >= 0.9 else YELLOW if _ratio >= 0.7 else GREEN
        parts.append(f"{_mc}msgs {_n}/{_msg_budget}{RESET}")
except Exception as e:
    if os.environ.get('STATUSLINE_DEBUG'):
        print(f"[DEBUG] msg count error: {e}", file=sys.stderr)
```

(`_cfg`, `RED`, `YELLOW`, `GREEN`, `RESET`, `DIM`, `ctx_pct`, `data`, `parts` already exist in `statusline.py`.)

- [ ] **Step 3: Manual test — warning + msg count appear**

```bash
cd /Users/tabber/claude-statusline-memes
TX=~/.claude/projects/-Users-tabber-Documents-Grafana-Mobile
TXF=$(ls -t "$TX"/*.jsonl 2>/dev/null | head -1)
printf '%s' "{\"model\":{\"display_name\":\"Opus 4.8\"},\"context_window\":{\"used_percentage\":88},\"workspace\":{\"current_dir\":\"$PWD\"},\"transcript_path\":\"$TXF\"}" \
  | python3 scripts/statusline.py
```
Expected: output line contains `⚠️ /clear` (red) and `msgs N/200` with N matching that transcript's user+assistant count.

- [ ] **Step 4: Manual test — low usage, no warning**

```bash
printf '%s' '{"model":{"display_name":"Opus 4.8"},"context_window":{"used_percentage":20},"workspace":{"current_dir":"'"$PWD"'"}}' \
  | python3 scripts/statusline.py
```
Expected: NO `⚠️ /clear`; no `msgs` part (no transcript_path given); statusline still renders normally.

- [ ] **Step 5: Commit**

```bash
git add scripts/statusline.py
git commit -m "feat(statusline): show /clear warning + msgs N/budget"
```

---

### Task 7: settings.json (200K default + PreCompact hook) + config keys

**Files:**
- Modify: `~/.claude/settings.json` (untracked — apply via the update-config skill or a careful JSON edit that preserves every existing key)
- Modify: `~/.claude/statusline-meme-config.json` (untracked)

- [ ] **Step 1: Back up settings**

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak-$(date +%s)
```

- [ ] **Step 2: Add the default 200K model**

Add a top-level `"model": "claude-opus-4-8"` to `~/.claude/settings.json` (no `[1m]` suffix → 200K). Preserve all existing keys (`statusLine`, `hooks`, etc.).

- [ ] **Step 3: Add the PreCompact hook**

In `~/.claude/settings.json`, add under `hooks` (alongside the existing `PermissionRequest` and `SessionStart` entries) — do not remove those:

```json
"PreCompact": [
  {
    "matcher": "",
    "hooks": [
      { "type": "command", "command": "/Users/tabber/claude-statusline-memes/scripts/precompact-checkpoint.py" }
    ]
  }
]
```

- [ ] **Step 4: Validate JSON**

```bash
python3 -c "import json; json.load(open('$HOME/.claude/settings.json')); print('settings.json OK')"
```
Expected: `settings.json OK`

- [ ] **Step 5: Add tunable config keys**

Merge into `~/.claude/statusline-meme-config.json` (preserve existing keys like `interval_minutes`/`custom_messages`):

```json
{ "budget_warn_pct": 80, "msg_budget": 200 }
```

Validate:
```bash
python3 -c "import json; json.load(open('$HOME/.claude/statusline-meme-config.json')); print('config OK')"
```

- [ ] **Step 6: Verify in a NEW Claude Code session**

Open a new session and run `/status` (or check the model indicator). Expected: model is **Opus 4.8 (200K)**, not `[1m]`. The statusline shows `Ctx … %` and (once messages accrue) `msgs N/200`.

---

### Task 8: End-to-end verification + finish

**Files:** none (verification) + merge

- [ ] **Step 1: Full test suite green**

```bash
cd /Users/tabber/claude-statusline-memes
python3 tests/test_context_budget.py -v && python3 tests/test_checkpoint.py -v
```
Expected: all PASS.

- [ ] **Step 2: Real compaction writes a checkpoint**

In a real session in any repo, run `/compact`. Then:
```bash
ls -t ~/.claude/checkpoints/*.md | head -1 | xargs tail -n 8
```
Expected: a fresh `## <ts> · manual · <cwd>` block with correct branch/HEAD/last-prompt.

- [ ] **Step 3: Confirm compaction was not blocked**

The `/compact` in Step 2 should have completed normally (context compacted, session continues). If it errored, inspect the hook — but the wrapper always exits 0, so this should pass.

- [ ] **Step 4: Resume-flow sanity**

Hit a high context%, see `⚠️ /clear`, run `/clear`, then in the fresh session `cat ~/.claude/checkpoints/<slug>.md` (tail) and confirm you can resume from the recorded facts. Token + msg counters reset.

- [ ] **Step 5: Finish the branch**

Use `superpowers:finishing-a-development-branch` to decide merge/PR. (Do not auto-merge to the default branch without Tabber's go-ahead.)

---

## Self-Review

**Spec coverage** (spec §3 → tasks):
- ① 200K default → Task 7 (steps 2,6). ✅
- ② PreCompact hook + checkpoint format → Tasks 3,4,5,7(step3),8(step2). ✅ Block format from spec matches `build_block` (Task 4). ✅
- ③ statusline warning + msgs N/200 (cached) → Tasks 1,2,6. ✅ Config keys `budget_warn_pct`/`msg_budget` → Task 7 step5. ✅
- ④ Resume (manual) → Task 8 step4. ✅ (No SessionStart hook — matches "빼자" decision.)
- Error handling (hooks never block; statusline never breaks) → Task 5 steps 3-4, Task 6 try/except. ✅

**Placeholder scan:** No TBD/TODO; every code/test step has complete code; every command has expected output. ✅

**Type/name consistency:** `should_warn`, `count_messages`, `slug_for`, `extract_last_prompt`, `git_info`, `build_block`, `append_checkpoint`, `run` — used identically across module defs, tests, hook wrapper (`checkpoint.run`), and statusline (`context_budget.should_warn`/`count_messages`). ✅ Config keys `budget_warn_pct`/`msg_budget` consistent between Task 6 reads and Task 7 writes. ✅ Cache path `~/.claude/statusline-msgcount-cache.json` consistent (Task 6). ✅
