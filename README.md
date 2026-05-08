# MiniCalc

一個小而美的 Python 計算機，使用 Tkinter GUI + headless 計算引擎，並提供 Programmer Mode 進位轉換。

## 架構
- `calculator.py` — 主程式（CalculatorEngine + CalculatorUI）
- `source/base_converter.py` — DEC/HEX/BIN/OCT 進位轉換與輸入驗證
- `tests/test_calculator.py` — 標準計算機回歸測試
- `tests/test_base_converter.py` — Programmer Mode 進位轉換測試
- `docs/` — PRD、架構設計、版本說明、經驗教訓

## 功能
- Standard Mode：四則運算、小數、百分比、正負號切換、退格與鍵盤輸入
- Programmer Mode：DEC、HEX、BIN、OCT 整數輸入與即時進位切換
- 依目前進位限制可輸入字元；HEX 顯示一律使用大寫 A-F
- 無效輸入會被忽略，不會造成程式崩潰

## 執行
```bash
python calculator.py
```

## 測試
```bash
pytest tests/ -v
```

## Programmer Mode 使用
啟動 GUI 後切換 `[Programmer]`，再使用 `[DEC|HEX|BIN|OCT]` 選擇目前進位。輸入會依進位限制，例如 BIN 只接受 `0` 和 `1`，OCT 只接受 `0` 到 `7`。PR-02 僅支援非負整數轉換。
