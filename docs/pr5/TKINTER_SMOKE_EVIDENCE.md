# MiniCalc PR-05 Tkinter Smoke Evidence

Date: 2026-05-15
Branch: `pr5-final-release`
Head at smoke time: `971d93b feat: record standard chaining history`

## Environment

The WSL session has no interactive display:

```text
TclError: no display name and no $DISPLAY environment variable
```

`xvfb-run` is available, so the GUI smoke was executed in a headless X virtual framebuffer. This verifies Tkinter window construction, widget layout, and real `CalculatorUI` callbacks without requiring Scott to manually click a visible Windows desktop window.

## Command

```bash
PYTHONPATH=. xvfb-run -a python3 /tmp/minicalc_pr5_tk_smoke.py
```

## Result

```text
PASS: Tkinter UI instantiated and PR-05 smoke checklist exercised under Xvfb
```

## Covered interactions

- Tk root instantiation, title, History frame, disabled History text widget.
- Standard chaining: `1 + 2 +` displays `3` and appends `[Standard] 1 + 2 = 3`.
- Continued calculation: `3 =` after previous step displays `6` and appends `[Standard] 3 + 3 = 6`.
- Operator replacement: `1 + -` appends no history.
- Controlled chaining error: `5 ÷ 0 +` displays `Error` and appends `[Standard:error] 5 ÷ 0 = Error`.
- Keyboard Enter: `8 / 4 Return` displays `2` and appends history.
- Memory keys: `MS`, `MR`, `MC` display and indicator behavior.
- Date Mode successful difference appends history.
- Programmer Mode DEC→HEX conversion appends history.

## Caveat

This is a real Tkinter GUI smoke under Xvfb, not a human-observed visible Windows desktop screenshot. It closes the local environment's executable GUI smoke gate; a human visible smoke can still be repeated on Scott's Windows desktop before merging if desired.
