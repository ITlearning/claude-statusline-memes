---
name: customize-layout
description: Customize the statusline layout — reorder or hide elements like model, 5h, 7d, Ctx, meme, and branch
---

You are helping the user customize their claude-statusline-memes layout. Be friendly, conversational, and efficient. Do exactly what the user asks — don't over-explain.

## Step 1 — Show the current layout

Read `scripts/statusline.py` to understand the current state of the `parts` list (lines 227–282). Then display the current layout visually:

```
현재 레이아웃:
[1] 모델명  [2] 5h  [3] 7d  [4] Ctx  [5] 밈  [6] 브랜치
```

Adjust the numbering to reflect any elements that are currently hidden (commented out with `# hidden by customize-layout skill`). Show hidden elements with a strikethrough indicator, e.g. `~~[3] 7d~~` or note them separately:

```
숨겨진 항목: 7d
```

## Step 2 — Ask what they want to change

Offer two options (they can do both at once):

**a. 순서 변경** — reorder elements by specifying a new order  
**b. 항목 숨기기/보이기** — toggle visibility of individual elements

Accept natural language, for example:
- "5h 7d 숨겨줘"
- "Ctx를 맨 앞으로"
- "브랜치 없애고 순서를 모델, 밈, Ctx, 5h, 7d로"
- "7d 다시 보이게 해줘"
- "1 5 4 2 3 6" (numbered reorder)

## Step 3 — Apply the changes

Before making any edits, use the Read tool to get the exact current content of `scripts/statusline.py`.

The six layout elements map to these `parts.append(...)` blocks:

| 항목 | 코드 블록 |
|------|-----------|
| 모델 | `if model:` block (model append) |
| 5h | `if fh is not None:` block + else |
| 7d | `if sd is not None:` block + else |
| Ctx | `if ctx_pct is not None:` block + else |
| 밈 | `t_color, t_text = time_greeting()` + meme append |
| 브랜치 | `if branch:` append block |

### Hiding elements
When hiding an element, comment out its `parts.append(...)` line(s) with `# hidden by customize-layout skill` at the end of the comment. For if/else blocks, comment out both branches. Example:

```python
# if fh is not None:  # hidden by customize-layout skill
#     p = float(fh)
#     countdown = fmt_remaining(fh_obj.get('resets_at'))
#     parts.append(f"5h {color_for(p)}{bar(p)}{RESET} {color_for(p)}{p:.0f}%{RESET}{countdown}")
# else:  # hidden by customize-layout skill
#     parts.append(f"5h {DIM}{bar(0)}{RESET} {DIM}--%{RESET}")
```

### Restoring hidden elements
When restoring a hidden element, uncomment all lines that have `# hidden by customize-layout skill`.

### Reordering elements
To reorder, physically move the code blocks within the `parts = []` section so they appear in the desired sequence. Use targeted Edit calls — move one block at a time if needed. Keep the variable setup code (like `rl = data.get('rate_limits') or {}`) in place above the parts section; only move the `parts.append(...)` blocks.

The separator variable `sep` and `parts = []` initialization must stay at the top. The final `if parts: print(sep.join(parts))` must stay at the bottom.

## Step 4 — Verify with a test run

After applying the changes, run:

```bash
echo '{"model":{"display_name":"claude-sonnet-4-6"},"rate_limits":{"five_hour":{"used_percentage":42},"seven_day":{"used_percentage":18}},"context_window":{"used_percentage":31},"workspace":{"current_dir":"'"$(pwd)"'"}}' | python3 scripts/statusline.py
```

Show the output to the user.

## Step 5 — Confirm or undo

Ask: "이렇게 보이면 괜찮아요? 아니면 되돌릴까요?"

If the user wants to undo, use the Read tool to check the current state and revert any commented/moved blocks back to the original positions. The original default order is: 모델 → 5h → 7d → Ctx → 밈 → 브랜치.

---

**Tips:**
- 밈(meme)과 브랜치는 논리적으로 짝이지만 분리할 수 있어요.
- 모델명도 다른 위치로 옮길 수 있어요.
- 한 번에 여러 변경(순서 변경 + 숨기기)도 가능해요.
- 항목을 삭제하지 말고 항상 주석 처리로 숨겨야 나중에 복원할 수 있어요.
