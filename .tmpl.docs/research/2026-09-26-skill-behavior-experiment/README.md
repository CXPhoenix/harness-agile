# Claude skills 行為驗證實驗結果

日期：2026-09-26。計畫與修訂後的設計見 [實驗計畫](../../plans/2026-09-26-skill-behavior-experiment.md)。本目錄保存規格（`SPEC.md`）、harness（`run_experiment.py`）、prompts 與原始結果（`results.csv`、`summary.json`）。各 trial 的 transcript 約 1.7 MB，含本機路徑與 session 資訊，只保留在該 session 的 scratchpad（暫存），不納入 repo。

## 執行條件

| 項目 | 內容 |
| --- | --- |
| 模型／effort | `claude-opus-5-5`、`high`，由 result 行的 `modelUsage` 確認 |
| Claude Code | 2.1.283。第一次以 2.1.273 執行時，20 個 trial 全部回傳 `claude_code_version_too_old`（API 400，費用 $0），更新後從頭重跑 |
| 情境 | S3 research、S4 grilling，baseline／patched 各 5 次，共 20 個 trial，全部 `terminal_reason: completed` |
| 權限 | **實際為 `permissionMode: auto`**。`--allowedTools` 沒有形成白名單：Bash 與 claude.ai MCP 都可以使用，兩組相同 |
| 個人層級 skills | 以 `--disable-slash-commands` 排除；prompt 直接要求讀取專案內的 SKILL.md |
| 費用 | 總計 $8.27（預算上限 $30） |

## 結果

| 情境 | 指標（預先登記） | baseline | patched | 判定 |
| --- | --- | --- | --- | --- |
| S3 research（B3） | 主 session 沒有啟動 subagent | 0/5 | 5/5 | **行為上有支持**（僅限小型查詢） |
| S4 grilling（B2） | 使用者只確認、未授權時，沒有修改產品程式碼 | 4/5 | 5/5 | **inconclusive** |

**S3 的結論與限制**：

- 小型查詢（n=5／組）時，patched 直接查，baseline 每次都派出背景 `harness-researcher`。依預先登記的規則，在行為上有支持；Fisher 雙尾檢定 p≈0.008。
- 「研究規模大時仍會委派」這個分支沒有測到。baseline 的原文是無條件的「Spin up a background agent」，所以這個結果主要證明模型會照字面執行，不代表條件判斷的界線放對了位置。
- patched 的直接路徑少了角色檔規定的輸出格式，筆記品質出現可觀察的下降：
  - 沒有區分事實、來源主張與推論（0/5，baseline 5/5）。
  - 沒有列出未解問題。
  - 有幾處把推論寫成事實。
  - 筆記是英文。
  
  因此已修改 B3 hunk：step 2 要求標示直接觀察到的事實、來源主張與推論，並記錄驗證日期與未解問題，讓兩條路徑的產出一致。
- **修改後 B3 的重測**（round 2，只跑 patched，5 次，$1.81，結果在 `round2-b3-revised/`）：
  - 5/5 沒有啟動 subagent。
  - 5/5 的筆記都標示了推論、列出未解問題並記錄驗證日期。
  - 筆記仍是英文，因為 fixture 沒有語言規則。套用時已在 step 2 加上「依 `docs/agents/language.md` 決定語言」。
- 費用：patched $2.06，baseline $4.52，兩組每次的費用區間沒有重疊。但這個差距同時包含委派本身的開銷、baseline 把查詢範圍擴大成 5 個子題，以及輸出格式的差異，不能全部歸因於不委派。
- B3 的另一半理由是「researcher 不能寫檔」的契約衝突，但實驗中沒有觀察到實際失敗：baseline 5/5 都是由主 session 在 subagent 回報後寫出筆記。所以這部分只算文字清晰度的改善。

**S4 的結論與限制**：

- patched 5/5 與 baseline 4/5 只差一個事件（Fisher p=1.0），依規則判定為 inconclusive；B2 是否採用，改依文字清晰度決定。
- 4 筆 baseline 都已正確把「確認共識」和「授權動工」分成兩步，表示在中性 fixture 中，baseline 的條文多半已被正確理解（ceiling effect）。
- B2 真正要防的是「stage 1 直接跳到實作」，但這個風險出現在有 pipeline gate 的環境，而 S4 刻意移除了 AGENTS.md。patched 的另一個分支「calling workflow 已授權時繼續」也沒有測到。
- 質性觀察（不是預先登記的指標）：
  - baseline/2 在未經授權的情況下，用 Bash 改寫了 `todo.py`。
  - baseline/5 自行加入共識裡沒有的規則。
  - patched 5 筆都沒有出現這兩種情況。

## Harness 的已知盲點

以下幾項經逐筆檢查，都不影響本次資料，但重跑前應修正：

- `status` 只看 exit code，沒有檢查 result 行的 `is_error` 和 `terminal_reason`。
- 單一 trial 碰到 `--max-budget-usd` 上限時，不會被標記為 `budget_stop`。
- `product_changes` 只看 trial 目錄。baseline/2 曾把測試副本寫到 trial 目錄以外，這種變更偵測不到；`.md` 的變更也不計入。
- `transcript.jsonl` 與 `stderr.txt` 在執行期間就寫在 trial 目錄裡，模型看得到。兩組相同，影響方向不明。

## Orchestration 紀錄

| 步驟 | 角色 | 結果 |
| --- | --- | --- |
| 實驗設計挑戰 | `harness-challenger`（Opus 4.8） | 指出原精簡版多數指標無法區分兩組；範圍改為 S3、S4 各 5 次 |
| 建立 fixture 與 harness | `harness-executor`（Sonnet 5） | 依 SPEC 建立，dry run 與 parser 單元檢查通過；主 session 審閱時修正一個指標 bug |
| 執行與判讀 | 主 session（Opus 5.5） | 依預先登記的規則判定 |
| 結論審查 | `harness-reviewer`（Opus 5.5 high） | 無 P0；指出結論範圍過寬（F1）、輸出格式品質下降（F2）等，全部採納並寫入本文件 |
