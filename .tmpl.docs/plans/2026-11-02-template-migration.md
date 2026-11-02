# 範本 Migration（upgrade／downgrade）Implementation Plan

**Goal:** 讓已採用的專案能用指定版本的建立器，把範本擁有的檔案與結構升級或降級到該版本，不覆寫使用者改過的內容，並保留可回復的紀錄。

**Architecture:** 混合式。逐檔 SHA-256 manifest 判斷範本擁有檔是否被本機修改，決定覆寫、建立、刪除或旁置新版檔；結構性變更（例如 `.gitignore` 加行）寫成宣告式 migration step，套用時把反向操作記入專案的 journal，讓較舊版本的 CLI 不需認識新版程式也能 downgrade。目標內容一律由「執行中的 CLI 版本」自帶的 bundle 經既有 `init-project.py` 渲染產生，不重寫初始化邏輯。

**Tech Stack:** Python 3.11+ 標準函式庫；沿用 `harness_agile/bundle.py`、`cli.py` 與 `scripts/init-project.py`。不新增依賴，不需網路。

---

## 狀態、授權與基準

- 日期：2026-11-02。狀態：**已核准並實作於 `claude/template-migration`；未 commit、未發布**。實作與計畫的差異見文末〈實作調整〉，結果見[完成紀錄](../history/2026-11-02-template-migration.md)。
- 已確認方向（2026-11-02 使用者選定）：混合式機制；本機修改檔以旁置 `.harness-new` 處理；目標版本內容來自執行中的 CLI（`uvx harness-agile@X migrate .`），較舊版本以 `--source` 指向本機 tag checkout；要求乾淨 Git 工作區且預設 dry-run。
- 本機基準：`main`／`0fcd87f`，harness-agile 0.4.0；`verify-project.py` PASS、unittest 24 項成功。
- 這是母範本維護：保留 Charter 與 placeholders，不建立產品 spec／ticket。核准範圍不含 commit、發布或合併。

## 現況與缺口

| 現況 | 影響 | 來源 |
|---|---|---|
| CLI 只有 `init`，且拒絕非空目錄 | 已採用專案沒有任何更新路徑 | `harness_agile/cli.py:22`、`INSTALL.md:95` |
| 版本間的必要遷移只寫在 CHANGELOG「使用注意」 | 例如 0.3.0 要手動在 `.gitignore` 加 `/.proj.handoffs/`，否則 verify 失敗 | `CHANGELOG.md:55` |
| `template-source.json` 只記 commit、content digest、建立器版本、日期 | 無逐檔 hash，無法判斷哪些檔被改過；無 name／one-liner／保留選項，無法重新渲染 | `harness_agile/cli.py:72` |
| 只有 CLI 會寫 `template-source.json` | GitHub template 與 `init-project.py` 路線沒有任何來源紀錄 | `scripts/init-project.py` |
| 初始化移除 `harness_agile/` | migrate 只能放在外部 CLI，不能放在專案內 | `scripts/init-project.py:33` |
| 2026-09-08 研究已把 update 列為延後，前提是差異預覽、所有權、衝突處理與回復方式 | 本計畫逐一回應這四項 | `.tmpl.docs/research/2026-09-08-template-distribution-bootstrap.md` §5.3 |

## 名詞表

| 名詞 | 定義 |
|---|---|
| 範本擁有檔（managed file） | 記錄在 state `files` 內、由範本產生的檔案。只有這些檔案會被 migrate 改動。 |
| 專案種子檔（seeded file） | 初始化時由範本產生、之後歸專案所有的檔案，永不同步：`README.md`、`.gitignore`、`.gitattributes`、`.proj.specs/OPEN-QUESTIONS.md`、`.proj.tickets/.gitkeep`、`docs/agents/template-source.json`。`.gitignore` 的必要變更交給 migration step。 |
| 渲染（render） | 把執行中 CLI 的 bundle 解到暫存目錄，以 state 記錄的 answers 與 options 執行該版 `init-project.py`，得到目標版本的完整樹。 |
| 本機修改（locally modified） | 專案檔的 SHA-256 與 state `files` 的紀錄不同。 |
| 旁置檔（sidecar） | 與本機修改衝突時，新版內容寫入 `<path>.harness-new`，本機檔不動。 |
| Migration step | 宣告式、可逆的結構操作，帶有引入版本與 id。v1 只提供 `ensure_line`／`remove_line`。 |
| Journal | state 的 `migrations`：每個已套用 step 的實際操作與反向操作。 |
| 採納（adopt） | 為沒有 schema 2 state 的既有專案建立 state 的一次性操作。 |

## State schema（`docs/agents/template-source.json`，schema 2）

沿用既有檔名，以 `schema: 2` 區分；舊檔沒有 `schema` 欄位，視為 legacy。

```json
{
  "schema": 2,
  "template_version": "0.5.0",
  "source": {
    "repository": "https://github.com/CXPhoenix/harness-agile",
    "commit": "0fcd87f9053311c4372a8c6b4867f7ea30aa8d9e",
    "dirty": false,
    "content_sha256": "…"
  },
  "generator_version": "0.5.0",
  "initialized_on": "2026-11-02",
  "answers": {"name": "我的專案", "one_liner": "它要解決的問題。", "date": "2026-11-02"},
  "options": {"keep_template_files": false},
  "files": {
    ".claude/skills/research/SKILL.md": "sha256:9f2c…",
    "AGENTS.md": "sha256:41ab…"
  },
  "migrations": [
    {
      "id": "handoffs-gitignore",
      "version": "0.3.0",
      "undo": [{"op": "remove_line", "path": ".gitignore", "line": "/.proj.handoffs/"}]
    }
  ],
  "history": [{"from": "0.4.0", "to": "0.5.0", "on": "2026-11-02", "generator_version": "0.5.0"}]
}
```

- `files` 的 hash 是**範本產生的內容**，不是解決衝突後的本機內容；本機與它相同才代表「未修改」。
- `undo` 只記錄這次**真正造成的變更**：`ensure_line` 時該行已存在，就不記 `remove_line`，避免 downgrade 刪掉使用者原有的設定。
- `skill_mode` 欄位移除（0.3.0 起已無作用）；讀取 legacy 檔時忽略。

## 指令介面

```bash
uvx harness-agile@0.5.0 migrate .              # 預設 dry-run，只列計畫
uvx harness-agile@0.5.0 migrate . --apply      # 寫入
uvx harness-agile@0.4.1 migrate . --apply      # 降級：方向由版本比較決定
python3 -m harness_agile migrate . --source /path/to/tag-checkout   # 使用本機未初始化範本
uvx harness-agile@0.5.0 migrate . --adopt --name … --one-liner … [--baseline-source PATH]
```

選項：`--apply`、`--json`、`--source PATH`、`--adopt`、`--baseline-source PATH`、`--name`、`--one-liner`、`--date`、`--allow-no-git`。migrate 不 commit、不 push；完成後執行專案內新版 `scripts/verify-project.py` 並回報結果，失敗不自動還原（Git 是回復手段）。

## 追溯矩陣（單一真相來源）

AC 由下表派生；新增行為先改這張表。M＝state 的 `files` 紀錄；L＝本機檔；N＝渲染後的目標檔。

### 檔案同步

| ID | M | L | N | 期望行為 | 報告類別 | 新 state `files` |
|---|---|---|---|---|---|---|
| F1 | 有 | ＝M | 有、≠L | 覆寫為 N | updated | N |
| F2 | 有 | ＝M | ＝L | 不動 | — | N |
| F3 | 有 | ≠M | ＝L | 不動（已收斂） | — | N |
| F4 | 有 | ≠M | 有、≠L、≠M | 保留 L，寫 `<path>.harness-new` | conflict | N |
| F14 | 有 | ≠M | ＝M | 不動：範本沒變，本機修改直接保留 | — | N |
| F5 | 有 | ＝M | 無 | 刪除 L，清除因此變空的目錄 | removed | 移除 |
| F6 | 有 | ≠M | 無 | 保留 L | orphaned | 移除 |
| F7 | 有 | 缺 | 有 | 不重建，尊重使用者刪除 | skipped-deleted | N |
| F8 | 無 | 缺 | 有 | 建立 | added | N |
| F9 | 無 | ＝N | 有 | 不動，納管 | adopted | N |
| F10 | 無 | 有、≠N | 有 | 保留 L，寫旁置檔 | conflict | N |
| F11 | 有 | 缺 | 無 | 不動 | — | 移除 |
| F12 | 種子檔 | 任意 | 任意 | 永不同步、不記入 `files` | — | 不記 |
| F13 | 任意 | 路徑上有 symlink、junction、目錄或解析到專案外 | 任意 | 整次中止，不寫任何檔；同樣檢查 step 操作的路徑 | blocked | — |
| F15 | 有 | ＝M | 無，但有僅大小寫不同的新路徑 | 不刪除（不分大小寫的檔案系統上兩者是同一檔） | — | 移除 |

### 前置檢查（任何一項不通過即不寫入，exit ≠ 0）

| ID | 條件 | 期望行為 |
|---|---|---|
| P1 | 目標不是 Git 工作區，或找不到 git | 拒絕；`--allow-no-git` 時繼續並警告無法以 Git 回復。Git 回報 dubious ownership 時一律拒絕並說明原因 |
| P2 | `git status --porcelain` 非空 | 拒絕，列出前幾個路徑 |
| P3 | 已存在任何 `*.harness-new`（檔案或目錄） | 拒絕：先解決上次衝突。在 Git 檢查之前執行，避免先被要求 commit 旁置檔 |
| P4 | 無 state 或為 legacy，且未給 `--adopt` | 拒絕，提示 `--adopt` |
| P5 | state `schema` 大於 CLI 支援值 | 拒絕，提示使用較新 CLI |
| P6 | 降級時 journal 有 CLI 不認識的 op | 拒絕，不做部分還原 |
| P7 | state 內任何路徑不安全（絕對路徑、`..`、不分大小寫的 `.git`、Windows 保留名），或 state 結構型別不符 | 拒絕；沿用 `bundle.unpack` 的路徑規則。state `files` 中不屬範本擁有的路徑（種子檔、`.proj.*` 等）忽略，不參與刪除 |
| P8 | bundle checksum 不符 | 拒絕（沿用 `unpack`） |
| P9 | 版本相同且無任何差異 | 回報 up-to-date，exit 0 |
| P10 | 未給 `--apply` | 只輸出計畫，不寫入，exit 0 |
| P11 | 目標 bundle 的版本無法判定 | 拒絕，避免被誤判為降級而還原所有 step |
| P12 | 未給 `--adopt` 卻給了 `--name`、`--one-liner`、`--date` 或 `--baseline-source` | 拒絕 |
| P13 | 目標或基準範本的 `init-project.py` 早於 migrate（不認得 `--template-version`、不寫 state） | 不傳該參數，以 migrate 自己的所有權規則計算 manifest |

### Migration step

| ID | 情境 | 期望行為 |
|---|---|---|
| S1 | 升級：step.version ∈ (舊版, 新版] 且 id 不在 journal | 套用，記入 journal |
| S2 | `ensure_line` 時該行已存在 | 不改檔；journal 的 `undo` 為空 |
| S3 | `ensure_line` 時檔案不存在 | 建立檔案；`undo` 為 `remove_line` |
| S4 | 降級：journal 中 step.version > 目標版本 | 依套用的相反順序執行 `undo`，自 journal 移除 |
| S5 | `remove_line` 時該行不存在 | 不改檔 |
| S6 | 升級時 id 已在 journal | 跳過 |

### 採納（adopt）

| ID | 情境 | 期望行為 |
|---|---|---|
| A1 | `--adopt`，無 `--baseline-source` | 以 N 為準：L＝N 納管；L≠N 寫旁置檔；L 缺則建立。全部 S 依 0.0.0 → 新版套用（S2 保證已有的行不重複） |
| A2 | `--adopt --baseline-source PATH` | 以該未初始化範本渲染出基準 B，當作 M；之後依 F1–F13 處理。含 placeholder 的檔案在 B 與 L 不同時視為本機修改 |
| A3 | state 已是 schema 2 時給 `--adopt` | 拒絕 |
| A4 | 缺 `--name`／`--one-liner` | 互動終端機詢問；`--json`／非 TTY 時失敗。`--date` 預設用 legacy `initialized_on`，再退回今天 |

### 建立時寫入 state

| ID | 路線 | 期望行為 |
|---|---|---|
| I1 | `harness-agile init` | 寫 schema 2 state：answers、options、`files`（排除種子檔）、`template_version` |
| I2a | 初始化目錄是 Git 工作區 | `files` 只含 Git 已追蹤的檔案，排除 gitignored 與未追蹤的本機檔（例如 `.claude/settings.local.json`） |
| I2 | `scripts/init-project.py`（GitHub template 路線） | 同 I1；`template_version` 取自初始化前的 `pyproject.toml`，讀不到則為 `"unknown"`；migrate 把 `unknown` 視為 0.0.0，所有 step 依 S2 冪等套用，不需 `--adopt` |
| I3 | `--keep-template-files` | `options.keep_template_files: true`，渲染時沿用 |
| I4 | 填入 token 的檔案 | 以 bytes 讀寫，保留原始換行；Windows 不轉成 CRLF |

## 驗收條件（由矩陣派生）

| AC | 內容 | 矩陣 |
|---|---|---|
| AC1 | 新建專案（兩條路線）都有 schema 2 state，且 `files` 與實際內容 hash 一致、只含範本產生的檔案 | I1–I4、F12 |
| AC2 | 升級只改動未修改的範本擁有檔；本機修改永不被覆寫或刪除；同版本重跑不再產生旁置檔 | F1–F15 |
| AC3 | 降級使用同一套同步規則，結構變更依 journal 還原，且只還原 migrate 自己造成的變更 | F1–F11、S2、S4、S5 |
| AC4 | 任何前置檢查失敗或 blocked 時，專案內沒有任何檔案被寫入 | P1–P8、P11、P12、F13 |
| AC5 | 預設 dry-run；`--json` 回報每個有動作路徑的類別，與實際 `--apply` 的結果一致 | P9、P10 |
| AC6 | legacy 與無 state 專案可經 `--adopt` 納管，不需網路；基準與目標可以是早於 migrate 的範本 | A1–A4、P13 |
| AC7 | 有未解決旁置檔時，專案的 `verify-project.py` 失敗；migrate 也拒絕再次執行 | P3 |
| AC8 | 升級後再降級回原版本（無本機修改時），專案內容與升級前逐 byte 相同（state 的 `history`、`source`、`generator_version` 除外） | F1、F5、F8、S1、S4 |

## 副作用檢查（新增保證前）

| 新保證 | 可能衝突的既有規則 | 處理 |
|---|---|---|
| verify 遇到 `*.harness-new` 即失敗 | 既有 verify 只檢查 skill trees 的快取檔 | 新增全樹檢查，不改既有檢查 |
| `files` 記錄範本內容而非本機內容 | 使用者手動解決衝突後，下次仍被視為「已修改」 | 屬預期：只有本機與範本相同才視為未修改，F3 會在內容收斂時自動對齊 |
| state 檔名沿用 `template-source.json` | 既有測試只檢查該檔存在 | 擴充測試驗證 schema 2；legacy 讀取保留 |
| `AGENTS.md` 為範本擁有檔 | Charter 填寫後每次升級都會產生旁置檔 | v1 接受；由使用者或助理合併。分區合併列為後續 |
| 移除 `skill_mode` 欄位 | CLI JSON 輸出的 `skill_mode` 相容性 | 只移出 state；CLI JSON 輸出維持不變 |

## 實作步驟

1. `bundle.snapshot` 在 `source` 加入 `template_version`（讀 `pyproject.toml`）。
2. 新增 `harness_agile/state.py`：state 讀寫、schema 判斷、檔案 hash、路徑安全檢查（抽出 `unpack` 既有規則共用）。
3. `scripts/init-project.py` 產生 schema 2 state（I2、I3）；`cli.create` 傳入版本並沿用（I1）。
4. 新增 `harness_agile/migrate.py`：渲染、前置檢查、同步計畫（F1–F13）、migration step registry 與 journal（S1–S6）、adopt（A1–A4）、apply 與報告。
5. `cli.py` 新增 `migrate` 子命令。
6. `scripts/verify-project.py` 新增旁置檔檢查（AC7）。
7. 文件：`INSTALL.md`、中英文 README、`docs/guide.md`（採用後的升級說明）、`.tmpl.docs/adoption.md`；CHANGELOG 於發行時由 `tw-emoji-release-note` 產生。
8. 完成紀錄寫入 `.tmpl.docs/history/`。

## 測試計畫表（待核准後才寫第一個測試）

所有測試以兩份暫存的母範本副本模擬「舊版」與「新版」（修改 `pyproject.toml` 版本並改動指定檔），透過 `--source` 執行，不需網路或模型。

| # | 測試 | 涵蓋 |
|---|---|---|
| T1 | `init` 產生 schema 2 state，`files` 每筆 hash 與檔案相符，且不含種子檔 | I1、F12 |
| T2 | `init-project.py` 直接執行也產生 state；`--keep-template-files` 記入 options | I2、I3 |
| T3 | 升級：未修改檔被更新、新增檔建立、移除檔刪除且空目錄清除 | F1、F5、F8 |
| T4 | 升級：本機修改檔遇新版變更產生旁置檔，本機內容不變 | F4、F10 |
| T5 | 升級：本機修改但新版移除 → 保留並回報 orphaned；本機刪除 → 不重建 | F6、F7 |
| T6 | 已收斂與相同內容不產生變更 | F2、F3、F9、P9 |
| T7 | 前置檢查：非 Git、dirty、既有旁置檔、無 state、schema 過新、不安全路徑、symlink 衝突時，專案檔案 hash 全部不變 | P1–P8、F13 |
| T8 | dry-run 的 JSON 計畫與 `--apply` 實際結果逐項一致 | P10、AC5 |
| T9 | migration step：`ensure_line` 已存在時不記 undo；降級只移除自己加的行；未知 op 拒絕 | S1–S6、P6 |
| T10 | 升級後降級回原版，內容逐 byte 相同 | AC8 |
| T11 | `--adopt` 無基準與有 `--baseline-source` 兩種結果 | A1–A4 |
| T12 | 有旁置檔時 `verify-project.py` 失敗 | AC7 |
| T13 | 打包：wheel 與 npm tarball 都能執行 `migrate`（延伸 `verify-distributions.py`） | 套件交付 |

## 範圍外

- 從 PyPI／GitHub 自動下載任意舊版（已選定由目標版本 CLI 提供內容）。
- 檔內衝突標記與 3-way merge；`AGENTS.md` 分區合併。
- 自動 commit、自動解決旁置檔、專用的 migrate skill。
- 0.5.0 以前的 CLI 不含 `migrate`：降到這些版本須用 `--source` 指向本機 tag checkout。
- `move` 等其他 step op：等實際有需要的版本再加入。

## 待確認

1. 首個內建 migrate 的版本號（暫定 0.5.0）。
2. 種子檔清單是否要加入 `docs/adr/0001`–`0005`（目前列為範本擁有檔；採用後若有專案修改 ADR，升級會產生旁置檔）。

## 實作調整（2026-11-02）

實作期間修正下列細節，矩陣與 AC 的行為不變。

| 項目 | 原計畫 | 實作 |
|---|---|---|
| I2 版本未知 | 提示需 `--adopt` | 視為 0.0.0，step 依 S2 冪等套用；`--adopt` 只用於沒有 schema 2 state 的專案 |
| 新專案的 journal | 未定 | 建立時為空；不大於 `template_version` 的 step 已內含於範本 |
| `ensure_line` 的 undo | `remove_line` | 另記實際附加的 `suffix` 與 `delete_if_empty`，降級時逐 byte 還原（含 CRLF 與無結尾換行） |
| adopt 的保留選項 | 未定 | 依專案是否有 `.tmpl.docs/` 判斷 `keep_template_files` |
| `--baseline-source` | 搭配 `--adopt` | 未搭配 `--adopt` 時拒絕 |
| 驗證 | 失敗不還原 | 有衝突時跳過驗證並提示先合併；無衝突且驗證失敗時 exit 1，變更保留 |
| 版本來源 | 讀 `pyproject.toml` | `bundle.snapshot` 讀 `pyproject.toml`，npm 套件根目錄則讀 `package.json` |
| 原始碼 checkout 專用檔 | 未定 | `harness_agile/`、`bin/`、`pyproject.toml`、`package.json`、`.github/` 與打包測試不納管，避免 `--keep-template-files` 的 GitHub 路線升級時誤刪 |
| 模組切分 | 新增 `harness_agile/state.py` | 未建立；state 讀寫與檢查集中在 `migrate.py`，路徑規則抽成 `bundle.check_path` 共用 |
| F13 範圍 | N 有時才檢查 | old∪new 全部路徑與 step 路徑都檢查，並偵測解析到專案外的路徑（含 Windows junction）|
| P6 範圍 | 降級時檢查 journal | 載入 state 時一律檢查，升級遇到不認得的 op 也拒絕 |
| 審查後新增 | — | F14、F15、P11–P13、I2a、I4；依 code review findings 補上，處理方式見完成紀錄 |

