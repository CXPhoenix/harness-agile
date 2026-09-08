# Claude Code 與 Codex 共用範本研究

查證日期：2026-09-08。範圍：專案指示、skills、執行權限、subagents 與交接。來源限 OpenAI 與 Anthropic 官方文件；本機另外確認 `codex-cli 0.153.4` 的 CLI 選項。本文記錄設定依據與建議，實際整合與驗證結果以專案設定及驗證輸出為準。

**建議採用一份共用規範、一份 skills 正本，加上各工具原生設定。** 共用工作流程不指定跨供應商模型名稱；各宿主保留自己的 review、工具與 worktree 能力。以下「建議」是依文件作出的專案設計判斷，並非模型能力評測。

## 1. 入口與 skills 差異

| 項目 | Claude Code | Codex | 本專案建議 |
| --- | --- | --- | --- |
| 專案指示 | `CLAUDE.md`，支援 `@path` import | `AGENTS.md`，每層優先找 `AGENTS.override.md` | `AGENTS.md` 放共用正文；`CLAUDE.md` 匯入它 |
| 專案 skills | `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` | 正本放 `.agents/skills/`，Claude 每個 skill 使用相對 symlink |
| 手動呼叫 | `/skill-name` | CLI／IDE 的 `$skill-name` 或 `/skills` | 文件首次出現時說明兩種語法 |
| 禁止自動觸發 | `SKILL.md` 的 `disable-model-invocation: true` | `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false` | 需要手動觸發的 skill 同時設定兩者 |
| Custom agent | `.claude/agents/*.md` 與 YAML frontmatter | `.codex/agents/*.toml` | 角色目標一致，設定格式各自維護 |

Claude 官方直接示範 `CLAUDE.md` 以 `@AGENTS.md` 匯入共用規範；Codex 則沿專案根目錄至目前目錄收集指示，每個目錄最多選一份，預設總量上限 32 KiB。Codex 官方沒有在這份指示文件中定義 Claude 的 `@path` 展開機制，因此共用文件應用明確的「先閱讀某路徑」指示或一般 Markdown 連結。[Claude 記憶與匯入](https://code.claude.com/docs/en/memory)、[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

兩者均明確支援 skill 資料夾 symlink。Codex 同名 skills 不會合併，可能同時出現在選擇器；因此專案正本要自足，不能依賴某位開發者家目錄的絕對連結。[Claude skills](https://code.claude.com/docs/en/skills)、[Codex skills](https://learn.chatgpt.com/docs/build-skills)

推薦目錄結構：

```text
AGENTS.md
CLAUDE.md                         # @AGENTS.md，再接 Claude 專用指示
.agents/skills/<name>/SKILL.md     # 隨 Git 攜帶的正本
.agents/skills/<name>/agents/openai.yaml
.claude/skills/<name>              # -> ../../.agents/skills/<name>
.claude/agents/reviewer.md
.codex/config.toml
.codex/agents/reviewer.toml
```

兩種手動觸發設定的最小範例：

```yaml
# SKILL.md frontmatter
name: init-template
description: Initialize a newly copied project template when explicitly requested.
disable-model-invocation: true
```

```yaml
# agents/openai.yaml
policy:
  allow_implicit_invocation: false
```

這些欄位控制 skill 的觸發方式。Claude 的 `allowed-tools`、`context: fork`、`$ARGUMENTS` 與動態 shell 注入是宿主擴充，不能假設 Codex 會照樣執行；可攜的核心指示應直接描述輸入、步驟、成果及委派需求。[Claude skills](https://code.claude.com/docs/en/skills)、[Codex skills](https://learn.chatgpt.com/docs/build-skills)

## 2. 專案設定與權限

Codex 支援 `.codex/config.toml` 專案覆寫，但只載入受信任專案的 `.codex/` 設定層。CLI 覆寫優先於專案設定，管理員政策也可能限制可用值；把設定放進 repo 不會自行取得專案信任。[Codex 設定基礎](https://learn.chatgpt.com/docs/config-file/config-basic)

以下欄位已對照官方 schema。範本可使用，無需綁定任何帳號或模型：

```toml
# .codex/config.toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"
web_search = "live"

[agents]
enabled = true
max_concurrent_threads_per_session = 4

[sandbox_workspace_write]
network_access = false
```

`max_concurrent_threads_per_session` 限制同時開啟的子 agent，不含主 agent。`network_access` 控制 sandbox 裡 shell 的對外網路；`web_search` 是另外的工具設定。此例讓研究可用即時搜尋，shell 網路需求依目前核准機制處理。[Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)、[Codex 設定參考](https://learn.chatgpt.com/docs/config-file/config-reference)、[Codex 設定基礎](https://learn.chatgpt.com/docs/config-file/config-basic)

專案信任屬開發者或管理者的本機決定。官方的 `projects.<path>.trust_level` 使用專案路徑；不應把某位開發者的絕對路徑、帳號、憑證或全機信任設定放進可攜範本。[Codex 設定參考](https://learn.chatgpt.com/docs/config-file/config-reference)

Claude Code 的工具權限放在 `settings.json`；`CLAUDE.md` 是工作指引，無法取代實際權限限制。因此兩個工具的設定應分開管理，不應將 Claude 的 `allowed-tools` 當作 Codex sandbox 限制。[Claude 設定位置](https://code.claude.com/docs/en/claude-directory)、[Claude 設定診斷](https://code.claude.com/docs/en/debug-your-config)

## 3. 各自使用原生 subagent 能力

Claude 可以在 `.claude/agents/*.md` 指定工具、模型與獨立工作目錄；`model: opus` 是 Claude 的模型別名，`model: inherit` 繼承主對話模型。Codex 使用獨立 TOML，未覆寫模型或 reasoning effort 時會依 spawn 設定、`[agents]` 預設與 parent 解析。共用規範應指定「獨立 reviewer 與 review 面向」，由各宿主設定選擇模型。[Claude subagents](https://code.claude.com/docs/en/sub-agents)、[Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

Claude reviewer 定義示例：

```markdown
---
name: reviewer
description: Review a bounded change for correctness and security risks.
tools: Read, Glob, Grep
model: opus
---
Read AGENTS.md and docs/agents/review.md before reviewing.
Return actionable findings with file references. Do not edit files.
```

Codex reviewer 定義示例：

```toml
name = "reviewer"
description = "Review a bounded change for correctness and security risks."
sandbox_mode = "read-only"
developer_instructions = """
Read AGENTS.md and docs/agents/review.md before reviewing.
Return actionable findings with file references. Do not edit files.
"""
```

這是工作角色的示例，不代表已啟動或驗證這兩個 agent。Codex 的 `name`、`description`、`developer_instructions` 是目前獨立 agent 檔案的必填欄位；省略 `model` 可保留執行環境的選擇。[Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

兩者的 readonly 預設仍須搭配宿主實際權限檢查。Codex 會將 parent 當次的 runtime 權限覆寫套用至 child；不能僅憑 agent TOML 宣稱所有宿主模式都強制 readonly。[Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

建議分工依實際工具與成果決定：Claude 可使用原生指定工具的 subagent、Opus 別名與 skill fork；Codex 可使用繼承當前模型的角色、終端機驗證及原生 review。兩邊都能研究、實作和審查，沒有足夠依據將某一工作永久分配給某一品牌。跨工具交叉 review 可以作為取得第二份獨立意見的方法，不能保證消除共同盲點。

## 4. Worktree、交接與攜帶限制

Claude subagent 可用 `isolation: worktree`，目前官方說明預設從 default branch 建立，未必是 parent 的 `HEAD`。Codex 桌面介面可選起始分支建立 worktree，預設 detached HEAD，並提供 Local／Worktree 間的 Handoff。review 未 commit 的變更時，須明確指定 checkout 與基準，避免 reviewer 看錯版本。[Claude subagents](https://code.claude.com/docs/en/sub-agents)、[Codex worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)

**本專案的跨工具交接建議**：以 Git 分支、ticket 與 Markdown 為媒介，記錄基準 commit、目標、已修改檔案、已執行驗證、尚待處理項目；下一個工具先核對工作目錄和 Git 狀態。Codex 的產品 Handoff 是 Local／Worktree 轉移，不能將它描述成 Claude／Codex 對話互轉。[Codex worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)

Skills 的相對 symlink 能隨 Git 保留，但搬移工具或平台可能不保留連結；專案驗證應確認每個 Claude 入口都能解析到 repo 內的正本。外部瀏覽器 CLI、MCP 登入與宿主內建指令不是 `SKILL.md` 的內容，仍應在啟動時檢查。

## 5. security-review 與驗證注意事項

Claude 官方將 `/security-review` 列為可經由 Skill tool 使用的內建指令。因此「找不到同名 SKILL.md」不等於 Claude 沒有它；從開發環境複製的自訂版本也應記錄來源，避免將它誤認為內建功能的完整實作。專案若提供同名可攜 skill，需在新 session 確認實際載入的版本。[Claude skills](https://code.claude.com/docs/en/skills)

本次本機檢查確認 `codex-cli 0.153.4` 提供 `--strict-config`、`review`、`exec`、`doctor` 與 `features`。`--strict-config` 會對目前 CLI 不認得的設定欄位報錯；它可以驗證設定格式，不能證明登入、模型可用性或完整模型工作流程。

整合後應驗證：初始化前後的共用入口、skills 正本與連結、兩種觸發設定、全部相對路徑、Codex 設定解析，以及兩邊新 session 的技能清單。Claude 可用 `/skills`、`/agents`、`/memory` 和 `/doctor` 檢查載入情況；完整工作流程需要另有真實產品與測試介面才能端到端驗證。[Claude 設定診斷](https://code.claude.com/docs/en/debug-your-config)

## 6. 本機來源與實際整合結果

以下為 2026-09-08 的本機觀察，與前述官方文件及設計建議分開記錄。

- **security-review 的本機位置**：`~/.local/bin/claude` 指向 `~/.local/share/claude/versions/2.1.263`。在該執行檔中找到 `security-review` 命令名稱、描述與 review 提示內容；它不是獨立的 SKILL.md 資料夾。
- **可攜來源**：採用 Anthropic 官方 `anthropics/claude-code-security-review` 的 commit `0c6a49f1fa56a1d472575da86a94dbc1edb78eda`，保留 `.claude/commands/security-review.md` 原文與 MIT 授權。官方也說明內建命令及客製檔案的關係。[官方說明](https://github.com/anthropics/claude-code-security-review#claude-code-integration-security-review-command)、[固定版本原始檔](https://github.com/anthropics/claude-code-security-review/blob/0c6a49f1fa56a1d472575da86a94dbc1edb78eda/.claude/commands/security-review.md)
- **專案 adapter**：`.agents/skills/security-review/SKILL.md` 使用實際 host 工具、明確 Git base、pending／untracked 範圍與專案威脅模型；來源原文另存 `references/upstream-security-review.md`，未將它誤稱為跨工具可直接執行的完整 skill。
- **tw-emoji 來源**：三個原始 skill 資料夾位於 `~/.agents/custom_skills/tw-emoji-commit`、`tw-emoji-pr-note`、`tw-emoji-release-note`；`~/.codex/skills/` 的同名入口原本是連結。已攜入 SKILL.md 與 sanitizer 腳本，排除本機 cache／備份，並改成優先使用載入中的專案副本。
- **research**：使用者原先新增的 `.agents/skills/research/` 與對應 Claude 連結已保留；初始化前後的副本內容比對一致。既有 `skills-lock.json` 的 research 安裝紀錄未由本次流程覆寫。

來源、checksum 與客製紀錄存放於 `docs/agents/skill-sources.json`。舊的 `.claude/skills-lock.json` mirror 紀錄已移入該檔，避免將現在的共用連結誤當成獨立 vendor 目錄。

| 驗證介面 | 實測結果 | 範圍限制 |
| --- | --- | --- |
| Python 初始化 CLI | 4 項 unittest 通過：共用 Charter、預覽不改檔、保留工具後拒絕重跑、拒絕不存在的日期 | 在暫存目錄執行，未初始化母範本 |
| 完整搬移副本 | 初始化前 31 skills、初始化後 30 skills；README 與 research 保留 | 本機 macOS、保留 symlink 的複製 |
| 三個 sanitizer | 經 Claude 連結解析後，在另一個工作目錄執行，成功清除 cci 連結並保留繁體中文與多行文字 | 未執行 commit、PR 或 release 發布 |
| 可攜性檢查器 | 正常副本通過；故意破壞外部連結、觸發政策或 sanitizer 時皆拒絕 | 結構與資源檢查，不代表模型行為 |
| Codex 0.153.4 原生 app-server | `--strict-config app-server --stdio` 成功；`config/read` 確認專案設定層與預期值；`skills/list` 回傳 31 個專案 skills，錯誤為 0 | 使用暫存 CODEX_HOME，僅在暫存設定內信任此路徑，未變更使用者設定 |
| Claude Code 2.1.263 原生 CLI | stream-json `initialize` 回傳全部 31 個專案 skill 名稱及 harness-reviewer／harness-researcher | 使用暫存 CLAUDE_CONFIG_DIR 與 project setting source；同名 security-review 仍以明確檔案路徑辨識專案版本 |
| 獨立 review | 完整副本與無 remote、pending／untracked review 情境通過；發現的初始化後測試命令問題已修正 | 沒有產品程式碼，未宣稱完整產品流程已執行 |

Codex 的 `--strict-config` 在此版本**不支援 `features` 子命令**；本次改用 app-server 實際載入驗證，不能把 `features list` 當成嚴格設定檢查。

Claude 的檢查只送 SDK 的 `initialize` control request，擷取 `commands` 與 `agents`，沒有送 user turn，也沒有輸出初始化回應中的 account 資料。這個方式依據官方 SDK 的初始化與 subprocess 協定。[官方 initialize 原始碼](https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/_internal/query.py)、[官方 subprocess 原始碼](https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/_internal/transport/subprocess_cli.py)

兩套工具都完成原生載入檢查；本次未呼叫模型進行產品實作，也未驗證任何帳號的模型供應、遠端服務或 MCP 登入。原生角色設定保留各自工具的模型選擇；跨工具協作以文件與 Git 狀態交接，不依賴對話紀錄互轉。

另以 skill-creator 的通用檢查器驗證新寫或改寫的 security-review、init-template、三個 tw-emoji 與 evidence-report，皆通過。該檢查器的欄位白名單不接受既有 agent-browser 的 `hidden` 或 i-have-adhd 的 `disable-model-invocation`；這兩項保留原有 host metadata，並以兩套工具的原生載入結果及專案觸發政策檢查為依據，沒有為了通用檢查器而移除手動觸發規則。
