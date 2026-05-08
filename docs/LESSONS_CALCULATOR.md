# Lessons — 計算/數值類

## [CALC-001] tkinter 必須延遲 import
- 觸發場景：Python GUI 專案，engine 需要獨立測試
- 錯誤表現：headless 環境 pytest 全部 ERROR（`no display name and no $DISPLAY`）
- 根本原因：import tkinter 放在 module level，headless 環境沒有 GUI 依賴
- 修復方式：把 `import tkinter` 移到 UI class `__init__` 內部或 `if __name__ == "__main__"` 區塊
- 適用邊界：僅適用於需要 headless 測試的 GUI 專案
- 不適用場景：純 CLI 工具、Web 後端
- 是否需要自動測試：是（conftest.py 加 try/except skip）
- 來源任務與日期：2026-05-08 MiniCalc

## [CALC-002] pytest 快取孤兒（Windows 權限鎖死）
- 觸發場景：WSL + Windows Python 交叉跑 pytest
- 錯誤表現：`.pytest_cache/pytest-cache-files-*` 權限變 `d--x--x--x`，WSL 和 cmd 都刪不掉
- 根本原因：Windows Python 建立的快取檔案在 WSL 下權限異常
- 修復方式：用 `cmd.exe /c "del /f /q /s"` 強制刪除；或在 prompt 中要求 3AI CLI 測試完自行清理
- 適用邊界：WSL + Windows 混合環境
- 不適用場景：純 Linux、純 Windows
- 是否需要自動測試：否（環境問題，非程式邏輯）
- 來源任務與日期：2026-05-08 MiniCalc

## [CALC-003] arch_plan.md File List 必須機器可解析
- 觸發場景：Contract Check 需要自動比對預期檔案 vs 實際產出
- 錯誤表現：正則解析失敗，誤抓到 Example/Addition/Title 等非檔案名
- 根本原因：arch_plan 中的 File List 格式不一致
- 修復方式：Phase 0 prompt 強制要求格式 `- filename.ext: description`，每行一個檔案
- 適用邊界：所有需要 Contract Check 的 pipeline
- 不適用場景：不產檔案的純分析任務
- 是否需要自動測試：是（Contract Check 自動驗證）
- 來源任務與日期：2026-05-08 MiniCalc

## [CALC-004] _format_decimal 反模式：先量化再檢查長度
- 觸發場景：`100000 / 3` 顯示 `3.33333333e+4` 而非 `33333.333333`
- 錯誤表現：科學記號過早觸發，大整數+小數的組合全部走 scientific
- 根本原因：先 quantize 到固定 8 位小數，再檢查總 digit 數，超了就直接科學記號
- 修復方式：先檢查整數部分長度，整數超過顯示上限才用科學記號；否則動態分配剩餘空間給小數位
- 修復邏輯：`int_digits > MAX_DISPLAY_DIGITS` → scientific；else → `decimal_places = min(8, MAX_DISPLAY_DIGITS - int_digits)`
- 適用邊界：所有需要數值格式化的計算機/金融工具
- 不適用場景：不需要科學記號備援的簡單顯示
- 是否需要自動測試：是（邊界 case：5位整數+小數、13位整數）
- 來源任務與日期：2026-05-08 MiniCalc PR-01

## [CALC-005] 百分比行為要對齊主流計算機
- 觸發場景：`100 + 10%` 顯示 `100.1` 而非 `110`
- 錯誤表現：百分比當成純除以 100，不符合使用者直覺
- 根本原因：只做了 `value / 100`，沒考慮 pending operator 的上下文
- 修復方式：
  - `+`/`-` 時：`percent = first_operand * value / 100`，立即執行 `_compute_pending()`，顯示結果
  - `*`/`/` 時：`percent = value / 100`，僅更新 current_input，等 `=` 再算
- 適用邊界：所有給「一般人」用的計算機
- 不適用場景：工程計算機（可能有不同 % 定義）
- 是否需要自動測試：是（`100+10%=110`, `100-10%=90`, `200*10%=20`）
- 來源任務與日期：2026-05-08 MiniCalc PR-01

## [CALC-006] toggle_sign 不應顯示 -0
- 觸發場景：初始狀態按 `+/-` 顯示 `-0`
- 錯誤表現：`0` 和 `-0` 在數學上等價，但 UI 上造成困惑
- 根本原因：`press_toggle_sign` 直接把 `"0"` 變成 `"-0"` 沒有攔截
- 修復方式：在 toggle_sign 中加入 `"0"` / `"-0"` 的判斷，保持為 `"0"`
- 適用邊界：所有有 +/- 切換的計算機
- 不適用場景：需要區分正負零的科學計算
- 是否需要自動測試：是
- 來源任務與日期：2026-05-08 MiniCalc PR-01
