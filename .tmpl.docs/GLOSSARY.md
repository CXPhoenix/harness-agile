# 範本維護術語

本詞彙表定義維護此範本時使用的開發助理與擴充能力名稱。CC／Codex 前綴表示使用環境，不表示必須維護兩份核心指引。

## 開發助理

**Coding assistant（開發助理）**：
協助維護者處理專案工作的 Codex 或 Claude Code。
_避免_：以未加前綴的 Agent 指稱開發助理。

**CC Agent**：
為 Claude Code 定義、具有特定職責與執行限制的開發代理角色。

**Codex Agent**：
為 Codex 定義、具有特定職責與執行限制的開發代理角色。

## 代理分層

**決策者（decider）**：
主 session。理解需求、規劃、委派、做最終決定、與使用者溝通、載入 skills 與 commit；model 與 effort 由使用者在工具中選擇，範本不設定。
_避免_：把 `harness-researcher` 當成獨立層級；它是決策者的延伸，一律繼承主 session。

**執行者（executor）**：
`harness-executor`。套用已核准的變更，並執行 gate 或驗證者要判讀的每個指令，回報原始輸出與 exit status；決策者委派 ticket 實作時，也由它照轉錄的 `/tdd` 循環跑 red 與 green。

**驗證者（verifier）**：
`harness-reviewer` 與 `harness-challenger`，共用一組 model／effort。審查、唱反調、依證據確認；可做唯讀檢視（讀取、列出、搜尋檔案，`git show`／`diff`／`log`／`status`，CodeGraph 查詢），不執行檢查、建置、測試、腳本或任何會改變狀態的指令，這些交給執行者。

**層級設定（tier setting）**：
一個 runtime 為執行者與驗證者各自選定的 model 與 effort，`inherit` 是合法值；由該 runtime 的 `setup-roles` 寫入，各 runtime 只設定自己的角色。

**角色紀錄（role record）**：
`docs/agents/template-source.json` 裡的 `roles.<runtime>`，記錄該 runtime 的層級設定與 `configured_on`。主 session 的角色設定提醒以目前 runtime 的 key 是否存在作為停止條件；各 runtime 的 `setup-roles` 只寫自己的 key。

## 程式碼工具

**程式碼地圖（code map）**：
CodeGraph 在 `.codegraph/` 建立的本機 symbol／呼叫圖索引。不進版控；CLI 由每台機器自行安裝。

## 工作指引與擴充套件

**Skill**：
維護者提供給開發助理、可按需載入的可重用工作指引；可由 Codex 或 Claude Code 使用。

**CC Skill**：
供 Claude Code 使用的 Skill。可與 Codex Skill 共用同一份核心指引。

**Codex Skill**：
供 Codex 使用的 Skill。可與 CC Skill 共用同一份核心指引。

**CC Plugin**：
供 Claude Code 安裝與管理的擴充套件，可封裝 Skill 或其他擴充能力。

**Codex Plugin**：
供 Codex 安裝與管理的擴充套件，可封裝 Skill 或其他擴充能力。
