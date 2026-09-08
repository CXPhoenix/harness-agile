# harness-agile

供 **Claude Code 與 Codex 共用**的 AI 協作開發範本：需求訪談、spec、獨立 review、拆票、TDD、驗證與交付。技術棧由新專案自行選擇，母範本保留未填的 Project Charter。

## 開始使用

這個 GitHub repo 同時是 template 與專案建立器，目前為 private，下載需要既有 Git 讀取權限。可以先在本機建立，以後才 push。套件版本為 `0.1.0`，以下使用固定 Git tag `v0.1.0`，不依賴 npm／PyPI registry 同名套件。

使用 uv：

```bash
uvx --from 'git+https://github.com/CXPhoenix/harness-agile.git@v0.1.0' \
  harness-agile init my-project --name '我的專案' \
  --one-liner '它要解決的問題。' --no-input
```

使用 npx（Node.js 18+，另需 Python 3.11+ 或 uv）：

```bash
npx --yes --package='git+https://github.com/CXPhoenix/harness-agile.git#v0.1.0' \
  create-harness-agile init my-project --name '我的專案' \
  --one-liner '它要解決的問題。' --no-input
```

使用 pnpx；也可將 `pnpx` 換成 `pnpm dlx`：

```bash
pnpx 'git+https://github.com/CXPhoenix/harness-agile.git#v0.1.0' \
  init my-project --name '我的專案' --one-liner '它要解決的問題。' --no-input
```

這三個入口使用同一套 Python 初始化邏輯與隨套件攜帶的範本。Node 入口會尋找 Python 3.11+，找不到才使用 uv；可用 `HARNESS_PYTHON` 指定 Python 執行檔。完整參數不需互動；省略參數時只有互動終端機會詢問缺值。

| 選項 | 行為 |
| --- | --- |
| `--dry-run` | 預覽來源與目標，不寫入成品；套件管理器仍可能使用 cache |
| `--json` | 輸出結果供 agent／CI 使用，缺少必要值時失敗、不詢問 |
| `--skill-mode copy` | 完全不使用 symlink；預設 `auto` 在連結不可用時改用副本 |
| `--date YYYY-MM-DD` | 指定採用日期 |
| `--keep-template-files` | 保留範本歷史、初始化工具與原 README |
| `--source PATH` | 使用指定的本機母範本，目標須在來源之外 |
| `--git` | 建立獨立 Git repo；不自動 commit、建立 remote 或 push |

目標必須不存在或為空，父目錄須已存在。建立器會保存採用來源及內容 digest 至 `docs/agents/template-source.json`。預設產生專案 README，保留 30 個 skills，移除範本專用內容。

也可以讓 agent 讀取 [INSTALL.md](INSTALL.md)，提供目標、名稱與描述後執行；獨立 bootstrap skill 位於 [bootstrap/create-harness-project](bootstrap/create-harness-project/SKILL.md)，不計入每個產品攜帶的 30 個 skills。

### 從 GitHub template 或本機母範本開始

```bash
gh repo create MY_ACCOUNT/my-project \
  --template CXPhoenix/harness-agile --private --clone
```

沒有 GitHub remote 的本機建立方式：在**另外取得的、未初始化母範本 checkout** 執行 `python3 -m harness_agile init /absolute/path/my-project --source . --name '我的專案' --one-liner '它要解決的問題。' --no-input`。`--keep-template-files` 成品保留的是範本說明與 init 工具，並非完整建立器 checkout；從成品再開新專案請使用上方 Git URL 指令。

若使用 GitHub template 或直接複製完整範本，保留隱藏檔；先同步 skills，再初始化。此路線需要 Python 3.11+ 與 Git。

```bash
cd my-project
python3 scripts/sync-skills.py
python3 scripts/verify-project.py
```

驗證通過後，從這個目錄開啟任一工具：

| 操作 | Claude Code | Codex |
| --- | --- | --- |
| 啟動 | `claude` | `codex`，或在 Codex app 開啟專案 |
| 初始化 | `/init-template` | `$init-template` |
| 定義 Charter | `/grill-with-docs` | `$grill-with-docs` |
| 查看 skills | `/skills` | `/skills` |
| 審查 ticket | `/code-review` | `$code-review` |

初始化會收集專案名稱與一句話描述，再填入共用規範與 ADR 日期。也可以直接執行：

```bash
python3 scripts/init-project.py --dry-run --name "我的專案" --one-liner "它要解決的問題。"
python3 scripts/init-project.py --name "我的專案" --one-liner "它要解決的問題。"
```

`--date YYYY-MM-DD` 指定採用日期；`--keep-template-files` 保留範本文件及初始化工具。預設會移除 `.tmpl.docs/`、建立器與初始化工具、專用測試及兩邊的 init skill 入口，並改寫為成品 README。共用規範、其他 skills、同步與驗證工具會保留。

接著用 `grill-with-docs` 定義 `AGENTS.md` 的 Project Charter，再建立真正端到端可執行的 walking skeleton。初始化不會安裝產品依賴、建立產品程式碼或替你選技術棧。

**Codex 專案設定需要本機信任。** 在自己的 Codex 環境確認這個 checkout 受信任後，`.codex/config.toml` 才會套用。信任、登入與 API keys 留在本機。長時間開啟的 session 可能保留舊 skills 清單，設定完成後請用新 session 檢查。

## 兩套工具如何共用

```text
AGENTS.md                         共用規範、Project Charter、交付流程
CLAUDE.md                         匯入 @AGENTS.md，加上 Claude 專用入口
.agents/skills/<name>/            skills 正本，含 scripts 與 references
.claude/skills/<name>             相對 symlink，或經驗證一致的副本
.claude/agents/                   Claude 原生 reviewer／researcher
.codex/config.toml                Codex 專案預設
.codex/agents/                    Codex 原生 reviewer／researcher
docs/agents/runtime.md            工具對應、分工、交接方式
docs/agents/skill-sources.json    來源、固定版本、checksum 與客製紀錄
```

兩邊都可以研究、實作和 review。Claude 保留原生工具限制、subagents 與互動訪談；Codex 保留終端機驗證、patch、worktree 與原生 review。角色預設繼承當前模型，使用者可用各自工具的模型選擇器調整。

npm 與 wheel 攜帶正本範本資料，不靠套件保存 symlink。修改 `.agents/skills/` 後，檢閱差異，再執行 `python3 scripts/sync-skills.py --refresh` 與 verifier。副本偏離時會報錯；Git 在不支援連結的環境留下的文字檔，也可由 sync 修復。

切換工具時，用 `handoff` 保存目標、spec／ticket 路徑、Git branch／HEAD、未提交變更、驗證結果和下一步。同一張票維持一位寫入者；並行實作使用不同 worktree。詳見 [runtime.md](docs/agents/runtime.md)。

## 隨專案攜帶的 skills

母範本共有 **31 個**，初始化後為 **30 個**。可用 `python3 scripts/verify-project.py` 重新計數及檢查。

| 用途 | Skills |
| --- | --- |
| 初始化與環境設定 | `init-template`、`setup-matt-pocock-skills`、`wizard` |
| 需求與決策 | `grilling`、`grill-me`、`grill-with-docs`、`wayfinder`、`to-questionnaire` |
| 規格與實作 | `to-spec`、`to-tickets`、`implement`、`tdd`、`prototype` |
| 架構與診斷 | `codebase-design`、`domain-modeling`、`diagnosing-bugs`、`improve-codebase-architecture` |
| 審查與驗證 | `code-review`、`security-review`、`agent-browser`、`evidence-report` |
| Git 文案與協作 | `tw-emoji-commit`、`tw-emoji-pr-note`、`tw-emoji-release-note`、`resolving-merge-conflicts`、`handoff` |
| 研究與知識傳遞 | `research`、`teach`、`writing-for-agents`、`wait-what`、`i-have-adhd` |

`setup-matt-pocock-skills` 用於更換 tracker 等設定；這份範本已有 `.proj.specs/` 與 `.proj.tickets/` 設定，不需要重新套用通用 `.scratch/` 預設。手動觸發的 skills 同時保留 Claude 與 Codex 的觸發政策；`i-have-adhd` 仍需手動啟用。

三個 `tw-emoji-*` 包含完整 sanitizer，直接從專案 skill 目錄尋找，不需要家目錄安裝。所有 `git commit` 變體都必須透過 `tw-emoji-commit` 產生並清理訊息；缺少 skill 時停止該動作。

**security-review 有同名原生命令。** Claude Code 內建 `/security-review`；本範本另外攜入 Anthropic 公開版本的原始檔與 MIT 授權，提供跨工具 adapter。要確定跑到專案版本，可要求：「讀取並執行 `.agents/skills/security-review/SKILL.md`」。Codex 可用 `$security-review` 選擇專案版本。

## 每個 epic 的流程

```text
需求訪談 → spec＋追溯矩陣 → 四軸 review → tickets → TDD
        → code review → security review → 實際介面驗證 → 合併
```

Walking skeleton 是第 0 輪，免 spec 與規格 review，合併後豁免結束。後續以 epic 交付可展示的增量；每張 ticket 有獨立分支，狀態記在 frontmatter。每個 epic 收尾時做漏洞鏈分析、證據報告與回顧。

細節見 [workflow.md](docs/agents/workflow.md)、[issue-tracker.md](docs/agents/issue-tracker.md) 與 [review.md](docs/agents/review.md)。有 GitHub remote 才使用 `gh`；其他平台用對應工具，沒有 remote 時在本機合併。

## 驗證與外部依賴

```bash
python3 scripts/verify-project.py
```

這會檢查共用入口、skills 連結、觸發政策、sanitizer、來源 checksum 與角色設定。維護尚未初始化的母範本時，另外執行 `python3 -m unittest discover -s tests -v`，在暫存目錄測試初始化。初始化會刪除這個專用測試，成品專案不再執行該命令。

瀏覽器工作需要 `agent-browser` CLI 或宿主可用且符合驗證需求的瀏覽器工具；a11y MCP、GitHub／GitLab CLI 與服務登入按需安裝。原生應用程式、CLI、daemon 等須自行建立 e2e harness。範本不攜帶本機 MCP 憑證，也不啟用權限繞過。

這些結構檢查不代表產品功能或模型執行品質已驗證。維護母範本時保留 placeholders；要建立新產品才執行 init。

<!-- TEMPLATE-DOCS:START -->
## 範本維護資料

範本設計背景、研究與改造歷程集中在 [.tmpl.docs/README.md](.tmpl.docs/README.md)。這是隨範本納入版本控制的隱藏目錄；搜尋時請使用 `rg --hidden`。新專案 init 時預設移除，使用 `--keep-template-files` 可保留。
<!-- TEMPLATE-DOCS:END -->
