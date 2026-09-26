# Claude skills 微調方法評估：prompt-audit 與官方 prompting 文章

日期：2026-09-26。評估對象是 `/claude-api prompt-audit` 流程，以及五篇官方 prompting 文章：best practices、Opus 5.5、Opus 5、Opus 4.8、Sonnet 5。文章原文於當日下載。

## 結論

兩者不是二選一：**文章是判準，prompt-audit 是流程。** 但原本「每個 skill 依角色換讀者模型」的主張不成立。

- **skill 本文的讀者是主 session。** subagent 不會載入 project skills，所以 `.claude/skills/` 的讀者就是使用者選的主 session 模型，通常是 Opus 5.5。以 Opus 5.5 為目標執行 prompt-audit，對 skill 本文而言是正確的設定。
- **多模型的差異出現在另一組表面。** 包括角色檔（`.claude/agents/`）、角色被指示去讀的文件，以及主 session 寫給 subagent 的指派文字。這些才需要依角色模型（Opus 5、Opus 4.8、Sonnet 5）的文章調整。
- **只用 prompt-audit 的問題：** 它的 pattern 表格是文章的濃縮版，會漏掉細節。這次就漏了三處：
  - A2 沒寫 confidence，也沒說明這個階段的任務是 coverage。
  - A5 把 TDD 迴圈中的測試執行誤判為過度驗證。
  - C13 把 Opus 5.5 專屬的前端建議寫成適用所有模型的規則。
- **只用文章的問題：** 文章沒有 inventory、來源追溯（provenance）、keep list、逐項 diff、行為探測等步驟，無法系統性地處理 4,900 行的 skill 表面。
- **建議：** 往後微調 skill 時，用 prompt-audit 的流程，判準則依表面的實際讀者，從對應模型的文章取用。[claude-orchestration.md](../../docs/agents/claude-orchestration.md) 已寫入「Writing for the reader」這條規則。

## 過程

依使用者指定的分工執行：主 session（Opus 5.5）先提出立場，再交由 critic 挑戰。

| 步驟 | 角色 | 實際狀況 |
| --- | --- | --- |
| 初步立場 | 主 session | 主張「以每個 skill 的角色決定讀者模型」 |
| Red team | `harness-reviewer` | 已執行並回報 22 項 findings。該角色在本 session 中途才改為固定 `claude-opus-5`，**實際使用的模型未經確認** |
| Devil's advocacy／替代方案 | `harness-challenger`（Opus 4.8） | 第一輪時新角色未被偵測；之後角色出現，已補跑並回報（見下節）。**實際使用的模型同樣未經確認** |
| 修改 | `harness-executor`（Sonnet 5） | **未執行**，原因同上。patch 的修訂由主 session 在 scratch 副本上完成 |

兩位 critic 都已執行，但實際模型都未經確認，而且稽核與立場都出自主 session，結論仍可能有偏誤。

## 主 session 對 red team findings 的裁決

| Finding | 裁決 | 處理 |
| --- | --- | --- |
| F1 讀者模型的前提不成立 | 採納 | 改寫結論；orchestration 文件加入「Writing for the reader」 |
| F2 誤讀 prompt-audit 對範例的立場 | 採納 | 撤回「articles win」這項對比 |
| F3、F4 高估文章的增量；把推論寫成事實 | 採納 | 本文不再列出這些說法 |
| F5 A1 的理由錯誤，hunk 自相矛盾 | 採納 | A1 改為只補上 `harness-reviewer` 的名稱，兩軸仍一律用 subagent |
| F6 A2／A3 不完整；upstream 門檻未被覆蓋 | 採納 | A2 加入 confidence 與 coverage；A3 明文覆蓋 upstream 的不報告門檻 |
| F7 A5 有回歸風險 | 採納 | 只拿掉「further edit 後重跑」，保留「修正失敗後重跑」 |
| F8 B2 失去授權延續 | 採納 | 改為確認後只延續已授權的工作 |
| F9 C7 與 scaffold 底色不一致 | 採納 | C7 加入點名清單，新增 C7b 將 `bg-stone-50` 改為 `bg-white` |
| F10 C13 寫成全稱規則 | 採納 | 依讀者模型分流 |
| F11 reviewer 角色檔缺少 coverage 語句 | 採納 | 已修改 `harness-reviewer.md` |
| F12 C1 把未驗證的說法寫成事實 | 採納 | 保留原本較保守的措辭 |
| F13–F22 orchestration 文件的缺口 | 採納 | 見下節 |

修訂後的 patch 共 46 項修改，涉及 27 個檔案（+70／−86），`git apply --check` 通過。

## Challenger（Opus 4.8）的挑戰與裁決

| 項目 | 裁決 | 處理 |
| --- | --- | --- |
| O1 subagent 不會載入 skills 缺少依據 | 部分採納 | 依據是角色的 `tools:` 沒有 Skill、也沒有 `skills:` 預載；orchestration 文件改寫為這個具體條件 |
| O2 skill 步驟會經 handoff 轉述給 executor | 採納 | orchestration 文件要求 handoff 依讀者撰寫（例如給 executor 時明寫 scope） |
| O3、O4 主 session 模型可切換；範本採用者的模型未知 | 採納 | skill 本文不寫模型名；主模型改變時重跑 prompt audit；採用者也照做 |
| O5 第一輪只有一位 critic | 採納 | 本輪補跑 |
| A1 探針通過才套用 | 採納 | 維持「分批套用並實跑」的建議，不整批套用 |
| A2、A3 依 stage 分流；改用委派模板 | 部分採納 | 以 handoff 依讀者撰寫處理；獨立的委派模板檔暫不新增 |
| A4、E1 5.5 的 code review 比 5 強 | 使用者已決定 | reviewer 改用 `claude-opus-5-5`、effort `high` |
| E2 目標是 5.5、基準卻用 5 的行為 | 採納 | 以 5 的行為為基準的刪改（例如 D8）應依 5.5 頁面重新確認 |
| A5 hunk 仍有回歸風險 | 採納 | 已查證 `/tdd` 沒寫要執行測試，**撤回 A5** |
| D10 `visual-check` 是否涵蓋四種尺寸 | 駁回 | delivery-contract.md:44-46 明載四種尺寸都會量測 |
| D5 可能被使用者層級同名 skill 覆蓋 | 採納 | D5 暫緩，先確認 Claude Code 實際載入的是哪一份 agent-browser |
| C13 在 skill 本文寫入模型名 | 採納 | **撤回 C13**，模型相關的前端指引只放在 orchestration 文件 |
| C7b 底色 | 保留 | 信心低，套用時確認 report 想要的美學 |
| D1、D2 與全域「skill 只產生、Claude 另外執行」規則的措辭有張力 | 交由使用者決定 | 見下方 |

撤回 A5、C13 後，patch 為 44 項修改、26 個檔案（+67／−83），`git apply --check` 通過。

**需要使用者決定：**
1. ~~reviewer 的模型~~：已決定改用 Opus 5.5、effort `high`（`effort:` frontmatter 經 Claude Code sub-agents 文件確認支援）。模型多樣性改由 challenger（Opus 4.8）提供。
2. tw-emoji skills 是否可以把 `git commit`／`gh` 執行步驟寫在 skill 裡。全域規則描述的是「skill 產生、Claude 另外執行」。

## Orchestration 設定（已寫入 repo）

- **角色檔：**
  - `.claude/agents/harness-reviewer.md` 改為固定 `claude-opus-5`，並要求回報所有 findings。
  - 新增 `harness-challenger.md`（`claude-opus-4-8`）與 `harness-executor.md`（`claude-sonnet-5`）。
  - `harness-researcher` 維持 `inherit`。
- **`docs/agents/claude-orchestration.md`：** 包含以下內容：
  - 分工表，並註明這是使用者的選擇、尚未量測。
  - 委派時機。
  - challenger 不擔任 stage 3 的第五位審查者。
  - findings 不經靜默過濾就交給使用者。
  - executor 沒有 Skill tool，需要由 parent 在指派中轉述 skill 步驟。
  - 依讀者模型撰寫文字的原則。
  - 模型不可用時的替代設定。
- **連結與一致性：**
  - `CLAUDE.md` 列出四個角色並指向 orchestration 文件。
  - `runtime.md` 與 `review.md` 移除「一律繼承模型」的說法。
  - `docs/README.md` 加入索引。

## 尚未確認

- `harness-challenger`、`harness-executor` 在新 session 中能否被發現，以及 reviewer 實際使用的模型：重開 session 後用 `/agents` 確認。
- 帳號是否能使用 `claude-opus-5`、`claude-opus-4-8`、`claude-sonnet-5`。
- 固定模型的角色要用什麼 effort：Claude Code 的 agent frontmatter 是否支援 effort，尚未查證。Opus 4.8 頁面建議智力敏感的工作至少用 `high`。
- 修訂後 patch 的實際行為：依 prompt-audit Step 7，應分批套用並實跑對應的 skill。
