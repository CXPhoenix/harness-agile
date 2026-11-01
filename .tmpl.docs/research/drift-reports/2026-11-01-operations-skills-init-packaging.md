# 操作文件、兩套 skills 與初始化／打包一致性診斷

## 結論

本次確認 **4 項指引／文件與目前來源不一致**：Codex research 的寫檔責任、協作指南的模型繼承描述、採用後 skill 數量，以及 init-template 的 ADR 數量。這些是依當前本機來源比對的結果，不代表已執行模型或重現操作失敗。

診斷狀態為 **partial**。主要操作、觸發政策、初始化／打包來源與所列主張已核對；未完整逐一驗證所有 skill 的內部 renderer／helper 行為，也未執行受檢程式、測試、套件建置、模型 session 或遠端查詢。不能將未查部分解讀為沒有漂移。

## 基準與執行界線

- 目的：依使用者明確叫用的專案 egm-drift-report，診斷現行文件、兩套 skills 與初始化／打包實作是否一致。
- 宿主：Codex desktop 本對話，使用本機讀檔／搜尋工具順序查核；未另外啟動子代理。沒有獨立取得模型／effort 設定，不推測。
- Branch：main。
- HEAD／本次唯一版本基準：9bc062a9e6397214b1ef31fc46f0ae26c60e7833；不是 branch diff review，未另選比較用 Git base。
- 初始 tracked 內容無 staged／unstaged 變更；既有未追蹤檔為 .tmpl.docs/research/2026-11-01-project-status.md，未作現況證據，保留原處。
- 本報告是非權威診斷，不更改 spec、traceability、ticket／frontmatter、ADR、程式、skills 或 gates；沒有修正、開票、commit、合併、發布、觸發 CI 或安裝套件。
- 本次時間／來源最終複查結果在末節記錄。本文完整路徑相對 repository 根目錄；同段落的 :行號 延續前一個檔案，兩樹 helper 的相同相對尾段依該列範圍解讀；目前檔案版本以附錄 SHA-256 為準。

## 範圍、搜尋方式與排除

文件集為根目錄 README.md／README.en.md、INSTALL.md、AGENTS.md／CLAUDE.md、第三方聲明、docs/ 的 Markdown，以及 .tmpl.docs 的現行 README、採用／維護／發布指引與術語表，共 29 份。以目前有效操作主張為準，不以文件最後修改日期推論過時。

實作集為兩套 skill trees 的 68 個 SKILL.md 入口、34 份 Codex metadata、相關引用文件與指定 helper；以及 harness_agile/、bin/、bootstrap/、scripts/init-project.py、verify-project.py、verify-distributions.py、project-readme.md、hatch_build.py、兩份 package manifests、.github/workflows/、runtime role/config。初始化與打包主鏈由入口逐層閱讀，不執行來源。

搜尋先列出 Git tracked 路徑，再使用限定檔案／目錄的 rg、行號讀取與 Python 標準函式庫做文字、JSON、路徑及 hash 比對。135 份 skill Markdown 做本機 Markdown 連結目標檢查，排除 code fences、遠端 URL、fragment 與動態 placeholder；這不包含 anchor 正確性、純反引號路徑或所有外部連結。沒有以一次搜尋未命中推論全專案不存在某功能。

排除 Git 內部內容、所有 .worktrees、.proj.handoffs、憑證／.env、cache、node_modules、dist、既有診斷報告、歷史研究／計畫、測試生成報告及未追蹤的狀態草稿。既有來源中的歷史驗證段落只依其日期判讀，不當成此次執行結果。沒有讀取實際打包產物或對外服務狀態。

## 已確認差異

### D1．Codex research 的寫檔責任與現行角色契約衝突

- 文件／skill 側：.agents/skills/research/SKILL.md:6–12 先要求啟動 background agent，接著以 Its job 將撰寫並保存 Markdown 檔交給該代理。
- 實作／契約側：.codex/agents/harness-researcher.toml:3 設定 read-only；:5 明定回傳引用給 parent 保存成果，並要求 Stay read-only。docs/agents/runtime.md:95–100 也將保存最終 reports 的責任交給 parent；docs/agents/issue-tracker.md:147–155 要求 concurrent researchers 回傳給單一寫入者、由 main session 保存 findings。
- 另一套入口：.claude/skills/research/SKILL.md:6–10 已明確要求 researcher 回傳證據、不寫檔，由呼叫端保存。這個對照只用來定位責任差異；確認依據是 Codex 自己的 role／runtime 契約，不是要求兩樹逐字相同。
- 影響：照 Codex skill 原文派工時，子代理收到的寫檔工作與其唯讀責任不相容；可能嘗試寫入或無法交付預期檔案。這裡確認的是文字契約衝突，沒有宣稱宿主必然拒絕寫入或已發生資料損毀。
- 信心：高；兩邊都有直接規定。
- 相關待確認：.agents/skills/wayfinder/SKILL.md:114 還要求研究子代理自行叫用 research；與 research 再啟動代理、角色禁止 nesting 的組合值得另驗證。此處沒有再計為獨立確認缺陷，也未實際執行該流程。

### D2．協作指南將模型繼承描述得過廣

- 文件側：docs/guide.md:47 將兩套 reviewer／researcher 角色一併描述為「模型預設繼承當前 session」。
- 設定側：.claude/agents/harness-reviewer.md:5–6 明確固定 claude-opus-5-5／high；docs/agents/claude-orchestration.md:10–13 區分固定 reviewer、challenger、executor 與 inherit 的 researcher。CLAUDE.md:9–11 也有相同區分。
- Codex 對照：docs/agents/runtime.md:95–98、.codex/agents/harness-reviewer.toml:1–9 與 .codex/agents/harness-researcher.toml:1–6 沒有固定 model，這部分與繼承 session 的描述相符。
- 影響：使用者可能誤認切換主模型會同時切換 Claude reviewer。此結論不涉及模型是否仍可取得，或帳號是否有使用權限。
- 信心：高；指南的概括與明確固定設定不一致。

### D3．採用指引仍寫每套保留 31 個 skills

- 文件側：.tmpl.docs/adoption.md:58 明言「目前 checkout」預設初始化後 Claude／Codex 各 31 個 skills。
- 現況與程式側：目前兩樹各有 34 個實體 skill 目錄；scripts/init-project.py:30–40 的移除清單對每樹只移除 init-template，故此來源的預設保留數為 33。harness_agile/cli.py:69–70 依實際目錄計數，scripts/verify-distributions.py:70 也以各 33 個驗證；docs/guide.md:21 已記為 33／34。
- 影響：採用者依這份指引檢查成品時，會得到不一致的預期數量。
- 信心：高；目錄盤點、移除邊界及現行數量斷言互相支持。本次未執行初始化，不把靜態推導冒充新一次實跑。
- 不是固定 tag 差異：該句主張的是目前 checkout，並非 v0.3.0 歷史套件。

### D4．兩套 init-template 仍描述「三份 ADR」

- 文件側：.agents/skills/init-template/SKILL.md:41–42、.claude/skills/init-template/SKILL.md:41–42 皆寫 the three shipped ADRs。
- 來源側：docs/README.md:28–32 列出 ADR-0001 至 ADR-0005；五份實際檔案各在第 3 行含 INIT_DATE token。scripts/init-project.py:21、68–90、131–146 會掃描符合條件且非範本專用的文字，替換 token，沒有僅限前三份 ADR 的條件。
- 影響：初始化內容的說明落後於新增 ADR；目前來源表示五份日期皆屬替換範圍。這不是確認日期替換功能失效。
- 信心：高；數量、tokens 與替換邏輯可直接核對。

## 已查主張與實作盤點

| 文件／介面 | 查核主張與對應來源 | 本次結果 |
|---|---|---|
| README.md:22–24、31–64；README.en.md 對應段落 | 共用規範、獨立 skill 副本、Python／Node 入口 | 與 harness_agile/bundle.py:9–15、harness_agile/cli.py:46–70、bin/create.cjs:2–5、bin/python.cjs:6–24 的靜態主鏈相符；遠端 registry 內容未查 |
| INSTALL.md:8–10、47–79 | 目標需不存在或空目錄、source 分離、dry-run 不寫目標、預設不建立 Git／commit | harness_agile/cli.py:22–57、58–79 有相應檢查與順序；未執行邊界案例 |
| INSTALL.md:81–94；兩套 init-template:32–42 | 獨立 skills、deprecated skill-mode、default／keep、README 與日期 | scripts/init-project.py:24–40、128–173 與 harness_agile/cli.py:63–70 相符；ADR 數量為 D4 |
| .tmpl.docs/adoption.md | 建立器／複製後原地初始化兩入口、保留內容 | 主鏈相符；目前 skill 數量為 D3 |
| .tmpl.docs/contributing.md:21–38；.tmpl.docs/README.md | 範本與產品文件分工、靜態／實測證據分開 | 初始化移除 .tmpl.docs、正式 docs 保留的實作相符；未執行文中命令 |
| .tmpl.docs/registry-publishing.md:3–16、20–27 | 手動發布、main 限制、tag／版本檢查、npm 待審 | .github/workflows/publish-pypi.yml:3–23、.github/workflows/publish-npm.yml:3–42、.github/workflows/build-release.yml:17–67 的設定相符；外部 2FA／Trusted Publisher／上架狀態待確認 |
| docs/guide.md:21、47–59 | skill 數、兩套 roles、更新不自動同步 | 數量與分樹相符；模型繼承概括為 D2 |
| AGENTS.md:55–89；docs/agents/workflow.md:40–104；docs/agents/review.md:18–69 | spec／matrix、四軸 fresh context、兩輪與 P0、測試表、commit 規則 | 與所讀 to-spec、implement、tdd、code/security review 入口的主要流程相符；不等於實際 gate 已執行 |
| docs/agents/issue-tracker.md:33–38、78–101、132–158 | 診斷非權威、ticket frontmatter、blocking 與單一寫入者 | 診斷入口契約相符；research 寫入責任為 D1 |
| docs/agents/language.md:33–65 | 英文 spec 權威、翻譯 hash 與時機 | 兩套 to-spec:8–21 均導向該規範；未建立或核對實際產品翻譯 |
| docs/agents/runtime.md:10–43、86–121 | 每樹獨立、manual-only 對應、Codex roles 繼承模型 | 34 對設定相符；CLI/API 的實際能力／模型可用性未測 |
| docs/README.md；ADR-0001～0005 | 流程入口及五份有效 ADR | 本機檔案可定位；D4 為引用它們的 skill 敘述落後 |
| docs/agents/domain.md:5–13；.tmpl.docs/CONTEXT.md | 領域文件缺少時可繼續、範本術語 | 不把根目錄 CONTEXT 缺少當缺陷，也不要求產品初始化 |
| docs/agents/codex.md:6–24 | 已授權範圍持續進行、使用實際介面、揭露限制 | 本次僅檢查此契約與相關入口，沒有量測模型是否遵守 |
| docs/agents/drift-report.md:11–143；兩套 egm-drift-report | 顯式、順序、只寫報告、證據不足／stale 不算無差異 | metadata／兩套入口／tracker 說明一致；這次報告自身亦依該邊界產出 |
| docs/security/windows-opener.md:7–9 | Windows deliver／preview 不自動開啟 | 兩樹 bin/open-artifact.mjs:18–24 有直接 win32 disabled 分支；兩份 helper hash 相同。未跑原生 Windows |
| docs/security/archify-dependencies.md:28–47 | fast-uri 3.1.9、生成 validators、支援子集 | 兩樹 package.json override／lock 均為 3.1.9；generate-validators.mjs:6–12、43–49 與 package scripts 相符。上游 npm test 的缺資源已明示不保證，不誤報為新漂移 |
| THIRD_PARTY_NOTICES.md:90–105 | egm-drift-report 為本機改編並附授權 | source／package manifests 涵蓋兩樹與 LICENSE glob；不是此次法律／外部上游或實際 wheel 審查 |
| Python／npm package manifests | 版本、入口、兩樹與 docs、授權隨分發 | pyproject.toml:6–25、package.json:2–44、hatch_build.py:7–17 與 harness_agile/bundle.py:9–48 靜態對應；三份版本欄位均為 0.3.0 |
| .github/workflows/verify.yml | 結構、unittest、portable／preview、audit、三入口打包驗證 | 指令與現有來源路徑可定位；不宣稱 CI 已通過 |
| bin/python.cjs；bootstrap/create-harness-project | Python 3.11+／uv、argv 傳遞、顯式建立器入口 | 對應 INSTALL 主張；bootstrap 的引導／metadata 可定位，沒有執行外部 CLI |
| scripts/project-readme.md；scripts/init-project.py:148–173 | default 產生產品 README，移除建立器／範本測試與發布 workflows | 刪除清單及 README 寫入邏輯相符；不把 source template 現況當成 adopted project |

## 兩套 skills 的檢查深度

每對皆核對入口存在、name／description、Codex metadata、manual-only 對應、本機 Markdown 引用與同名文字差異。兩樹各 34 個入口、所有對應 policy 相同；135 份 skill Markdown 的受支援本機連結目標沒有找到缺檔。這是本次自行對原始文字／路徑做的靜態盤點，**沒有執行 scripts/verify-project.py**。

相同名稱不表示應逐字相同。docs/agents/runtime.md:10–21 明確允許兩樹分別調校。來源 JSON 亦記錄 upstream snapshot 與 local adaptations，所以與 installer lock 中的上游 hash 不同，本身不構成漂移。

下表「結構相符」只指上述入口／政策／引用範圍；所有 skill 的實際模型效果、全部 helper 與指令正確性都未由本次盤點完整證明。

| Skill | 兩樹 manual-only | 本次結果 |
|---|---|---|
| agent-browser | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| archify | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| code-review | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| codebase-design | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| diagnosing-bugs | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| domain-modeling | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| egm-drift-report | 是／是 | 兩入口共用診斷契約，觸發與寫入邊界相符 |
| evidence-report | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| grill-me | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| grill-with-docs | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| grilling | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| handoff | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| i-have-adhd | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| implement | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| improve-codebase-architecture | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| init-template | 否／否 | D4：兩套 ADR 數量描述落後 |
| prototype | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| research | 否／否 | D1：Codex 寫檔責任衝突 |
| resolving-merge-conflicts | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| security-review | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| setup-matt-pocock-skills | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| tdd | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| teach | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| to-questionnaire | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| to-spec | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| to-tickets | 是／是 | 上游範例由 tracker 覆蓋；不另計差異 |
| tune-skills | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| tw-emoji-commit | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| tw-emoji-pr-note | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| tw-emoji-release-note | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| wait-what | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| wayfinder | 是／是 | 入口／政策／引用結構相符；完整功能未驗證 |
| wizard | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |
| writing-for-agents | 否／否 | 入口／政策／引用結構相符；完整功能未驗證 |

## 待確認與預期差異

1. **待確認：所有宿主的實際行為。** 模型選用、skills discovery、metadata 支援、fresh-context／唯讀是否實際生效，本輪未透過原生 session 或工具強制拒絕驗證。沒有把角色宣告當成執行證據。
2. **待確認：實際初始化與分發產物。** 本輪只讀 Python／Node／Hatch／workflow 來源，沒有建置 wheel／sdist／npm tarball、安裝或重跑 tests；外部 registry 的 0.3.0 內容及帳號設定也未查。白名單／files 的靜態涵蓋不保證一次實際建置的內容。
3. **待確認：深層 helpers。** Archify 的 renderer、完整 preview 行為、generated validators、schema／browser exports、update checker 等未逐一追到所有葉節點，也未跑瀏覽器／跨平台。只核對了所述 Windows opener、生成 validators、依賴與入口主張。
4. **待確認：re-tune 的歷史 baseline。** skill-sources.json 的 model targets 仍指向有日期的舊調校紀錄，兩套 tune-skills 會參考舊報告。預設初始化移除 .tmpl.docs 後，這些歷史來源是否可取得，以及缺失時流程如何降級，未實際執行；不將此未查情境計為已重現缺陷。
5. **預期差異：上游 tracker 範例。** to-tickets 中仍有 .scratch／ready-for-agent 範例，但 AGENTS.md:67–69、docs/agents/runtime.md:39–43、docs/agents/issue-tracker.md:126–158 明定既有 tracker 覆蓋這些預設，因此沒有單憑範例文字認定會另建 tracker 或破壞 gates。
6. **預期差異：固定版與母範本進度。** README／INSTALL 固定 0.3.0，docs/guide.md:21、INSTALL.md:91–92 明確提醒目前 checkout 與固定 tag 可不同。未把尚未另發版視為打包功能缺失，也不假設 registry 已包含本次 main。
7. **預期差異：歷史驗證數字。** 安全文件中的舊版本、22 tests、Windows 未驗證等段落有日期／快照語境，不以本次目錄數量或先前聊天的成功結果覆寫它們。
8. **預期差異：根目錄 domain 文件。** docs/agents/domain.md:13 明定缺少時繼續，產品 Charter 亦仍保留範本 placeholders；本次不要求新增產品、CONTEXT 或票券。

## 可選的後續處理

若要處理，先釐清 D1 的實際寫入責任與 D2 的角色模型說明，再更新 D3／D4 的數量描述即可。是否改文件、skill 或角色契約由使用者決定；本報告不自行選擇修正方案、不新增 ticket，也不修改現行流程。未確認的項目可另選明確範圍作下一次診斷／驗證。


## 最終版本複查與來源清單

- 本機時間：2026-11-01T17:24:12+08:00（Asia/Taipei）。
- Checkout：/Users/phoenix/dev/edu-projects/harness-agile-template。
- 產出前逐一複查 244 份輸入的 SHA-256，皆與首次擷取值相同；HEAD、branch 與相關 Git 狀態未變。
- 狀態維持 **partial**；不將缺少的實際執行證據視為一致性通過。
- 下表列出實際讀取／掃描路徑及版本。內容／定點查核不代表已完整逐條驗證整份文件；引用掃描僅涵蓋本報告所述的連結規則。

| 路徑 | 查核深度 | SHA-256 |
|---|---|---|
| .agents/skills/agent-browser/SKILL.md | 內容／定點主張查核 | `7c0ba009c3d84040b6bb92d2179eb6e94b8d662a94572de626ce6d29f7e96b13` |
| .agents/skills/agent-browser/agents/openai.yaml | 內容／定點主張查核 | `8619a54e8c098122a7f3881394f84ca89b684366e848233a29ad18b6ec363935` |
| .agents/skills/archify/SKILL.md | 內容／定點主張查核 | `ec1d40cdc1f80c0d281dcb603fe93d54303dc6725f0e696d28525705c0b01ece` |
| .agents/skills/archify/THIRD_PARTY_NOTICES.md | 本機引用路徑掃描，未逐條語意驗證 | `0b7fb59365dc21c93b0f62526d74ee913aeec9ae532c112bc76afa7edcd56e14` |
| .agents/skills/archify/agents/openai.yaml | 內容／定點主張查核 | `bcd33cb236fba13839a2427b9afa45bd8474426944e6181bad542d9ed7221c33` |
| .agents/skills/archify/bin/open-artifact.mjs | 內容／定點主張查核 | `e58b51af0bd37ef3bff980a0145d3130f56324bec5a7efd4fbaf9959b1176edf` |
| .agents/skills/archify/bin/preview.mjs | 版本／結構盤點，未完整語意查核 | `aac5c4e796fc31a0f0ae7fa2267106ff125bea8d2d7628806034f57a25176f1d` |
| .agents/skills/archify/brand-marks/README.md | 本機引用路徑掃描，未逐條語意驗證 | `8b771a16322ce9ea47fdc00b9935e33adf0f3af608f2d735235443e15ef622e2` |
| .agents/skills/archify/package-lock.json | 版本／結構盤點，未完整語意查核 | `12a357be1940c31c0f9d3d592b6a8abb2a43d7bc67bf1d4a216e69395d26786d` |
| .agents/skills/archify/package.json | 內容／定點主張查核 | `6b912a553d168d78adbb71825ad60a58b33abec1c0b834890bd25ed7416bf759` |
| .agents/skills/archify/references/authoring-contract.md | 本機引用路徑掃描，未逐條語意驗證 | `873494557cf9be91d9eed8ecce37072886c0e98b851ad59ab8938f405c6fbc5e` |
| .agents/skills/archify/references/brand-marks.md | 本機引用路徑掃描，未逐條語意驗證 | `8010869da70677e686ecb312d9c3eec2d20723a44f817ab2bbf5525361c8a136` |
| .agents/skills/archify/references/delivery-contract.md | 本機引用路徑掃描，未逐條語意驗證 | `19feab54023ae14f67a13f6f6634ff95635aca25c5381ca5a8f223f99c942e4a` |
| .agents/skills/archify/references/viewer-runtime.md | 本機引用路徑掃描，未逐條語意驗證 | `dc0d9ffe6b9987d73d2d48710fce5ab4c120bbf1940ff1eb9355259c5d4f32b6` |
| .agents/skills/archify/renderers/dataflow/README.md | 本機引用路徑掃描，未逐條語意驗證 | `18c4f86ba62fcee371d9fe38094625b3a68cc76231c36ab8c8124acb4c1ffa42` |
| .agents/skills/archify/renderers/lifecycle/README.md | 本機引用路徑掃描，未逐條語意驗證 | `f8ef88dc859189bb18bad7bb2e27d997cbc9d30936cf20f8bf401bae7f57deec` |
| .agents/skills/archify/renderers/sequence/README.md | 本機引用路徑掃描，未逐條語意驗證 | `a442335dcf44b1587d3ad88809e31b001a4fafdf7a134040e8b1927455af4206` |
| .agents/skills/archify/renderers/workflow/README.md | 本機引用路徑掃描，未逐條語意驗證 | `7e1bd65cc5cc38206304ae2f61f4f0f493da98d71a111a61d0754c9da362c5c9` |
| .agents/skills/archify/schemas/README.md | 本機引用路徑掃描，未逐條語意驗證 | `f4ca94ec18cf60ad02211f2c5bb64e9c26a87467a22215e06db34dbfc5d6145f` |
| .agents/skills/archify/scripts/generate-validators.mjs | 版本／結構盤點，未完整語意查核 | `a5f5f67d3cd4675b16fa620043a5463f3c15aad89afb1b0c7cf42cf35e883f9a` |
| .agents/skills/code-review/SKILL.md | 入口／政策／引用／同名差異掃描 | `21a2ea582f69452eb13aef6ac072b3b44ad0e3e9b4fd42c1bcc72ad367ffd64b` |
| .agents/skills/code-review/agents/openai.yaml | 內容／定點主張查核 | `8229ca854e11dc8e6aef2131ee03f31fb1561cf905fab9ccc325180cf3331352` |
| .agents/skills/code-review/references/review-surface.md | 本機引用路徑掃描，未逐條語意驗證 | `8a85a4c34990bef206b522a6ffbab37ae185557ae3d936d5f138aa65432835cd` |
| .agents/skills/code-review/references/smell-baseline.md | 本機引用路徑掃描，未逐條語意驗證 | `e30141db30d50f41113abcf29baec544fabaf4f743dc69f0a1943bccae2bd213` |
| .agents/skills/codebase-design/DEEPENING.md | 本機引用路徑掃描，未逐條語意驗證 | `f3dd099ce99289bd213914d8ee3e2429b78309c3957ca4583f7659551b1d53c1` |
| .agents/skills/codebase-design/DESIGN-IT-TWICE.md | 本機引用路徑掃描，未逐條語意驗證 | `8e740bf98446dbd4dfdc132ac4346d9a7eedaf93de6a495889171cf7f99f16bd` |
| .agents/skills/codebase-design/SKILL.md | 入口／政策／引用／同名差異掃描 | `2c20617f87ec8af6a434859f381b2f061a69b530444e74eb39e78bb016a6d1e2` |
| .agents/skills/codebase-design/agents/openai.yaml | 內容／定點主張查核 | `edebc9e4fcfe102114012575eaa9600b9b5fd08c311664f389c36e7bc717740f` |
| .agents/skills/diagnosing-bugs/SKILL.md | 入口／政策／引用／同名差異掃描 | `77f3cf31bc99b2f49af943222526531fcc9fc41d047626d3640e875e85af3e84` |
| .agents/skills/diagnosing-bugs/agents/openai.yaml | 內容／定點主張查核 | `3e430dbe4334a87597488c060cb3dc3786bb00c9182877d6f5ec41f62490e90b` |
| .agents/skills/domain-modeling/ADR-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `944c92aa790e8fbdc9199640b170979abb8a34ba8d0fe18c2a01a63bce140ca0` |
| .agents/skills/domain-modeling/CONTEXT-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `17ab16ce783e4d2801ee52fd9acdf550cbf44de65ae76797a93943bbedf22a13` |
| .agents/skills/domain-modeling/SKILL.md | 入口／政策／引用／同名差異掃描 | `327a2b50620e2fd70abc6893cd6965e76b20f8d0adb0dc2c8d5eb3845efb643e` |
| .agents/skills/domain-modeling/agents/openai.yaml | 內容／定點主張查核 | `f6bf2aa996c6e6f53fdd0708e18a0d16a56aed8322cca59fedbe3c0d2c75f06b` |
| .agents/skills/egm-drift-report/SKILL.md | 內容／定點主張查核 | `a340b35f51d80f91a4e90ec67284cc6a72c77c48877920b12c43a447f4a9d1ca` |
| .agents/skills/egm-drift-report/agents/openai.yaml | 內容／定點主張查核 | `a1499d95abd8447558c535fe5554adcc3c9b988a0a39264a6283d430effe1e94` |
| .agents/skills/evidence-report/SKILL.md | 入口／政策／引用／同名差異掃描 | `d3469822af2746394f7fcbd7629204f321bf295956fbffc20d1e0ddcad0d68bd` |
| .agents/skills/evidence-report/agents/openai.yaml | 內容／定點主張查核 | `8619a54e8c098122a7f3881394f84ca89b684366e848233a29ad18b6ec363935` |
| .agents/skills/grill-me/SKILL.md | 入口／政策／引用／同名差異掃描 | `e0a2070992b1ed7f4d4d8504e0fae0cf9c96c8bab4dd50c37989b0f4c7ff1010` |
| .agents/skills/grill-me/agents/openai.yaml | 內容／定點主張查核 | `c061e39c3e0f9d865fb1b97556d485704af2a8a58f4b8221a8917a5c2074a32b` |
| .agents/skills/grill-with-docs/SKILL.md | 入口／政策／引用／同名差異掃描 | `fc6401cbf34f1f3b6cb5e97253e25671d822733fc3f985117fe0d162639abf61` |
| .agents/skills/grill-with-docs/agents/openai.yaml | 內容／定點主張查核 | `94cd0ab161fb468a836349f5ed482ba58ce8e709a05c57ce533d739dbd35cca9` |
| .agents/skills/grilling/SKILL.md | 入口／政策／引用／同名差異掃描 | `ddad6f07e4883861d3c0ca3e017a755dc426801ca269c1beae38e1f2171ac473` |
| .agents/skills/grilling/agents/openai.yaml | 內容／定點主張查核 | `1411d7df7d99b7e621a1ff8283c8133cc2464be63d064e52d8ce169c6800ee9b` |
| .agents/skills/handoff/SKILL.md | 內容／定點主張查核 | `e6961a3339556d9453ce8acd4fbe29ea23aa853934e2a1ddf1ff8110f8bfc5b3` |
| .agents/skills/handoff/agents/openai.yaml | 內容／定點主張查核 | `5c479fd562c691851690e8b18c8501045bef0943c10743d636b2fae26add1d28` |
| .agents/skills/i-have-adhd/SKILL.md | 入口／政策／引用／同名差異掃描 | `78b25f611a660d350c9516da77152384b7d541f100b353d40c2dcae10de6268f` |
| .agents/skills/i-have-adhd/agents/openai.yaml | 內容／定點主張查核 | `2c51291283dcefdca43ca6b0c08172f225c7c26a9783ec444d6bdfa51ca96f8f` |
| .agents/skills/implement/SKILL.md | 內容／定點主張查核 | `026bca7fac4522aa59107c4209b16f3cd420654bf1d543202c68083525b76096` |
| .agents/skills/implement/agents/openai.yaml | 內容／定點主張查核 | `8970a8596ade0c28ab427f41a4ea242d6bdf6186c59ebf55e1238dbecaab79dc` |
| .agents/skills/improve-codebase-architecture/HTML-REPORT.md | 本機引用路徑掃描，未逐條語意驗證 | `581e8bb5a521e46bbda8ca7e19b15948bed882187108092ebb90c62513b77528` |
| .agents/skills/improve-codebase-architecture/SKILL.md | 入口／政策／引用／同名差異掃描 | `7f56f1ddbdec147b6f7ebc92c549d9ad98d846c5abe208e4857da14df2589c8b` |
| .agents/skills/improve-codebase-architecture/agents/openai.yaml | 內容／定點主張查核 | `c8cb20f68ebf0edb4e497bc11ae5fcaa196004e661cd189015b04f4109ced7f1` |
| .agents/skills/init-template/SKILL.md | 內容／定點主張查核 | `0bd98803e9ec75a6cb7a7831256c271b3195aea2dc8c62a37b298846b24df500` |
| .agents/skills/init-template/agents/openai.yaml | 內容／定點主張查核 | `8619a54e8c098122a7f3881394f84ca89b684366e848233a29ad18b6ec363935` |
| .agents/skills/prototype/LOGIC.md | 本機引用路徑掃描，未逐條語意驗證 | `f61c7d249e786a79ef289018901c348271e1798dd0b0bc5607b5c6f4d4a01ab9` |
| .agents/skills/prototype/SKILL.md | 入口／政策／引用／同名差異掃描 | `714de632d116bb73f65cdb5a882db15b9369a6713b9a47c0fad827848f0bfbe3` |
| .agents/skills/prototype/UI.md | 本機引用路徑掃描，未逐條語意驗證 | `723211e878acbc7b6ff09755263f3295cde724ba902ff0064da41eed51d45ad3` |
| .agents/skills/prototype/agents/openai.yaml | 內容／定點主張查核 | `5af65e43ab41a350436697b81e27b7f848d36782043b73c322bb2c9fa9cc55dc` |
| .agents/skills/research/SKILL.md | 內容／定點主張查核 | `985569f15739c713d6784887c3d186d4ef9ac85bec5ad9c068d25bf0739928e4` |
| .agents/skills/research/agents/openai.yaml | 內容／定點主張查核 | `9b4c470d63221c1f68f22df70b83e2f12401b317babe0d1b7b5f24a974474d0d` |
| .agents/skills/resolving-merge-conflicts/SKILL.md | 入口／政策／引用／同名差異掃描 | `9d8114f8ef0b31f535a265fc05c364bd8cf2e2895a830040e06c22acb11f54b0` |
| .agents/skills/resolving-merge-conflicts/agents/openai.yaml | 內容／定點主張查核 | `a1f4f96838f2ed6282eb28abbbf99029cb8fadce552baf53da90a025b8bffddf` |
| .agents/skills/security-review/SKILL.md | 入口／政策／引用／同名差異掃描 | `c7a056cdbf74a8e6952f4e535a05acd5ef5bd857bce18372c77b7b4c33636c93` |
| .agents/skills/security-review/agents/openai.yaml | 內容／定點主張查核 | `8619a54e8c098122a7f3881394f84ca89b684366e848233a29ad18b6ec363935` |
| .agents/skills/security-review/references/upstream-security-review.md | 本機引用路徑掃描，未逐條語意驗證 | `dd1d451f909dbb8798f4a4de010c35e7dd9152f02bb2f7988442cdd138f29e39` |
| .agents/skills/setup-matt-pocock-skills/SKILL.md | 內容／定點主張查核 | `148b0d20265200bfdaf17e8fe6b326a733d493e113d26b436f373a1b6c9dff4a` |
| .agents/skills/setup-matt-pocock-skills/agents/openai.yaml | 內容／定點主張查核 | `9527de0110541c45712319025155aeab8dc7d77c6ed6e5e83271bab1851ab939` |
| .agents/skills/setup-matt-pocock-skills/domain.md | 本機引用路徑掃描，未逐條語意驗證 | `edc6d6131fdffc4b7135704f5262124fc43355c95f61b7399dc5a4db643e28ca` |
| .agents/skills/setup-matt-pocock-skills/issue-tracker-github.md | 本機引用路徑掃描，未逐條語意驗證 | `afd6852a80185217bd28aa5cbe456bef1e85be25be7bd1fba382d5b8ee428325` |
| .agents/skills/setup-matt-pocock-skills/issue-tracker-gitlab.md | 本機引用路徑掃描，未逐條語意驗證 | `ea175f73d193b3f55819c0ed9bbccf6ee0e70ad8f928e3d7607596c53380acd6` |
| .agents/skills/setup-matt-pocock-skills/issue-tracker-local.md | 本機引用路徑掃描，未逐條語意驗證 | `7dcda20a2eb4bdc89b95d1143423c0691309921cadae3132e6424f371030506e` |
| .agents/skills/setup-matt-pocock-skills/triage-labels.md | 本機引用路徑掃描，未逐條語意驗證 | `4f53c9b40ce2651e3611aa090eaedbd6dbc9b71ef8c5f7e65eac0d8263190d0d` |
| .agents/skills/tdd/SKILL.md | 入口／政策／引用／同名差異掃描 | `08a43d1e605501d7fb3eeda0cfe9ad2236fab560df039abc63e351bc9340f4a2` |
| .agents/skills/tdd/agents/openai.yaml | 內容／定點主張查核 | `ea6f01cf1b8c06a4b0f5b649d74b1b8ce8685e72af1b38d70d877693e092af0b` |
| .agents/skills/tdd/mocking.md | 本機引用路徑掃描，未逐條語意驗證 | `3ceb807fdf4a47d6a93d4d9a891e5ba6d362a6247bd08adc451feebfc17361ef` |
| .agents/skills/tdd/tests.md | 本機引用路徑掃描，未逐條語意驗證 | `859f9e592c188fda4fc7277dd180e4ce9c7a2e13f6efe1f6f29eccc9d28c106a` |
| .agents/skills/teach/GLOSSARY-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `9b99859ec28437668130d8f2ce5a342938970f8a1ed4fd38c3eab4f4b5fff210` |
| .agents/skills/teach/LEARNING-RECORD-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `701fa34b6748aa89e6c960ffb815257f481a7d77fb2900f9028f7edf3fdd6052` |
| .agents/skills/teach/MISSION-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `8cacbb3c0644d3ae0ea4965564797099401a6930a23f7cf462918576587f2418` |
| .agents/skills/teach/RESOURCES-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `e9cacf34026e11a8d1c8f9de88abe5bcbf654f4ebdb25cae8c0de0d5f48f44ec` |
| .agents/skills/teach/SKILL.md | 入口／政策／引用／同名差異掃描 | `371f690f80f316826997a07dbd8f8a423cb66b8d97ecef0ef21a91928725c992` |
| .agents/skills/teach/agents/openai.yaml | 內容／定點主張查核 | `5856f3ae8aec742f1499c640aecdd5f1d6af5fa210a7c6ec794de8263a6f733f` |
| .agents/skills/to-questionnaire/SKILL.md | 入口／政策／引用／同名差異掃描 | `f6f8227600d4ccf60ac4f39a27baea1d5a73bbcca3864e11a9e3b3c0ef3e077f` |
| .agents/skills/to-questionnaire/agents/openai.yaml | 內容／定點主張查核 | `9e8a06c38c8842eea8d4922cb9d1ead8e3ace647bab259b943c994a1b4742bc2` |
| .agents/skills/to-spec/SKILL.md | 內容／定點主張查核 | `be9df70fa2ad16fdd51e938a44da057e5f52e2b3d0e69854d9061871aac99e0d` |
| .agents/skills/to-spec/agents/openai.yaml | 內容／定點主張查核 | `1c5b4d1e3d8e52287ef19cc2742fdbbfae1914ac75d33af3e4c8174f08cc55bb` |
| .agents/skills/to-tickets/SKILL.md | 內容／定點主張查核 | `611ff3528bbf210d964c794f1994c0343b03e27be9bacc70794727d1104a7f06` |
| .agents/skills/to-tickets/agents/openai.yaml | 內容／定點主張查核 | `21bc6215fffcd7614e9f772bb1760e87cc5fc7dcc707e7d282bc9414267a6090` |
| .agents/skills/tune-skills/SKILL.md | 內容／定點主張查核 | `9766735760cc0f08fcd1526ac2dcb02cffaa65ac861ab66b6bffd9c45a00ed1a` |
| .agents/skills/tune-skills/agents/openai.yaml | 內容／定點主張查核 | `a1499d95abd8447558c535fe5554adcc3c9b988a0a39264a6283d430effe1e94` |
| .agents/skills/tune-skills/references/gpt-6.md | 本機引用路徑掃描，未逐條語意驗證 | `9e4b474bf557568f2e404c3f263b6cad208366f1f006f47a966ee8c73c5ac9a4` |
| .agents/skills/tw-emoji-commit/SKILL.md | 入口／政策／引用／同名差異掃描 | `9beaaf2e191ae18e7801775740b51279d57dd142383831c5589c2cb0c6e853b9` |
| .agents/skills/tw-emoji-commit/agents/openai.yaml | 內容／定點主張查核 | `8619a54e8c098122a7f3881394f84ca89b684366e848233a29ad18b6ec363935` |
| .agents/skills/tw-emoji-commit/scripts/sanitize_commit.py | 內容／定點主張查核 | `4e8503cc9e53ccc28f358e6f4a328168dda3d93e308d138f2c95a776a707e7f0` |
| .agents/skills/tw-emoji-pr-note/SKILL.md | 入口／政策／引用／同名差異掃描 | `47c8c03b2f13f96850b12e5b3d0caaaf3b1afab9ace5121576447cae7840e055` |
| .agents/skills/tw-emoji-pr-note/agents/openai.yaml | 內容／定點主張查核 | `8619a54e8c098122a7f3881394f84ca89b684366e848233a29ad18b6ec363935` |
| .agents/skills/tw-emoji-pr-note/scripts/sanitize_pr_note.py | 內容／定點主張查核 | `4e8503cc9e53ccc28f358e6f4a328168dda3d93e308d138f2c95a776a707e7f0` |
| .agents/skills/tw-emoji-release-note/SKILL.md | 入口／政策／引用／同名差異掃描 | `f5af62383d8f4df8e5290818507629d1ce2d30dca6d221b69ada5b8436e981a7` |
| .agents/skills/tw-emoji-release-note/agents/openai.yaml | 內容／定點主張查核 | `8619a54e8c098122a7f3881394f84ca89b684366e848233a29ad18b6ec363935` |
| .agents/skills/tw-emoji-release-note/scripts/sanitize_release_note.py | 內容／定點主張查核 | `4e8503cc9e53ccc28f358e6f4a328168dda3d93e308d138f2c95a776a707e7f0` |
| .agents/skills/wait-what/SKILL.md | 入口／政策／引用／同名差異掃描 | `3ec28b97e0783fe49ea89f5a016e622396b9ab9c5704916d3a26b52ed9dac01a` |
| .agents/skills/wait-what/agents/openai.yaml | 內容／定點主張查核 | `b41faadf741d51e4ea184148b2d1854d93f947aaf754c7844f70a00f04194999` |
| .agents/skills/wayfinder/SKILL.md | 入口／政策／引用／同名差異掃描 | `d6cebf5a9714865037dc3a379d687b19e5c6aeb09e34c708b58e78101e558d99` |
| .agents/skills/wayfinder/agents/openai.yaml | 內容／定點主張查核 | `88bc81a11a6d52ac67aeaa76b8b619e387020d47c5133a4dd4927fd15c4ad073` |
| .agents/skills/wizard/SKILL.md | 入口／政策／引用／同名差異掃描 | `bdf31d48211ea559878f95a4f344aeabf8d85897488ba564382bab0b000daac1` |
| .agents/skills/wizard/agents/openai.yaml | 內容／定點主張查核 | `98f44d682d58e262f160dc59a8befc365e0aa65820dd0261864af26aa8e59d83` |
| .agents/skills/writing-for-agents/SKILL-MECHANICS.md | 本機引用路徑掃描，未逐條語意驗證 | `19236d48d89016ec5ef83ef40ea380e8e532061319286931f82ad03ac5e25141` |
| .agents/skills/writing-for-agents/SKILL.md | 入口／政策／引用／同名差異掃描 | `551adca942227b44192edba88acd4e8db911f0121ce58ad16944ccf6a896a74a` |
| .agents/skills/writing-for-agents/agents/openai.yaml | 內容／定點主張查核 | `eacb24b2a618cfb81dacb0416f4fdd75ddf3a8060f8ddb99aae1b1e301907e4b` |
| .claude/agents/harness-challenger.md | 內容／定點主張查核 | `80dcfe68c3bc53aa5cb1a01aa7556c0076aeb122951c1489899f24b7a90f7819` |
| .claude/agents/harness-executor.md | 內容／定點主張查核 | `62bdd2bb648a0926bcbd0d69dab335a8e102ac7d285b4740b1dbfe3ef4cce147` |
| .claude/agents/harness-researcher.md | 內容／定點主張查核 | `44802eb27c6a2e67627c9ff8d6f2e698005a575e116d7faf2a516b3759758963` |
| .claude/agents/harness-reviewer.md | 內容／定點主張查核 | `8e7968d9510871eb1f341c8358ca54b78668f12db786e02c2e1c7a2729409e9d` |
| .claude/skills/agent-browser/SKILL.md | 內容／定點主張查核 | `201db858af5f3a3bebb8e7f2b6f5467f3304e021c675deda3768cdc773b1898c` |
| .claude/skills/archify/SKILL.md | 入口／政策／引用／同名差異掃描 | `2ebe295ff478c95e30717ec7e161d3ff83421a05a04d8c6990619415af2a6b30` |
| .claude/skills/archify/THIRD_PARTY_NOTICES.md | 本機引用路徑掃描，未逐條語意驗證 | `0b7fb59365dc21c93b0f62526d74ee913aeec9ae532c112bc76afa7edcd56e14` |
| .claude/skills/archify/bin/open-artifact.mjs | 版本／結構盤點，未完整語意查核 | `e58b51af0bd37ef3bff980a0145d3130f56324bec5a7efd4fbaf9959b1176edf` |
| .claude/skills/archify/bin/preview.mjs | 版本／結構盤點，未完整語意查核 | `aac5c4e796fc31a0f0ae7fa2267106ff125bea8d2d7628806034f57a25176f1d` |
| .claude/skills/archify/brand-marks/README.md | 本機引用路徑掃描，未逐條語意驗證 | `8b771a16322ce9ea47fdc00b9935e33adf0f3af608f2d735235443e15ef622e2` |
| .claude/skills/archify/package-lock.json | 版本／結構盤點，未完整語意查核 | `12a357be1940c31c0f9d3d592b6a8abb2a43d7bc67bf1d4a216e69395d26786d` |
| .claude/skills/archify/package.json | 版本／結構盤點，未完整語意查核 | `6b912a553d168d78adbb71825ad60a58b33abec1c0b834890bd25ed7416bf759` |
| .claude/skills/archify/references/authoring-contract.md | 本機引用路徑掃描，未逐條語意驗證 | `873494557cf9be91d9eed8ecce37072886c0e98b851ad59ab8938f405c6fbc5e` |
| .claude/skills/archify/references/brand-marks.md | 本機引用路徑掃描，未逐條語意驗證 | `8010869da70677e686ecb312d9c3eec2d20723a44f817ab2bbf5525361c8a136` |
| .claude/skills/archify/references/delivery-contract.md | 本機引用路徑掃描，未逐條語意驗證 | `551ceb3c22fb6220072ce4a9532b073c13528fbb5383fb396c36c7182b6fe680` |
| .claude/skills/archify/references/viewer-runtime.md | 本機引用路徑掃描，未逐條語意驗證 | `dc0d9ffe6b9987d73d2d48710fce5ab4c120bbf1940ff1eb9355259c5d4f32b6` |
| .claude/skills/archify/renderers/dataflow/README.md | 本機引用路徑掃描，未逐條語意驗證 | `18c4f86ba62fcee371d9fe38094625b3a68cc76231c36ab8c8124acb4c1ffa42` |
| .claude/skills/archify/renderers/lifecycle/README.md | 本機引用路徑掃描，未逐條語意驗證 | `f8ef88dc859189bb18bad7bb2e27d997cbc9d30936cf20f8bf401bae7f57deec` |
| .claude/skills/archify/renderers/sequence/README.md | 本機引用路徑掃描，未逐條語意驗證 | `a442335dcf44b1587d3ad88809e31b001a4fafdf7a134040e8b1927455af4206` |
| .claude/skills/archify/renderers/workflow/README.md | 本機引用路徑掃描，未逐條語意驗證 | `7e1bd65cc5cc38206304ae2f61f4f0f493da98d71a111a61d0754c9da362c5c9` |
| .claude/skills/archify/schemas/README.md | 本機引用路徑掃描，未逐條語意驗證 | `d25d4e6e44486b6cad4737cca9a126184f1fcb61ec405844d66058f8486b4a6b` |
| .claude/skills/archify/scripts/generate-validators.mjs | 版本／結構盤點，未完整語意查核 | `a5f5f67d3cd4675b16fa620043a5463f3c15aad89afb1b0c7cf42cf35e883f9a` |
| .claude/skills/code-review/SKILL.md | 入口／政策／引用／同名差異掃描 | `498361f5b752eb73428ad054ccfcfbf16f5d3e2d43c0ebe916ef4e738a3ce970` |
| .claude/skills/code-review/references/review-surface.md | 本機引用路徑掃描，未逐條語意驗證 | `8a85a4c34990bef206b522a6ffbab37ae185557ae3d936d5f138aa65432835cd` |
| .claude/skills/code-review/references/smell-baseline.md | 本機引用路徑掃描，未逐條語意驗證 | `e30141db30d50f41113abcf29baec544fabaf4f743dc69f0a1943bccae2bd213` |
| .claude/skills/codebase-design/DEEPENING.md | 本機引用路徑掃描，未逐條語意驗證 | `f3dd099ce99289bd213914d8ee3e2429b78309c3957ca4583f7659551b1d53c1` |
| .claude/skills/codebase-design/DESIGN-IT-TWICE.md | 本機引用路徑掃描，未逐條語意驗證 | `d1c86774592564d610695d5c849dd80055afedb3bb3ee2c286706b898bdc5cfd` |
| .claude/skills/codebase-design/SKILL.md | 入口／政策／引用／同名差異掃描 | `2c20617f87ec8af6a434859f381b2f061a69b530444e74eb39e78bb016a6d1e2` |
| .claude/skills/diagnosing-bugs/SKILL.md | 入口／政策／引用／同名差異掃描 | `c584b6d5daf047cc6f8c0b67d69648e19d3d872002a01acb394470f2560712fc` |
| .claude/skills/domain-modeling/ADR-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `944c92aa790e8fbdc9199640b170979abb8a34ba8d0fe18c2a01a63bce140ca0` |
| .claude/skills/domain-modeling/CONTEXT-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `17ab16ce783e4d2801ee52fd9acdf550cbf44de65ae76797a93943bbedf22a13` |
| .claude/skills/domain-modeling/SKILL.md | 入口／政策／引用／同名差異掃描 | `327a2b50620e2fd70abc6893cd6965e76b20f8d0adb0dc2c8d5eb3845efb643e` |
| .claude/skills/egm-drift-report/SKILL.md | 入口／政策／引用／同名差異掃描 | `935906fefd93005855de89818f947a6a33644e28737bb4b9ae69befc1717fb0f` |
| .claude/skills/evidence-report/SKILL.md | 入口／政策／引用／同名差異掃描 | `0a9256df141b2ab7adf2ec22bcdbbf1df75c282d661b6ba821b33293ffd2d1f7` |
| .claude/skills/grill-me/SKILL.md | 入口／政策／引用／同名差異掃描 | `caaf8b8de1684f96e26b28f3c29189db5c89cce4b73e1c93d86164f66ef88637` |
| .claude/skills/grill-with-docs/SKILL.md | 入口／政策／引用／同名差異掃描 | `7de372c13488f1ee96cc11cd8907b56b6809cc93eef776eeddd37de6b6cbe3fe` |
| .claude/skills/grilling/SKILL.md | 入口／政策／引用／同名差異掃描 | `d9ed7c64655d7f81014022a5782ff1f1da1c6100c92ab28ef9bd110a2776baa9` |
| .claude/skills/handoff/SKILL.md | 入口／政策／引用／同名差異掃描 | `99ebde4654139e6fd72d9e5e9534c8ace28cfd29e98ffcc524b1443d2c51480d` |
| .claude/skills/i-have-adhd/SKILL.md | 入口／政策／引用／同名差異掃描 | `67268928e74fe581ebfa764c7f0d9c9cfd7a5d00d43a0fac88547034b7fbf68d` |
| .claude/skills/implement/SKILL.md | 入口／政策／引用／同名差異掃描 | `9cf1a58552064cba2f8c6758e918033893def2ca408b4b3443f79b7c6db615c5` |
| .claude/skills/improve-codebase-architecture/HTML-REPORT.md | 本機引用路徑掃描，未逐條語意驗證 | `7253a9687478f59547d83e1b67536eced1ae83293382d2c92f3fe2ec323aa813` |
| .claude/skills/improve-codebase-architecture/SKILL.md | 入口／政策／引用／同名差異掃描 | `6fd7cbdf07928939735e5ba5323b1dc2e276dd80e460bfb644e5f3264a6edcce` |
| .claude/skills/init-template/SKILL.md | 內容／定點主張查核 | `a607bf78cf3a81c59f2692341aa66617c1b237d2676b007db33a018f9ba7ab22` |
| .claude/skills/prototype/LOGIC.md | 本機引用路徑掃描，未逐條語意驗證 | `858e249605e2fce1d02ee949c5e38ef7e2fce57ccc259948285606d030abaa17` |
| .claude/skills/prototype/SKILL.md | 入口／政策／引用／同名差異掃描 | `714de632d116bb73f65cdb5a882db15b9369a6713b9a47c0fad827848f0bfbe3` |
| .claude/skills/prototype/UI.md | 本機引用路徑掃描，未逐條語意驗證 | `8f469840ad94e385768410d8b70e205666b92588d70dab3ccc510a0243654aef` |
| .claude/skills/research/SKILL.md | 內容／定點主張查核 | `cfd580d0dd307c92ff24ac3cb3d2df1ff77f5bf9a9af947cb7610a17f7fcbbda` |
| .claude/skills/resolving-merge-conflicts/SKILL.md | 入口／政策／引用／同名差異掃描 | `9d8114f8ef0b31f535a265fc05c364bd8cf2e2895a830040e06c22acb11f54b0` |
| .claude/skills/security-review/SKILL.md | 入口／政策／引用／同名差異掃描 | `9fe2681708bd833ac214b561993ba203d8747824ef29ea37d52b58c37f4958d3` |
| .claude/skills/security-review/references/upstream-security-review.md | 本機引用路徑掃描，未逐條語意驗證 | `dd1d451f909dbb8798f4a4de010c35e7dd9152f02bb2f7988442cdd138f29e39` |
| .claude/skills/setup-matt-pocock-skills/SKILL.md | 入口／政策／引用／同名差異掃描 | `7f9c07fce06b08b54bd1a283f8c83d1ea9faee7c38ba4cc946aa6439b7b421fb` |
| .claude/skills/setup-matt-pocock-skills/domain.md | 本機引用路徑掃描，未逐條語意驗證 | `edc6d6131fdffc4b7135704f5262124fc43355c95f61b7399dc5a4db643e28ca` |
| .claude/skills/setup-matt-pocock-skills/issue-tracker-github.md | 本機引用路徑掃描，未逐條語意驗證 | `afd6852a80185217bd28aa5cbe456bef1e85be25be7bd1fba382d5b8ee428325` |
| .claude/skills/setup-matt-pocock-skills/issue-tracker-gitlab.md | 本機引用路徑掃描，未逐條語意驗證 | `ea175f73d193b3f55819c0ed9bbccf6ee0e70ad8f928e3d7607596c53380acd6` |
| .claude/skills/setup-matt-pocock-skills/issue-tracker-local.md | 本機引用路徑掃描，未逐條語意驗證 | `7dcda20a2eb4bdc89b95d1143423c0691309921cadae3132e6424f371030506e` |
| .claude/skills/setup-matt-pocock-skills/triage-labels.md | 本機引用路徑掃描，未逐條語意驗證 | `4f53c9b40ce2651e3611aa090eaedbd6dbc9b71ef8c5f7e65eac0d8263190d0d` |
| .claude/skills/tdd/SKILL.md | 入口／政策／引用／同名差異掃描 | `08a43d1e605501d7fb3eeda0cfe9ad2236fab560df039abc63e351bc9340f4a2` |
| .claude/skills/tdd/mocking.md | 本機引用路徑掃描，未逐條語意驗證 | `3ceb807fdf4a47d6a93d4d9a891e5ba6d362a6247bd08adc451feebfc17361ef` |
| .claude/skills/tdd/tests.md | 本機引用路徑掃描，未逐條語意驗證 | `859f9e592c188fda4fc7277dd180e4ce9c7a2e13f6efe1f6f29eccc9d28c106a` |
| .claude/skills/teach/GLOSSARY-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `9b99859ec28437668130d8f2ce5a342938970f8a1ed4fd38c3eab4f4b5fff210` |
| .claude/skills/teach/LEARNING-RECORD-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `701fa34b6748aa89e6c960ffb815257f481a7d77fb2900f9028f7edf3fdd6052` |
| .claude/skills/teach/MISSION-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `8cacbb3c0644d3ae0ea4965564797099401a6930a23f7cf462918576587f2418` |
| .claude/skills/teach/RESOURCES-FORMAT.md | 本機引用路徑掃描，未逐條語意驗證 | `e9cacf34026e11a8d1c8f9de88abe5bcbf654f4ebdb25cae8c0de0d5f48f44ec` |
| .claude/skills/teach/SKILL.md | 入口／政策／引用／同名差異掃描 | `690d74d52ef3f12024d08385d2ad4a865869e072e57b93a0aae665ab5fa7ccce` |
| .claude/skills/to-questionnaire/SKILL.md | 入口／政策／引用／同名差異掃描 | `b5eb929842ee0e93d867c5e906d183d350f2f2d149eaeaa86967d94d8eda1d3b` |
| .claude/skills/to-spec/SKILL.md | 內容／定點主張查核 | `35746bd77ae77df3f091ae64a486854d98ec033b07da7299c0c6a08972e63cd9` |
| .claude/skills/to-tickets/SKILL.md | 入口／政策／引用／同名差異掃描 | `9d91e5d42dfa88b688f31dddfa001ca04c00e82d26f7efe381b1bf6803a2b462` |
| .claude/skills/tune-skills/SKILL.md | 入口／政策／引用／同名差異掃描 | `63053ad50356bbc3f2e354c3873a66b0d43e7ddbce524b920816c2a6486dddf1` |
| .claude/skills/tw-emoji-commit/SKILL.md | 入口／政策／引用／同名差異掃描 | `f929532e2a1cfaf5755676946b2d0312e271bd2c50f2c63f7ebf49ec46e4910a` |
| .claude/skills/tw-emoji-commit/scripts/sanitize_commit.py | 版本／結構盤點，未完整語意查核 | `4e8503cc9e53ccc28f358e6f4a328168dda3d93e308d138f2c95a776a707e7f0` |
| .claude/skills/tw-emoji-pr-note/SKILL.md | 入口／政策／引用／同名差異掃描 | `2e2c3a5387cbf8ad30b5a0734bea0c539f8fde32e8cacd01f781acf01d744945` |
| .claude/skills/tw-emoji-pr-note/scripts/sanitize_pr_note.py | 版本／結構盤點，未完整語意查核 | `4e8503cc9e53ccc28f358e6f4a328168dda3d93e308d138f2c95a776a707e7f0` |
| .claude/skills/tw-emoji-release-note/SKILL.md | 入口／政策／引用／同名差異掃描 | `cfe6c3ffe578a9353411db39d256a32c70a3f8d0412f5d4e005bb6b4b933edc5` |
| .claude/skills/tw-emoji-release-note/scripts/sanitize_release_note.py | 版本／結構盤點，未完整語意查核 | `4e8503cc9e53ccc28f358e6f4a328168dda3d93e308d138f2c95a776a707e7f0` |
| .claude/skills/wait-what/SKILL.md | 入口／政策／引用／同名差異掃描 | `e3f44e3ccbc0e7b62f20ba70b295fc9c9f4aa3f96c77168faee1c71bacbf4215` |
| .claude/skills/wayfinder/SKILL.md | 入口／政策／引用／同名差異掃描 | `44d3bb9f5a06c2f69141b8174c3244a2aa9d424d4b241eeb6f4563c063b95346` |
| .claude/skills/wizard/SKILL.md | 入口／政策／引用／同名差異掃描 | `bdf31d48211ea559878f95a4f344aeabf8d85897488ba564382bab0b000daac1` |
| .claude/skills/writing-for-agents/SKILL-MECHANICS.md | 本機引用路徑掃描，未逐條語意驗證 | `49e114d953fb9a15f2f760ae8c3168ceb962089d83df95bd55dc815ccde250c3` |
| .claude/skills/writing-for-agents/SKILL.md | 入口／政策／引用／同名差異掃描 | `61d16241d750bb4d2f5116712afb030588ddea8863462cd8b6d3491ff9569cdb` |
| .codex/agents/harness-researcher.toml | 內容／定點主張查核 | `060090fb8724cb5316259721d8404716e4d8d46ea14cbf44c237cc5f901fdcca` |
| .codex/agents/harness-reviewer.toml | 內容／定點主張查核 | `646bed10563615475ad4b0594cb14cae335a1d6523c0deaf59154045d6bb4d56` |
| .codex/config.toml | 內容／定點主張查核 | `79d32bc214f44f5d0e06b171024a0140dbc1b816c9b34784225e4bbdd390314e` |
| .gitattributes | 內容／定點主張查核 | `a595010607d6619522440b62bd23e4131f8b46171f2f3ffdb6ca48c1d102f212` |
| .github/workflows/build-release.yml | 內容／定點主張查核 | `4a40c77f2f7f6c44f54be4ee49816ea764ea4744d73f072addb36f5ecf97533a` |
| .github/workflows/publish-npm.yml | 內容／定點主張查核 | `a76faa8887fed48dd4661491a6b39d5abf63009548098eca18ad766f6012a5e0` |
| .github/workflows/publish-pypi.yml | 內容／定點主張查核 | `ad41f6522902850101053a88c5ca38d271e29c485d66bde714329827eca430fc` |
| .github/workflows/verify.yml | 內容／定點主張查核 | `6fa7fd85bd5ade43e47459566133934d3d04d13c32738a9e56782c97b7ac6582` |
| .gitignore | 內容／定點主張查核 | `ec13005b749dc300455df6af9a30f0309a76f189d26d642d54bdbb0e5bbec84d` |
| .tmpl.docs/CONTEXT.md | 內容／定點主張查核 | `af014f9442eb48543fbc33700d82a7489491eb8abfdd79f325bd9aa9a94b0816` |
| .tmpl.docs/README.md | 內容／定點主張查核 | `04e6257d103528ffbc233176597efedbeb8d5c79912ac440ea1adab304f2f71d` |
| .tmpl.docs/adoption.md | 內容／定點主張查核 | `8c2225f42db7ffb52d2f4c0116516d2bdc878f07d73fce1294de2933ccc72a7a` |
| .tmpl.docs/contributing.md | 內容／定點主張查核 | `1de563981c525c720f86206c872f6725f4ade50d63229377d3596bb33a87f38b` |
| .tmpl.docs/registry-publishing.md | 內容／定點主張查核 | `54b217b6637018eb4830aed3b7d8191ed1af2e09af6f5854f6c452a0c10ae3ba` |
| AGENTS.md | 內容／定點主張查核 | `d90eba47efbd06424eecc9c811068f2a9996717ca5c9acaae887ab4255e53950` |
| CLAUDE.md | 內容／定點主張查核 | `5b1487e0b660d0bb692073f558d73a7dfba1475a0bdd80c4d4f3350144b44d87` |
| INSTALL.md | 內容／定點主張查核 | `6c375ba65e984e45b7c99a9e7a0b2807c75ed58bd2ff2be0753b04871c641915` |
| README.en.md | 內容／定點主張查核 | `4d0b5852a62493c0b2f52b3dc32276fe45a28ff1871673c8a6abc6ff293a1c87` |
| README.md | 內容／定點主張查核 | `700e5b1d76bef7ecedd6e6194058e4587cd471f240befb8f3c0a8b261b8b1a8f` |
| THIRD_PARTY_NOTICES.md | 內容／定點主張查核 | `5b167b2449e9c74dcfe1b549b1a7d0a273d924f7e9af956c0e4f412bc3ee793a` |
| bin/create.cjs | 內容／定點主張查核 | `0f92f30feb71fb7f6669655a2b6a6c02716cdb40ce61bd2af0c1b27df40835c2` |
| bin/python.cjs | 內容／定點主張查核 | `98b85c093dbf80f4ecc59de41b46459596db9cb766378852a94eb329d951d754` |
| bootstrap/create-harness-project/SKILL.md | 內容／定點主張查核 | `8c351fffc4d7ce225a8555e395fc3f616b27d5d6fb612623e234c022f84fe495` |
| bootstrap/create-harness-project/agents/openai.yaml | 內容／定點主張查核 | `685f37fb9e2d8398885e20e2af396d10cb410b896e8c2a367bca72ed8d35e242` |
| docs/README.md | 內容／定點主張查核 | `61b43af0f156e645dd715a82a74e14d704f6f1ccff4e52073fc85ae650fb9c00` |
| docs/adr/0001-walking-skeleton-then-epic-loop.md | 內容／定點主張查核 | `916e752995b2997a610ca69564d788a681df0e50bb1016aed6b7e66b42f71288` |
| docs/adr/0002-ticket-status-in-frontmatter.md | 內容／定點主張查核 | `828ace6cb8ef748fe924afe210c66e664aa976241810ae4277aa945a6eb588a7` |
| docs/adr/0003-adversarial-review-fixed-axes-two-rounds.md | 內容／定點主張查核 | `cc714a74c0c5ca194f28d81fded9918078f150a60e2effbbb64a449b6f6d172d` |
| docs/adr/0004-fresh-context-spec-review.md | 內容／定點主張查核 | `1dc3898d3d7718478805c11b20467d843761bf58e6b80c8b7d70f2420131bb00` |
| docs/adr/0005-drift-diagnosis-native-host-verification.md | 內容／定點主張查核 | `016dac5a64bf52bcca0d142913cc0148af88dce5ca3fb1cf6eca2e08bf6c3c0b` |
| docs/agents/claude-orchestration.md | 內容／定點主張查核 | `dec4799eb7211323a0281b54cdd211ee254042c929ba15c7f8d49d7c6165f8ad` |
| docs/agents/codex.md | 內容／定點主張查核 | `20ab3a45cf34c28f7f4973c4c978aaba188674add1ecb2a585b1667605db1929` |
| docs/agents/domain.md | 內容／定點主張查核 | `a8787a7e5b90612009b44db690c66d32169505048f767a480bed389ce3d8ac84` |
| docs/agents/drift-report.md | 內容／定點主張查核 | `407d225e1d551ed14ecc6d0291ec491b442b82424ab7fd624d1eae4abbf62cd3` |
| docs/agents/issue-tracker.md | 內容／定點主張查核 | `baa7ee97b3fa6c880e5ee8aad112af3d6d3bbb071231bb0c71196f467e21f6dd` |
| docs/agents/language.md | 內容／定點主張查核 | `b3da5aee9cfcc3495f865f91f5f881aa925e2fe5641759be6ded17d46943af45` |
| docs/agents/review.md | 內容／定點主張查核 | `039fb97e77b5ac346c062356a26f7fd1d424a11df99f3b6f6a852f9967b4df43` |
| docs/agents/runtime.md | 內容／定點主張查核 | `1088214a9ae85f345251ce1b0c08382bddaaf604eda48287f3ada0f7557e4b15` |
| docs/agents/skill-sources.json | 版本／結構盤點，未完整語意查核 | `e7e0a15be3d13a72af17b71cfddf16831f10150e69059f256654c0794d18a496` |
| docs/agents/workflow.md | 內容／定點主張查核 | `b3c000482fc0c25c18615ce84271be6c196e34e834ed46454c7cc863eaadfae1` |
| docs/guide.md | 內容／定點主張查核 | `23c99bcce3472f745fc934fbf521c2e014d712839dcabfaf22b576f97bc5527f` |
| docs/security/archify-dependencies.md | 內容／定點主張查核 | `5aaf21da777e3e288f8a9070815de099c72f17d06c30bc73891283d05befa3d7` |
| docs/security/windows-opener.md | 內容／定點主張查核 | `4db0982d35c5060d490b5869c23c98b965336ff8ad0bd58ca1e541ebe1d5d52d` |
| harness_agile/__init__.py | 內容／定點主張查核 | `b59bb7d5d80fc28d0874687509c7f1ee5fbf839f1bc30264631768a371d8ded1` |
| harness_agile/__main__.py | 內容／定點主張查核 | `935a1c1166b0c1ea35a82256345000bf2c73ded718d77773bc27a71ecce28f7d` |
| harness_agile/bundle.py | 內容／定點主張查核 | `87acb74d2c71db0017af74583fc5ba0ecf4a783bbd60a8542e9e8714978e1981` |
| harness_agile/cli.py | 內容／定點主張查核 | `dfdf0d6190886bd04ebc80b771f86ee8a5a9c9d7a3d069fc56446b0b482f57e1` |
| hatch_build.py | 內容／定點主張查核 | `7f202629c53046e2550e39be3358fe056efad43e2211e9f3f51a5e20039a0d9f` |
| package.json | 內容／定點主張查核 | `b95b69a80835446a33d23c7b94748fbc78a2000f9e6fd33162c54a62398045ae` |
| pyproject.toml | 內容／定點主張查核 | `7f52c175fcf4d48c1c2701f0a9cc882725bed2cde3dfa0902ea6ba4a4f4023a9` |
| scripts/init-project.py | 內容／定點主張查核 | `c7de29ca503b96e2f672848eb5d588e55cde23f47707c45d70118aefab94e04d` |
| scripts/project-readme.md | 內容／定點主張查核 | `0c599067da1e61f37e1e33a80a839df86d9a9e43d1ff02d5174cdddb5c0245ee` |
| scripts/verify-distributions.py | 內容／定點主張查核 | `71ebb60c852f7a261cc09915d365d768cbf3f2c8c9bd1488ed223a965e157ee4` |
| scripts/verify-project.py | 內容／定點主張查核 | `1d6a8079e7f05d0416549f1d4a4e0e9b1f028ed3406180c82fbc6b8203d522f1` |
| skills-lock.json | 版本／結構盤點，未完整語意查核 | `9f587ca240ed81d3cc2f37a56974e76a6f4595e811f4c19959073de7cf11d66a` |
