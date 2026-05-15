# MiniCalc

一個小而美的 Python 計算機，使用 Tkinter GUI + headless 計算核心。PR-04 增加 session-only Calculation History / Session Tape；PR-03 增加 Date Calculator、Standard Mode Memory Keys，並把模式邏輯整理到 headless controllers，方便測試與後續擴充。

## 架構

- `calculator.py` — Tkinter UI wrapper；負責 widget 建立、layout、display 更新
- `source/calculator_engine.py` — Standard Mode headless arithmetic engine
- `source/mode_controllers.py` — Standard / Programmer / Date headless mode controllers
- `source/memory_store.py` — Standard Mode memory-key storage
- `source/date_calculator.py` — ISO date difference and duration arithmetic
- `source/base_converter.py` — DEC/HEX/BIN/OCT 進位轉換與輸入驗證
- `source/history_store.py` — session-only Calculation History / Session Tape
- `tests/test_calculator.py` — Standard arithmetic engine regression tests
- `tests/test_base_converter.py` — Programmer Mode converter tests
- `tests/test_memory_store.py` — Memory Keys headless core tests
- `tests/test_date_calculator.py` — Date Calculator headless core tests
- `tests/test_history_store.py` — HistoryStore headless core tests
- `tests/test_mode_controllers.py` — Standard / Programmer / Date controller tests
- `tests/test_programmer_ui.py` — lightweight UI coordination tests（不啟動 Tk 視窗）
- `docs/` — PRD、架構設計、版本說明、PR3 規劃與開發歷程

## 功能

- Standard Mode：四則運算、小數、百分比、正負號切換、退格與鍵盤輸入
- Calculation History（session-only）：
  - Standard Mode：記錄 `=` / keyboard Enter 完成的計算與 controlled errors
  - Date Mode：記錄成功日期差與日期加減
  - Programmer Mode：記錄成功 base conversion
  - `Clear History` 清除目前 session 歷史
- Memory Keys（Standard Mode）：`MC`、`MR`、`MS`、`M+`、`M-`
- Date Mode：
  - 日期差：`end_date - start_date`
  - 日期加減：years / months / weeks / days
  - ISO 日期格式：`YYYY-MM-DD`
  - 月底與閏年使用 deterministic clamp 規則
- Programmer Mode：DEC、HEX、BIN、OCT 整數輸入與即時進位切換
- Programmer Mode 以 64-bit unsigned integer 為輸入上限，超出範圍的輸入會被忽略或拒絕
- 清除鍵顯示為 `AC`，避免與 HEX digit `C` 混淆
- 依目前進位限制可輸入字元；HEX 顯示一律使用大寫 A-F
- 無效輸入會被控制處理，不會造成程式崩潰

## 執行

```bash
python calculator.py
```

## 測試

```bash
python -m pytest -q
```

目前 PR-04 自動化測試覆蓋 Standard arithmetic、MemoryStore、DateCalculator、HistoryStore、mode controllers、Programmer converter 與 lightweight UI coordination。

## 手動 GUI smoke checklist

- PR-04：`docs/pr4/PR4_SMOKE_CHECKLIST.md`
- PR-03：`docs/pr3/PR3_SMOKE_CHECKLIST.md`
- Programmer Mode 專項：`docs/programmer_mode_smoke_checklist.md`

## Programmer Mode 使用

啟動 GUI 後切換 `[Programmer]`，再使用 `[DEC|HEX|BIN|OCT]` 選擇目前進位。輸入會依進位限制，例如 BIN 只接受 `0` 和 `1`，OCT 只接受 `0` 到 `7`。PR-02/PR-02.1/PR-03 目前僅支援非負整數轉換，範圍限制為 64-bit unsigned integer。

## Date Mode 使用

啟動 GUI 後切換 `[Date]`：

- Difference：輸入 start date 與 end date，按 `Calculate`，顯示 day difference。
- Date +/-：輸入 base date、選擇 `add` 或 `subtract`，填入 years / months / weeks / days，按 `Calculate`，顯示結果日期。

限制：Date Mode 僅支援 ISO 日期，不支援 time zone、time-of-day、business days。

## Memory Keys 使用

Memory Keys 僅在 Standard Mode 啟用：

- `MS`：儲存目前顯示值
- `MR`：把 memory recall 到目前 Standard input/display
- `M+` / `M-`：用目前顯示值加到 / 減到 memory
- `MC`：清除 memory

限制：memory 是 session-only，關閉 app 後不保存。


## Calculation History 使用

History panel 會顯示目前 session 的近期計算：

- Standard：只記錄按 `=` 或鍵盤 Enter 完成的計算；controlled error 也會記錄，例如除以零。
- Date：只記錄成功的日期差或日期加減。
- Programmer：只記錄成功切換 base 的 conversion；輸入 digit、backspace、same-base click 不會產生歷史。

`Clear History` 只清除目前 session 的歷史。關閉 app 後 history 不會保存。
