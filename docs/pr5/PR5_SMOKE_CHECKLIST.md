# MiniCalc PR-05 Smoke Checklist

Run command:

```bash
python3 calculator.py
```

## Standard Mode

- [ ] `1 + 2 +` displays `3` and appends history `Standard: 1 + 2 = 3`.
- [ ] Continue `3 =` after the previous step displays `6` and appends `Standard: 3 + 3 = 6`.
- [ ] `1 + -` replaces the operator and does not append history.
- [ ] `5 ÷ 0 +` displays `Error`, appends error history, and `AC` recovers.
- [ ] Explicit `2 + 3 =` still records history.
- [ ] `Clear History` clears the visible tape.

## Regression

- [ ] Memory buttons still work in Standard Mode.
- [ ] Date Mode successful calculations still append history; invalid inputs do not.
- [ ] Programmer Mode base switches still append history; same-base click does not.
- [ ] History panel remains scrollable and visible.
