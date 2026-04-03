#!/bin/bash
# Lightweight subagent tracker for statusline
# Tracks active agents via SubagentStart/SubagentStop hooks

INPUT_DATA=$(cat)
STATE_FILE="$HOME/.claude/statusline-agents.json"

INPUT_DATA="$INPUT_DATA" STATE_FILE="$STATE_FILE" /usr/bin/python3 << 'PYEOF'
import json, os, sys, time

raw = os.environ.get("INPUT_DATA", "{}")
state_file = os.environ.get("STATE_FILE", "")


try:
    d = json.loads(raw)
except Exception:
    sys.exit(0)

event = d.get("hook_event_name", "")
agent_id = d.get("agent_id", "")
session_id = d.get("session_id", "")
agent_type = d.get("agent_type", "")

def read_state():
    try:
        with open(state_file) as f:
            return json.load(f)
    except Exception:
        return {"agents": []}

def write_state(state):
    tmp = state_file + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(state, f)
        os.replace(tmp, state_file)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass

state = read_state()

if event == "SubagentStart":
    if agent_id and not any(a.get("id") == agent_id for a in state["agents"]):
        state["agents"].append({
            "id": agent_id,
            "type": agent_type,
            "session": session_id,
            "started_at": time.time()
        })
    write_state(state)

elif event == "SubagentStop":
    state["agents"] = [a for a in state["agents"] if a.get("id") != agent_id]
    # Also clean stale agents (>2 hours)
    now = time.time()
    state["agents"] = [a for a in state["agents"] if now - a.get("started_at", 0) < 7200]
    write_state(state)

elif event == "SessionEnd":
    state["agents"] = [a for a in state["agents"] if a.get("session") != session_id]
    write_state(state)
    # Clean up legacy notchi state files
    import glob
    for f in glob.glob(os.path.expanduser("~/.claude/statusline-state-*.json")):
        try:
            os.remove(f)
        except Exception:
            pass
PYEOF
