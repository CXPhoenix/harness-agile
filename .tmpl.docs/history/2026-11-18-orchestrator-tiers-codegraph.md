# 三層 orchestrator 角色與 CodeGraph 程式碼地圖

日期：2026-11-18～19（Asia/Taipei）。分支：`claude/orchestrator-tiers-codegraph`，從 `main`（`b436f80`）切出；尚未發布，目標版本 0.6.0。計畫與決策：[plans/2026-11-18-orchestrator-tiers-codegraph.md](../plans/2026-11-18-orchestrator-tiers-codegraph.md)。

## 交付內容

- **三層分工**：決策者（主 session，沿用使用者選的 model／effort）、執行者（`harness-executor`）、驗證者（`harness-reviewer`＋`harness-challenger`）；`harness-researcher` 是決策者的延伸，一律繼承。共用定義在 `AGENTS.md` 的 Orchestration 段與 `docs/agents/orchestration.md`。
- **角色預設改為 inherit**：Claude 四個角色 `model: inherit`、不寫 `effort`；Codex 角色不寫 `model`／`model_reasoning_effort`。Codex 新增 `harness-executor.toml` 與 `harness-challenger.toml`，並移除角色檔中不會生效的 `sandbox_mode`。
- **`setup-roles`**：兩棵 skill 樹各一份，手動觸發，只改自己 runtime 的三個角色檔，並把選擇記在 `docs/agents/template-source.json` 的 `roles.claude`／`roles.codex`。在母範本 checkout 中會先停下，不改出貨預設值。
- **提醒機制**：只在主 session 觸發。已初始化的專案缺少自己 runtime 的紀錄時，提醒目前的角色設定與 `setup-roles`；runtime 仍註冊 CodeGraph 但沒有 `.codegraph/` 時，提醒 CodeGraph 設定。init-template、CLI、`init-project.py`、`project-readme.md`、INSTALL.md、guide、adoption 都採用同一個順序：setup-roles、選用的 CodeGraph、grill-with-docs。
- **CodeGraph**：隨附 `.mcp.json`（Claude Code）與 `.codex/config.toml` 的 `[mcp_servers.codegraph]`（Codex），以環境變數 `DO_NOT_TRACK=1`、`CODEGRAPH_TELEMETRY=0` 關閉 telemetry 與每日更新檢查；隨附 `codegraph.json`，把兩棵 skill 樹排除在索引外；`.gitignore` 加 `/.codegraph/`，migrate 新增 `codegraph-gitignore` step（0.6.0）；說明文件為 `docs/agents/codegraph.md`。
- **verify 與測試**：`setup-roles` 列為必要 skill；verify 允許 executor／verifier pin model，但 researcher 必須繼承；註冊 CodeGraph 時必須忽略 `/.codegraph/`；新增範本專用測試，確認出貨角色皆為 inherit，並確認兩份註冊設定一致。

## 驗證

| 證據 | 範圍 |
|---|---|
| `python3 scripts/verify-project.py` PASS（35 skills） | 母範本 checkout 的靜態結構 |
| `python3 -m unittest discover -s tests` 74 個測試 OK | 初始化、建立器、migrate、verify、bundle |
| codegraph 1.6.2 實測：`serve --mcp` 的 MCP `initialize` 正常；加上 `--no-telemetry` 時 `unknown option`、exit 1 | 決定只用環境變數關閉 telemetry |
| 審查者在 scratch 副本實測 `codegraph init`、`codegraph_explore`、`.gitignore` 生效；`codegraph.json` 讓索引檔數從 383 降到 32 | CodeGraph 在本機的行為 |
| 五個角度的對抗式審查：95 個發現，經逐一反駁後 77 個成立（0 P0、13 P1），已依計畫「審查與修正」段處理 | 文件、skill、腳本 |

## 未驗證

- 真實 Claude Code／Codex 宿主是否載入新角色與 `setup-roles`，以及 `/agents` 是否顯示新設定。
- Codex `network_access = false` 對 MCP server 子行程的影響；Windows 上 npm shim（`codegraph.cmd`）的啟動方式。
- `scripts/verify-distributions.py` 需要先建置 wheel 與 npm 套件，這次沒有執行。
- 0.5.0 → 0.6.0 的 migrate round-trip 測試留給發版 commit（見計畫「發版時」）。

後續（2026-11-22）：
- 前兩項**部分完成**，只驗證了 Codex CLI 的 `exec` 這個 surface（[宿主驗證紀錄](../research/2026-11-22-host-verification-roles-codegraph.md)）。
  - 通過：Codex 載入專案角色、`codegraph_explore` 可用、建索引後不再提 CodeGraph。
  - 子代理略過提醒通過，但鑑別力低。
  - 主 session 在第一則回覆開頭提醒，嚴格只有 2／4 次。
  - `network_access = false` 下 MCP 照常運作，但這個值本來就是 workspace-write 的預設值，無法證明是專案那一行生效。
  - `$setup-roles` 在 `codex exec` 下寫不進 `.codex/agents/`，因為 `.codex/` 是 Codex 的受保護路徑。[#24](https://github.com/CXPhoenix/harness-agile/pull/24) 改善了文件與 skill 的處理方式，受保護路徑本身不變。
  - 仍未驗證：
    - Claude Code 的 `/agents`、`.mcp.json` 核准與提醒。
    - Codex 互動 session 的核准流程。
    - 設定後的下一個 session 不再提醒。
    - Windows shim。
- 第三項：PR #23 的 head 與 merge commit `886e9bb` 的三平台 CI 都執行過 verify-distributions，並且通過。
- 第四項：0.6.0 的 release 分支新增了 `test_codegraph_gitignore_step_round_trips`，涵蓋 0.5.0 的 CodeGraph 狀態升到 0.6.0 再降回；結果見 0.6.0 的發版紀錄。
