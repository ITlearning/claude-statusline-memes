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
