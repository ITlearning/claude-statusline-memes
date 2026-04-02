#!/usr/bin/env python3
"""Fetch rate limits from Anthropic OAuth API and save to local cache."""
import json, os, subprocess, time, urllib.request
from datetime import datetime, timezone


def resets_at_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
    except Exception:
        return None


cache_path = os.path.expanduser('~/.claude/statusline-rl-cache.json')

try:
    raw = subprocess.check_output(
        ['security', 'find-generic-password', '-s', 'Claude Code-credentials', '-w'],
        stderr=subprocess.DEVNULL, text=True
    ).strip()
    token = json.loads(raw)['claudeAiOauth']['accessToken']

    req = urllib.request.Request(
        'https://api.anthropic.com/api/oauth/usage',
        headers={
            'Authorization': 'Bearer ' + token,
            'anthropic-beta': 'oauth-2025-04-20'
        }
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=5).read())
    fh = resp.get('five_hour') or {}
    sd = resp.get('seven_day') or {}

    try:
        with open(cache_path) as f:
            cache = json.load(f)
    except Exception:
        cache = {}

    cache['five_hour'] = {
        'used_percentage': round(float(fh.get('utilization', 0)), 1),
        'resets_at': resets_at_ts(fh.get('resets_at'))
    }
    cache['seven_day'] = {
        'used_percentage': round(float(sd.get('utilization', 0)), 1),
        'resets_at': resets_at_ts(sd.get('resets_at'))
    }
    cache['api_fetched_at'] = time.time()

    tmp = cache_path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(cache, f)
    os.replace(tmp, cache_path)
except Exception:
    pass
