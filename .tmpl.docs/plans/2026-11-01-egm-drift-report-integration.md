# egm-drift-report 整合 Implementation Plan

> **For Claude／Codex:** 計畫與測試表核准後，依本機 runtime 契約載入 `executing-plans`、`writing-for-agents` 及 `tdd`，逐一完成核准的 seam。這份文件不是開始實作的授權。

**Goal:** 提供顯式觸發的文件／實作漂移診斷，產出有來源、範圍與限制的報告；保留既有 spec、traceability、ticket 與所有交付 gates。

**Architecture:** 建議將 EGM drift 機制改編為兩套 runtime 各自的 `egm-drift-report` skill，以 `docs/agents/drift-report.md` 保存共用契約。主助理依序比對指定文件與指定實作，只建立新的 Markdown 報告；不引入完整 EGM plugin、背景服務、額外 reviewer 或診斷引擎。

**Tech Stack:** Markdown、Claude frontmatter、Codex `agents/openai.yaml`、既有搜尋／讀檔／報告寫入工具；Python 3.11+、Git 與既有初始化／套件驗證。規劃不增加 runtime 套件相依。

## 1. 狀態與已確認範圍

- 日期：2026-11-01。狀態：**已依核准計畫完成實作；驗證結果與限制見執行證據。使用者後續已授權 commit、push 與 PR，不合併或發布。**
- 使用者已確認：先擬定實作計畫與測試表；保留 spec／traceability／ticket 流程與 gates；維持顯式觸發的診斷工具定位；先不要實作。
- 本機基準：`main`／`110a6224773d69b792b840e2a94c9966ed3ea110`，套件 manifest 為 0.3.0。已有未提交的 `.tmpl.docs/research/2026-11-01-project-status.md`，不覆寫或清除。
- 上游基準：`google/elephant-goldfish-model@403d8881d62022490637d740657b33f01e321ea8`；本輪透過 GitHub API 確認 main 仍指向同一 commit。
- 本案是母範本維護，計畫保存在 `.tmpl.docs/plans/`，保留 Charter 與 project placeholders；不為規劃建立產品 spec、traceability 或 ticket，也不分配 ticket ID。未來產品的修正仍依既有流程進行。
- 使用者已核准方案 A、以下輸出契約與測試表；執行結果另記，不以核准代替驗證。

本文件中的程式碼路徑皆相對 repository 根目錄。正式 agent 文件／skills 使用英文；使用者指南、診斷報告與維護紀錄使用台灣繁體中文。

## 2. 上游查核與整合方式

### 事實與本機改編的分界

上游 drift skill 要求指定文件目錄，依序讀文件、找實作、比對並累加 `{YYYY-MM-DD}_DRIFT_REPORT.md`；包括文件描述卻未實作，以及實作存在卻未被文件描述的差異。它只直接引用 runtime guide，沒有要求 fresh 子代理、persona、standard、script 或外部 API。文件／程式修正屬於後續由人決定的 reconciliation。[U1][U2][U3]

上游要求完整 plugin 安裝，不能把單一改編 skill 宣稱為完整 EGM 安裝。本機方案移植 drift 流程，改用本機 runtime、輸入與報告契約；不保留指向未內附 plugin 資源的路徑。[U3][U4]

上游沒有完整定義空輸入、讀取失敗、同日重跑、來源版本變動或範圍完整性；其 scenario 也有「目錄」與單檔輸入的落差。以下對這些情境的設計是本機新增契約，不宣稱為上游既有保證。上游結構／scenario 測試不能當成本機模型偵測品質的證據。[U1][U5]

| 方案 | 交付內容與取捨 | 本案建議 |
|---|---|---|
| A．本機雙 runtime 改編 | 各一個 skill、共用契約、來源與授權；可隨範本傳遞，需自行維護改編 | **採此方案擬定下列計畫**；保留名稱以供呼叫，明示為本機改編 |
| B．選用官方 plugin＋專案 adapter | 維護者另裝完整 plugin；須另驗證帳號環境、安裝與產物／gate 映射 | 保留為替代選項，不與 A 同時實作 |
| C．內附完整 EGM bundle | 引入其餘 skills、reviewers、standards、runtime 與打包責任 | 本輪範圍外 |

### 授權與來源

採 A 時以 Apache-2.0 衍生改編處理：兩套 skill 各附固定版本的 LICENSE，修改檔案註明來源 commit、本機改編與變更日期；根目錄第三方聲明及 provenance 記錄採用範圍。固定版本完整 tree 未附 NOTICE，故不憑空新增上游 NOTICE；實作時若來源改版，重新確認適用 notices。[U6]

## 3. 預期使用方式與輸入

使用者在 Claude 明確叫用 `/egm-drift-report`，或在 Codex 叫用 `$egm-drift-report`；以自然語言提供以下輸入。這不是新增 CLI，也不引入參數 parser。

| 輸入 | 契約提案 |
|---|---|
| 文件範圍 | 檔案清單或單一目錄；清單逐檔處理，目錄遞迴列出 Markdown 後固定清單。相同實體檔只處理一次，逐檔順序穩定 |
| 實作範圍 | 明確的目錄／檔案清單；可包含程式、設定、CLI、skills 與 runtime adapter，不限於程式語言檔案 |
| 比對基準 | 預設目前 checkout 的實際內容，包含指定的 staged／unstaged 檔案。明確選入的 untracked 一般檔案可讀取並記 hash；搜尋到但未列入的項目只能列為範圍外線索 |
| 文件生效狀態 | 依文件、已合併交付紀錄與票券證據判斷；無法確定時記為待確認，不把 spec 的存在等同已實作 |
| 所屬範圍 | 範本維護、單一既有 epic 或跨 epic；用於選擇報告位置。沒有 epic 時使用專案層位置，不為報告新建 epic |
| 輸出 | 依下節的既有文件根目錄選位置；首次缺少 slug 時以目標範圍命名。每次產生新檔，保留既有報告 |

若目前上下文已明確提供輸入就沿用。缺少文件或實作範圍時只詢問缺項，不擅自掃描整個 repository。空目錄、找不到任何可比對文件、必要來源全不可讀時，回報 blocked 與原因；不能回報「無差異」。

預設納入指定範圍內的 hidden 目錄，包括 `.proj.specs/`、`.agents/` 與 `.claude/`。排除 `.git/`、`.proj.handoffs/`、憑證／`.env`、cache、`node_modules/`、建置產物、既有診斷報告與 Git 忽略項目；不追蹤 symlink 到其他實體範圍。明確輸入落在排除範圍時說明排除理由，請使用一般檔案或已遮蔽副本。擴大掃描範圍需另有明確指示。

這些是 skill 的工作邊界，不是工具層 sandbox 保證；沿用宿主實際權限，報告揭露能力限制。

## 4. 比對與報告契約

### 一次診斷的順序

1. 固定 scope：repository／checkout、branch／HEAD（無 Git 時註明不可用）、相關 dirty 狀態、文件／實作清單、排除項目、文件生效依據。記錄實際 runtime／可取得的模型資訊，不推測隱藏設定。
2. 讀取必要專案規範；對實際採用的文件與實作記錄內容 SHA-256。HEAD 不代替未提交內容的版本識別。使用既有工具／Python 標準函式庫計算，不新增常設 helper。
3. 逐份文件擷取可驗證的主張，先讀其直接引用，再在限定實作範圍搜尋並讀取現況；同時盤點指定實作範圍的對外行為是否有相應文件。記錄已讀來源與未完成項目。
4. 分類每項結果並附上證據；搜尋未命中只代表該範圍未找到，不單憑這點斷言整個專案沒有實作。已存在但刻意不公開的內部細節，也不因「文件沒寫」自動列為缺陷。
5. 完成前重查已讀來源的 hashes 與相關 Git 狀態；受檢來源變動即標示 stale，停止對目前狀態作結論。另次叫用可重跑，診斷本身不加入 review 收斂 loop。
6. 只寫入新報告並回傳位置、結果與限制。報告生成失敗時保留診斷／錯誤摘要於回覆，不能宣稱報告已成功落盤。

超出可處理的上下文／時間時，在文件邊界停止，列已查與未查清單，結果為 partial；不靜默省略文件，也不自動啟動其他代理。是否擴大範圍或拆成下一次診斷由使用者決定。

### 每項結果與信心

| 分類 | 判斷依據 |
|---|---|
| 已確認差異 | 現行文件與目前實作有可指出的矛盾；分為缺漏／多出行為、介面或欄位不符、固定值取代宣告邏輯、架構／設定不符。依證據指出哪邊需後續釐清，不自動選擇改文件或程式 |
| 待確認 | 文件生效狀態不明、實作來源未找到、讀取失敗、缺少外部服務／執行證據等；說明缺什麼才能判斷 |
| 預期差異／排除 | 未到實作階段的 spec、有證據的刻意取捨、歷史研究、翻譯副本、已撤銷文件、生成檔或明示範圍外內容；記錄原因與依據 |
| 在已查範圍未發現差異 | 所述主張已與來源核對，且相應實作範圍完成盤點；僅描述這次掃描結果，不保證沒有其他缺陷 |

`spec.en.md` 是產品規格權威；翻譯依現有 `synced_from_sha` 規則檢查，過期翻譯不得拿來判定程式違反 spec。ticket 是交付狀態證據，不取代規格主張；歷史文件以其日期／基準解讀。skill 與 runtime 文件亦可作被診斷的實作／契約，但不因文字一致就宣稱模型實際行為一致。[L1][L2]

報告的高／中／低信心由已讀證據、搜尋範圍與限制說明；不輸出沒有量測依據的信心百分比。優先順序用影響描述與建議處理順序，不將診斷結果自動授予 Stage 3 的 P0／P1／P2 裁決效力。

### 報告狀態與位置

`complete`＝指定範圍全部完成且來源未變；可有已確認差異。`partial`＝部分已查、仍有來源／範圍未查證。`blocked`＝缺少必要輸入或無法開始有效比對。`stale`＝受檢來源在診斷期間改變。狀態只屬於這份報告，不寫進 ticket frontmatter；complete 也不等於 gate 通過。

| 所屬範圍 | 新報告位置提案 |
|---|---|
| 母範本維護（`.tmpl.docs/` 存在且本次屬範本維護） | `.tmpl.docs/research/drift-reports/YYYY-MM-DD-<scope>.md` |
| 採用後、明確對應既有單一 epic | `.proj.specs/<existing-epic>/reports/YYYY-MM-DD-drift-<scope>.md` |
| 採用後、跨 epic 或沒有 epic | `.proj.specs/_reports/YYYY-MM-DD-drift-<scope>.md` |

日期使用使用者／宿主提供的當地時區並記錄時區。首次檔名已存在時依序使用 `-02`、`-03`；以排他建立避免覆寫。輸出路徑必須位於 checkout 內上述適用目錄，且不可透過 symlink 逸出；無法確認或建立就回報寫入失敗。指定其他 checkout 外的位置、HTML renderer 與另存格式留待後續需求。

每份報告至少包含：診斷用途與 status、時間／runtime、基準與 dirty 狀態、輸入清單及 hashes、排除／未查來源、逐文件主張及結果、差異的雙邊 `path:line`／必要短摘錄、信心與影響、範圍內實作盤點、限制及建議後續處理。缺少其中一邊來源時列待確認並記搜尋範圍，不捏造行號。報告引用使用 repository-relative path 與行號，方便專案搬移；對話回覆使用實際檔案連結。

## 5. 與既有流程及 gates 的關係

- Claude 設 `disable-model-invocation: true`；Codex 設 `policy.allow_implicit_invocation: false`。只討論、研究或規劃此 skill 不等於授權執行診斷。一般進度查詢與其他 pipeline skills 不自動叫用它。
- 使用者明確叫用時，主助理順序執行並只寫新報告；預設不派子代理，不要求 Goldfish 或額外 fresh-context gate。Stage 3 的每軸／每輪 fresh-context 規定仍依原規範執行。
- 診斷不修改 spec、traceability、翻譯、ticket 狀態、程式、ADR 或 gate 規範；不自動開票、修正、commit、合併、發布或觸發 CI。
- 報告只提供後續工作輸入。發現新需求時先回需求收斂與 spec；修正既有交付時由使用者決定處理方式，再依現行 spec／ticket、測試表、TDD、review、security、實際介面驗證及 landing 規則進行。
- 本輪不修改 `AGENTS.md`、`docs/agents/workflow.md`、`docs/agents/review.md`、既有 `to-spec`／`to-tickets`／`implement`／`tdd` 或 reviewer 角色設定。tracker 僅補充 Markdown 診斷報告位置的說明，不增設狀態或 gate。[L1]

## 6. 預計變更檔案與實作順序

以下步驟在計畫與測試表核准後才執行；一個 seam、一個最小案例、一項最小修改，避免先寫完整測試集。

### Task 1：固定維護分支與第一個可觀察案例

- 使用 `using-git-worktrees` 建立單一寫入者的 `codex/egm-drift-report` 維護分支。已有產品 ticket 的修正仍使用 `tickets/<ticket-id>/<slug>`；本案不虛構產品 ticket。
- 明確複製本計畫與必要未提交研究到新 worktree，保留原稿；重查 base／HEAD、來源 commit 與核准範圍。
- 建立 `.tmpl.docs/research/2026-11-01-egm-drift-report/README.md` 測試協定，及第一個最小文件／實作 fixture。已知答案保存在測試 oracle，執行診斷的 session 不讀 oracle。
- 先記錄目前沒有該正式 skill 的基線；若臨時一般分析也能找出缺陷，如實記錄成功，不捏造模型偵測 red。新技能缺席、輸出契約或範本可攜性可作確定性的 red。

**完成條件：**實作授權與核准測試表可定位，來源面固定，第一個 seam 有可觀察結果。

### Task 2：先完成一條診斷路徑，再補邊界

- 新增 `docs/agents/drift-report.md`：第 3–5 節的共用英文契約，作為唯一行為定義。
- 新增 `.agents/skills/egm-drift-report/SKILL.md`、`agents/openai.yaml`、`LICENSE`；新增 `.claude/skills/egm-drift-report/SKILL.md`、`LICENSE`，不放 Codex metadata。
- 各 skill 保存精簡步驟、runtime 載入與共用契約的相對入口；來源規則取自 `../../../docs/agents/drift-report.md`，實作時從 skill 所在目錄驗證。移除上游 plugin guide 依賴，標記 Apache-2.0 改編。
- 先以一項已知文件／實作矛盾完成「顯式叫用 → 讀雙邊來源 → 寫新報告」；再依測試表逐一加入相符、預期差異、證據不足、版本改變與輸出失敗邊界。

**完成條件：**兩套入口依同一契約產出可查證診斷，不需要新 role、runner 或額外相依。

### Task 3：觸發政策與範本可攜性

- 修改 `scripts/verify-project.py`：將新 skill 納入兩套必要項目；確認它在兩邊都為顯式觸發。現有檢查只要求同名政策相同，兩邊同時誤改為 implicit 仍可能通過，因此需補此 skill 的獨立不變條件。
- 在 `tests/test_verify_project.py` 加入「任一樹缺新 skill」「兩邊都失去 manual-only 政策」的最小 mutation 案例。先觀察公開 verifier 回報失敗，再補最小驗證。
- 在 `tests/test_bootstrap.py` 延伸既有預設／keep 初始化案例：確認兩套 skill、LICENSE、共用契約及相對入口保留；預設仍移除 `.tmpl.docs/`。固定數量由產品 32→33、母範本／keep 33→34，同步該檔現有數量斷言，不以動態數量掩蓋缺 skill。
- 修改 `scripts/verify-distributions.py` 的固定數量 32→33，確認新 skill／LICENSE／共用契約隨 uvx、npx、pnpx 保留。
- `.agents/skills`、`.claude/skills`、`docs` 已在 `harness_agile/bundle.py` 的 PATHS 與 npm files 清單內；兩套 LICENSE 已有 Python glob。預計不改 `bundle.py`、根 `package.json` 或 `pyproject.toml` 清單，直接以實際套件證明涵蓋；若驗證揭露缺口，先揭露必要調整再作最小修正。[L3]

**完成條件：**缺 skill／觸發政策退化會被 verifier 擋下；採用後正式執行不依賴已刪除的維護研究目錄。

### Task 4：使用入口、來源與流程說明

- 修改 `docs/guide.md`：新增顯式診斷操作及適用情境，更新 skill 數量為採用後 33、母範本 34。
- 修改 `docs/README.md`：增加共用診斷契約入口。
- 修改 `docs/agents/issue-tracker.md`：僅說明 `reports/` 可保存非權威 Markdown drift 報告，不改既有 HTML evidence-report、目錄語意、spec freeze、ticket frontmatter 或 gates。
- 修改 `docs/agents/skill-sources.json`、`THIRD_PARTY_NOTICES.md`：記錄上游 SHA、檔案／授權 hash、兩套改編與適用聲明；不覆寫既有技能來源或假稱完整 EGM 安裝。
- 保存 `.tmpl.docs/history/2026-11-01-egm-drift-report-integration.md` 的實際結果與限制；日期以真正實作日期調整。若跨日，fixtures／證據目錄亦以實作日期命名。

**完成條件：**使用者找得到顯式入口，另一個 runtime 可依正式契約接續工作，來源可定位。

### Task 5：實際宿主、打包與交付檢查

- 依下方測試協定在 Codex 與 Claude 各開新 session，確認 discovery、顯式觸發與模型行為；不將長時間 session 直接讀新檔視為 discovery 成功。
- 執行既有結構、unittest、來源 default／keep 初始化、wheel／npm 三入口驗證；受影響檔案的正式入口與授權都需位元組一致。
- 完成 coverage report table，再依專案 `code-review` 檢查 Standards／本核准計畫，依 `security-review` 檢查 captured diff；端到端介面是實際宿主的 skill 執行與檔案產物，不是瀏覽器截圖。
- 缺少帳號／工具的測試標示未驗證；若兩套 live 未完成，不宣稱雙 runtime 行為已通過。不得以替代宿主或預製結果冒充。
- 本輪計畫不授權 commit／push／PR／合併／發布；後續若獲授權，所有 Git 文案遵守專案 `tw-emoji-*` skills。

**完成條件：**逐項對照 AC 與核准測試表交付真實結果；未覆蓋項目、失敗與限制有明確紀錄。

## 7. 驗收條件與測試表（待核准）

| ID | 驗收條件 |
|---|---|
| AC1 | 兩套 skill 僅顯式觸發；一般進度／pipeline 操作不產生 drift 報告 |
| AC2 | 單檔／清單／目錄、hidden 檔案與指定實作範圍可定位，範圍、版本及排除項目可查 |
| AC3 | 雙向診斷有實際來源，區分確認差異、待確認、預期差異與已查未發現差異 |
| AC4 | 缺輸入、讀取不足、部分未查與版本變動各有正確狀態，不冒稱完整或無差異 |
| AC5 | 只建立 checkout 內的新報告；來源與 tracker 不變，同日重跑、symlink／路徑逸出及寫入失敗有明確處理 |
| AC6 | spec.en、traceability、翻譯、ticket frontmatter、四軸／兩輪／P0 及既有交付 gates 保持現行意義 |
| AC7 | 兩套 runtime 的入口、契約及 LICENSE 會隨 default／keep 與 wheel／npm 傳遞；manual-only 退化可被檢查 |
| AC8 | 以實際宿主證據交付，附 coverage table、來源與限制，不把合成案例推論為一般偵測率或完整隔離 |

| Seam | Test intent | Scope | Acceptance criterion | Boundary conditions |
|---|---|---|---|---|
| T01．原生 skill 顯式入口 | 新 session 可發現並叫用 skill，讀共用契約、寫出一份符合欄位的新報告 | Codex／Claude 原生宿主，各記錄實際版本與叫用證據 | AC1、AC7、AC8 | 不假定宿主自動刷新；缺帳號即未驗證 |
| T02．主張與實作比對 | 最小 fixture 先驗證介面／欄位不符，再逐案擴充缺漏功能、固定值、架構差異及有義務文件化的額外行為 | 模型行為；獨立 oracle 核對證據位置，不比對逐字文句 | AC2、AC3 | 每項 findings 需雙邊來源或明示搜尋範圍；不得用單次 rg 無結果斷言全專案缺漏 |
| T03．相符與預期差異 | 相符案例未誤報；未實作 spec、歷史文件、已記錄取捨不當成現況違約；過期翻譯列待確認 | 最小正負對照 fixtures，沿用權威規格／生效證據 | AC3、AC6 | 只有 ticket 狀態不足以取代實作讀取；先讓每個案例獨立通過再合併測試 |
| T04．範圍與檔案列舉 | 單檔／清單／目錄、重複檔、hidden、空目錄與必要輸入缺項行為正確 | 暫存 checkout 與實際檔案清單 | AC2、AC4 | 不讀忽略／敏感／範圍外來源；不擅自變成全專案掃描 |
| T05．證據不足與部分完成 | 一部分來源缺漏／無法讀取／範圍未完成時為 partial；全部無法開始為 blocked；未查證不能成為零差異 | 來源缺檔可原生重現；讀取拒絕僅在宿主可支援時原生注入 | AC3、AC4 | 預製錯誤只能驗證決策層，不冒充工具權限拒絕證據；停止時列已查／未查清單 |
| T06．版本與 dirty 來源 | 受檢未提交內容以 hash 識別；讀取後改變 fixture，最終報告為 stale | 測試控制端只修改暫存 fixture，觀察前後 hash 與報告 | AC2、AC4 | HEAD 不變也要發現內容改變；若宿主無法做中途注入，此子項保留未驗證 |
| T07．唯一寫入邊界 | 執行前後來源／spec／traceability／ticket／gate 檔 hash 不變，只有適用位置的新報告；現有同名報告不變 | 真實檔案比對與輸出檔案列舉 | AC5、AC6 | 重跑得到 -02；寫入失敗不宣稱完成；報告輸出不成為下一次 normative 輸入 |
| T08．輸出路徑 | 適用的範本／epic／專案層位置正確，checkout 外或 symlink 逸出不寫入 | 暫存目錄、既有報告及 symlink 邊界 | AC5、AC7 | 不在測試中對真實外部目錄寫入；Windows 無建立 symlink 能力時明列限制 |
| T09．非顯式觸發 | 只要求進度／規劃，或執行既有 pipeline 操作時，不執行 drift、不產生報告 | 有合法既有 spec／ticket 的 adopted fixture，原生宿主負向案例 | AC1、AC6 | 討論名稱不等於執行；靜態政策檢查與實際行為分開回報 |
| T10．結構政策退化 | 刪任一樹新 skill，或兩邊同時改為 implicit，公開 verifier 均失敗 | 延伸 `tests/test_verify_project.py`，以 verifier 結果判斷 | AC1、AC7 | 不能只檢查兩邊相等；不用逐字比對 SKILL.md 當模型行為測試 |
| T11．來源初始化 | default／keep 後新 skill、相對契約入口與授權可用，兩套政策正確 | 延伸既有 bootstrap tests 與兩種實際初始化 | AC6、AC7 | default 移除 `.tmpl.docs/` 後仍可執行；Charter／project tokens 按原規則替換 |
| T12．分發與授權 | wheel／npm snapshots 一致，uvx／npx／pnpx 可建立具備新 skill 的專案；LICENSE 實際隨成品保留 | 既有分發驗證、wheel licenses、npm tarball 及一個 keep 套件樣本 | AC7 | 採用後各樹 33；keep／母範本各樹 34；無 plugin-cache 或宿主絕對路徑相依 |

### 模型行為的執行協定

- 由專案提供 `.tmpl.docs/research/<execution-date>-egm-drift-report/` 的 fixture、scope prompt、oracle 與檔案 hash 比對程序；測試介面是原生宿主 skill 與實際報告，並非只跑 unittest。
- 每個 runtime 先測 T01 與 T02 的最小矛盾案例，之後依序完成其餘核准案例。session 只取得輸入與待執行要求，不讀 oracle 或另一個 runtime 的答案；負向控制使用獨立新 session。
- 記錄實際工具讀取、報告檔案、耗時、host／模型（可取得時）與每案結果；不承諾 token 節省。符合欄位／證據／分類即可，允許合理措辭差異；缺陷漏報或不當斷言均記為失敗。
- 只對實際失敗的 seam 修正並定點重測；相同 fixture 成功不持續重跑，也不引入上游五輪／兩次 clean 的收斂要求。對新報告版本重新診斷不算 Stage 3 額外審查輪次。
- 實作後首次證據只代表指定案例／宿主，不提供統計偵測率；若要比較品質或成本，另提研究設計。

### 既有檢查與打包指令

實作後執行下列既有介面；本輪規劃不執行建置或安裝：

```sh
python3 scripts/verify-project.py
python3 -m unittest discover -s tests -v
git diff --check
uv build --out-dir dist
npm pack --pack-destination dist
python3 scripts/verify-distributions.py --wheel dist/harness_agile-0.3.0-py3-none-any.whl --npm dist/create-harness-agile-0.3.0.tgz
```

檔名依實作時 manifest 的實際版本調整，不為本機驗證先 bump 或發布。wheel／npm 是本機測試產物，不能冒充 registry 更新。來源 default／keep 與套件 keep 的額外驗證使用暫存目標，不初始化母範本本身。

結案時產出既有格式的 coverage report：`Seam | Tests | Measured coverage | Acceptance criterion | Uncovered, and why`。這是指引／模型工作流程，程式碼 coverage 百分比不適用；列實際案例及 runtime 覆蓋。

## 8. 核准與停止點

本輪交付為此實作計畫及第 7 節測試表；不新增正式 skill、共用契約、fixture、測試、角色、產品 spec／ticket 或 pipeline 行為。

待核准的主要設計是：**方案 A 的雙 runtime 本機改編、Markdown 報告與三種既有範圍的輸出位置、第 7 節 seams／測試案例。** 核准前停在規劃；後續若 scope、報告格式或 seam 有實質變更，先取得該變更的核准。

Claude live、真實故障注入、Codex tune-skills 或新版發布不是撰寫本計畫的前置條件；相關項目分別在實作測試或既有待辦追蹤，不混成新的全域 gate。

## 來源

- [U1：固定版本 drift skill](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-drift-report/SKILL.md)
- [U2：drift 設計與後續 reconciliation](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/designs/drift_report.md)
- U3：[Codex guide](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/codex.md)、[Claude guide](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/claude.md)
- [U4：上游 README／plugin 安裝邊界](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/README.md)
- U5：[drift TEST](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-drift-report/TEST.md)、[scenario](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-drift-report/test_scenarios.yaml)
- U6：[LICENSE](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/LICENSE)、[固定版本完整 tree](https://api.github.com/repos/google/elephant-goldfish-model/git/trees/403d8881d62022490637d740657b33f01e321ea8?recursive=1)
- L1：[workflow](../../docs/agents/workflow.md)、[tracker](../../docs/agents/issue-tracker.md)、[review](../../docs/agents/review.md)、[runtime](../../docs/agents/runtime.md)
- [L2：語言與翻譯同步規則](../../docs/agents/language.md)
- L3：[verifier](../../scripts/verify-project.py)、[bootstrap tests](../../tests/test_bootstrap.py)、[分發驗證](../../scripts/verify-distributions.py)、[bundle PATHS](../../harness_agile/bundle.py)、[Python manifest](../../pyproject.toml)、[npm manifest](../../package.json)
- 既有背景：[EGM 整合研究](../research/2026-11-01-elephant-goldfish-integration.md)、[上游研究](../research/2026-11-01-elephant-goldfish-upstream.md)。歷史狀態以來源日期解讀。

上游事實由本輪唯讀研究代理核對一手來源，本機接點由主助理讀取目前檔案確認；本計畫的提案不代表已完成的行為驗證。

## 執行與交付紀錄

實作與已完成的驗證見[執行證據及 coverage table](../research/2026-11-01-egm-drift-report/evidence.md)。本文件先前「規劃／未授權實作」的段落保存規劃時的停止點；後續使用者已核准實作與測試表，並另授權使用專案 tw-emoji skills 提交、推送與建立 PR。未驗證項目維持明列，不合併或發布。
