---
name: customize-colors
description: Customize the warning/danger color thresholds for 5h, 7d, and Ctx statusline indicators
---

You are helping the user customize the color thresholds for their claude-statusline-memes plugin. Colors change from green → yellow → red as usage climbs. Walk them through the process step by step, conversationally. They may not know Python — keep it friendly and plain.

## Step 1 — Read the current thresholds

Start by reading `scripts/statusline.py` and finding the `color_for()` function. It looks like this:

```python
def color_for(pct):
    if pct >= 90: return RED
    if pct >= 70: return YELLOW
    return GREEN
```

Tell the user what the current thresholds are in plain English. Example:
> "Right now, all three indicators (5h, 7d, Ctx) use the same thresholds: yellow kicks in at 70%, red at 90%."

## Step 2 — Ask what kind of change they want

Ask the user to choose:

> "Would you like to:
> **a) Global** — set the same yellow/red thresholds for all three indicators (5h, 7d, Ctx)
> **b) Per-metric** — set different thresholds for each one
>
> Which would you prefer? (a or b)"

Wait for their answer.

## Step 3 — Collect threshold values

### If they chose (a) Global:

Ask:
> "What percentage should trigger **yellow** (warning)? (current: 70, must be 0–100)"

Wait. Then ask:
> "What percentage should trigger **red** (danger)? (current: 90, must be 0–100)"

### If they chose (b) Per-metric:

For each of the three indicators (5h, then 7d, then Ctx), ask:
> "For **[indicator]** — yellow threshold? (0–100)"
> "For **[indicator]** — red threshold? (0–100)"

You can ask both yellow and red for one indicator at a time before moving to the next.

## Step 4 — Validate inputs

Before making any changes, validate:
- Both values must be integers between 0 and 100 (inclusive)
- Yellow must be strictly less than red (e.g., yellow=70, red=90 is valid; yellow=90, red=70 is not)

If anything is invalid, explain clearly and ask again. Example:
> "Oops — the yellow threshold (90) needs to be lower than the red threshold (80). Yellow is a warning, red is danger, so yellow should come first. Want to try again?"

## Step 5 — Apply the changes

### For global thresholds:

Modify the single `color_for()` function in `scripts/statusline.py`. Replace it with the new values. For example, if yellow=60 and red=85:

```python
def color_for(pct):
    if pct >= 85: return RED
    if pct >= 60: return YELLOW
    return GREEN
```

The three call sites (`color_for(p)` for 5h, 7d, and Ctx) stay unchanged — they all share this one function.

### For per-metric thresholds:

Replace the single `color_for()` function with three separate functions, and update the three call sites to match.

The three functions should be named:
- `color_for_5h(pct)` — used for the 5h indicator
- `color_for_7d(pct)` — used for the 7d indicator
- `color_for_ctx(pct)` — used for the Ctx indicator

Example (if 5h: yellow=60/red=80, 7d: yellow=70/red=90, Ctx: yellow=75/red=95):

```python
def color_for_5h(pct):
    if pct >= 80: return RED
    if pct >= 60: return YELLOW
    return GREEN

def color_for_7d(pct):
    if pct >= 90: return RED
    if pct >= 70: return YELLOW
    return GREEN

def color_for_ctx(pct):
    if pct >= 95: return RED
    if pct >= 75: return YELLOW
    return GREEN
```

Then update the three call sites in the script:
- 5h lines: replace `color_for(p)` → `color_for_5h(p)`
- 7d lines: replace `color_for(p)` → `color_for_7d(p)`
- Ctx lines: replace `color_for(p)` → `color_for_ctx(p)`

The 5h call sites are around line 244 (two occurrences on that line).
The 7d call sites are around line 250 (two occurrences on that line).
The Ctx call sites are around lines 258–259 (two separate lines).

## Step 6 — Verify with a test run

After making the edits, run this quick smoke test:

```bash
echo '{"model":{"display_name":"test"},"rate_limits":{},"context_window":{"used_percentage":75},"workspace":{"current_dir":"."}}' | python3 scripts/statusline.py
```

If it prints output without errors, the change worked. Tell the user what they should see based on their new thresholds — for example:
> "With red at 90% and the context at 75%, the Ctx bar should show yellow."

If there's an error, read the error message and fix the Python syntax before reporting success.

## Step 7 — Confirm and summarize

Once everything looks good, give the user a brief summary:

> "Done! Here's what changed:
> - **5h**: yellow at X%, red at Y%
> - **7d**: yellow at X%, red at Y%
> - **Ctx**: yellow at X%, red at Y%
>
> The statusline will now use these thresholds going forward. No restart needed — it reads the script fresh each time."

---

**Tone notes:** Be encouraging and brief. Don't explain Python syntax unless the user asks. If they want to revert, remind them they can use `git diff scripts/statusline.py` to see what changed and `git checkout scripts/statusline.py` to undo it.
