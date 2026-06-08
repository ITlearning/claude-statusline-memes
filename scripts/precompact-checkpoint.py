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
