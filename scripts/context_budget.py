"""Pure helpers for the context-budget statusline additions. Stdlib only, no I/O on import."""


def should_warn(used_percentage, threshold=80.0):
    """True when context usage % is at/above threshold."""
    if used_percentage is None:
        return False
    try:
        return float(used_percentage) >= float(threshold)
    except (TypeError, ValueError):
        return False


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
