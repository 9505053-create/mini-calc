# MiniCalc

一個小而美的 Python 計算機，使用 Tkinter GUI + headless 計算引擎。

## 架構
- `calculator.py` — 主程式（CalculatorEngine + CalculatorUI）
- `tests/test_calculator.py` — 28 個單元測試
- `docs/` — PRD、架構設計、版本說明、經驗教訓

## 執行
```bash
python calculator.py
```

## 測試
```bash
pytest tests/ -v
```
