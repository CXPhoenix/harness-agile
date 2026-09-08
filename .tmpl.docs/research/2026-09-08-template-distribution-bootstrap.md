# 範本發布與快速建立專案研究

研究日期：2026-09-08。檢查基準：`18b38a61d58d878ff5bd446b36e7b6110882ed62`。本文是研究與方案建議，**不是已交付的建立器使用手冊**；尚未建立 GitHub repository、發布套件或實作新 CLI。

## 結論

可以同時提供 GitHub template、終端機建立、離線本機建立，以及 agent 讀取指引建立專案。GitHub 的 template 標記只是其中一個入口；它不會自動產生 `npx`／`uvx` 套件，也不會執行本專案的 placeholder 替換。GitHub 官方支援從 template 透過網頁、CLI 或 REST API 建立 repository；本專案的設定工作則由現有 Python initializer 負責。[GitHub template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)、[generate API](https://docs.github.com/en/rest/repos/repos#create-a-repository-using-a-template)

**建議：維持一套可獨立執行的初始化核心，讓不同入口呼叫它。** 第一階段提供 GitHub template、固定版本的本機取得方式及 agent 安裝指引；若要自己的單行指令，優先沿用 Python 實作建立器並提供 `uvx`，有 Node 使用者需求時再加 `npx` 薄包裝。這是依目前程式結構與維護成本做出的建議，不是外部工具的必要規定。

## 1. 目前專案實際具備什麼

以下來自本次本機檢查，無須靠外部產品文件推測：

| 能力 | 現況 |
| --- | --- |
| 已取得完整範本後初始化 | 已有 `scripts/init-project.py` |
| 快速填參數 | 已有 `--name`、`--one-liner`、`--date` |
| 預覽／保留範本歷史 | 已有 `--dry-run`、`--keep-template-files` |
| Agent 引導 | 已有 `.agents/skills/init-template/SKILL.md`，Claude 入口為相對 symlink |
| 全新目錄的建立、下載來源／版本選擇 | 現有 initializer 沒有處理 |
| npm／Python distribution | 找不到 `package.json` 或 `pyproject.toml`，尚無套件 entry point |
| GitHub remote | `git remote -v` 沒有輸出；不能據此宣稱外部不存在同名 repo，但本機尚未連接 |
| Git、remote、commit 自動化 | initializer 不會 `git init`、建立 remote、commit 或 push |
| 支援既有產品 repo 合併 | 沒有衝突計畫、備份或 merge engine，不能當成安全的 overlay installer |

現有 initializer 透過 `Path(__file__).resolve().parent.parent` 找根目錄。這表示它適用於**已複製完成的專案**；不能原封不動把它安裝到 uv cache，再期待它修改使用者的目標目錄。新建立器需要明確的 target path，並把「套件資源所在目錄」和「新專案輸出目錄」分開。

現有 init skill 會收集名稱與一句話描述，但文字仍要求詢問兩者。若之後提供快速引數流程，應明確規定「使用者已給定的值直接採用，只詢問缺少項目」。目前的 CLI 已能完全透過引數執行；skill 快速路徑的體驗仍可改善。

初始化只替換專案識別與採用日期、清除範本專用資料；**一句話描述不等於完整 Project Charter**。下一步仍需 `grill-with-docs`。快速建立不能宣稱已完成產品需求、技術棧選擇或交付流程。

本機證據：[initializer](../../scripts/init-project.py)、[README](../../README.md)、[AGENTS.md](../../AGENTS.md)、[verifier](../../scripts/verify-project.py) 與 [init skill](../../.agents/skills/init-template/SKILL.md)。這些連結指向目前工作目錄；歷史行為以本文基準 commit 為準。

## 2. 不需要每次先到 GitHub 網頁

| 入口 | 是否先建立 GitHub repo | 是否需要我們發布套件 | 適用情境 |
| --- | --- | --- | --- |
| GitHub「Use this template」 | 是 | 否 | 偏好網頁，直接取得新 remote |
| `gh repo create --template` | 是，但不經網頁 | 否 | 已登入 GitHub CLI，想建立 remote 並複製到本機 |
| 下載固定 commit archive／用 Giget 取檔 | 否 | 不需要發布自己的套件 | 先在本機開工，以後才 push |
| 本機 `git archive` 匯出 | 否；來源已在本機即可離線 | 否 | 個人常用母範本、內網或可重現建立 |
| 自有 `uvx`／`npx create-…` | 不必 | 需打包；可先從 Git 安裝而不進 registry | 統一下載、參數、檢查、建立流程 |
| Agent 讀取安裝指引 | 不必 | 否 | 用自然語言收集參數，再呼叫同一套建立器 |

前兩種來自 [GitHub template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template) 與 [gh repo create](https://cli.github.com/manual/gh_repo_create)；archive 來自 [GitHub source archives](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives) 與 [git archive](https://git-scm.com/docs/git-archive)；Giget 來自其[官方 README](https://github.com/unjs/giget)。其餘入口的需求見下文。

### GitHub CLI：可以不開瀏覽器，但仍在 GitHub 建立

以下是假設未來已發布成 template 的示意；`OWNER`／`MY_ACCOUNT` 需換成實際帳號，這次沒有執行：

```bash
gh repo create MY_ACCOUNT/my-project \
  --template OWNER/harness-agile-template --private --clone
cd my-project
python3 scripts/verify-project.py
python3 scripts/init-project.py --name "我的專案" --one-liner "它要解決的問題。"
python3 scripts/verify-project.py
```

`--private` 指新 repo 的可見性；`--clone` 將新 repo 複製到目前目錄。需要 GitHub CLI 可用且已完成相應驗證。母範本可用 `gh repo edit OWNER/harness-agile-template --template` 標記，但本次沒有執行。[create](https://cli.github.com/manual/gh_repo_create)、[edit](https://cli.github.com/manual/gh_repo_edit)

GitHub template 建立的新 repo 從單一 commit 開始；fork 則保留母 repo 歷史。template 的衍生專案適合獨立產品。這也表示不能把它當成會自動接收母範本更新的依賴管理機制；後續同步需要另外設計。[GitHub 的差異說明](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)

`gh --template` 及 generate API 沒有選擇特定 tag／commit 的參數；API 提供 default branch 或所有 branches。需要嚴格指定採用版本時，使用固定 commit 的 archive／建立器來源選項。[gh 參數](https://cli.github.com/manual/gh_repo_create)、[API 參數](https://docs.github.com/en/rest/repos/repos#create-a-repository-using-a-template)

### 本機來源：現在就能使用，無須發布

以下是 macOS／POSIX shell 範例；在新專案的父目錄執行，`my-project` 必須不存在。逐步執行並確認成功。archive 只包含指定 commit 的受追蹤檔案，沒有 `.git` 與未提交變更。[git archive](https://git-scm.com/docs/git-archive)

```bash
mkdir my-project
git -C /path/to/harness-agile-template archive \
  --format=tar --output="$PWD/my-project.template.tar" \
  18b38a61d58d878ff5bd446b36e7b6110882ed62
tar -xf my-project.template.tar -C my-project
cd my-project
python3 scripts/verify-project.py
python3 scripts/init-project.py --name "我的專案" --one-liner "它要解決的問題。"
python3 scripts/verify-project.py
git init -b main
```

最後一步建立獨立 Git repo；之後 commit 依專案 `tw-emoji-commit` 規則執行。這個方式不需要刪除母 repo 的 `.git`，也不會帶入母 repo 的 remote。本次實測範圍為 archive、解壓、初始化與驗證，沒有為暫存專案建立 commit。

### 現成下載器：可先取得 `npx` 體驗

Giget 已提供下載 GitHub 範本的 CLI，可省去自行發布 npm 建立器的工作。以下以 `GIGET_VERSION` 及 `TEMPLATE_COMMIT` 表示未來選定的版本，並非現在可直接複製執行的具體發布值：

```bash
npx giget@GIGET_VERSION 'gh:OWNER/harness-agile-template#TEMPLATE_COMMIT' my-project
cd my-project
python3 scripts/verify-project.py
python3 scripts/init-project.py --name "我的專案" --one-liner "它要解決的問題。"
python3 scripts/verify-project.py
```

這裡執行的是 **Giget 套件**，它負責取得檔案；不代表本範本自己已經是 npm package。Giget 支援 ref、私有來源驗證與 cache／offline 選項；離線成功仍需先有工具及相應的範本 cache。這次只查證其文件，沒有對本範本執行 Giget 端到端驗證。[Giget 官方用法](https://github.com/unjs/giget)

## 3. `npx`／`pnpx`／`uvx` 的實際工作

這些工具負責取得並執行程式；**要問哪些問題、支援哪些引數、建立什麼檔案，是被執行的建立器負責**。

| 入口 | 必須提供的內容 | 對本專案的影響 |
| --- | --- | --- |
| `npx create-harness-agile@VERSION …` | 可安裝的 npm package，明確的 executable／`bin` | 新增 Node 啟動入口、打包與發布；名稱只是建議，尚未確認可用性 |
| `npm create harness-agile@VERSION -- …` | 依命名規則找到 `create-harness-agile` | 可共用上面的同一套 npm package |
| `pnpm create harness-agile@VERSION …` | create initializer package | 不需要再發布 pnpm 專用套件 |
| `pnpm dlx create-harness-agile@VERSION …`／`pnpx …` | npm 相容的 package executable | 同一套 Node 建立器的不同啟動方式 |
| `uvx --from PACKAGE==VERSION harness-agile …` | 可安裝 Python distribution 與 command entry point | 最貼近目前 Python 核心；通常用 `pyproject.toml` 的 `[project.scripts]` |
| `uvx --from git+https://…@COMMIT harness-agile …` | 同樣可安裝的 Python 專案 | 可先從 Git 發送，不必先發布 PyPI；仍須 build metadata、可執行入口及資源打包 |

官方依據：[npm init 的 create 映射與引數轉送](https://docs.npmjs.com/cli/v11/commands/npm-init/)、[npm package.json](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/)、[pnpm create](https://pnpm.io/cli/create)、[pnpm 執行入口](https://pnpm.io/cli/pnx)、[uv tools](https://docs.astral.sh/uv/guides/tools/)、[Python entry points](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#creating-executable-scripts)。

npm 也接受 Git URL、tarball 與本機 package 來源，不是只能從 npm registry 安裝；但來源仍須符合 package 結構，不能省略建立器入口。Python 路線同樣要提供 build backend／可安裝內容，只有 `[project.scripts]` 名稱還不夠。[npm package spec](https://docs.npmjs.com/cli/v11/using-npm/package-spec/)、[uv project configuration](https://docs.astral.sh/uv/concepts/projects/config/)

查核當日，未固定版的 pnpm `/cli/dlx` 文件導向 `/cli/pnx`，目前頁面仍列 `pnpm dlx`、`pnpx` 為 aliases。為顧及既有使用者，指引可採 `pnpm dlx`，並在發版驗證時記錄真正測過的 pnpm 版本。[pnpm 官方文件](https://pnpm.io/cli/pnx)

`uvx` 是 `uv tool run` 的別名，在隔離的工具環境執行；`uv tool install` 則適合經常使用、希望 command 保留在 PATH 的人。首次執行仍可能需要下載 Python、套件及依賴，不能宣稱零依賴或首次即可離線。[uv tools](https://docs.astral.sh/uv/guides/tools/)

也可以在已取得範本後用 `uv run --no-project --python 3.11 scripts/init-project.py …` 跑腳本。這是 **`uv run` 腳本模式**，不是已提供 `uvx` 套件，更不會替它下載完整範本。遠端直接執行目前 `init-project.py` 不適合，因為它依賴自己的檔案位置找專案根目錄。[uv scripts](https://docs.astral.sh/uv/guides/scripts/)

### 可以借鏡的實際專案

- **Vite**：`npm create vite`／`pnpm create vite` 展現專用建立器與引數的入口。可借鏡互動／非互動體驗，但不能因此替本範本限定產品使用 Node。[Vite Getting Started](https://vite.dev/guide/)
- **GitHub Spec Kit**：使用 `uvx --from git+https://github.com/github/spec-kit.git specify init …`；其 Python metadata 有 `specify` entry point。它是「agent 工作流＋CLI 初始化」直接相關的案例。[官方一次性使用指引](https://github.com/github/spec-kit/blob/main/docs/install/one-time.md)、[pyproject.toml](https://github.com/github/spec-kit/blob/main/pyproject.toml)
- **Giget**：把取得 repository snapshot 做成可重用工具，適合初期快速提供下載入口。[官方 README](https://github.com/unjs/giget)
- **Copier**：除了生成專案，還處理範本演進與更新。若未來大量產品需要持續合併母範本更新，值得評估；需引進其設定、答案保存與更新規則，不能假定現有 placeholder 格式直接具備更新能力。[官方概念與設定](https://copier.readthedocs.io/en/stable/)
- **Cookiecutter**：成熟的參數化專案產生器，需要配合其範本結構和設定。就目前只有少量 tokens 的專案而言，換引擎是否划算取決於後續需求。[官方 README](https://cookiecutter.readthedocs.io/en/stable/README.html)

Spec Kit 本次查到的 `main` metadata 已包含 core resources 的 wheel 打包設定；不要沿用「每次 init 一定另外抓 GitHub release」的舊假設。其 main 仍會演進，借鏡實作時應重新固定來源版本。[metadata](https://github.com/github/spec-kit/blob/main/pyproject.toml)

## 4. Agent 讀取 prompt 就能建立嗎？

可以提供這種入口，但它是「使用者指派 agent 讀取指引，agent 用工具執行建立流程」，不是一個所有 agent 都會自動讀取遠端 `INSTALL.md` 的通用協定。

有真實案例：Superpowers **目前 OpenCode** 的安裝入口請使用者要求 agent 讀取遠端 `.opencode/INSTALL.md`。本次查到的 Codex 入口已是 plugin marketplace，舊 `.codex/INSTALL.md` URL 回傳 404；不能拿舊文章的指令當現行 Codex 官方機制。[目前 README](https://github.com/obra/superpowers#opencode)、[OpenCode 安裝指引](https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md)

可為本範本設計下列使用者 prompt；**其中 INSTALL.md 尚未實作**，URL 與參數都是未來介面的示意：

```text
請讀取 https://raw.githubusercontent.com/OWNER/harness-agile-template/COMMIT/INSTALL.md。
依照該版本的建立指引，在 /absolute/path/my-project 建立新專案。
名稱：我的專案
一句話描述：它要解決的問題。
同時保留 Claude Code 與 Codex 支援，僅在本機建立。
使用已提供的值；只有缺少必要資料才詢問。
完成後驗證檔案與 skills，回報來源 commit、輸出位置與下一步。
```

建議 INSTALL.md 只負責：檢查 target／可用工具、補齊必要值、選擇固定版建立命令、執行 dry-run 與建立、驗證輸出、引導 Charter。檔案生成規則集中在程式，不要求模型自行重寫 31 個 skills。這是本研究的介面設計建議。

指引與下載的程式仍受使用者授權及宿主權限約束；它們不負責替使用者登入服務或自動信任新專案。本範本目前的 Codex 設定也明確保留本機 trust 邊界，見 `docs/agents/runtime.md`。缺少網路或終端機能力的 agent，只能交付操作步驟，不能宣稱已建立。

可以再提供一個獨立 **`create-harness-project` skill**，供「還沒有這份專案」的人安裝或臨時使用。現有 `init-template` 的前提是 repository 檔案已在，所以兩者用途不同。Agent Skills 規格允許隨 SKILL.md 攜帶 scripts／references／assets；安裝技能本身不代表自動建立整個專案。[Agent Skills specification](https://agentskills.io/specification)

Vercel 的 `skills` CLI 可安裝到指定 agent，也提供 `skills use` 產生一次性 prompt／啟動支援的 agent。這是第三方工具的能力，不是 Codex／Claude 本身的共同原生命令；本次沒有實測新 bootstrap skill，不能對本範本宣稱支援。只安裝現有 `init-template` 不會一併取得根目錄 initializer、AGENTS.md 和整套 docs。[skills 官方 README](https://github.com/vercel-labs/skills)

建立後，Codex 依本機 project 路徑載入 `AGENTS.md` 與 `.agents/skills/`；Claude 可透過現有 `CLAUDE.md` 匯入共用規範。Claude skill 有 `$ARGUMENTS` 替換語法，但跨工具 skill 應採自然語言欄位與普通 CLI 引數，不假定 Codex 會執行相同替換。新專案建好後從目標目錄開新 session，讓指令與 skills 正確載入。[Codex instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Codex skills](https://learn.chatgpt.com/docs/build-skills)、[Claude memory](https://code.claude.com/docs/en/memory)、[Claude skill arguments](https://code.claude.com/docs/en/skills#pass-arguments-to-skills)

## 5. 對這個專案最重要的工程取捨

### 5.1 不能直接把 symlink 當 npm 套件資源

npm 官方明確說明套件不包含 symbolic links。本專案的 `.claude/skills/*` 正好都是 symlink，因此 npm 發布不能只是把 repository 複製進 package。[npm publish](https://docs.npmjs.com/cli/v11/commands/npm-publish/#files-included-in-package)

建議 bundle 真正的 `.agents/skills` 及 link manifest，再由建立器在目標重建相對 links；另一個選項是隨套件攜帶受控 archive 或下載固定來源。無論採哪個方式，都要驗證解開的成品，而不只檢查原始碼。Python wheel 的資源也應驗證實際 build output，不能假定它跟 Git checkout 相同。

Git 若設 `core.symlinks=false`，checkout 出來的連結會變成寫著 link target 的普通文字檔。現有 verifier 要求真實 symlink，所以原生 Windows 仍需獨立驗證及明確政策；「自動複製兩份技能」目前會違反 verifier 的契約，不能宣稱已有 fallback。[Git config](https://git-scm.com/docs/git-config#Documentation/git-config.txt-coresymlinks)、本機 `scripts/verify-project.py`

### 5.2 一套核心與多個入口

建議核心依序完成：驗證引數 → 在暫存目錄取得固定版範本 → 產生目標內容／重建 links → 套用 init → 驗證 → 發布到新的 target → 回報。入口只負責參數解析／互動和工具啟動。

Python 核心符合現有實作與 Python 3.11+ 要求。Node wrapper 若仍呼叫 Python／uv，就必須明確顯示這個依賴；`npx` 本身不會替本 initializer 提供 Python。若希望真正只需要 Node，就要移植並決定單一正本，增加兩套引擎只會多出行為同步成本。

若 bundle 範本：版本一致、暖 cache 後較容易離線，但 package 較大，每次範本變更需要 release。若執行時下載：package 較薄且可獨立選範本 ref，但首次需要網路，並需固定 **CLI 版本與範本版本兩者**。上述為架構取捨，不是 package manager 的保證。

### 5.3 新建、採用既有專案、更新要分開

第一版只處理不存在或經確認為空的 target。既有專案可能已有 AGENTS.md、CLAUDE.md、.codex 設定與 docs，直接覆蓋會改掉既有工作約定。若加入 `adopt`／`update`，需另設差異預覽、所有權、衝突處理及回復方式。Copier 可作為後續更新能力的候選，但不需為了單次建立先引入。[Copier lifecycle 概念](https://copier.readthedocs.io/en/stable/)

### 5.4 快速參數的建議契約

以下是候選設計，尚未實作，也不表示所有參數都應一次做完：

| 項目 | 建議行為 |
| --- | --- |
| positional `DIRECTORY` | 新專案的明確目標；拒絕指向母範本或非空目錄 |
| `--name`、`--one-liner` | 延續現有意義；有值直接採用，非互動缺值回傳錯誤 |
| `--date`、`--keep-template-files` | 延續現有初始化選項 |
| `--template-ref` 或固定 bundle version | 記錄解析後的完整 commit，不只保存 `main` |
| `--source` | 進階支援本機來源／離線，以後再增加自訂 URL |
| `--no-input` | agent／CI 明確禁止互動；不等同略過驗證或權限限制 |
| `--dry-run` | 不寫入 target；若允許下載至 cache，要在契約中明說 |
| `--json` | 回傳 target、來源版本、驗證結果與下一步，供 agent／CI 使用 |
| `--git`／`--no-git` | 明確控制 `git init`；第一版不自動 commit 或 publish |
| runtime 選擇 | 第一版維持兩者共用；若加 `--agent`，同步修改 verifier、文件與數量契約 |

不建議一開始做 `--force` 覆蓋非空專案或讓 `--yes` 代替必要資料。`npx -y` 是套件執行層的提示選項；是否略過建立器問題，仍由建立器自己的引數決定。[npm init forwarding](https://docs.npmjs.com/cli/v11/commands/npm-init/)

### 5.5 版本與 provenance 要留在成品中

GitHub 建議用 commit ID 穩定 archive 內容；branch／tag 都可能移動，而且 GitHub 即時產生的壓縮檔位元組可能變動，即使解開內容相同。不要把「固定 commit」誤寫成「GitHub tar.gz 永遠相同 checksum」。若要發佈固定 archive checksum，使用自建 release artifact 並驗證該 artifact。[GitHub archives 的保證](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives#stability-of-source-code-archives)

建議成品新增精簡來源紀錄，例如 `docs/agents/template-source.json`，保存 template repository／commit、建立器版本、初始化日期與非敏感選項。因 `.tmpl.docs/` 預設刪除，採用版本不能只記在這裡。現有 skill-sources.json 是技能來源，不等於整個範本的採用紀錄。

## 6. 建議交付順序

1. **先把現有範本發布成可用 GitHub template**：補齊實際 OWNER URL、固定 release／commit 的採用指引；網頁與 `gh` 皆可使用。同步公開本機 archive 流程。
2. **新增小而完整的 bootstrap 流程**：明確 target、重用 init 核心、拒絕非空目錄、驗證輸出、記錄版本；再寫 INSTALL.md 引導 agent 使用。同時測人類互動與完整引數流程。
3. **提供 Python package／`uvx` 入口**：先 Git commit 安裝即可；如需短 package 名稱與常態 release，再發布 PyPI。必須從真正 build 出來的 wheel 驗證資源。
4. **視使用者需求提供 npm wrapper**：沿用同一核心、明示 Python／uv 需求；或評估是否改為 Node 單一核心。`npx` 與 `pnpm` 共用同一發布套件。
5. **有持續更新需求才增加 adopt／update 或評估 Copier**：避免將「快速起新專案」擴張為未定義的跨專案同步系統。

母範本繼續保留 placeholders；bootstrap 用的 metadata、測試與維護文件不應污染成品。根 README 中所有「初始化前才能執行」的範例，也需在成品 README 中妥善處理。目前 initializer 只移除帶標記的範本文件入口，成品 README 仍保留已刪 initializer 的使用說明；這是新建立器上線前應一併改善的體驗。

## 7. 驗證範圍與未驗證事項

本次實際執行：

- 從基準 commit 用 `git archive --format=tar` 匯出，解開到 `/private/tmp` 的獨立暫存目錄；路徑含繁中與空白。
- 確認沒有複製 `.git`，31 個 Claude skill links 全部是真實且可解析的 symlink。
- 執行 `verify-project.py`、init dry-run、正式 init、再次 verify，全部 exit 0。
- 初始化後為 30 個 skills，`.tmpl.docs/` 與 initializer 已刪除，AGENTS.md 含給定名稱。
- macOS／Python 3.14.3／Git 2.54.0。這次沒有在 Windows、Linux 或 Python 3.11 上重跑；不能據此宣稱跨平台全通過。

本次沒有執行：GitHub 遠端建立／標記／push、npm／PyPI 發布、Giget 或未來 uvx／npx 建立器的端到端執行、遠端 prompt 實際啟動模型、既有產品 repo 的採用／更新。官方文件查核證明工具提供相應能力，不能替代我們未來套件的整合驗證。

未來最少驗收：固定版本新建成功、缺必要引數失敗且無部分成品、非空 target 不覆蓋、來源無法取得時清楚失敗、dry-run 契約、實際套件 assets／links 完整、初始化後 verifier 通過、母範本不變、Claude／Codex 新 session 原生載入、完整引數不多問，以及公開承諾的每個 OS。

本次僅新增研究文件與維護索引，讓後續是否實作、選擇哪個入口的決策有可追溯依據。
