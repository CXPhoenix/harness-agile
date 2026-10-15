# Claude 版 tune-skills 實測：以 Sonnet 5.5 為主模型（只產報告）

日期：2026-10-16。分支：`claude/test-tune-skills`。依 `.claude/skills/tune-skills/SKILL.md` 執行到第 4 步（取得核准）為止，patch **沒有套用**到 `.claude/skills/`，`skill-sources.json` 也沒有更新（那是第 6 步）。

## 前提

- **測試設定**：假設使用者的主模型改為 Claude Sonnet 5.5、effort `high`。目前紀錄是 `claude-opus-5-5`／`high`（`docs/agents/skill-sources.json` 的 `runtime_trees.claude_tuned_for`）。
- **執行者**：本 session（Opus 5.5）依 skill 文字操作，不是真的在 Sonnet 5.5 上跑。所以測到的是「流程是否走得通、產出是否合理」，不是 Sonnet 5.5 讀這些 skill 時的實際行為。
- **範圍**：`.claude/skills/**` 中會被模型讀取的 Markdown（69 個檔，排除 archify 程式碼、`THIRD_PARTY_NOTICES.md` 與 `upstream-security-review.md`），以及 `.claude/agents/*.md` 和 `docs/agents/claude-orchestration.md`。
- **判準**（2026-10-16 讀取）：
  - [Prompting Claude Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)：該頁說明 Sonnet 5 的 pattern 仍是合理的起點。
  - [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)。
  - `/claude-api` skill 內附的 `shared/prompt-audit.md`，以及 `shared/model-migration.md` 的 Sonnet 5.5 章節。
- **方法：只審和模型有關的差異**：
  - 2026-09-26 的 [Opus 5.5 稽核](../2026-09-26-claude-skill-prompt-audit.md)已處理和模型無關的 cruft（Group 1a／1c、Group 2 的過時事實與矛盾），這次沒有重跑。
  - 本次只針對兩件事：一是依 Opus 5／5.5 行為調過的內容（過度委派、過度驗證、前端預設風格）；二是 Sonnet 5.5 文件點名的 pattern，包括勸阻工具使用、update suppressor、要求在回覆中寫出推理、主動性與範圍。
  - 這些 pattern 都用 grep 掃過完整的 69 個檔案。
- **Group 4**（request config）：範圍內沒有 API 請求程式碼，不適用。

## 摘要

提出修改 7 項，全部在同一份 [patch](sonnet-5-5.patch) 中：High 1、Medium 6，涉及 4 個檔案，+21／−7。另有 6 項只標記、不修改。

影響最大的三項：

1. **`claude-orchestration.md` 缺少 Sonnet 5.5**（T1a，High）。tune-skills 第 3 步要求「依讀者模型的官方頁面審查，連結見 claude-orchestration.md」，但清單裡沒有 Sonnet 5.5，這次只好自己去找頁面。這同時是 tune-skills 本身的缺口，見下方 M1。
2. **implement 沒有寫明範圍**（T2）。Sonnet 5.5 頁面記載，它在任何 effort 下都傾向加上沒被要求的測試、文件和小檔案。這會撞上 hard rule 2：測試只能寫在核准過的 seam 上。
3. **前端方向的寫法**（T4、T5）。Opus 5.5 適用的「點名要避免的預設風格」對 Sonnet 系列不夠用。Sonnet 5 頁面的建議是提供具體規格，或先提出幾個方向讓使用者選。teach 和 prototype/UI 補上「先定方向」；其他三處原本就有具體規格，維持 clean。

## 提出修改的 findings

| ID | 位置 | 模式 | 過時原因 | 信心 | 動作 |
|---|---|---|---|---|---|
| T1a | docs/agents/claude-orchestration.md:57 | Group 2 會過時的具體細節 | 官方頁面清單停在 Sonnet 5；tune-skills 依這份清單找判準 | High | add：Sonnet 5.5 連結 |
| T1b | claude-orchestration.md:70-72 | keep list #11（新模型需要補充指引） | 前端方向的分流只寫到 Sonnet 5；Sonnet 5.5 頁面沿用 Sonnet 5 的 pattern | Medium | rewrite：把 Sonnet 5.5 併入「具體規格或提出方向」那一組 |
| T1c | claude-orchestration.md:67-69 與新增兩條 | keep list #11 | Sonnet 5.5 有三個 Opus 沒有的傾向：會憑訓練知識回答、在 low／medium effort 會提早停下來確認、會加上沒被要求的檔案；另外在 low effort 可能沒跑檢查就回報完成 | Medium | add：Verification 補一句，另新增「Sources over recall」與「Initiative and scope」兩條 |
| T2 | .claude/skills/implement/SKILL.md:21-22 | keep list #11 | Sonnet 5.5 頁面 Steer initiative and scope：「tends to add tests, documentation, and small supporting files」，而且在任何 effort 下都會；本專案的測試必須先經過 test plan 核准 | Medium | add：不加 tickets 與 test plan 沒有要求的功能、測試、檔案、文件或 refactor；值得加的寫進報告 |
| T3 | .claude/skills/teach/SKILL.md:30 | 1a 加壓；Sonnet 5.5 tool use in knowledge work | 「Never trust」是加壓寫法（9/26 的 C14 已標記），但用意正好符合 Sonnet 5.5 會憑訓練知識回答的傾向，所以改寫，不刪除 | Medium | rewrite：改用官方建議的寫法「check specifics … even when you feel confident」 |
| T4 | teach/SKILL.md:51 | 前端方向（Sonnet 5 Design and frontend defaults） | 只有避免清單和抽象形容詞；Sonnet 系列遇到泛泛的指示時，會換成另一套固定配色 | Medium | add：還沒有共用 stylesheet 時，先提出 2–3 個方向（底色 hex、強調色 hex、字體、一句理由）讓使用者選 |
| T5 | .claude/skills/prototype/UI.md:54 | 同上 | 三個變體沒有各自的具體方向，容易共用同一套預設外觀 | Medium | add：起草前替每個變體指定底色 hex、強調色 hex 與字體 |

**副作用檢查**（全域守則 5）：

- T2 的範圍句明文排除「test plan 要求的測試」，不會和 `/tdd` 的 red→green 迴圈衝突。
- T4 在 teach 多了一個停下來詢問的點，但只會在第一份 stylesheet 出現之前發生一次。
- 修改後的 skill 文字都不含模型名稱。模型專屬的說法只放在 `claude-orchestration.md`，符合 tune-skills 第 3 步的規定。
- 這些寫法對 Opus 5.5 讀者也成立，不會讓目前的調校退步。

## 只標記、不修改的項目

- **F1 effort 條件：提早停下來確認**。主模型如果是 Sonnet 5.5、而且在 `low`／`medium` 下跑長任務，可以考慮在 `CLAUDE.md` 加上官方的「Keep working until everything the user asked for is done…」段落。
  - 不直接修改的理由：這屬於使用者習慣（第 1 步規定習慣寫進 CLAUDE.md），而且那一段要和專案的 gate 並存。gate 是使用者核准點，正好是「can't go on without the user」的情況，要由使用者確認措辭。
- **F2 effort 條件：自行加跑審查**。在 `xhigh`／`max` 下，Sonnet 5.5 可能自己再派 reviewer subagent，疊在 `/code-review` 規定的兩個 reviewer 之上。真的發生時，可以加上官方的「don't launch reviewer sub-agents unless the user asked for a review」。
- **F3 effort 條件：驗證**。在 `low` 下改程式時，可以把官方的「run a real check that exercises the change」段落加進 `CLAUDE.md`。目前假設 `high`，所以沒有提出。
- **F4 Literal readers 那一條**沒有加入 Sonnet 5.5。Sonnet 5.5 頁面只說它會照字面遵守勸阻工具的指示，沒有寫到一般性的字面理解，證據不足（Low）。
- **F5 依 Opus 5 調過的委派限制**（9/26 的 B3、B4、C2、C3）維持不動。這些都是有條件的委派句，不是勸阻使用工具；Sonnet 5.5 在 `high` 下也沒有記載過度委派的情況。
- **F6 角色檔讀者改變**。`harness-researcher` 是 `model: inherit`，主模型換成 Sonnet 5.5 之後讀者也跟著換。它的內容本來就要求打開並引用一手來源，符合 Sonnet 5.5 的建議，因此不修改。其他三個角色固定使用自己的模型，不受影響。

## Clean（在本次差異範圍內沒有 findings）

- **前端**：
  - `evidence-report/SKILL.md:70-84` 有具體色彩規則，避免清單也已涵蓋 Sonnet 頁面提到的紫藍漸層和 Inter。
  - `improve-codebase-architecture/HTML-REPORT.md:96-97` 有 scaffold，指定白底、slate 文字，強調色限 emerald／indigo。
  - `prototype/LOGIC.md:50` 指定 system font 加一個強調色。
- **grep 結果為零的類別**：
  - 勸阻工具使用（`strictly necessary`、`minimize tool calls`）。
  - update suppressor（`hold all findings`、`don't narrate`）。
  - 要求在回覆中寫出推理（`show your reasoning`、`think step by step`、`<thinking>`）。
  - 三個 tw-emoji 中出現的「scratchpad」指的是暫存目錄，不是 prompt scaffold。
- **其餘檔案**：在本次差異範圍內沒有命中。和模型無關的部分，沿用 9/26 稽核的結論。

## tune-skills 本身的測試結果

| 步驟 | 結果 |
|---|---|
| 1 判斷是否需要調校 | 紀錄是 Opus 5.5／`high`，假設的主模型是 Sonnet 5.5／`high`，兩者不同，所以繼續。反向的情況也檢查過：主模型若是 Opus 5.5 且 effort 也相同，會在這一步停止。不過 session 內的模型無法自己得知目前的 effort，只能問使用者（見 M4） |
| 2 預算 | 計畫中只有本 session 執行 audit，第 5 步的 reviewer 不在測試範圍，所以沒有任何 subagent，也沒有需要設上限的支出。實際花費：2 次 WebFetch，0 個 subagent；token 金額未量測 |
| 3 Audit | `/claude-api prompt-audit` 可以使用，keep list 也照著傳入。缺少 Sonnet 5.5 頁面連結，改為自己去找（M1） |
| 4 核准 | 報告與 patch 已產出，`git apply --check` 通過，停在核准點，沒有套用 |
| 5／6 | 沒有執行。不過在暫時套用 patch 的狀態下跑過確定性檢查，結果見下方「驗證」，跑完已還原 |

**流程缺口**（已在 `claude/fix-tune-skills` 修正：Claude 版 M1–M5 全部修改；Codex 版只移植 M2、M3，因為 M1 已有「找不到 reference 時先研究」的步驟，M4 只比對模型，M5 的預算句本來就只在有 Codex Agent 時才適用）：

- **M1**：第 3 步假設讀者模型的頁面已列在 `claude-orchestration.md`。建議補一句：沒有列出時，從 Claude 文件找出該頁，並在第 6 步把連結補進清單。
- **M2**：第 4 步把報告固定存到 `docs/agents/skill-tuning/`。但在母範本中，AGENTS.md 規定範本研究要放在 `.tmpl.docs/`，這次因此改存 `.tmpl.docs/research/`。建議補一句：`.tmpl.docs/` 存在時，存到 `.tmpl.docs/research/`。
- **M3**：第 3 步要求「每個檔案都列為 clean 或有 findings」，卻沒有說可以只審和上次報告的差異。如果全部重審，會重做和模型無關的 findings，成本接近 9/26 那次。建議明文允許：以上次報告作為基準，只審模型相關的 pattern，並在報告中寫明。
- **M4**：第 1 步要比對 effort，但模型在 session 內看不到自己的 effort 設定，一定要問使用者。建議把「effort 一律問使用者」寫進去。
- **M5**：第 2 步在沒有 subagent 時沒有東西需要設上限。可以註明：沒有 subagent 時，說明這點後直接進入第 3 步。

## 驗證

| 檢查 | 未套用 patch（HEAD） | 暫時套用 patch |
|---|---|---|
| `python3 -B scripts/verify-project.py` | PASS（33 skills） | PASS（33 skills） |
| `python3 -B -m unittest discover -s tests` | 22 tests OK | 22 tests OK |
| `git apply --check sonnet-5-5.patch` | 通過 | — |
| grep 被改寫的句子在其他地方的引用 | 只有 Codex 樹的同名副本（不在範圍內）與 9/26 的稽核紀錄 | — |

**尚未驗證**：Sonnet 5.5 讀到修改後的 skill 會不會改變行為。依 prompt-audit 第 7 步，每項修改都只是假設；要確認，需要用 Sonnet 5.5 headless 跑 implement 與 prototype/UI，比較套用前後的差異。
