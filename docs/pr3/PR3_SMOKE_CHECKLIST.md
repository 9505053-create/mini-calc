# PR-03 Manual GUI Smoke Checklist

Use this checklist after automated tests pass. Run from the repo root:

```bash
python calculator.py
```

## 1. Launch

- [ ] App window opens without traceback.
- [ ] Initial mode is Standard.
- [ ] Display shows `0`.
- [ ] Mode buttons include `Standard`, `Programmer`, and `Date`.

## 2. Standard Mode Regression

- [ ] Press `2`, `+`, `3`, `=` → display shows `5`.
- [ ] Press `AC` → display shows `0`.
- [ ] Press `5`, `÷`, `0`, `=` → display shows controlled `Error`.
- [ ] Press `AC` after `Error` → display returns to `0`.
- [ ] Keyboard digits and `Enter` still work for basic arithmetic.

## 3. Standard Mode Memory Keys

- [ ] Press `1`, `2`, `MS` → display remains `12`, memory indicator shows `M`.
- [ ] Press `AC`, `MR` → display shows `12`.
- [ ] Press `AC`, `2`, `M+`, `MR` → display shows `14`.
- [ ] Press `AC`, `3`, `M-`, `MR` → display shows `11`.
- [ ] Press `MC` → memory indicator clears.
- [ ] In `Error` state, `MS` does not overwrite existing memory.

## 4. Programmer Mode Regression

- [ ] Switch to `Programmer` → DEC base selected.
- [ ] Enter `15`, switch to `HEX` → display shows `F`.
- [ ] Press `C` in HEX → display appends HEX digit `C` rather than clearing.
- [ ] Press `AC` → display clears to `0`.
- [ ] Switch to `BIN`; digits `2-9` and `A-F` are disabled or ignored.
- [ ] In HEX, enter `FFFFFFFFFFFFFFFF`; one more `F` is ignored.

## 5. Date Mode

- [ ] Switch to `Date` → display shows `Date Mode` and date fields appear.
- [ ] Difference workflow: start `2026-05-15`, end `2026-05-16`, Calculate → display shows `1 day`.
- [ ] Difference workflow: start `2026-05-16`, end `2026-05-15`, Calculate → display shows `-1 day`.
- [ ] Date +/- workflow: base `2024-01-31`, operation `add`, months `1`, Calculate → display shows `2024-02-29`.
- [ ] Date +/- workflow: base `2024-03-31`, operation `subtract`, months `1`, Calculate → display shows `2024-02-29`.
- [ ] Invalid date `2026-02-30` shows controlled `Invalid date`.
- [ ] Invalid duration component `abc` shows controlled `Invalid duration`.

## 6. Mode Switching

- [ ] Switch Standard → Programmer → Date → Standard repeatedly; no traceback.
- [ ] Memory value survives mode switching during the same session.
- [ ] Date widgets hide outside Date Mode.
- [ ] Programmer HEX buttons hide outside Programmer Mode.

## Result

- [ ] PASS — all checks above completed.
- [ ] FAIL — record failed step and screenshot/log before fixing.
