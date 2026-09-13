# 協作指南

在專案目錄開啟 Claude Code 或 Codex，從目前的 spec、ticket 與驗證紀錄接續工作。如果剛完成初始化，先用 `grill-with-docs` 定義 `AGENTS.md` 裡的 Project Charter，再建立 walking skeleton。

## 開始一段工作

告訴開發助理這次要完成的事，以及相關文件或 ticket 路徑。專案目的與流程以 [AGENTS.md](../AGENTS.md) 為準；執行細節見[交付流程](agents/workflow.md)。

| 操作 | Claude Code | Codex |
| --- | --- | --- |
| 定義需求與 Charter | `/grill-with-docs` | `$grill-with-docs` |
| 查看 skills | `/skills` | `/skills` |
| 審查變更 | `/code-review` | `$code-review` |
| 保存交接紀錄 | `/handoff` | `$handoff` |

Codex 專案設定需在自己的環境信任這個 checkout 後才會套用。帳號、API keys 與信任設定留在本機。完成設定或更新 skills 後，開啟新 session 檢查清單，避免沿用舊的載入結果。

## 找到適合的 skill

目前 checkout 初始化後保留 31 個 skills；母範本另外有 `init-template`，共 32 個。固定 tag 的內容可能不同，請以 `python3 scripts/verify-project.py` 檢查所採用版本的數量與結構。

| 工作 | Skills |
| --- | --- |
| 環境與工具設定 | `setup-matt-pocock-skills`、`wizard` |
| 需求與決策 | `grilling`、`grill-me`、`grill-with-docs`、`wayfinder`、`to-questionnaire` |
| 規格與實作 | `to-spec`、`to-tickets`、`implement`、`tdd`、`prototype` |
| 架構與診斷 | `codebase-design`、`domain-modeling`、`diagnosing-bugs`、`improve-codebase-architecture`、`archify` |
| 審查與驗證 | `code-review`、`security-review`、`agent-browser`、`evidence-report` |
| Git 文案與協作 | `tw-emoji-commit`、`tw-emoji-pr-note`、`tw-emoji-release-note`、`resolving-merge-conflicts`、`handoff` |
| 研究與知識傳遞 | `research`、`teach`、`writing-for-agents`、`wait-what`、`i-have-adhd` |

這份專案已設定 `.proj.specs/` 與 `.proj.tickets/`。需要更換 tracker 時才使用 `setup-matt-pocock-skills` 調整，避免重新套入通用 `.scratch/` 預設。標示為手動觸發的 skills 需明確呼叫，包含 `i-have-adhd`。

Claude Code 有同名的原生 `/security-review`。要使用專案版本，可明確要求「讀取並執行 `.agents/skills/security-review/SKILL.md`」；Codex 使用 `$security-review` 選擇專案版本。

## 兩套工具如何共用工作

`AGENTS.md` 是共用規範；`CLAUDE.md` 匯入它。`.agents/skills/` 保存 skills 正本，Claude 的入口使用相對 symlink 或經驗證一致的副本。兩套工具各自保留 reviewer／researcher 角色設定，模型預設繼承當前 session。

切換工具前，使用 `handoff` 保存工作目標、spec／ticket 路徑、branch／HEAD、未提交變更、驗證結果與下一步。接手者確認 Git 狀態後再繼續。同一張 ticket 維持一位寫入者；並行實作使用不同 worktree。完整對應見 [runtime.md](agents/runtime.md)。

## 更新與搬移 skills

修改 `.agents/skills/` 正本並檢閱差異，再同步 Claude 入口：

```bash
python3 scripts/sync-skills.py --refresh
python3 scripts/verify-project.py
```

如果搬移後出現失效連結，先執行 `python3 scripts/sync-skills.py`。不使用 symlink 的環境可加 `--mode copy`。副本若與正本不同，先確認差異來源再更新，避免覆蓋未整理的修改。

## 確認工作真的完成

結構檢查需要 Python 3.11+：

```bash
python3 scripts/verify-project.py
```

這會檢查共用入口、skills 連結或副本、觸發政策、sanitizer、來源 checksum 與角色設定。它驗證協作設定，產品的 build／test 命令由 walking skeleton 建立。

瀏覽器功能可用 `agent-browser`，或宿主提供且符合驗證需求的瀏覽器工具；原生應用程式、CLI 與 daemon 需要對應的 e2e harness。GitHub／GitLab CLI、MCP 連線與服務登入按需設定。回報結果時，說明實際驗證了哪個介面。

每次 `git commit`（含 amend）都使用專案的 `tw-emoji-commit` 產生並清理訊息；PR 與 release 文案使用對應的 `tw-emoji-*` skill。若 skill 不可用，停止該動作並回報。沒有 remote 時可在本機合併，有 remote 時依所在平台的流程交付。

Windows 的 Archify 自動開啟功能已停用，包含 `deliver --open` 與 `preview`；請手動開啟產物或預覽網址。詳見[停用範圍與驗證方式](security/windows-opener.md)。
