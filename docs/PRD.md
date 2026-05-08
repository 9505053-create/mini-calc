# PRD — 小算盤（Mini Calculator）  
版本：v0.2 Draft  
提出者：Scott  
用途：提供 Hermes 作為「新程式開發能力」測試專案，用於驗證 Hermes + 3AI CLI 協作、規格理解、任務拆解、Coding、Debug、Review 流程是否順暢。

---

# 1. 專案目標

建立一個簡單但完整的小算盤程式。

此專案重點不是功能複雜度，而是：

- 驗證 Hermes 是否能：
  - 理解 PRD
  - 自主拆分任務
  - 調度 3AI CLI
  - 建立 GitHub 專案
  - 開發
  - Debug
  - 修復錯誤
  - 做版本管理
  - 產生 release note

本專案屬於：

> 「Hermes 新程式開發能力驗證用專案」

---

# 2. 專案名稱

MiniCalc

備選名稱：

- Hermes Calculator
- ScottCalc
- Mini Desktop Calculator

---

# 3. 預期平台

第一階段：

- Windows Desktop
- Python Tkinter 或 HTML 單頁版皆可
- 優先簡單快速完成

第二階段（可選）：

- Web UI
- Electron
- Android APK
- PWA

---

# 4. 核心功能

## 基本運算

需支援：

- 加法
- 減法
- 乘法
- 除法

## 數值精度

- 浮點數顯示精度建議最多 **8 位小數**，以避免 `0.1 + 0.2` 類型的顯示異常（如 JavaScript 浮點問題）。
- 顯示位數上限建議為 **12 位數字**，超出時顯示科學記號或截斷。

---

## UI 需求

需有：

- 數字按鈕
- 運算按鈕
- 顯示區域
- 清除鍵（C）
- 等於鍵（=）

---

## 額外功能（加分）

若 Hermes 判定容易完成，可加入：

- 小數點
- 百分比
- 正負切換
- 鍵盤輸入
- 計算歷史紀錄

---

# 5. UI 設計方向

風格：

- 簡潔
- 現代
- 深色模式優先
- 不需要華麗動畫

重點：

- 功能正常
- UI 不要太醜
- 視窗不要過大

---

# 6. 技術建議（非強制）

Hermes 可自行決定。

建議方向：

## 方案A（推薦）

Python + Tkinter

優點：

- 開發快
- 易 Debug
- Windows 相容性高

---

## 方案B

HTML + JavaScript

優點：

- 容易做漂亮 UI
- 可直接部署 GitHub Pages

---

## 安全性限制（必須遵守）

禁止：

- 使用 `eval()`、`exec()` 或任何動態程式碼執行函式進行計算邏輯。
- 理由：這類做法在接受使用者輸入時存在嚴重安全漏洞（代碼注入風險）。

必須：

- 使用狀態機（arithmetic state machine）或正規表達式解析器處理運算邏輯。
- Python 方案可使用運算元 stack 方式實作；JavaScript 方案同樣應避免 `eval()`。

---

# 7. Hermes 工作流程要求

Hermes 需：

## 開發前

- 分析 PRD
- 建立 task list
- 決定技術方案

---

## 開發中

可調度：

- Codex CLI
- Claude CLI
- Gemini CLI

進行：

- UI
- 邏輯
- Debug
- Review

---

## Debug 要求

禁止：

- 假裝成功
- 未驗證即宣稱完成
- 編造測試結果

必須：

- 真實執行
- 顯示錯誤
- 修復後重新驗證

---

# 8. GitHub 要求

需：

- 建立 Git repo
- 定期 commit
- commit message 清楚
- 最終產生 release note

---

# 9. 驗收標準

最低要求：

- 可正常四則運算
- UI 可操作
- 不 crash
- 支援連續運算（定義：按下第二個運算子時，立即更新顯示結果，例如 `1 + 1 +` 顯示 `2`）

## 錯誤處理（必要）

必須處理下列異常情況，顯示錯誤訊息（例如 `Error`）而非讓程式崩潰：

- **除以零**：如 `5 ÷ 0`，顯示 `Error` 並允許使用者按 `C` 清除後繼續使用。
- **溢位**：結果超出顯示範圍時顯示 `Overflow` 或以科學記號呈現。
- **非法輸入序列**：如連續按兩個運算子，應忽略第二次或取代第一次。

---

# 10. 品質保證（QA）

Hermes 需為核心運算邏輯撰寫**自動化單元測試**：

測試案例至少須涵蓋：

| 測試項目 | 範例 |
|---|---|
| 基本四則運算 | `2 + 3 = 5`、`10 - 4 = 6` |
| 除以零 | `5 ÷ 0 → Error` |
| 浮點數運算 | `0.1 + 0.2 → 0.30000000` (精度截斷) |
| 連續運算 | `1 + 2 + 3 = 6` |
| 負數結果 | `3 - 5 = -2` |

測試工具建議：

- Python：`unittest` 或 `pytest`
- JavaScript：`Jest`

---

# 11. Scott 對 Hermes 的特別要求

這個專案主要是：

> 驗證 Hermes 是否具備「真正自主開發小型程式」能力。

比起功能多寡：

更重視：

- 任務拆解能力
- Debug 能力
- 誠實回報能力
- 多 AI 協作能力
- Git 管理能力

若遇到問題：

應優先誠實回報，
而不是虛構完成狀態。

---

# 12. 建議開發流程（參考）

Phase 1：
- 建立 repo
- 建立 UI

Phase 2：
- 完成四則運算

Phase 3：
- Debug
- 優化 UI
- 撰寫單元測試

Phase 4：
- Release v1.0

---

# 13. 預期成果

至少應輸出：

- 原始碼
- GitHub repo
- 執行畫面截圖
- Release note
- 開發歷程摘要
- 單元測試報告

---

# 14. 專案性質

此專案為：

- 練習型
- 驗證型
- AI Agent 工作流測試型

不要求商業等級。

重點是：

> 驗證 Hermes + 3AI CLI 工作流是否成熟。
