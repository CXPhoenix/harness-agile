# 三層角色、setup-roles 與 CodeGraph：真實宿主驗證

日期：2026-11-22（Asia/Taipei）。對象為 PR #23 合併後的 `main` = `886e9bb`，涵蓋[交付紀錄](../history/2026-11-18-orchestrator-tiers-codegraph.md)「未驗證」清單的前兩項（[計畫](../plans/2026-11-18-orchestrator-tiers-codegraph.md)見 D-C、D-D、D-F）。本次只驗證並保存證據，沒有修改範本內容、commit 或發版。初稿經 `harness-challenger` 對照原始證據挑戰後修訂；修訂處以挑戰項目代號（C-a…）標注。

**整體為部分完成。**

- 已有 Codex 原生證據的項目：
  - 角色載入。
  - CodeGraph MCP 可用。
  - `network_access = false` 不影響 MCP。
- 有發生但不穩定的項目：
  - 主 session 的提醒，嚴格算只有 2／4 次在第一則回覆開頭出現。
  - 子代理略過提醒的測試鑑別力偏低。
- 卡住的項目：
  - 兩個 runtime 的 `setup-roles` 實際寫入，以及設定後不再提醒。
  - Claude Code 的 headless 驗證，因為登入失敗。

## 測試環境

| 項目 | 值 |
| --- | --- |
| 暫存專案 | `python3 -m harness_agile init --source <checkout> --name 宿主驗證 --one-liner '驗證 0.6.0 角色與 CodeGraph 的暫存專案' --no-input --git <scratchpad>/hv-project`；`template_version` 0.5.0、`source.commit` `886e9bb`、`dirty: false`；init 後 `verify-project.py` PASS（34 skills）。one-liner 的「0.6.0」是測試輸入，A2、C3 的回覆照抄成專案描述 |
| Codex | `codex-cli 0.161.0`；所有 turn context 為 `gpt-6.1-sol`、effort `high`、approval `never`（`exec` 一律 `never`，即使專案設定 `on-request` 已載入） |
| Claude Code | `2.1.322`（CLI）；本次維護 session 為 Claude 桌面 app 的 Code 分頁，2026-11-22T04:51Z 開始 |
| CodeGraph | `1.6.2`；以 `DO_NOT_TRACK=1 CODEGRAPH_TELEMETRY=0 codegraph init -y .` 只在暫存專案建索引（依 `codegraph.json` 排除 skill 樹後索引 1 個檔案、13 nodes）；init 後 AGENTS.md、`.mcp.json`、`.codex/config.toml` 與 baseline 相同，沒有產生 `.claude/CLAUDE.md` 或 `.claude/settings.json` |

證據取自 `codex exec --json` 事件流、`~/.codex/sessions/2026/11/22/` 的原生 rollout（以 thread id 對應），以及本 session 的工具結果。原始檔留在本機暫存目錄，含帳號 id 與使用者全域指令，不納入 repo；下表只摘錄判讀所需欄位。

| Run | 目錄 | 信任 | Sandbox | 指令重點 |
| --- | --- | --- | --- | --- |
| A1 | 暫存專案 | — | — | `claude -p '你好，請用三句話介紹這個專案目前的狀態。'` |
| A2 | 暫存專案（無索引） | 否 | read-only | `codex exec -c 'projects."<path>".trust_level="trusted"' …` 同上問候 |
| B1 | 範本 checkout | 是 | workspace-write | 唯讀任務：呼叫 `codegraph_explore`（`projectPath` 指向暫存專案）、spawn `harness-researcher`、回報 sandbox |
| C1 | 暫存專案（有索引） | 否 | read-only | 「你好。請先回覆我，再啟動一個子代理……」 |
| C2 | 暫存專案 | 本次啟動後變成是（F3） | workspace-write | `codex exec -s workspace-write` + `$setup-roles` 並附上選擇；沒有 `-c` |
| C3 | 暫存專案 | 是 | workspace-write | 同 A2 問候，沒有 `-s` |
| D1 | 暫存專案 | 是 | workspace-write | 「這是唯讀測試……用 harness-researcher 啟動子代理……原樣貼出」 |

## 結果

| # | 檢查 | Surface | 結果 | 證據 |
| --- | --- | --- | --- | --- |
| H1 | 主 session 在第一則回覆開頭給角色提醒，內容依角色檔實際值 | Codex CLI `exec`，暫存專案 | **2／4 嚴格符合**（C-a） | A2、C3 第一則 agent message 是提醒，接著才回答；C1 的提醒在第三則訊息；D1 沒有提醒（F5）。A2 的提醒只在中間訊息，`-o` 寫出的最後訊息沒有：只讀最後訊息的自動化看不到提醒。A2、C3 先猜錯角色檔名（`.codex/agents/executor.toml`、`verifier.toml`）才改讀 `harness-*.toml`；C1 沒讀 `harness-challenger.toml`（C-g）。讀到的 `template-source.json` 沒有 `roles` 鍵（C-d） |
| H2 | 沒有 `.codegraph/` 時給 CodeGraph 提醒，建索引後不再提 | 同上 | **pass** | A2（無索引）：「CodeGraph 已註冊但尚無索引，安裝與建立索引由你決定」；C1、C3（有索引）只有角色提醒。A2 未信任，codegraph 其實沒有載入，提醒仍說「已註冊」，因為條件看的是檔案內容，不是實際生效的設定（C-h） |
| H3 | Codex 載入專案角色 | Codex CLI `exec`，已信任的 checkout | **pass** | B1、D1 子 rollout `session_meta.agent_role = "harness-researcher"`；developer message 與 `.codex/agents/harness-researcher.toml` 的 `developer_instructions` 逐字相同 |
| H4 | 子代理不給提醒 | Codex CLI `exec`，暫存專案（沒有 `roles.codex`） | **pass，鑑別力低** | D1 的 `harness-researcher` 只回「你好，我是 Codex 研究助理，負責查核第一手來源…」。但 D1 主 session 在同一個 prompt 下也沒提醒，C1 的子代理輸出又被限制成一句話，所以分不出是遵守略過規則，還是這類 prompt 本來就不會引發提醒（C-H4） |
| H5 | `codegraph_explore` 可用 | Codex CLI `exec`，已信任的 checkout | **pass** | B1 `mcp_tool_call` server `codegraph`、status `completed`，回傳 `verify`、`main` 等 7 個 symbol |
| H6 | 同上 | Claude 桌面 app 本 session | **可用，註冊來源未確認**（C-H6） | 本 session 以同一 `projectPath` 呼叫，得到相同 7 個 symbol。`~/.claude.json` 與 `~/.claude` 設定都沒有 codegraph；server 自述「started somewhere with no `.codegraph/`」，與範本 checkout 沒有索引一致。最可能來自專案 `.mcp.json`，但沒有直接證據 |
| H7 | `network_access = false` 是否擋住 MCP | Codex CLI `exec` | **不擋** | 父、子 turn context 的 `sandbox_policy` 都是 `workspace-write`、`network_access: false`，H5 的 stdio server 照常回應；同一批 session 的 stderr 也顯示，使用者另外設定的三個遠端 HTTP MCP 有連線並拿到 401 回應。限制：`network_access: false` 本來就是 workspace-write 的預設值，無法證明是專案那一行生效（C-f） |
| H8 | `setup-roles` 不會被模型自動觸發 | Claude 桌面 app 本 session | **pass（旁證）**；手動觸發未測 | 本 session 可見的專案 skill 正好是 19 個沒有 `disable-model-invocation` 的，16 個設為 `true` 的（含 `setup-roles`）都不在其中。session 開始時間晚於 `setup-roles` 的新增 commit（`b56b564`，2026-11-19），所以不是舊清單造成的 |
| H9 | `$setup-roles` 寫入角色檔與 `roles.codex` | Codex CLI `exec -s workspace-write` | **fail：Codex 預設的受保護路徑** | 見 F1。每個在 `exec` 的 workspace-write 下執行的採用者都會遇到，不是這台機器的特例（C-H9） |
| H10 | 設定後的下一個 session 不再提醒 | — | **未驗證** | 依賴 H9 |
| H11 | Claude Code 角色、`/agents`、`.mcp.json` 核准、提醒 | Claude Code CLI `-p` | **blocked** | 巢狀 `claude -p` 回傳 `Failed to authenticate: OAuth session expired and could not be refreshed`；憑證屬於使用者，沒有處理 |

## 發現

**F1：Codex 在 workspace-write 下，專案的 `.git`、`.agents`、`.codex` 是唯讀。** C2 rollout 的 `permission_profile`（`type: managed`）把 `hv-project` 本身列為 `write`，把 `hv-project/.git`、`.agents`、`.codex`、`.aws` 列為 `read`。B1 在範本 checkout 也一樣。C2 的 `apply_patch` 目標全在 `.codex/agents/` 內，被拒絕的訊息是 `patch rejected: writing outside of the project; rejected by user approval settings`。字面上雖然說「寫到專案外」，直接證據是上面的 permission profile（C-F1）。

skill 的處理正確：角色檔沒寫成，就沒寫 `roles.codex`，並如實回報。

後續實測（P1，已信任的暫存專案，workspace-write、approval `never`）：
- `apply_patch` 新增 `docs/_probe.md` 成功。
- `apply_patch` 新增 `.agents/_probe.md`、`.codex/_probe.md` 都被拒，錯誤訊息同上。
- shell `touch` 寫入 `.agents/`、`.codex/`、`.git/` 都回傳 `Operation not permitted`（rollout 有原文）。
- 測試前後 `~/.codex/config.toml` 相同；探測檔已刪除。

官方出處（`harness-researcher` 查證，2026-11-22）：
- [Agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security.md) 列出 workspace-write 的受保護路徑：`.git`，以及以目錄形式存在的 `.agents`、`.codex`、`.aws`，保護是遞迴的。
- openai/codex 原始碼 `codex-rs/protocol/src/permissions.rs` 的 `PROTECTED_METADATA_PATH_NAMES` 就是這四個名稱，0.164 到 0.171 都有。
- `apply_patch` 由 `core/src/safety.rs::assess_patch_safety` 判斷：approval `never` 時回 `Reject`，`on-request` 時回 `AskUser`。拒絕訊息只有 read-only 與 outside-project 兩種，所以受保護路徑也顯示成 outside-project。
- shell 由 OS sandbox（macOS 的 seatbelt）擋下。
- `exec/src/lib.rs` 的 headless 預設是 approval `Never`。
- 所以 `managed` 是 Codex 預設 profile 的類型，不是這台機器另有管理政策。
- 互動 session 的 `on-request` 會跳出核准請求，這點有原始碼支持，但還沒實測。

**已處理（本次）：**
- `docs/agents/runtime.md` 的 Codex 段新增一段，說明受保護路徑，以及受影響的工作：commit、`$setup-roles`、`$tune-skills` 與 skill 雙樹維護。
- Codex 樹 `setup-roles` 第 4 步改為：寫入被拒時停下、不寫 `roles.codex`、列出每個檔案預定的內容，請使用者在互動 session 重跑。
- Claude 樹的 `setup-roles` 不受影響，沒有修改。
- 修改後的實測（C4）：把新版 skill 與 runtime.md 複製到暫存專案，用 `codex exec`（已信任、workspace-write、approval `never`）跑 `$setup-roles` 並附上選擇。結果如下：
  - Codex 引用第 4 步停下。
  - 列出三個檔案的預定設定（executor `model_reasoning_effort = "medium"`，reviewer、challenger `"high"`）。
  - 請使用者在互動 session 重跑。
  - 角色檔、`template-source.json`（沒有 `roles` 鍵）與 `~/.codex/config.toml` 都沒有變動。
  - 它看到 approval 是 `never` 就直接停下，沒有先嘗試寫入。

**F2：Codex 專案設定只在持久信任後才載入。**
- 未信任的暫存專案，`codex mcp list` 看不到 codegraph，加上 `-c 'projects."<path>".trust_level="trusted"'` 也一樣。
- 已信任的範本 checkout 會列出 codegraph，env 已遮罩。
- 未信任時 AGENTS.md 仍會載入，所以提醒照常出現。但 C1 說「目前的子代理工具無法選取自訂 agent role」，這是模型看了工具 schema 後的自述，它沒有實際以 `agent_type` 呼叫 spawn 並得到錯誤；D1（已信任）成功使用是旁證（C-F2）。
- 以上與 `.codex/config.toml` 開頭的註解、runtime.md 的說法一致，不是缺陷。

**F3：這次執行之後，`~/.codex/config.toml` 多了暫存專案的持久信任。**
- 檔案修改時間 12:59:31 與 C2 rollout 的開始時間（04:59:31Z）在同一秒，新增的是 `[projects."<scratchpad>/hv-project"] trust_level = "trusted"`。
- C2 的指令只有 `-s workspace-write`，沒有 `-c`；先前的 `codex mcp list -c …` 是在建索引之前跑的，比 C2 早。
- 之後 C3 沒帶 `-s` 也拿到 workspace-write，跟專案 `sandbox_mode` 已載入一致。
- 證據只有時間相關。觸發條件是 `-s workspace-write`、任何非 read-only 的 sandbox 還是其他旗標，沒有分辨（C-F3）。
- 使用者的 config 裡還有上百筆暫存目錄的 trusted 記錄，看起來這個副作用反覆出現過。
- 查證原始碼的結果：0.169.0 以上的 `codex exec` 只有明確加 `--trust`、而且專案還沒有 trust 決定時，才會寫入 trust；0.164 到 0.168 的 `exec/src/lib.rs` 沒有寫入 trust 的程式碼。本機是 0.161.0，不在查證的範圍內，所以寫入來源仍然不明。
- P1 是在已信任的專案跑 `codex exec`，前後 config 沒有變化。
- 要定案，需要先備份 config，在新目錄分別跑 `-s read-only`、`-s workspace-write`、`--full-auto` 後比對差異。這會改到使用者的全域設定，要經使用者同意。
- 該筆是否移除也由使用者決定。

**F4：`harness-researcher` 在 B1 自稱「verifier」，成因未定。** B1 父代理給子代理的 `task_name` 是 `host_role_verification`，任務是「用一句話說出你的角色名稱」；同一個角色在 D1（`task_name` 不同）自稱「Codex 研究助理，負責查核第一手來源」。任務名稱可能直接引導出這個回答，所以證據不足以判定角色文字缺少 tier 說明（C-b）。不影響功能，屬於 P2 觀察。

**F5：主 session 的提醒不穩定，而且可能有混淆因素。**
- D1 的 prompt 要求範圍很窄的精確輸出，主 session 沒讀任何檔案，也沒提醒。
- 模型優先照使用者的精確要求輸出，本身是合理的，不一定算缺陷。
- 有提醒的 A2、C1、C3 都先讀了使用者全域的 Codex skill `using-superpowers`。那份 skill 要求「回應前先檢查」，等於多了一段開場儀式；D1 連它也沒讀。所以 2–3／4 的提醒率可能被這台機器的全域 skill 拉高，沒裝的採用者可能更低（C-F5）。
- 樣本只有 4 次、單一模型。
- 可選的做法：
  - 維持現狀：提醒本來就不擋工作。
  - 改成更強的必做句：依使用者的全域守則「加保證類修法要做副作用檢查」，要先檢查會不會跟 `exec` 腳本化與精確輸出的要求衝突。
  - 由程式穩定提示：`verify-project.py` 在缺少 `roles.<runtime>` 時印出非阻擋提示，或 Claude 端用 SessionStart hook。
  - 在 AGENTS.md 的提醒段直接寫出角色檔路徑：可順便修正 C-g 的檔名誤猜。
- 決定前應該先在停用 `using-superpowers` 的條件下，對三種 prompt 各重測幾次。

**F6：其他環境因素。**
- `using-superpowers` 在 A2、C1、C2、C3 都被讀取，D1 沒有。它不只是雜訊，也是 F5 的混淆變數（C-c）。
- `~/.codex/config.toml` 開了 `use_memories`，C2 搜尋過 `~/.codex/memories/MEMORY.md`。裡面有先前範本維護的記憶，沒有這次的記憶（C-i）。
- B1 stderr 的 `collab spawn failed: no thread with id …` 出現在子代理已經回覆之後，整個 rollout 只有一次 `spawn_agent`，原因沒有追查（C-j）。

## 更正

| 先前說法 | 更正 | 依據 |
| --- | --- | --- |
| 交付紀錄：「`scripts/verify-distributions.py` 這次沒有執行」 | 本機沒跑，但 CI 在 ubuntu、macOS、Windows 三平台都建置 wheel 與 npm tarball 並執行該腳本：PR #23 的 head（run 44347767784 等）與 merge commit `886e9bb` 的 push（run 44349688065）都是 success | `.github/workflows/verify.yml:16`、`:50-52`；`gh pr checks 23`；`gh run list --commit 886e9bb…` |

## 留給使用者在互動 session 確認

1. Claude Code：在暫存專案開新 session，確認以下各項：
   - `.mcp.json` 的核准提示。
   - `/agents` 列出四個 `harness-*` 角色。
   - 第一則回覆開頭有兩個提醒。
   - `/setup-roles` 出現在 slash 選單。
   - `codegraph_explore` 可用。
2. Claude Code：執行 `/setup-roles`，確認以下各項，再開新 session 確認不再提醒：
   - `.claude/agents/` 的三個角色檔有寫入。
   - `roles.claude` 有寫入。
   - `verify-project.py` PASS。
3. Codex：在暫存專案開互動 session，執行 `$setup-roles`，確認以下各項，再開新 thread 確認不再提醒：
   - 寫入 `.codex/agents/` 時是否跳出提權請求（F1）。
   - 核准後 `roles.codex` 有寫入。
   - `verify-project.py` PASS。
4. 仍未驗證：Windows 上 npm shim（`codegraph.cmd`）的啟動方式；F1 對 `.agents`、`.git` 的實際寫入行為；F3 的觸發條件。
