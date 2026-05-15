# PR-04 Manual GUI Smoke Checklist — Calculation History

Run from repo root:

```bash
python calculator.py
```

## Launch and layout

- [ ] App opens without traceback.
- [ ] History panel/list is visible or clearly toggleable.
- [ ] History panel is scrollable or does not break layout as entries accumulate.
- [ ] Standard, Programmer, and Date mode controls remain usable.

## Standard Mode history

- [ ] Enter `2 + 3 =`; history shows `2 + 3 = 5`.
- [ ] Enter `5 ÷ 0 =`; history shows controlled `Error` entry and app remains usable.
- [ ] Press digits / backspace / sign toggle / percent without `=`; no unwanted history spam is added.
- [ ] Press `1 + 2 +`; display may update, but no PR-04 chaining entry is required.
- [ ] Press keyboard `Enter` for a calculation; history behaves like `=` button.

## Date Mode history

- [ ] Difference calculation records one readable history line.
- [ ] Date add/subtract duration records one readable history line.
- [ ] Invalid date input shows controlled error and does not add successful history.

## Programmer Mode history

- [ ] DEC `255` → HEX records one conversion line.
- [ ] Same-base click does not create a history line.
- [ ] Digit entry / backspace / ignored invalid input does not create history spam.

## Clear History

- [ ] `Clear History` removes all visible entries.
- [ ] After clearing, new calculations append from an empty history.
