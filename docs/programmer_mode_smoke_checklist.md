# Programmer Mode Smoke Checklist

Use this checklist for PR-02.1 manual verification on Windows before moving to PR-03.

## Launch

```bash
python calculator.py
```

## Standard Mode regression

- [ ] App opens in Standard mode.
- [ ] `2 + 3 =` shows `5`.
- [ ] `AC` clears display to `0`.
- [ ] Keyboard Backspace removes one digit while entering a number.
- [ ] `100 + 10 %` shows `110`.

## Programmer Mode

- [ ] Click `[Programmer]`; display starts from current non-negative integer or `0`.
- [ ] Clear button label is `AC`, so it does not conflict with HEX digit `C`.
- [ ] In HEX mode, pressing `A`, `B`, `C`, `D`, `E`, `F` appends HEX digits.
- [ ] Pressing `AC` clears Programmer value to `0`.
- [ ] DEC `255` -> HEX shows `FF`.
- [ ] HEX `FF` -> DEC shows `255`.
- [ ] DEC `10` -> BIN shows `1010`.
- [ ] BIN mode disables digits `2-9` and A-F buttons.
- [ ] OCT mode disables digits `8-9` and A-F buttons.
- [ ] Keyboard Backspace in Programmer mode removes one digit.
- [ ] Escape in Programmer mode clears to `0`.
- [ ] Entering beyond 64-bit unsigned max is ignored rather than freezing or expanding indefinitely.

## Mode switching

- [ ] Switching back to `[Standard]` preserves Standard calculator display/state.
- [ ] Switching from non-integer Standard display into Programmer mode resets Programmer value to `0` by design.
