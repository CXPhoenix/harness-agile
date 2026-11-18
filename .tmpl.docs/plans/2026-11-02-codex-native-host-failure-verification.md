# Codex 原生宿主與失敗情境驗證計畫

> 執行者：後續獲准執行時載入 `executing-plans`，依專案 runtime adapter、此計畫及核准測試表逐項處理。此文件不是執行授權。

**Goal:** 補足 v0.4.0 的 Codex 原生行為與失敗情境證據；記錄 Claude 缺口並延後，不修改現有產品或流程。

**Architecture:** 將 Stage 3 fresh reviewer、EGM 顯式診斷、控制端事件及 gate 判斷分開觀察。以隔離 fixture、新原生工作階段、實際工具事件及檔案雜湊核對驗證；無法安全注入或看見的情境保留 blocked／未驗證，不製造成功結果。

**Tech Stack:** Codex desktop 原生 collaboration API、Codex CLI、既有專案 skills／契約、Git、Python 標準函式庫；不新增正式 runner、套件相依、skill 或設定。

## 1．狀態、範圍與停止點

- 日期：2026-11-02（Asia/Taipei）。狀態：**計畫與測試表待核准；模型驗證未執行**。
- 目前 `main`／`origin/main`／`v0.4.0^{commit}` 均為 `0fcd87f9053311c4372a8c6b4867f7ea30aa8d9e`。執行前須重新記錄當時版本，不將本次檢查當作未來基準證明。
- 保留兩份未提交的 project-status 文件。本次僅新增此計畫，不建立 fixture、控制端、測試程式、產品 spec／ticket、分支或 worktree，不啟動模型、commit、推送或發布。
- 後續建議只執行核准的驗證。若觀察到缺陷，保存結果並提出修正選項，不自動修正、開票、調校模型或推進交付 gate。
- 母範本維護不初始化產品，保留 Charter、placeholders 與既有 spec／traceability／ticket 流程。此文件的案例 ID 不是 ticket ID。

**本期納入：** Codex desktop 的 Stage 3 與受控 EGM 案例、Codex CLI 的 EGM 失敗邊界、必要能力盤點、成本及證據紀錄。

**本期不納入：** Claude live、Codex CLI 的完整 Stage 3 矩陣、兩套 tune-skills 實測、wayfinder 契約修正、Windows 原生行為、模型偵測率／成本效益比較。這些不構成本計畫的隱含前置工作。

## 2．沿用的基準與證據邊界

| 既有證據 | 本計畫的處理 |
| --- | --- |
| Codex desktop：1 次 baseline、四軸兩輪共 8 次 reviewer，72 次必要檔案 hash/read 回報符合 | 不重跑完整兩輪來累積次數；新增一個四軸零 P0 的控制組及失敗案例 |
| Stage 3 的 G1–G10 為預製 gate 狀態 | 保留為決策層證據；逾時／crash／能力不足須另有原生事件才算宿主驗證 |
| Codex CLI EGM：顯式入口、hidden／models、非顯式查詢、重跑 suffix、symlink、真實 stale 已測 | CLI 僅補控制組與新失敗邊界；desktop 的受控案例另列，不跨宿主抵用 |
| Codex desktop 已有本專案實際診斷與 research smoke | 不再宣稱 desktop 完全未測；補受控 fixture，不泛化為完整矩陣已完成 |
| reviewer 曾取得 workspace-write、MEMORY_SUMMARY；受檢檔案 hashes 不變 | 記錄實際狀態；不宣稱角色唯讀等於工具強制唯讀，或 fresh context 等於移除記憶體服務 |

依據：[發行後待辦](../research/2026-11-01-post-v0.4.0-next-steps.md)、[Stage 3 evidence](../research/2026-11-01-fresh-context-review/evidence.md)、[既有 gate cases](../research/2026-11-01-fresh-context-review/gate-cases.md)、[EGM evidence](../research/2026-11-01-egm-drift-report/evidence.md)、[desktop 診斷](../research/drift-reports/2026-11-01-operations-skills-init-packaging.md)。

權威規則：[review](../../docs/agents/review.md)、[runtime](../../docs/agents/runtime.md)、[workflow](../../docs/agents/workflow.md)、[drift-report](../../docs/agents/drift-report.md)、[ADR-0005](../../docs/adr/0005-drift-diagnosis-native-host-verification.md)。本計畫不改寫這些規則。

## 3．必要能力與執行前檢查

下列是個別測試的可執行條件，不是新增全域 gates。本次只從現有設定及紀錄規劃，**尚未確認執行當天的能力**；不因「工具名稱存在」就宣稱可用。

| 能力 | 後續須取得的證據 | 不可用時 |
| --- | --- | --- |
| 新 Codex desktop 測試工作階段 | 使用者提供的新工作階段、宿主版本／工作區、實際 session ID 或宿主提供的識別碼 | desktop 案例 blocked；不自行建立使用者側欄 chat，不以 CLI 取代 |
| Stage 3 fresh reviewer | 原生新建 reviewer、顯式 `fork_turns: "none"` 或當次 API 的等效控制；角色／ID、啟動與完成紀錄 | Stage 3 未完成；禁止以單一對話自評替代 |
| 模型與 effort | 沿用執行主 session 的選擇；記錄可觀察值及來源，未知則寫未知 | 不自行覆寫模型、不觸發 tune-skills；若核准預算綁定特定模型而無法確認，暫停該批 |
| 原生 CLI 新 session | 執行前查本機 CLI 版本與 help，確認目前支援的新 session、事件輸出與停止方式；使用現有登入 | 缺帳號／入口則 CLI 案例 blocked；不登入、不改憑證、不臆造旗標 |
| 讀取與完成事件 | 可辨識特定 session、來源、首次讀取／建立報告時點的原生 trace | 無法同步的 stale／競爭案例 blocked；不能以事後修改冒充競態 |
| 安全故障控制 | 可針對本次唯一 session／獨立 worker 逾時、取消或異常終止，且有事件回報 | 分別標明 unavailable；不停止整個 desktop app、其他代理或使用者工作 |
| 可驗證的 I/O 拒絕 | 在 fixture 內以相同有效身分確認 EACCES 等錯誤；只用無敏感資料的探針 | 不能只憑 chmod 推論；無法成立則該權限案例 blocked |
| 用量與預算觀測 | 每個 session 的 usage（若提供）、開始／結束時間、執行次數及剩餘預算 | 用量缺失不填零；維持次數／時間硬上限，金額保持未知 |

所有啟動沿用 trust、sandbox、網路與角色設定；不為了讓測試成功而放寬權限。Stage 3 建議最多 2 個 reviewer 同時執行，實際槽位不足就分批，不干擾既有代理。EGM 每次只在它自己的當前對話內順序執行，不派子代理。

## 4．Fixture、觀測與責任邊界

後續獲准後才建立一次性的 fixture。建議 raw traces／controller／oracle 放在本機私有暫存目錄；正式可審閱證據另存 `.tmpl.docs/research/<執行日期>-codex-native-host-verification/`。不要沿用或清除既有 `/private/tmp/harness-*` 驗證目錄。

1. **控制端：** 準備範圍、hashes、注入事件及預期結果；只可改當次 fixture allowlist。記錄每次寫入者與時間，不把控制端注入誤報為模型擅改。
2. **Stage 3 reviewer：** 唯讀讀取當次封包與指定軸；回傳實際讀取、完成狀態及 findings。主助理保存報告、核對所有必要輸入及 gate；reviewer 不再啟動代理。
3. **EGM session：** 使用明確 `$egm-drift-report` 測試請求及指定文件／實作 scope；載入當次專案 skill。負向觸發案例不包含此叫用。只允許契約指定的新報告；不能修改 fixture 來源或 tracker。
4. **判定端：** session 結束後才讀 oracle，比對 trace、實際報告、前後 inventory、hashes 與 Git 狀態。控制端摘要或模型自評都不能代替原生事件。

每例只複製必要的正式規範、角色與 skills，以及新合成資料；不提供舊答案、既有診斷報告或 oracle。oracle 存在輸入 scope 外；這是測試資料隔離，不宣稱工具層無法存取。若 trace 顯示答案污染，案例記 invalid，不算成功。

Stage 3 使用全新合成 clean spec／matrix／contract；四軸共用相同 bytes 與 frozen prompt。內容版本在每個獨立故障案例前固定，案例間不能把已改版本當作同一輪技術補跑。S03 僅重用 S02 的相同封包及三個有效軸。

EGM 使用 4–6 份合成文件、2–3 份實作，涵蓋 current、planned、history、相符與可判斷的固定值差異。dirty 案例使用基準 commit 的隔離本機 clone，僅呈現必要檔案，保持 HEAD 固定，分別準備 staged-only、unstaged-only、untracked 及部分 staged 的檔案。**不建立任何新 commit**；新診斷讀目前工作樹 bytes，不能將 index 當作已 staged 檔案的實際讀取內容。

故障前後都記錄必要輸入與派工 hashes、Git index／工作樹摘要、檔案新增／刪除／修改清單。EGM 報告依 fixture 是範本維護或採用後專案，使用契約對應根目錄，日期取執行時 Asia/Taipei。模型不得讀取或執行 fixture 程式；I/O 與生命週期注入由控制端執行。

## 5．Codex 測試表（待核准）

### A．Stage 3：Codex desktop

`原生啟動上限` 計算 reviewer 新建嘗試，不是模型內部的每次 API request。所有列目前均為 **not run**。

| ID／seam | 觸發方式與可觀察證據 | 預期結果／驗收 | 邊界與無法測時的處理 | 原生啟動上限 |
| --- | --- | --- | --- | ---: |
| S01 四軸控制組 | 新 clean fixture；四個 fresh reviewer，捕捉明確啟動設定、ID、必要讀取與 before／after hashes | 四軸有效完成才判 gate；若有非預期 finding 如實保留，不強迫零 P0；有效零 P0 可第一輪停止 | 不新增第二輪；結果與 oracle 不符先分析，不改 oracle 配合輸出 | 4 |
| S02 真實逾時路徑 | 同一 clean packet 的四個新 reviewer；對一軸的必要讀取使用宿主支援的受控延遲／timeout，其餘三軸正常 | 原生事件證明該軸未完成；主助理不計為零 findings、不推進 gate；捕捉取消後的晚到結果 | 只有控制端 deadline 而沒有原生 timeout 時，記 controller deadline／被中止；原生 timeout coverage 仍 blocked | 4 |
| S03 同 bytes 技術補跑 | 修復 S02 的故障條件；只用一個新 reviewer 補失敗軸，重核四軸 packet hashes | 原三軸 bytes 未變才可保留；補跑成功後重新判斷，沿用同輪，不重設輪數；舊失敗 ID 不 resume | 依賴 S02；S02 blocked 時本例 skipped_dependency，不另花預算製造合成成功 | 1 |
| S04 明確取消 | 一個新 reviewer 真正啟動後，控制端使用原生取消；記取消請求、ack 與 completion | 區分取消與 timeout／crash；沒有有效回覆就不是完整軸，不把晚到回覆悄悄補入舊結果 | 單軸生命週期測試，不宣稱整套四軸通過；無取消能力則 blocked | 1 |
| S05 非預期 crash | 僅當 desktop 提供可安全終止的本次獨立 worker，於讀取後非正常終止，保存 exit／error | 真實 failure 不能當無 findings；保存已讀資料及未完成狀態 | 不把 S04 取消、合成錯誤或關閉整個 app 當 crash；無獨立 worker 控制則 blocked | 1 |
| S06 無 fresh 能力 | 在隔離測試環境以宿主支援方式停用／拒絕 fresh 啟動，記原生拒絕及能力盤點 | Stage 3 incomplete；不退回單一上下文作通過依據，不開票 | 禁止只在 prompt 宣稱無能力；無安全停用能力則 blocked；最多一次啟動嘗試 | 1 |
| S07 真正 stale | 四個新 reviewer；觀察至少一軸已讀必要來源後、最後結果採用前，控制端改該已讀來源；保存事件與 hashes | 來源版本不一致必須揭露，受影響結果不能通過原 snapshot gate；原輸出留存，不自動修訂重跑 | 缺首次讀取事件則 blocked；沒有造成時間窗就記 injection_missed，不宣稱已測 stale | 4 |
| S08 缺必要輸入 | 單軸新 session；封包明確列出一個不存在的必要 contract，其他檔案可讀 | 回報缺證據／incomplete，不填補隱含決策或回報 clean | 單軸 seam；不以模型記憶補檔，主助理不得自動補寫規格 | 1 |
| S09 gate 與兩輪規則對照 | 不叫模型，逐項對照新 native 結果與既有 G1–G10；另標為決策 replay | 有效零 P0 可通過；R2 P0→split；incomplete 不推論 P0；爭議交使用者；不開第三輪 | 兩輪成功已有歷史原生證據；本次 replay 不是新的兩輪 live 測試 | 0 |

S02／S07 的四軸各自屬於獨立故障 fixture 驗證，不是 S01 的第二／第三輪。不得借案例改名去重審同一個產品 spec 的第三個修訂版。S07 stale 與 S08 missing 的後續修復驗證不在本期預設預算內。

### B．EGM：Codex CLI 與 desktop 分列

以下每個正常 session 只做一次診斷。控制端用原生生命週期功能停止 session，不以再叫一次診斷補成 clean。所有列目前均為 **not run**。

| ID／宿主 | 觸發方式與可觀察證據 | 預期結果／驗收 | 邊界與無法測時的處理 | 新 session 上限 |
| --- | --- | --- | --- | ---: |
| D01 CLI 控制組 | 新 session 顯式入口、小型混合狀態 fixture；留讀取 trace、report 及 hashes | 辨識 seeded current 差異，planned／history 不當成違規；只新增一份報告，完整性依實際 coverage 判定 | 不沿用舊答案，不把有 drift 誤判成不能 complete | 1 |
| D02 desktop 控制組 | 使用相同 fixture bytes，在使用者提供的新 desktop session 顯式診斷 | 與 D01 各自判定；入口、來源與輸出均可追溯，來源未改 | 不要求措辭逐字相同；CLI 通過不能抵用本列 | 1 |
| D03 CLI＋desktop dirty | 各一個新 session，HEAD 固定；文件與實作的 staged-only、unstaged-only、untracked、部分 staged 有預先記錄的不同 bytes | 報告標示相關狀態、實際讀取 hash；判斷依當前工作樹，不只 HEAD／index；輸入狀態保持不變 | 合計兩列結果分宿主保存；不需要新增 commit；忽略檔／憑證仍排除 | 2 |
| D04 CLI 讀取拒絕 | 有一組可比較來源，另一份必要來源先以相同身分確認 EACCES；記工具實際失敗 | partial，列已查／未查與解決條件；不能將不可讀來源當沒有 drift | 若所有比較均不可進行則 blocked 合理；無真實拒絕則本例 blocked | 1 |
| D05 CLI 寫入拒絕 | 來源皆可讀，適用輸出根目錄以同身分確認無法寫入；保存寫入錯誤與目錄前後 inventory | 在對話回傳診斷／錯誤摘要，明示未保存；不換根目錄繞過、不修權限、不改原檔 | 拒絕發生在路徑檢查或建立時皆記實際層次；若根本未嘗試保存則另列觀察限制 | 1 |
| D06 CLI exclusive-create 競爭 | 在原生候選檔名已知、首次建立尚未完成時，控制端以 exclusive create 搶占該候選，保存 marker／事件 | 原 marker hash 不變；診斷選下一 suffix，只新增自己的報告；無覆寫 | 需要可同步的建立前事件；只預放同名檔屬 suffix 控制組，不能冒充競爭；無 hook 則 blocked | 1 |
| D07 CLI 軟性時間截止 | 六文件範圍；在第二份比較完成後以原生可用控制通知剩餘 30 秒，要求於文件邊界收斂 | 能收斂時 partial，列未查範圍與限制，不偽稱全查；保存通知時點、read set 與 report | 不是硬性 context overflow；無安全 steering／可觀測文件邊界則 blocked | 1 |
| D08 desktop 硬中止 | 確認首次來源讀取後，對本次新 session 發原生停止，保存 ack 與檔案狀態 | 分別記宿主 interrupted 與報告狀態；不得宣稱 complete／clean 或自動續跑 | 強制中止不要求模型有機會落盤 partial；未完成檔如存在，保留且標 unusable，不當正式報告 | 1 |
| D09 desktop 非顯式查詢 | 新 session 只問 fixture 目前進度，不要求診斷 | 無 EGM 呼叫、無新 drift 報告、檔案清單及 hash 不變 | 不執行其他 pipeline skill，不藉此推進票券狀態 | 1 |
| D10 desktop stale | 首讀完成後改一個已讀來源，保存原生讀取／controller 事件／hash | stale，保留捕捉證據，明示結論不適用新版本；不自動重試成 clean | 只補 desktop 受控證據，不否認 CLI 既有 stale 成功；未注入成功則 invalid | 1 |
| D11 desktop 寫入拒絕 | 以 D05 同規模的新 fixture，在 desktop 有效身分下預驗證拒絕 | 錯誤摘要與未保存聲明，來源未改；與 CLI 分開記錄 | desktop 身分與權限須實查；無法成立就 blocked | 1 |

EGM 的 `complete／partial／blocked／stale` 是契約規定的診斷狀態。測試結果則用 `pass／fail／blocked／invalid／skipped_dependency`，另記 native 終止原因；例如「blocked 診斷正確回報」可以是 pass，宿主無法注入則是測試 blocked。

真正的 context exhaustion、disk-full、原生 Windows、全部 pipeline skills 的非顯式觸發矩陣不納入本批。D07 的軟截止不能用來宣稱 context exhaustion 已測，D05 也不能代替 disk-full。

## 6．執行預算提案（待核准）

預算單位是**原生新 session／reviewer 啟動嘗試**；一次 session 內可能包含多次模型請求、工具回合與 continuation，不能把以下次數當成 API 呼叫數或固定費用。

主助理的控制與彙整回合不另算新 session，但其可觀測 tokens 與主動工作時間也納入總預算；不額外派研究／審查代理。若用量無法彙總，明列缺失，以次數及時間控制，不聲稱 token 警戒可強制執行。

| 批次 | 測試表配置 | 啟動上限 | 技術補跑預留 | 含預留硬上限 |
| --- | --- | ---: | ---: | ---: |
| A．Stage 3 desktop | S01–S08；S09 不叫模型；S06 即使拒絕也算一次嘗試 | 17 | 2 | 19 |
| B．EGM CLI | D01、D03 CLI、D04–D07 | 6 | 1 | 7 |
| C．EGM desktop | D02、D03 desktop、D08–D11 | 6 | 1 | 7 |
| 合計 | 含條件式 crash／能力停用；不支援則保留未用額度 | **29** | **4** | **33** |
| Claude | 本期僅記錄延期，不啟動 CLI／模型／驗證代理 | **0** | **0** | **0** |

- **併發：** Stage 3 最多 2，EGM 全部順序執行；不同批次不重疊。S03 已在 17 次內，不重複扣預留。
- **單例時間：** reviewer 最多 6 分鐘、EGM 最多 10 分鐘；故障注入預定在首次讀取後，受控等待窗口最多 90 秒，包含在單例上限。測試專用 deadline 不改產品協定。每次工具等待不超過 60 秒，維持進度更新。
- **停止能力：** 啟動前確認可停止本次 session；無法安全停止就不啟動該 surface 的模型測試。達 deadline 後記錄停止是否確實完成，未取得 ack 不能宣稱工作已停止；殘留活動必須列入結案限制，不再啟動新案例。
- **整批時間：** 預估 4–6 小時，包含能力盤點／fixture 準備約 45–60 分鐘及證據整理約 60 分鐘；本批主動工作累計達 **6 小時**即停止。等待使用者／帳號／不可用宿主的時間另記，不藉等待增加執行額度。這是規劃估計，不保證完成所有列。
- **技術補跑：** 只用於注入未命中、暫時性工具失敗等，不用於追到喜歡的 findings。每例至多 1 次，且受該批預留及總額度限制；超出就保存未完成結果。S03 是特定測試，不等同預留補跑。
- **tokens：** 歷史 CLI 10 sessions 的原生 usage 合計 input 1,671,536（其中 cached 1,444,480）、output 39,239；reasoning output 另列 5,477，不擅自重複加算。這是過去宿主的統計，不能當新模型報價或 desktop 用量。
- **觀測警戒：** 建議累計可見 input（含 cached）達 5,000,000，或 output 達 150,000 時，停止啟動新案例並結算；每例結束核對一次，可能超過一個 session 的用量。不是工具強制 token 上限，缺失用量不能視為零。
- **金額：** 本計畫不提供虛構金額。沿用既有登入／方案，不建立付費資源或切換計費方式。若使用者需要金額硬上限，執行前須指定方案與上限並確認可強制限制的方式；無法觀測時就不能承諾金額上限。

建議先跑 S01 與 D01 兩個控制組（共最多 5 次啟動），檢查 trace、觀測及時間是否足以支援後續。若控制組無有效證據，就停止該 surface 的新模型呼叫；仍可整理其他 surface 的已核准項目，不用完預算為目標。任何批次達上限、來源契約改變、無法限制影響範圍或發現非 fixture 寫入，立即停止該批並保存證據。

## 7．後續執行順序與交付

1. **確認授權及固定基準。** 使用者核准此計畫／測試表／預算並明確要求執行後，才準備 fixture 或啟動模型。重查 HEAD、dirty 檔案與既有草稿 hashes，讀取未變的規範時沿用已知內容。計畫核准本身不等於本回合已執行。
2. **盤點能力、建立最小 fixture。** 先做不用模型的版本／help／有效身分／事件能力檢查，記錄每列可測或 blocked。只準備即將執行案例，不實作通用 runner。必要的一次性控制步驟不進 production skill；若需要正式 helper 或協定修改，停止並另提核准計畫。
3. **控制組與 Stage 3。** 先跑 S01／D01，確認可用後依 A 批順序執行。S02 確認失敗後才做 S03；S07 前固定新案例封包。四軸與技術補跑的參數、ID、hashes、結果皆可回查。
4. **EGM 新邊界。** 執行 B 批剩餘案例，再做 C 批。每例新 session、獨立 fixture，保存對話摘要、原始報告、注入事件與檔案差異。缺 desktop 新工作階段時保留 C 批 blocked，不用代理代演 EGM。
5. **彙整，不修正。** 逐列產出 coverage report table：案例／host/version／observed model-effort／實際啟動數／native event／read hashes／測試結果／診斷或 gate 狀態／用量與時間／未覆蓋原因／證據連結。彙整確認缺陷與待確認線索，但不自動開票或修改。

後續證據目錄建議包含 `README.md`（實際協定）、`capabilities.md`、`cases.md`（每例結果）、`manifest.json`（版本與 hash）、`budget.md`（用量及剩餘額度）、`coverage.md`；實際 EGM 原始報告可存副本並標明原始位置。raw trace 先保存在本機，確認無憑證、帳號或無關內容後才挑選必要片段納入證據。只在必要時連結本機檔，避免把敏感原始 trace 納入 Git。

結案須區分：已測通過、實際失敗、因能力不足未驗證、注入未命中、依賴未成立而未執行。**完成這批證據整理不等於所有測試通過，也不宣稱 Claude、其他 OS 或強制隔離已驗證。** 本計畫不授權 commit／PR／tag／發布。

## 8．Claude 延期紀錄

| 項目 | 現有紀錄 | 本期狀態 | 未來恢復條件 |
| --- | --- | --- | --- |
| Stage 3 fresh 四軸及兩輪 | 2026-11-01 紀錄：Claude Code 2.1.283，當時 loggedIn=false，未執行 live | **deferred_by_user，0 次啟動** | 使用者另行要求；重新查實際版本、帳號、角色、fresh 語意及預算後再擬／核准 Claude 測試表 |
| EGM 顯式診斷與失敗情境 | 入口、政策與可攜性有靜態證據，沒有對應 Claude live suite | **deferred_by_user，0 次啟動** | 另開原生 Claude 測試批次，沿用診斷契約但不借用 Codex 結果 |
| 有效權限／外部 memory／用量 | 未取得足以涵蓋本計畫情境的實際 trace | **未驗證，延後** | 取得該宿主自己的可觀察證據，未知部分保留限制 |

本期不檢查 Claude 登入、不要求重新認證、不啟動 Claude 子代理；「當時未登入」不能寫成現在仍未登入。延期不新增全域 gate，也不阻擋本批 Codex 證據交付。

## 9．既有流程不變

EGM 維持顯式觸發、當前對話順序執行、只寫一份新報告，不自動修正／重試／開票。Stage 3 維持四軸、每軸／輪 fresh、相同 frozen prompt、最多兩輪；全部有效完成才計 P0，第二輪仍有 P0 就拆分回 Stage 1，技術失敗不等於零 findings。

此為母範本維護驗證計畫，不代替產品 spec／traceability 或核准測試表；後續若有實作，仍依原有 requirement／spec／ticket、TDD、code review、security review、實際 surface 驗證及 landing 流程。本期不新增規則，也不將單次模型輸出當作隔離、普遍正確性或缺陷偵測率的保證。
