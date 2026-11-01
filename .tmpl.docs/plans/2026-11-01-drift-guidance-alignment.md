# 四項操作指引差異修正 Implementation Plan

> **For Claude／Codex:** 未來獲准執行時，載入適用的 `executing-plans`、專案 `writing-for-agents`，依核准範圍逐項處理。涉及新增測試或實作行為時，先依專案 `tdd` 及核准測試表進行。本文件只供計畫與驗證表審閱，不授權實作、開票或 Git 交付。

**Goal:** 修正診斷報告 D1–D4 的現行文字契約差異，讓操作文件及兩套 skills 對齊既有角色、初始化與交付規則。

**Architecture:** 沿用 `docs/agents/runtime.md`、角色設定與現行初始化程式為既有契約，針對五份文件／skill 入口做最小修正，並補充既有 provenance。維持雙 runtime 各自維護；不調整模型分工、權限、初始化邏輯、套件入口或 gates。

**Tech Stack:** Markdown、既有 JSON provenance、Python 3.11+ 結構與 unittest 驗證、現有初始化／分發 harness；原生宿主檢查另列證據。不新增相依套件或常駐服務。

## 1. 規劃狀態與來源

- 日期／時區：2026-11-01，Asia/Taipei。
- 狀態：**提案；修正計畫與驗證表待使用者審閱。本輪未實作、未新增測試、未開票。**
- 授權範圍：只針對已確認的四項差異擬定計畫與驗證表；不擴大處理原報告的待確認項目。
- Checkout：`/Users/phoenix/dev/edu-projects/harness-agile-template`；branch `main`；HEAD `9bc062a9e6397214b1ef31fc46f0ae26c60e7833`。
- 原始證據：[操作文件、兩套 skills 與初始化／打包一致性診斷](../research/drift-reports/2026-11-01-operations-skills-init-packaging.md)，狀態為 `partial`。其 D1–D4 是靜態契約差異；未查項目不因本計畫存在而視為完成。
- 本輪重新讀取四項差異的來源，文字仍與診斷相符。兩套 skills 各 34 個；目前有五份 ADR。這是來源盤點，不是初始化或模型實跑結果。
- 既有未追蹤狀態草稿 `.tmpl.docs/research/2026-11-01-project-status.md` 與診斷報告保留原處；本輪只新增本計畫。

下列程式碼路徑除 checkout 外均相對 repository 根目錄。正式 skill／agent 文件繼續使用英文，使用者指引與本計畫使用台灣慣用繁體中文。

## 2. 修正方式與範圍

建議修改描述以符合現有明確契約。另一種做法是修改角色權限／模型或初始化邏輯來配合舊敘述，但會改變既有分工及行為，超出四項文字差異；另建動態文件產生器也會增加維護責任。本案採最小文字修正，數量容易再變動的 ADR 說明改為依 token 描述。

| 差異 | 預計修改檔案 | 修正後契約／建議文字 | 對照來源與完成條件 |
|---|---|---|---|
| D1：research 寫入責任 | `.agents/skills/research/SKILL.md:6–12` | 主助理派出既有研究工作；researcher 讀取第一手來源並回傳附引用的證據、觀察／推論、日期與未解問題；**主助理**依既有位置及語言規範保存 Markdown。明確區分 researcher 的回傳步驟與 parent 的保存步驟；沿用角色的唯讀及不啟動下一層代理限制 | `.codex/agents/harness-researcher.toml:3–5`、`docs/agents/runtime.md:95–100`、`docs/agents/issue-tracker.md:147–155`；沒有再把任何檔案保存工作交給 researcher，也不另訂派工門檻或 fallback 政策 |
| D2：指南過度概括模型繼承 | `docs/guide.md:47` | 建議替換末句：「Codex 的 reviewer／researcher 預設繼承當前 session 的模型與 reasoning effort；Claude 的 researcher 繼承 session，reviewer 則使用角色指定的模型與 effort。Claude 其他角色與完整分工見模型協作規則。」連結到既有 `agents/claude-orchestration.md` | `.codex/agents/harness-reviewer.toml`、`.codex/agents/harness-researcher.toml`、`.claude/agents/harness-reviewer.md:5–6`、`docs/agents/claude-orchestration.md:8–13`；不在指南複製容易過期的模型 ID，不修改任何角色設定 |
| D3：採用後數量落後 | `.tmpl.docs/adoption.md:58` | 將「Claude 與 Codex 各 31 個 skills」改為「Claude 與 Codex 各 33 個 skills」；保留目前 checkout 與固定 tag 不同的限定。來源為各 34 個，預設移除各自的 `init-template` | `scripts/init-project.py:30–40`、`harness_agile/cli.py:69–70`、`scripts/verify-distributions.py:70`、`docs/guide.md:21`；default 各 33，keep 各 34，兩樹獨立 |
| D4：ADR 數量落後 | `.agents/skills/init-template/SKILL.md:41–42`、`.claude/skills/init-template/SKILL.md:41–42` | 兩套均改為依日期 token 描述，例如：`Shipped ADRs containing the INIT_DATE placeholder are dated when this project adopts them, not when they were first written.` 實際落筆沿用程式中 `{{INIT_DATE}}` 的拼法；移除固定「three」，不再換成另一個固定數字 | `docs/README.md:28–32`、五份 `docs/adr/*.md:3`、`scripts/init-project.py:68–90,131–146`；描述限於含該 token 的 ADR，已有固定日期的內容不宣稱會重寫 |

必要的伴隨紀錄為 `docs/agents/skill-sources.json`：在既有 `local_adaptations` 補記 Codex research 的「researcher 回傳／parent 保存」調整，並補充 `init-template` 的 token 日期描述。保持原有欄位結構、上游 revision、installer lock、授權與 checksum 的原始意義；不將本機修改偽裝為上游版本變更。

`.claude/skills/research/SKILL.md` 已有正確分工，本輪僅作對照，不為逐字同步而修改。兩套 `init-template` 則需各自修改並查核。

### 保持現況的檔案與行為

- 不修改 `AGENTS.md`、`CLAUDE.md`、`docs/agents/workflow.md`、`review.md`、`issue-tracker.md`、`runtime.md`、既有角色設定及 `.codex/config.toml`。
- 不修改 `scripts/init-project.py`、`harness_agile/`、`bin/`、套件 manifests、版本號、CI／發布 workflows 或 helper 實作。
- 不修改 `egm-drift-report` 入口、metadata 或共用診斷契約。它繼續維持顯式觸發、當前對話順序執行、只產出新報告的定位。
- 原診斷報告保留當時證據；後續驗證另存維護紀錄，不把歷史報告改寫成「已通過」。
- wayfinder 的 nesting、re-tune 歷史 baseline、深層 helpers、外部 registry／帳號狀態等原報告待確認項目不併入修正。

## 3. 既有流程與 gates

本案屬母範本維護，計畫依 `.tmpl.docs/README.md` 放在 `plans/`，保留 Charter／project placeholders。本輪不建立產品 spec、traceability 或 ticket，不分配 ID，也不另造 tracker 或 gate。

未來開始修正前，先核對使用者對本計畫、驗證表及執行範圍的授權。診斷報告與計畫核准不代表任何交付 gate 已通過：

1. 涉及產品或既有 ticket 的修正，沿用適用的 spec、traceability 與 ticket 證據；有新需求或超出原核准範圍時回到需求收斂，不用本計畫取代規格。
2. 適用 Stage 3 時，保留四軸、每軸／每輪 fresh context、最多兩輪、全軸有效完成且零 P0；診斷或本輪的主助理文字檢查不具替代效力。
3. 拆票仍須使用者核准；若後續授權開票，才依既有 tracker 分配全域永久 ID，並使用一票一分支 `tickets/<ticket-id>/<slug>`。純範本維護分支沿用現有慣例，於執行階段建立，不在本輪建立。
4. 寫第一個新測試前，先核准測試表；若修改程式行為，依專案 `tdd` 一個 seam、一個 red、一個最小 green。這次建議範圍主要為文件／prompt，使用契約檢查及既有測試，不為可逆文字替換新增逐字斷言測試，也不把人工差異檢查冒稱 unit-test red。
5. 修正後仍依適用流程進行專案 `code-review`、`security-review` 與實際介面驗證。未取得原生宿主證據時如實保留未驗證，依賴該證據的 gate 不能記為通過。
6. ticket 結案仍需 coverage report table；本案維護紀錄亦回填下表的實際結果／介面／未涵蓋項目。文件檢查與模型行為不混用百分比 coverage。
7. commit、push、PR、合併與發布另依當時有效授權處理；所有 commit 使用專案 `tw-emoji-commit`，PR 使用 `tw-emoji-pr-note`。本輪沒有這些動作。

規範依據：`docs/agents/workflow.md`、`docs/agents/review.md`、`docs/agents/issue-tracker.md`、`docs/agents/runtime.md` 及 `.tmpl.docs/contributing.md`。不因文件修正範圍小而宣告所有 gates 豁免。

## 4. 預定執行順序

以下是核准後才可執行的步驟；不是本輪已完成事項，也不是新建票券。

### 步驟 A：固定範圍與基準

1. 重查 HEAD、dirty 狀態、附錄來源 hashes、計畫與驗證表的核准紀錄；來源變動時先重新確認受影響差異。
2. 依適用工作流程建立修正分支／隔離 worktree，保持單一寫入者。未追蹤報告與計畫需明確帶入所需副本，不能假設 worktree 自動包含。
3. 記錄 V1–V4 的修正前契約差異，確認沒有把原報告待確認項目擴大為已確認缺陷。

### 步驟 B：修正 D1，核對單一寫入者

1. 僅調整 Codex research 的任務分工段落，讓研究輸出返回主助理，再由主助理保存。
2. 以角色／runtime／tracker 及已正確的 Claude 版逐句核對，完成 V1。
3. 在既有 provenance 補充此次本機調整；不更動 readonly 設定或模型欄位。

### 步驟 C：修正 D2–D4

1. 更新指南的一般模型說明，連結 Claude 協作規則，完成 V2。
2. 更新 adoption 的目前 checkout 數量，完成 V3 的來源盤點。
3. 兩套 init-template 各改日期 token 描述，核對 D4 與原有三個 project tokens 的說明是不同概念；完成 V4。
4. 補充 init-template provenance，核對這輪沒有非必要的跨 runtime 措辭複製。

### 步驟 D：驗證與審查

1. 先做 V5–V8 的靜態與既有測試，再於來源外的暫存成品完成 default、keep、dry-run 驗證。**不在母範本原處執行初始化。**
2. 因修改 skills／guide 會進入分發內容，執行 V9 的現有打包驗證；只建置及驗證，不發布。
3. 完成 V10 的實際 Codex research smoke。若宿主工具或角色能力不足，記錄缺項；不能拿結構驗證代替。
4. 對最終 captured diff 進行 V11 的適用 review；保持既有 gates。
5. 新增 `.tmpl.docs/history/<執行日期>-drift-guidance-alignment.md`，填入各項實際結果、來源版本、介面與未驗證項目；原診斷報告不覆寫。不自動叫用 `egm-drift-report` 作結案程序。

## 5. 驗證表提案

所有列目前均為 **待核准後執行**；本輪的來源閱讀不是下列測試已通過的紀錄。V1–V4 是內容契約檢查，V5–V9 是結構／CLI／套件介面，V10 才提供原生模型執行證據。

| ID／Seam | 驗證意圖與方式 | 範圍／驗收條件 | 邊界與證據限制 |
|---|---|---|---|
| V1／research 分工（D1） | 對照 Codex skill、researcher role、runtime、tracker、Claude 正確版本，人工列出「讀取／回傳／保存」責任 | researcher 只讀取並回傳證據；主助理保存；保留引用、觀察／推論、日期及未解問題；沒有指派子代理寫檔或另起一層代理 | 正反案例：使用 background researcher 時仍由 parent 保存；主助理可寫不代表子代理可寫。靜態文字不能證明工具權限強制生效 |
| V2／模型指引（D2） | 將指南逐一對照兩套 reviewer／researcher 設定及 Claude orchestration 表 | Codex 繼承 session；Claude researcher 繼承，reviewer 依角色設定；新連結存在；角色設定與 effort 不變 | 不聲稱切換主 session 會切換所有 Claude 角色；不聲稱模型可用性或帳號權限已驗證 |
| V3／採用數量（D3） | 盤點兩套實體 skill 入口與 `TEMPLATE_ONLY` 的移除邊界，對照 adoption／guide／分發斷言 | 此基準 source 各 34；default 各 33；keep 各 34；guide 與 adoption 的「目前 checkout」一致 | 若修正前有新增／移除 skill，依新盤點重新審閱數量，不硬套 33；不拿歷史固定 tag 作 current 證據 |
| V4／ADR 說明（D4） | 對照兩套 init-template、五份 ADR 及 token 掃描範圍 | 兩套均依 `{{INIT_DATE}}` 說明日期替換，移除固定 three，保持英文；不誤改「three tokens」的正確敘述 | ADR 已有固定日期時不應宣稱會重寫；不將 source skill 文字改為 initializer 新功能 |
| V5／diff、provenance 與路徑 | `git diff --check`；檢閱檔案清單、JSON 差異與新增相對連結 | 僅五份目標與既有 provenance，加核准的計畫／驗證紀錄；保留上游鎖定、授權、metadata、角色與 gate 規則 | 無額外 files、spec／ticket 狀態變更；既有草稿與歷史診斷原樣；用語及文件語言正確 |
| V6／專案結構與既有測試 | 執行下列既有 verify 及 unittest 命令 | 結束碼均為 0；保留兩套獨立 skills、觸發政策、角色設定及初始化既有案例 | 既有 initializer tests 使用 fixture，不能單獨證明真實 checkout 的 34／33 或五份 ADR；需 V7／V8 補充 |
| V7／完整 checkout 的 default／keep 成品 | 各用全新暫存目錄，經本機 CLI `--source` 建立；固定合法日期，分別不帶／帶 `--keep-template-files`；讀取成品後執行成品 verify | default 兩樹各 33、兩個 init-template 移除、`.tmpl.docs` 移除；keep 兩樹各 34、保留 init-template 與歷史；兩模式五份 ADR 日期皆替換；research／guide 修正隨成品保留；母範本不變 | 固定日期如 2026-11-01；keep 的歷史 placeholders 應維持原值；成品仍有 Charter gate；無 `--git` 時不建立 Git |
| V8／dry-run 不寫入 | 用第三個全新目標對同一 CLI 加 `--dry-run`；比對前後目標與來源快照 | 目標仍不存在／原空目錄仍空；來源內容 hash 不變；只預覽初始化 | 不在原始 checkout 執行會刪除模板的 script；dry-run 成功不能代替 V7 的實際成品驗證 |
| V9／wheel／npm 內容與現有三入口 | 依現有 CI 建置 wheel、sdist、npm tarball，再跑 `scripts/verify-distributions.py`；在來源／archive 中比對六份修正內容，確認 Python bundle 與 npm 一致 | 現有分發 harness 的 uvx／npx／pnpx 成功；新內容隨套件及應保留的成品傳遞；default 移除項目保持既有邊界 | 需要對應本機工具／可能的下載；不能用本機 build 宣稱遠端 CI、公開 registry 或發布完成；未改 manifests／版本 |
| V10／Codex research 實際介面 | 在支援的原生宿主用最小、無外部服務的本機研究題，載入修改後 skill；主助理派唯讀 researcher，記錄 agent 回傳、實際工具及唯一寫入者 | researcher 回傳可追溯證據，沒有檔案寫入或 nested-agent 行為；parent 保存單一 Markdown 到正確位置，引用／日期／未解事項完整 | 題目限小型本機 fixture；記錄 host、可見模型、實際生效權限與來源版本。無原生能力時留未驗證；不宣稱驗證所有 Claude 行為或工具層拒絕能力 |
| V11／review 與流程界線 | 依最終 base／HEAD／pending snapshot 執行適用的專案 code-review、security-review；人工核對授權與 gates | D1–D4 都有對應驗證證據；沒有放寬權限、改模型配置、另造 tracker、隱式診斷或未核准實作 | 審查使用各 stage 的既有角色／freshness 規則；缺少規格、snapshot 或宿主證據如實標示，不能以本表代替 gate |

### 預定命令與操作位置

以下僅供後續執行；本輪沒有執行：

```bash
# 修正 checkout，Python 3.11+
python3 scripts/verify-project.py
python3 -m unittest discover -s tests -v
git diff --check
```

V7／V8 使用既有 CLI：`python3 -m harness_agile init <來源外的全新暫存目標> --source <修正checkout絕對路徑> --name '指引驗證' --one-liner '驗證既有契約。' --date 2026-11-01 --no-input --json`；keep 案加 `--keep-template-files`，預覽案加 `--dry-run`。三案使用不同目標，父目錄事先存在。初始化及計數檢查只是暫存驗證，不初始化母範本。

V9 的現有建置命令為 `uv build --out-dir <暫存產物目錄>`、`npm pack --pack-destination <同目錄>`，再執行 `python3 scripts/verify-distributions.py --wheel <實際wheel絕對路徑> --npm <實際tgz絕對路徑>`。實作時依當前 manifest 取實際檔名，不安裝或驗證舊 cache 的產物；該 harness 會使用 uvx／npx／pnpx。CI 中未受本次修改影響的 Archify checks 保持原設定，不為此四項修正新增其功能測試。

不新增永久文字斷言測試；若執行時發現確實需要新測試、初始化邏輯調整或角色權限變更，先回到適用的需求／規格／核准測試表，不在原計畫內直接擴充。

## 6. 驗證結果回填格式

後續完成紀錄使用以下欄位；本輪沒有可填入的 passing／coverage 數字：

| Seam／驗證 ID | 實際命令或原生操作 | 介面／版本／證據 | 結果 | 對應 D1–D4 | 未涵蓋項目與原因 |
|---|---|---|---|---|---|
| 待執行 | 待執行 | 待執行 | 未驗證 | 待回填 | 尚未獲准實作及執行驗證 |

文字契約修正完成與原生模型行為驗證分別回報。V1–V4 可證明四項描述已對齊，V10 未完成時仍需明列模型行為限制；這不會把原報告的全範圍 `partial` 自動改成 `complete`。

## 7. 規劃時來源版本

以下 hash 供未來執行前確認基準；不是新一輪 drift 診斷。來源有變動時只重新核對受影響項目，再依核准範圍決定是否調整計畫。

| 路徑 | SHA-256 |
|---|---|
| `.tmpl.docs/research/drift-reports/2026-11-01-operations-skills-init-packaging.md` | `e02ea34cb61bbf40cd3a6f1d11112cafd0e90ba689aae73488236b947c0af9fd` |
| `.agents/skills/research/SKILL.md` | `985569f15739c713d6784887c3d186d4ef9ac85bec5ad9c068d25bf0739928e4` |
| `docs/guide.md` | `23c99bcce3472f745fc934fbf521c2e014d712839dcabfaf22b576f97bc5527f` |
| `.tmpl.docs/adoption.md` | `8c2225f42db7ffb52d2f4c0116516d2bdc878f07d73fce1294de2933ccc72a7a` |
| `.agents/skills/init-template/SKILL.md` | `0bd98803e9ec75a6cb7a7831256c271b3195aea2dc8c62a37b298846b24df500` |
| `.claude/skills/init-template/SKILL.md` | `a607bf78cf3a81c59f2692341aa66617c1b237d2676b007db33a018f9ba7ab22` |
| `docs/agents/skill-sources.json` | `e7e0a15be3d13a72af17b71cfddf16831f10150e69059f256654c0794d18a496` |
| `.codex/agents/harness-researcher.toml` | `060090fb8724cb5316259721d8404716e4d8d46ea14cbf44c237cc5f901fdcca` |
| `.codex/agents/harness-reviewer.toml` | `646bed10563615475ad4b0594cb14cae335a1d6523c0deaf59154045d6bb4d56` |
| `.claude/agents/harness-reviewer.md` | `8e7968d9510871eb1f341c8358ca54b78668f12db786e02c2e1c7a2729409e9d` |
| `docs/agents/runtime.md` | `1088214a9ae85f345251ce1b0c08382bddaaf604eda48287f3ada0f7557e4b15` |
| `scripts/init-project.py` | `c7de29ca503b96e2f672848eb5d588e55cde23f47707c45d70118aefab94e04d` |
