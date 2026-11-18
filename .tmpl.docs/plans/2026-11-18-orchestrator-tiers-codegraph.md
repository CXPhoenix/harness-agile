# 三層 orchestrator 角色與 CodeGraph 程式碼地圖

日期：2026-11-18。分支：`claude/orchestrator-tiers-codegraph`。目標版本：下一個 minor（0.6.0），migrate step 以此標記。

## 需求（使用者原話整理）

1. Orchestrator 分三層：**決策者**（認知、計畫、最終決策，沿用使用者當下的 model 與 effort）、**執行者**、**驗證者**（後設認知、確認、驗證；需要實際執行的驗證交給執行者）。執行者與驗證者要在專案開始時由 model 主動提醒使用者設定。Claude 只設定 Claude 的角色，Codex 只設定 Codex 的角色。
2. 整合 [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)，作為專案的程式碼地圖。

## 已核准的決策（2026-11-18，使用者於對話中選定）

| # | 決策 | 選項 |
|---|---|---|
| D1 | 驗證層對應 | 保留角色名稱：`harness-reviewer`＋`harness-challenger` 歸驗證層，共用一組 model／effort；`harness-researcher` 是決策者的延伸，一律 inherit。Codex 新增 `harness-executor` 與 `harness-challenger`。 |
| D2 | 出貨預設值 | 執行者與驗證者改為 inherit（Claude `model: inherit`、不寫 `effort`；Codex 不寫 `model`／`model_reasoning_effort`）。範本 repo 本身也改成 inherit。 |
| D3 | 設定方式 | 新增手動 skill `setup-roles`，兩棵樹各一份，各自只改自己 runtime 的角色檔。 |
| D4 | CodeGraph 註冊 | 範本直接附註冊：Claude `.mcp.json`，Codex `.codex/config.toml` 的 `[mcp_servers.codegraph]`。 |

## 名詞表

| 名詞（英文文件用字） | 中文 | 定義 |
|---|---|---|
| decider | 決策者 | 主 session。理解需求、規劃、委派、做最終決定、與使用者溝通、載入 skills、commit。model 與 effort 由使用者在宿主選擇，範本不設定。 |
| executor | 執行者 | `harness-executor`。套用已核准的變更，並執行 gate 或驗證者要判讀的每個指令，回報原始輸出與 exit status；決策者委派 ticket 實作時，也由它跑轉錄的 `/tdd` 循環（含 red／green）。 |
| verifier | 驗證者 | `harness-reviewer`＋`harness-challenger`。審查、唱反調、依證據確認；可做唯讀檢視（讀取、列出、搜尋檔案，`git show`／`diff`／`log`／`status`，CodeGraph 查詢），不執行檢查、建置、測試、腳本或任何會改變狀態的指令。 |
| tier setting | 層級設定 | 一個 runtime 對 executor 與 verifier 各自選定的 model 與 effort，`inherit` 是合法值。 |
| role record | 角色紀錄 | `docs/agents/template-source.json` 的 `roles.<runtime>`，提醒的停止條件。 |
| code map | 程式碼地圖 | CodeGraph 在 `.codegraph/` 建立的本機 symbol／呼叫圖索引。 |

## 角色紀錄 schema

```json
"roles": {
  "claude": {
    "configured_on": "2026-11-18",
    "executor": {"model": "inherit", "effort": "inherit"},
    "verifier": {"model": "claude-opus-5-5", "effort": "high"}
  },
  "codex": { "...": "同結構，由 Codex 的 setup-roles 寫入" }
}
```

- 每個 runtime 只寫自己的 key，其他 key 原樣保留。
- `template-source.json` 是 SEEDED 檔，migrate 以 `state.update` 合併、保留未知 key（`harness_agile/migrate.py:427`），init 會重新產生但那時尚無紀錄。
- 檔案不存在（母範本 checkout）時不寫紀錄、不提醒：範本維護不受產品 gate 約束（`AGENTS.md` Template maintenance）。

## 型別 × 邊界矩陣

| 輸入 | Claude 寫法 | Codex 寫法 | 邊界與退路 |
|---|---|---|---|
| model = inherit | `model: inherit` | 刪除 `model` 行 | 永遠合法 |
| model = 別名／完整 ID | `model: <值>` | `model = "<值>"` | Claude：完整 ID 需夠新的 Claude Code，舊版失敗時退回 `inherit`。Codex：model 依帳號而定 |
| effort = inherit | 刪除 `effort` 行 | 刪除 `model_reasoning_effort` 行 | Claude：角色與主 session 不同 model 時，session effort **不**套用，改用該 model 預設。Codex：pin `model` 卻省略 effort 時沿用 session 當下的 effort，pin 的 model 不支援就 spawn 失敗；兩者同設或同省略 |
| effort = 等級 | `effort: low…max` | `model_reasoning_effort = "<值>"` | Claude 不支援的等級會降級；Codex 不支援的等級會讓 spawn 失敗 |
| 其他覆寫來源 | `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`、`CLAUDE_CODE_EFFORT_LEVEL`（舊版另有 `CLAUDE_CODE_SUBAGENT_MODEL`）會讓角色檔失效；Agent tool 呼叫時帶的 `model`／`effort` 優先於 frontmatter | 角色省略 `model` 時，spawn 時帶的 model／effort 或 `[agents]` 的 `default_subagent_model`／`default_subagent_reasoning_effort` 會取代 session 的值 | setup-roles 要告知；`orchestration.md` Fallbacks 記錄 |

## 驗證流程（「驗證的執行就是執行者」）

gate 或驗證者要判讀的證據一律由執行者執行：stage 5 gate 的測試與 coverage、stage 7 修正後的驗證、stage 8 end-to-end，以及驗證者要求的任何指令。實作本身也是執行：決策者委派 ticket 實作時，由執行者跑轉錄的 `/tdd` 循環（含 red／green）。

1. 決策者決定要驗證什麼，或驗證者在報告中要求某個證據。
2. 決策者把確切的指令交給執行者，執行者照跑並回報原始輸出與 exit status，不自行判定通過與否以外的結論。
3. 決策者把輸出交給驗證者判斷；最終決定仍在決策者，爭議交使用者（`docs/agents/review.md`）。
4. 例外：決策者可以直接做唯讀查詢，或在委派成本高於工作本身時做瑣碎修改，並跑該修改需要的快速檢查（例如一行修改後的 `scripts/verify-project.py`、`setup-roles`／`tune-skills` 內的檢查）（沿用 `claude-orchestration.md` 既有規則，並修正 `CLAUDE.md` 的「only the executor changes the checkout」矛盾）。
5. 不變的約束：stage 3 維持四軸、無仲裁者；發現原封不動交給使用者；角色不巢狀派工；commit 由決策者透過 commit skill 進行。

## CodeGraph 整合規格

- **事實來源**（2026-11-18 研究；本機實測 1.6.2）：MIT；npm `@colbymchenry/codegraph` 最新 1.6.3；stdio MCP `codegraph serve --mcp`；預設只暴露 `codegraph_explore`；`.codegraph/` 是本機索引，不 commit；telemetry 預設開啟，`DO_NOT_TRACK=1` 同時關閉 telemetry 與每日更新檢查。
- **實測**：1.6.2 的 `serve` 不接受 `--no-telemetry`（`error: unknown option '--no-telemetry'`，exit 1），不帶這個參數時 MCP `initialize` 正常回應。所以範本**只用環境變數**關閉 telemetry，不加這個 arg。
- **註冊**：
  - `.mcp.json`：`mcpServers.codegraph = {type: "stdio", command: "codegraph", args: ["serve", "--mcp"], env: {DO_NOT_TRACK: "1", CODEGRAPH_TELEMETRY: "0"}}`。
  - `.codex/config.toml`：`[mcp_servers.codegraph]`，`command`、`args` 相同，`env = { DO_NOT_TRACK = "1", CODEGRAPH_TELEMETRY = "0" }`。
- **不使用 `codegraph install`**：它的 local 模式會改寫根目錄 `AGENTS.md`（Codex）、`.claude/CLAUDE.md`、`.claude/settings.json`，並加上 `UserPromptSubmit` hook，與本專案的檔案歸屬衝突。
- **gitignore**：根目錄 `.gitignore` 加 `/.codegraph/`；migrate 新增 step `codegraph-gitignore`（0.6.0，`ensure_line`）；`NOISE_DIRS` 加 `.codegraph`，避免非 schema-2 路徑把資料庫算進 manifest。
- **使用規則**（AGENTS.md，runtime 中立）：有 `.codegraph/` 時，先用 `codegraph_explore`（或 shell `DO_NOT_TRACK=1 codegraph explore "<問題>"`）定位 symbol、caller、影響範圍；沒有就跳過。git worktree 的 repository root 是 worktree 自己的根目錄，那裡沒有 `.codegraph/` 就跳過。編輯檔案或把它當證據引用前，直接讀該檔，索引可能落後於最近的修改。
- **子代理**：Claude 四個角色的 `tools` 加上 `mcp__codegraph__codegraph_explore`；Codex 子代理繼承父 session 的 MCP。
- **安裝**：每台機器自行安裝，建議 `npm install -g @colbymchenry/codegraph@<固定版本>`（npm 套件自帶 Node runtime，系統 Node 只用來執行 npm）；`curl | sh` 安裝器會執行遠端腳本，由使用者自行決定。安裝與建立索引都需要使用者同意。
- **未驗證**：Codex `network_access = false` 是否影響 MCP server 子行程；sandbox 內執行 shell 備援時能否寫入 `~/.codegraph`。文件要標明未驗證。

## 提醒機制

- 持久觸發點：`AGENTS.md` 新增的 Orchestration 與 Code map 段落，只有主 session（決策者）會提醒，子代理略過。
  - 角色：`docs/agents/template-source.json` 存在且缺少目前 runtime 的 key（Claude Code `roles.claude`、Codex `roles.codex`；另一個 runtime 的 key 不影響）時，每個 session 在第一則回覆開頭提醒一次，說明角色檔目前設定的 model／effort（先讀檔，不斷言 inherit），並建議 `/setup-roles`（Codex `$setup-roles`）。
  - CodeGraph：已初始化、目前 runtime 的檔案仍註冊 CodeGraph（Claude Code `.mcp.json` 的 `mcpServers.codegraph`；Codex `.codex/config.toml` 的 `[mcp_servers.codegraph]`）且沒有 `.codegraph/` 時，每個 session 在第一則回覆開頭提一次；兩者都成立時放在同一則訊息。移除註冊即表示不採用。
  - 提醒不阻擋工作。「不碰另一個 runtime 的檔案」只限角色設定：提醒與 setup-roles 只改目前 runtime 的角色檔與 key，範本維護與 skill 雙樹同步不受限。
- 入口指向：`init-template` 第 4 步（兩棵樹）、`harness_agile/cli.py` 的 `next_step`、`scripts/init-project.py` 結尾輸出、`scripts/project-readme.md`。
- `setup-roles` 是 `disable-model-invocation: true`／`allow_implicit_invocation: false`：model 只提醒，由使用者呼叫。

## 追溯矩陣

| ID | 需求 | 落點檔案 | 驗收 |
|---|---|---|---|
| R1 | 三層定義為共用規則 | `AGENTS.md` Orchestration；新 `docs/agents/orchestration.md` | 文件審查：定義、對應表、驗證流程齊備 |
| R2 | 決策者沿用使用者 model/effort | `docs/agents/orchestration.md`、`claude-orchestration.md`、`codex.md` | 文件中沒有設定主 session model 的指示 |
| R3 | 執行者／驗證者可逐層設定，預設 inherit | `.claude/agents/*.md`、`.codex/agents/*.toml` | verify：researcher 不得 pin model；其他 Codex 角色允許 `model`；四個 Claude 角色 `model: inherit` 且無 `effort` |
| R4 | Codex 角色齊備 | `.codex/agents/harness-executor.toml`、`harness-challenger.toml`（新） | verify 角色清單四個名稱、Claude 對應檔存在 |
| R5 | 專案開始時主動提醒 | `AGENTS.md`、`init-template`×2、`cli.py`、`init-project.py`、`project-readme.md` | 文件審查；`init-project.py` 輸出含 setup-roles |
| R6 | 各 runtime 只設定自己的 | `setup-roles`×2 的 scope 段 | 文件審查：Claude 版不提 `.codex/` 寫入，反之亦然 |
| R7 | 角色紀錄與停止條件 | `setup-roles`×2、`orchestration.md` | schema 一致；只寫自己的 key |
| R8 | 驗證由執行者執行 | `AGENTS.md`、`CLAUDE.md`、`orchestration.md`、`harness-executor`×2、`claude-orchestration.md`、`workflow.md`、`review.md` | 文件審查；`CLAUDE.md` 矛盾已修 |
| R9 | 新 skill 註冊 | `skill-sources.json`、`verify-project.py` REQUIRED、計數（`verify-distributions.py`、`tests/test_bootstrap.py`、`docs/guide.md`、`.tmpl.docs/adoption.md`） | `unittest` 全過 |
| R10 | CodeGraph 註冊隨範本出貨 | `.mcp.json`（新）、`.codex/config.toml`、`bundle.PATHS`、`package.json` files | `tests/test_bundle.py`、`verify-distributions` |
| R11 | 索引不進版控 | `.gitignore`、`migrate.py` STEP＋NOISE_DIRS、`verify-project.py` | 新 migrate 測試；verify 檢查有註冊時必須忽略 `/.codegraph/` |
| R12 | CodeGraph 使用規則與設定文件 | `AGENTS.md` Code map、新 `docs/agents/codegraph.md` | 文件審查；實測 MCP initialize |
| R13 | 舊敘述同步 | `runtime.md`、`codex.md`、`review.md`、`guide.md`、`tune-skills`×2、`.tmpl.docs/GLOSSARY.md`、README×2 | 全文搜尋不再出現「Codex roles inherit the session model」等過時敘述 |
| R14 | Codex 角色檔 `sandbox_mode` 無效 | `.codex/agents/harness-reviewer.toml`、`harness-researcher.toml`、`runtime.md` | 移除該行；文件改寫為「唯讀靠指示約束」 |

## 副作用檢查（加保證前）

- D2 改成 inherit 後，原本 reviewer 的 `effort: high` 消失：stage 3 審查深度改由使用者設定的驗證層決定。`claude-orchestration.md` 原有「reviewer 為何用 Opus 5.5」的理由改寫成 setup-roles 可參考的建議，不再是規範。
- 新增的 verify 檢查都只針對範本自己的不變量，不新增「角色尚未設定」錯誤：verify 在 create 與 migrate 後都會執行，錯誤會讓每個新專案建立失敗。
- 採用者修改過的角色檔，日後範本更新時會產生 `.harness-new` sidecar；文件要求合併時保留自己的 model／effort 行。
- `.mcp.json` 已存在的採用者，migrate 時會得到 sidecar；`docs/agents/codegraph.md` 要說明如何合併。

## 發版時

- F1 不在本分支處理：0.6.0 的 release commit 透過 `/tw-emoji-release-note` 一起調升 `pyproject.toml`、`package.json`、`harness_agile/__init__.py` 的版號，並新增 0.5.0 → 0.6.0 的 migrate round-trip 測試，斷言 `.gitignore` 加入 `/.codegraph/` 且 verify 通過。

## 審查與修正

實作後跑了 adversarial review：5 個面向，共 95 項 findings，確認 77 項，0 個 P0、13 個 P1。決策者的處理決定：

- D-A：gate 或驗證者要判讀的證據一律由執行者執行（stage 5 gate 測試、stage 7 修正驗證、stage 8 end-to-end、驗證者要求的指令）；委派實作時執行者跑轉錄的 `/tdd` 循環；決策者仍可做瑣碎修改並跑該修改需要的快速檢查。
- D-B：驗證者不執行檢查、建置、測試、腳本或改變狀態的指令，但可做唯讀檢視（讀檔、搜尋、`git show`／`diff`／`log`／`status`、CodeGraph 查詢）。
- D-C：提醒只在主 session（決策者）觸發，子代理略過。
- D-D：角色提醒的觸發條件是 `template-source.json` 存在且缺少目前 runtime 的 key；提醒內容依角色檔實際讀到的 model／effort，不斷言 inherit。
- D-E：「不碰另一個 runtime 的檔案」只限角色設定，範本維護與 skill 雙樹同步不受影響。
- D-F：CodeGraph 提醒條件是已初始化、目前 runtime 仍註冊 CodeGraph 且沒有 `.codegraph/`；每個 session 在第一則回覆開頭提一次，移除註冊即表示不採用。
- D-G：shell 備援改用 `DO_NOT_TRACK=1 codegraph explore`；編輯或引用前直接讀檔；worktree 沒有自己的 `.codegraph/` 就跳過 CodeGraph。
- D-H：所有入口一致的順序：先 `/setup-roles`（Codex `$setup-roles`），再視需要設定 CodeGraph，最後 `/grill-with-docs` 填 Project Charter。
- D-I：附上根目錄 `codegraph.json`，把 vendored skill 樹排除在索引外；格式須先依 upstream README 確認並以 `codegraph init` 實測，無法確認就只寫文件、不出貨。
- 不修正：F1（版號屬於 release commit，見「發版時」）、CG-07（verify 不檢查 telemetry 環境變數，改以文件說明）、L3。
