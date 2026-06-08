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
