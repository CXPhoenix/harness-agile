# Claude skills prompt audit

日期：2026-09-26。依 `/claude-api prompt-audit` 流程執行；只提出修改，未套用到 repo。

> **修訂**：經 `harness-reviewer` 紅隊審查後，A1、A2、A3、B2、C1、C7 已修正，並新增 C7b；經 `harness-challenger` 挑戰後，撤回 A5 與 C13，D5 暫緩。下表是修訂後的版本，被撤回的項目以刪除線標示；修訂理由見[方法評估](2026-09-26-claude-skill-tuning-method.md)。

## 前提

- **範圍**：`.claude/skills/**` 中會被模型讀取的 Markdown（SKILL.md 與 reference 文件）、`.claude/agents/*.md`、`CLAUDE.md`。排除：`security-review/references/upstream-security-review.md`（有 checksum 鎖定的上游快照）、archify 的程式碼、測試、LICENSE 與 THIRD_PARTY_NOTICES。`AGENTS.md` 兩個 runtime 共用，不在本次範圍。
- **目標模型**：Claude Opus 5.5，在 Claude Code 中執行。行為基準沿用 Opus 5 文件記載的傾向：會自己驗證、容易委派 subagent、會照字面遵守 severity filter、書面產出偏長；Opus 5.5 另外在前端設計上會落回幾種預設風格。
- **無 API 請求程式碼**：範圍內沒有 Messages API 呼叫，因此 Group 4（request config）沒有項目。
- **非 Anthropic 標記**：`.agents/skills/*/agents/openai.yaml` 與 `.codex/` 屬於 Codex 那一邊，不在範圍內；Claude 副本中殘留的 Codex 用語列為 fossil。
- **來源**：`501c8a2` 是 upstream 匯入；`c4b2f8f`（2026-09-12／13）依 GPT／Codex 的 prompt 建議改寫了 code-review、grilling、to-spec、tdd、implement、init-template、agent-browser 與 SKILL-MECHANICS。該批改動在 2026-09-26 拆分時被一起複製到 Claude 副本。
- **執行方式**：四個唯讀 subagent 各掃描一組 skills。主 session 抽查了引文與行號，並把 i-have-adhd 的禁用語清單由 Medium 降為 flag，理由是它屬於使用者主動啟用的無障礙規格（keep list #1）。

## 摘要

- 提出修改的 finding 共 39 項：High 1、Medium 38；另有 24 項 flag 只記錄、不修改。
  - Group 1a（加壓語氣）9 項；1c／1f（過度指定、字數上限）6 項；1d（fossil、update suppressor）8 項。
  - Opus 5 行為變化相關：過度委派 7 項、過度驗證 4 項、severity filter 1 項、書面產出長度 1 項。
  - Opus 5.5 前端預設風格 6 項；Group 2（彼此矛盾的重複內容、會過時的具體細節）5 項；Group 3（觸發描述）1 項。
- **影響最大的三項**：
  1. `code-review` 對 Claude 自己在 `/implement` 裡的修改，一律派兩個 subagent 審查，再加上 400 字的報告上限。這同時踩到 Opus 5 的過度委派與過度驗證，而字數上限會壓低找出的問題數量。
  2. `tw-emoji-pr-note`／`release-note` 的「只輸出 code block」會讓 Claude 停在草稿，不接著執行 `gh pr create`／`gh release create`，與 CLAUDE.md 的規則直接矛盾。三個 tw-emoji skill 的範例還用雙引號包住草稿，草稿裡的反引號會被 shell 執行。
  3. `research` 與 `wayfinder` 會形成「subagent 再呼叫 subagent」的巢狀委派，而且要求 `harness-researcher` 寫檔，但它沒有寫檔工具。

## 提出修改的 findings

每一項在 patch 中是獨立的 commit／hunk，可以只挑想要的套用。

| ID | 位置 | 模式 | 過時原因 | 信心 | 動作 |
|---|---|---|---|---|---|
| B1 | init-template/SKILL.md:46 | 1d fossil | `$grill-with-docs` 是 Codex 的呼叫語法；Claude 副本只需要 `/grill-with-docs` | High | rewrite |
| A1 | code-review/SKILL.md:41 | 1d fossil | 「runtime adapter」是跨 runtime 的間接說法。兩軸一律用 subagent 屬於專案 gate，保留 | Medium | rewrite：直接寫出 `harness-reviewer` |
| A2 | code-review/SKILL.md:55 | 1f 字數上限 | 400 字上限會讓 reviewer 捨棄 findings；Opus 會照字面遵守 | Medium | rewrite：列出全部 findings，包含不確定的，附證據、confidence 與嚴重度，並說明此階段的任務是 coverage |
| A3 | security-review/SKILL.md:49 | severity filter | 在找候選問題時就套用 HIGH／MEDIUM 門檻會壓低找出的數量；門檻應只在最後過濾時使用 | Medium | rewrite：明文覆蓋 upstream 方法論中的不報告門檻 |
| A4 | diagnosing-bugs/SKILL.md:22 | 1a 加壓 | 「Be aggressive…Refuse to give up」會套用過度，並與「建不出 loop 就停下來問」互相衝突 | Medium | rewrite |
| ~~A5~~（撤回） | implement/SKILL.md:16-17 | 過度驗證 | 「further edit 後重跑」是 Codex 那批加入的 | Medium | rewrite：保留「修正失敗後重跑」 |
| A6 | security-review/SKILL.md:31-33 | 1d fossil | 說明理由寫的是 Codex 行為 | Medium | rewrite |
| B2 | grilling/SKILL.md:28 | scope 擴張 | 「proceed」會把 stage 1 直接推進到實作，跳過 spec、審查與 tickets | Medium | rewrite：確認後只延續已授權的工作；實測結果為 inconclusive，依文字清晰度決定 |
| B3 | research/SKILL.md:6-12 | 過度委派＋契約不符 | 無條件開 background agent；`harness-researcher` 無法寫檔 | Medium | rewrite；已實測：小型查詢時行為上有支持，並依實驗補上輸出格式（[實驗結果](2026-09-26-skill-behavior-experiment/README.md)） |
| B4 | wayfinder/SKILL.md:77,115 | 過度委派 | 每張 ticket 開一個 subagent，裡面又呼叫會開 agent 的 research | Medium | rewrite |
| B5 | wayfinder/SKILL.md:124 | 1a「If in doubt, use…」 | 預設叫用 skill 的寫法會造成過度觸發 | Medium | rewrite |
| B6 | to-tickets/SKILL.md:11 | Group 2 重複內容不一致 | upstream 的 `.scratch/` 範例與專案 tracker 設定衝突 | Medium | rewrite：指向 issue-tracker.md |
| B7 | to-tickets/SKILL.md:65 | scope 擴張 | 放在 Publish 段落下，讀起來像要開始實作 | Medium | rewrite |
| B8 | to-spec/SKILL.md:7 | 1a 大寫加壓 | 與第 19 行「確認 seam」互相矛盾 | Medium | rewrite |
| B9 | to-tickets/SKILL.md:31 | 1a 大寫加壓 | 規則本身正確，只是語氣過重 | Medium | rewrite |
| B10 | wayfinder/SKILL.md:57 | Group 2 會過時的具體細節 | 「100K token」綁定舊的 session 大小 | Medium | rewrite |
| C1 | writing-for-agents/SKILL-MECHANICS.md:10-14 | 1d fossil | Codex 時期的但書；Claude 樹裡已沒有 `agents/` 資料夾 | Medium | rewrite：保留原本較保守的 context 成本說法 |
| C2 | codebase-design/DESIGN-IT-TWICE.md:21 | 過度委派 | 「3+」沒有上限 | Medium | rewrite |
| C3 | improve-codebase-architecture/SKILL.md:27 | 過度委派 | 強制交給 subagent，連「感受到的摩擦」這種判斷也外包出去 | Medium | rewrite |
| C4 | prototype/LOGIC.md:50 | Opus 5.5 前端預設 | 「beautiful but restrained」太模糊，改成點名要避免的風格 | Medium | rewrite |
| C5 | teach/SKILL.md:51 | Opus 5.5 前端預設 | 「Think Tufte」容易導向米白底加襯線斜體，正好是預設風格 | Medium | rewrite |
| C6 | prototype/UI.md:54 | Opus 5.5 前端預設 | 三個變體可能共用同一套預設外觀 | Medium | add |
| C7 | improve-codebase-architecture/HTML-REPORT.md:96, :26 | Opus 5.5 前端預設 | 「not corporate」只是把一種預設換成另一種；scaffold 的 `bg-stone-50` 正是預設底色 | Medium | rewrite＋C7b 改為 `bg-white` |
| C8 | HTML-REPORT.md:52,123 | 1f 字數上限＋砍細節 | 「≤6 words」與禁用語清單 | Medium | rewrite |
| C9 | i-have-adhd/SKILL.md:130-142 | 自我檢查陷阱 | 每次回覆前的刪除清單，與前面的規則重複 | Medium | rewrite：只保留判準 |
| C11 | teach/SKILL.md:41 | 1a hedge | 「Try to」會被當成可以不做到 | Medium | rewrite |
| C12 | writing-for-agents/SKILL.md:81 | 1a | 教作者用更強烈的字眼加重語氣 | Medium | rewrite |
| ~~C13~~（撤回） | writing-for-agents/SKILL.md:74 | keep list #11（新模型需要補充指引） | 「只用正向描述」會讓作者刪掉前端的點名避免清單 | Medium | add：依讀者模型分流（Opus 5.5 用點名清單；4.8／Sonnet 5 用具體規格） |
| D1 | tw-emoji-pr-note:54; release-note:63 | 1d update suppressor | 「Output only」會讓模型把 code block 當成整個回合的終點 | Medium | rewrite：改為「code block 是 skill 的完整輸出，開 PR／發 release 不在此 skill 範圍」（依使用者決定，不寫執行步驟） |
| D2 | tw-emoji-commit/SKILL.md:36, :57-62 | 1d update suppressor | 「Output only」與同檔第 57-62 行的 commit 流程衝突 | Medium | rewrite＋remove：輸出範圍比照 D1，並移除第 57-62 行的 commit 執行段，改為指向 AGENTS.md 的 commit 規則（依使用者決定） |
| D3 | 三個 tw-emoji 的 sanitize 範例 | Group 2 自由度錯置 | 雙引號裡的反引號會觸發指令替換；應固定為一種安全寫法 | Medium | rewrite |
| D4 | evidence-report/SKILL.md:74-77 | Opus 5.5 前端預設 | 點名清單的形式是對的，但缺少 Opus 5.5 自己常用的預設風格 | Medium | add |
| D5（暫緩） | agent-browser/SKILL.md:3 | Group 3 觸發描述 | Codex 那批把描述從 925 字元砍到 199 字元，失去 stage 8 的觸發點 | Medium | rewrite |
| D6 | agent-browser/SKILL.md:54-61 | 1c padding | 推銷段落與第 18 行「優先用原生工具」互相矛盾 | Medium | remove |
| D7 | evidence-report/SKILL.md:79-83 | 過度驗證 | 交付前的開檔核對步驟 | Medium | rewrite：保留層級要誠實的品質底線 |
| D8 | evidence-report/SKILL.md:46-55 | 書面產出偏長 | 七段固定結構，卻沒有長度指引 | Medium | add |
| D9 | archify/SKILL.md:35 | Group 2 重複內容不一致 | 「never edit」與 visual review 修正後要重跑的規則衝突 | Medium | rewrite |
| D10 | archify/SKILL.md:87; delivery-contract.md:98 | 視覺輸入 scaffolding | 手動量測四種尺寸，與 `visual-check` 工具重複 | Medium | rewrite：工具保留 |
| D12 | archify/schemas/README.md:167 | Group 2 重複內容不一致 | 只寫 GitHub，但其他文件允許 Gitee 與 local-only | Medium | rewrite |


## 只標記、不修改的項目

- **A7**：security-review 的 runtime 中立用語（`host terminal tool`、`native agent API`）。
- **A8**：CLAUDE.md:9-10「bounded independent work」是開放式的委派邀請。可改為「pipeline stage 要求獨立 reviewer 或 research 時才用」。
- **A9**：tdd/SKILL.md:8「Reuse unchanged guidance」是 Codex 時期留下的句子。
- **A10**：兩個 agent 角色的「Do not edit／start subagents」已經由 `tools:` 限制強制執行。
- **A11**：resolving-merge-conflicts 的「Understand deeply」語氣偏重。
- **A12（範圍外，但值得注意）**：resolving-merge-conflicts:14「Stage everything and commit」與 Hard rule 5 衝突：它沒有經過 `/tw-emoji-commit`，也可能把 `uv.lock` 這類無關檔案一起加進去。
- **B11**：grilling 的「relentlessly」出現在內文，不是觸發描述。
- **B12**：grilling:26 的委派句。
- **B13**：to-spec／to-tickets 的「Do NOT」只是語氣問題。
- **B14**：domain-modeling:64 把同一件事重複說了三次。
- **C10**：i-have-adhd 的禁用開場白與結尾語清單。這是使用者主動啟用的無障礙規格，所以不改。
- **C14**：teach:30「Never trust your parametric knowledge」。
- **C15**：improve-codebase-architecture:60 的大寫。
- **C16**：i-have-adhd:19 的持續生效句。compaction 之後可能仍需要，所以保留。
- **C17**：「Cap lists at 5」是受眾需求。
- **C18**：prototype/UI.md 把「sub-shape A」這個偏好重複講了六次。
- **C19**：SKILL-MECHANICS:22 的授權延續措辭。
- **C20**：writing-for-agents 沒有提醒作者避免驗證與委派步驟，可以補一行。
- **D11**：archify「不要用文字規劃座標」。thinking 常開時這條無法遵守，但來源證據不足。
- **D13**：archify 重複寫了兩次「不得宣稱成功」。
- **D14**：archify 有附日期的 Windows opener 歷史說明。規則本身保留。
- **D15**：evidence-report「ends with」與結構順序不一致。
- **D16**：tw-emoji-commit 的類型表缺少 `security`／`test`。
- **D17**：agent-browser 的 `hidden: true` 需要確認 Claude Code 是否支援。本 session 列出的 agent-browser 帶的是 upstream 的長描述，可能是使用者層級的同名 skill 蓋過了專案版本。

## 刻意保留的內容

- **專案 gate**：兩張表格、凍結的 review prompt、zero P0、stage 6 的兩個審查軸、security 的 false-positive 過濾，以及 tickets 核准迴圈。
- **固定腳本與契約**：review-surface 的 Git 指令、init-template 腳本、wizard 的 `bash -n`／shellcheck，以及 archify 的 CLI、receipt、schema 契約。
- **格式範本**：commit／PR／release 格式、spec／ticket／ADR／CONTEXT 模板。
- **其他**：agent-browser 的 Apache-2.0 修改聲明，以及 evidence-report 原本就採用點名形式的避免清單。
- **沒有 findings 的檔案**：各 subagent 報告中列為 clean 的檔案，例如 code-review 的兩份 references、tdd 的 tests／mocking、handoff、wizard、archify 的 renderer README。

## Patch 與驗證

- 合併 patch：[2026-09-26-claude-skill-prompt-audit.patch](2026-09-26-claude-skill-prompt-audit.patch)。修訂後共 45 項修改、26 個檔案，+67／−87；在目前的 HEAD `244c555` 上執行 `git apply --check` 通過。
- 逐項 patch：45 個 `git format-patch` 檔案，放在本 session 的 scratchpad `patches5/`，屬於暫存。D5 仍在 patch 中，確認 agent-browser 的載入來源之前不要套用。
- **尚未驗證**：修改後的行為。依 prompt-audit Step 7，移除只是假設；建議每次套一小批，實際跑對應的 skill（例如 `/code-review`、`/tw-emoji-pr-note`、`/research`），比較套用前後的行為。
