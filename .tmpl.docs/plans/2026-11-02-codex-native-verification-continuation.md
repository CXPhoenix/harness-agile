# Codex 原生驗證續測計畫

> 後續明確獲准執行時載入 `executing-plans`，依核准批次、測試表與預算執行。此文件只規劃，不建立新對話、啟動測試或授權設定變更。

**Goal:** 優先釐清上一批 CLI 無法落盤的原因與 fixture 缺漏，以新的短控制對話續測可執行的 Codex 案例；Claude 維持延後。

**Architecture:** 先做不叫模型的設定來源與 fixture 查核；必要時用一個最小 canary session 驗證有效寫入，再重做 EGM 控制組。CLI 邊界與 Stage 3 使用不同短控制對話、分批預算及固定輸入，不在舊長對話持續展開驗證。

**Tech Stack:** 現有 Codex CLI／desktop 原生介面、專案契約、Git、Python 標準函式庫、一次性暫存控制端。沒有正式程式、skill、runner 或套件相依變更。

## 1．狀態與範圍

- 日期：2026-11-02，Asia/Taipei。狀態：**續測計畫／測試表／預算待核准，尚未執行**。
- 規劃時 HEAD：`0fcd87f9053311c4372a8c6b4867f7ea30aa8d9e`。原計畫、兩份 project-status 草稿及上一批證據保留，不覆寫歷史結果。
- 本次只新增此文件；沒有執行 CLI 能力探針、建立／修補 fixture、建立 chat、啟動代理、變更 trust／sandbox／設定、實作修正或開票。
- 建議本輪只核准下方 **A／B／C 核心續測，上限 13 次測試啟動**。缺乏原生能力的項目及 desktop EGM 完整矩陣列為後續條件式工作，**本輪模型預算為 0**，不暗中擴大範圍。
- 不重跑已通過的 S01、S04 或完整兩輪審查。S07 必須以新完整四軸案例續測，不能把舊的兩軸與新兩軸拼成通過。

依據：[上一批結果](../research/2026-11-02-codex-native-host-verification/README.md)、[能力盤點](../research/2026-11-02-codex-native-host-verification/capabilities.md)、[coverage](../research/2026-11-02-codex-native-host-verification/coverage.md)、[實際用量](../research/2026-11-02-codex-native-host-verification/budget.md)、[原核准計畫](2026-11-02-codex-native-host-failure-verification.md)。

## 2．已知事實與待查假設

上一批 CLI 0.161.0 的啟動參數沒有 model／effort／sandbox override；fixture 的 `.codex/config.toml` 寫有 workspace-write，並註明須先取得本機 trust 才生效。**設定檔存在不證明被載入或最終有效值為 workspace-write。**

CLI 原生 trace 沒有寫入命令；session 回報唯讀，退出碼 0，檔案清單及 hashes 未變。stderr 的 filesystem violation 為 path=unknown，無法指認是報告寫入。故尚不能判定根因，也不能把 D01 抵用為受控 write-denial 通過。

| 待查假設 | 下一批要取得的證據 | 可接受的結論 |
| --- | --- | --- |
| CLI 預設／profile／啟動環境選到 read-only | 實際版本、argv、cwd、profile 選擇、可安全取得的設定來源與有效 sandbox | 來源及有效政策可核對；取不到就保留 unknown |
| fixture 的專案設定未因 trust 或目錄探索而載入 | checkout 邊界、設定檔位置／hash、相關 trust 設定及宿主載入／忽略訊息 | 不能僅看 config 內容推定生效；不自行新增 trust |
| 上層 managed policy 蓋過專案設定 | 宿主實際宣告或可用的政策來源資訊 | 有證據才歸因 managed policy，無證據不猜測 |
| 模型將可寫環境誤判為唯讀 | 同一啟動條件的有效政策，加上最小 native canary 的工具結果 | 實際寫入成功才證明該條件可寫；只有自述仍不足 |
| 輸出路徑、檔案權限或 symlink 阻擋 | 適用輸出根的實體路徑、owner／mode、父目錄與真實 errno | 與 CLI sandbox 分層記錄；父 shell 可寫不等於 CLI 可寫 |

此處是調查設計，不是對上述原因的確認。正式契約沿用 [runtime](../../docs/agents/runtime.md)、[review](../../docs/agents/review.md)、[drift-report](../../docs/agents/drift-report.md) 與 [ADR-0005](../../docs/adr/0005-drift-diagnosis-native-host-verification.md)。

## 3．A 批：先釐清 CLI，再建立有效控制組

### A0：無模型查核

以下步驟僅在後續獲准執行後進行，本次不執行。

1. 在新的短控制對話固定 main／所需來源版本、argv、工作目錄及原始檔案 hashes；重新查當時 CLI version／help，不假定舊旗標或設定 schema 仍適用。
2. 只擷取相關設定欄位與來源：sandbox、approval、project trust、profile、managed policy、工作目錄。不要輸出整份全域設定、環境變數、認證、帳號或 token。不存在的 introspection 介面不可臆造。
3. 若宿主有不叫模型即可觀察有效設定／執行環境的正式介面，優先使用。它必須對應**同一 CLI 執行條件**，不能用父 shell 探針或 desktop 設定代替。
4. 檢查輸出根的實體範圍、既有父目錄及相同有效身分的基礎 I/O；只用新 fixture 的無敏感資料探針，分開記錄 OS 與 CLI 結果。
5. 若已確知 read-only 或更上層禁止寫入，停止 CLI 模型測試並交付根因／剩餘疑點。若仍未知但有安全停止能力，才考慮 R01 canary。不得為了測試自行改 trust、全域 config、sandbox override、approval bypass 或登入。

若解除限制必須變更設定，先保存實際來源與可審閱的最小調整方案，留待另外授權；這份計畫不授權該變更，也不以切換到另一個工作目錄／宿主掩蓋原環境問題。

### A1：fixture 必要脈絡補齊方案

後續獲准時建立**新的暫存複本**，不修補上一批 fixture，也不修改正式來源。先列出必要依賴清單及每份檔案的角色，再複製當次來源 bytes／hash：

| 類別 | 最低檢查範圍 | 檢查方式 |
| --- | --- | --- |
| 指令入口 | `AGENTS.md`、`docs/agents/runtime.md`、`codex.md`、`drift-report.md` | 從載入入口追到本次實際需要的共用規則，不用自行改寫的精簡規則替代 |
| 上批缺漏 | `.tmpl.docs/README.md`、`docs/agents/language.md`、`docs/agents/domain.md` | 三份均須存在並可讀；`domain.md` 所需詞彙／ADR 也須可取得 |
| 母範本維護脈絡 | `.tmpl.docs/contributing.md`、`.tmpl.docs/CONTEXT.md`，以及必要 workflow／review／issue-tracker／ADR | 區分真正必讀與只是導覽／歷史連結；必讀缺漏先停止，不花模型預算 |
| 執行入口與政策 | `.agents/skills/egm-drift-report/` 的 SKILL、metadata、LICENSE；所用 `.codex/config.toml` | 相對入口、內容 hash 與 invocation policy 一致；記錄設定是否實際生效，不為複本新增 trust |
| Stage 3（C 批） | reviewer role、review／runtime／Codex 規則、spec／matrix／contract／frozen prompt | 必要文件完整列舉；只有 R06 刻意缺一個 contract，其他依賴完整 |
| 新合成比較資料 | 4–6 份文件、2–3 份實作，涵蓋 current／planned／history／match | 使用新的案例值與 scope 名稱；oracle 置於指定輸入範圍外，不提供舊答案 |

依賴清單區分「必讀且已提供」「明確不適用」「僅歷史／可選參考，未納入」。不要求盲目複製整個 repository 或所有歷史報告；如執行中發現新的必要來源缺漏，記為 fixture_invalid，停止該例，不靠模型猜測補足。

新 fixture 不複製既有診斷報告、handoff、oracle、cache、憑證或 release archive。`.tmpl.docs/README.md` 的歷史導覽不因此變成測試答案輸入。Stage 3／EGM 各自 scope 與權威文件仍保持可追溯。

### A2：canary 與 D01 重測

R01 不是診斷。必要時以新的最小 CLI session，只要求在適用報告根內 exclusive-create 一個唯一 UTF-8 canary、讀回並回報結果；不讀 ops／src、不載入 EGM、不安裝或呼叫外部服務。保留原始政策，若禁止就回報禁止，不繞過。捕捉原生工具事件、errno 與實際 inventory，不接受「我可以寫」的自評。

canary 與後續 EGM 必須使用相同 cwd、profile、argv 條件、有效政策與輸出父目錄；只有任務 prompt／唯一輸出名稱不同。canary 檔保留並納入 baseline，避免事後刪除掩蓋變更。若已有同條件的直接有效寫入證據，可免 R01，額度不挪作其他案例。

只有可寫前提及 fixture 必要脈絡均成立，才執行 R02。R02 是新 CLI session 的顯式 EGM，必須實際保存一份新報告、正確分類 seeded 差異及 expected exclusions、前後來源不變。退出碼 0、模型自評 complete 或控制端代存 final message 都不等於落盤成功。

## 4．新的短對話與證據封包

- **由使用者開啟新的普通對話**，選擇本專案，分別承接 A、B、C 批；不 fork 舊長對話、不附全文聊天／release 歷程、不由工具自行建立側欄 chat。這次規劃不建立任何對話。
- 新控制對話先讀本文件的狀態、授權、對應批次與預算；其他部分按需讀取。手動提供的啟動訊息與批次摘要合計目標 **≤8 KiB**，避免整份貼入歷史輸出或 trace。
- 每批啟動封包只列：核准範圍、來源版本、必要規範路徑、案例 ID／預算、證據輸出根、已驗證／blocked 的必要依賴。模型只能以完整必要來源判斷，不能為省 tokens 省略 gate／角色規則。
- A／B 的 CLI 為新獨立 session；C 的 reviewer 每次明確 `fork_turns: none`。模型／effort 沿用使用者於該新對話的選擇，不自行 override 或啟動 tune-skills；能觀察才記錄實際值。
- 原生工具／系統／memory 注入不受 8 KiB 目標保證；如第一輪實際 context 已很大，立即記錄並縮小該批執行量，不宣稱新對話自動移除 memory。
- raw trace 由一次性控制端以資料方式擷取／計數；模型只讀必要事件與簡短計數，不反覆全文讀 trace 或整份歷史 JSON。每例完成即把結果、hash、用量與剩餘額度存檔，下一個短對話不靠前文續算。

可在新 A 批對話貼入以下啟動文字；它是後續使用者操作範例，本次不執行：

```text
依 .tmpl.docs/plans/2026-11-02-codex-native-verification-continuation.md，
在此新短對話開始已核准的 A 批。先確認核准範圍與預算，再做無模型設定／fixture 查核；
符合前提才做 R01／R02。不要自動改 trust、sandbox 或正式檔案。
Claude 延後；不修正、開票、commit 或發布。停止時保存結果與剩餘預算，不自動轉批。
```

B 使用相同形式，只帶 A 的精簡前提結果；若 A 沒有有效可寫控制組，B 停止。C 可在獨立新短對話執行，不依賴 CLI 成功，但仍受總預算與必要能力限制。批次交接以檔案為準，不自動跨 chat 傳訊。

## 5．核心測試表（待核准）

各列目前均 not run。啟動數為新的測試 session／reviewer，非內部 API request；無模型控制步驟不占該數，但主助理用量與時間仍計入。

| ID／對應原案例 | Surface／上限 | 觸發與觀測 | 預期結果與停止條件 |
| --- | --- | --- | --- |
| R00 設定與 fixture | 控制端，0 | 設定來源、有效政策、cwd／profile／version、輸出路徑、必讀依賴／hash 清單 | 已知／未知分開；缺前提不花模型預算。明確唯讀則停止 CLI，不自行調整 |
| R01 有效寫入 canary | CLI，最多1 | 同條件新 session，exclusive-create 唯一無害檔並讀回；捕捉真實工具與 inventory | 寫入成功且來源未變；若真實拒絕或只自述無法寫入，分別記 errno／證據不足，停止 A，不反覆提示取得成功 |
| R02 原 D01 控制組 | CLI，1 | 完整新 fixture、顯式 EGM、原生讀取／保存與前後 hashes | 正確分類 current／match／planned／history；只新增一份實際報告。未保存或必要來源缺漏，B 不執行 |
| R03 原 D03 dirty | CLI，1 | 固定 HEAD 的隔離本機 clone；staged-only、unstaged-only、untracked、部分 staged 有不同 bytes | 依當前工作樹比對，記錄 dirty 與實讀 hashes；不只讀 HEAD／index；不新增 commit |
| R04 原 D04 read denial | CLI，1 | 同一有效身分確認單一必要來源 EACCES，其餘可讀；捕捉 native read error | partial 並列已查／未查；全部無法比較則 blocked 合理。父 shell 探針不抵用模型行為；拒絕未成立則 blocked |
| R05 原 D05 write denial | CLI，1 | 可讀來源、原本可寫基準已成立；僅新 fixture 輸出根設受控拒絕，記真實錯誤 | 回傳摘要及未保存聲明，不修權限、不改根目錄繞過；不能用 R01 的未知唯讀限制抵用 |
| R06 原 S08 缺必要輸入 | Desktop reviewer，1 | 新完整封包僅刻意缺 contract；單軸 fresh reviewer、其餘必要輸入可讀 | incomplete，列缺證據，不補寫規格、不當零 findings；這不是四軸 gate 通過案例 |
| R07 原 S07 完整 stale | Desktop reviewer，4 | 新封包，四個新 ID，最多2併發；原生 trace 證明首讀後、最後採用前控制端改已讀來源 | 四軸實際執行與讀取／終止證據齊全，parent 核對前後 hash 並拒收原 snapshot 通過；不計 P0 總數、不自動重跑成 clean |
| R08 結案對照 | 控制端，0 | 對照原表、原生事件、allowlist、用量及未覆蓋項目 | pass／fail／blocked／invalid／依賴未成立分開；不以決策 replay 冒充 timeout、crash 或完整兩輪 live |

R07 的四軸啟動前先確認預算可容納整組；不足就不要啟動半組。若開始後才達警戒，停止新啟動、保存部分結果，不以硬撐完成四軸越過預算。控制端注入只動新 fixture allowlist，先後時序沒有命中就記 invalid，不更改 oracle 配合結果。

## 6．本輪預算提案

| 批次／短控制對話 | 基本測試啟動 | 技術補跑預留 | 測試硬上限 | Input 觀測配置（含 cached） |
| --- | ---: | ---: | ---: | ---: |
| A：R00–R02 | 2（canary 可免） | 1 | **3** | **700,000** |
| B：R03–R05 | 3 | 1 | **4** | **900,000** |
| C：R06–R07 | 5 | 1 | **6** | **800,000** |
| 結案整理預留 | 0 | 0 | 0 | **600,000** |
| 合計 | **10** | **3** | **13** | **3,000,000** |

- 另有最多 **3 個新的短控制對話**（A／B／C），不混入 13 次測試數；它們的所有可見用量均已包含在上表配置。合計最多 16 個新控制／測試上下文，不等於 16 次 API request。這次沒有建立它們。
- 本輪預算是新配置，不承接上批剩餘 25 次啟動額度。Claude 與 desktop EGM 均為 0；除表內 R01 canary 外，不另支用模型探索能力。
- **時間：** A 最多45分鐘、B最多45分鐘、C最多60分鐘、結案30分鐘，合計主動工作最多 **3小時**；等待使用者另記。CLI 單例最多10分鐘、reviewer最多6分鐘；須能安全停止本次 session，沒有停止能力就不啟動。
- **技術補跑：** 每批最多1次、每例最多1次，只限注入未命中／暫時性工具錯誤；必須有前次證據。R07 若需重跑完整四軸不可能靠單次預留完成，應先交付 invalid／未完成並另提預算，不偷偷挪用其他批次額度。
- **用量：** input 含 cached，全程按新控制對話、CLI、reviewer 各自最後累計差額加總，避免重複累加 cumulative events；output 建議配置上限 **80,000**，reasoning output 另列不擅自重複加算。取消缺失或無法取得的用量標 unknown，不當零。
- **提早停止：** 任一批達其 input 配置，或執行階段累計達 **2,400,000 input／60,000 output**，停止新案例，進入結案預留。不把最後一個 session 的超出量隱藏，也不宣稱觀測配置是工具強制 token／金額上限。不能取得用量時，最多完成已啟動案例便暫停新模型，先補齊計量能力。
- 每次啟動前，以同類已測 session 的可見用量及當批剩餘額度作保守估算；尤其 C 批先預留完整四軸與主助理核對成本。無可信估算或沒有足夠餘額就不啟動。結案也必須縮短，不回舊長對話全文重跑分析。
- **金額：** 不提供未驗證費率推估，不建立付費資源、不切換模型／計費方案。若需要金額硬上限，須先指定方案並確認可強制限制方式，本預算不冒充金額保證。

## 7．仍待能力的原案例

| 原案例 | 後續測試方向 | 本輪安排／啟動預算 |
| --- | --- | --- |
| S02 timeout、S03同bytes補跑 | 必須有指定軸必要讀取的原生 timeout／pause 及事件；成功後才測同輪新ID補跑 | 保留 blocked／dependency；0。不用 sleep、controller deadline 或取消冒充 |
| S05 crash | 能安全異常終止僅屬本例的獨立 worker，取得 exit／error | 0。不終止整個 desktop 或其他工作 |
| S06 fresh 停用 | 有隔離能力停用／拒絕介面，可證明真實拒絕 | 0。不耗盡其他人槽位，不改全域 agents 設定 |
| D06 exclusive-create 競爭 | 必須取得可同步的建立前控制點，保證控制端先佔候選再觀察碰撞處理 | 0。只有預放同名檔仍是 suffix 案例，不能算競態 |
| D07 軟截止 | 同一原生 session 的即時 steering 與文件邊界事件 | 0。不以硬中止代替，不為本期引入新 production 介面 |
| Desktop EGM：D02、D03、D08–D11 | 新頂層 session 的控制組、dirty、硬中止、非顯式查詢、stale、write denial，各自保留原驗收 | 本輪0。未來需使用者提供各例新頂層測試對話及另核預算；A／B的CLI及C的reviewer不抵用 |
| Claude 全部 | 另行要求時重新查原生能力／版本並擬定該宿主測試表 | **deferred_by_user，0次**；本輪不檢查登入 |

無模型的本機 help／已提供 API 能力查核可記錄新線索；不能因找到工具名稱就自動啟動上述 0 預算模型案例。能力具備後再提出具體測試表差異與預算，不新增為全域 gate。

## 8．後續交付與停止點

獲准後每批的證據放在新的 `.tmpl.docs/research/<執行日期>-codex-native-continuation-<batch>/`，不覆寫上批目錄。交付短摘要、capabilities／fixture依賴清單、每例原生事件與 read/write hashes、coverage、預算 ledger／計量截止時間及 manifest。raw trace 先留本機，只保存必要且遮蔽敏感資訊的節錄。

A 批即使受阻，也應交付：哪些設定來源已確認、哪些仍未知、fixture 必要脈絡是否完整、是否真的寫入／拒絕、目前可安全採取的最小下一步；不可再只回覆「唯讀所以沒存」而省略證據層次。若沒有足夠證據找出根因，結論仍須保留 unknown。

EGM 維持顯式觸發、當前對話順序執行、僅建立新報告；不派代理、不自動修正或重試。Stage 3 維持四軸、fresh context、frozen prompt、最多兩輪及零 P0 gate；測試控制案例不代表真實產品多了一輪審查，也不代替 spec／traceability／ticket。必要實作仍須走原核准測試表、TDD、review、security review、實際 surface 驗證及 landing 流程。

此計畫的結案或任何局部 pass 都不推進其他 gate。本輪不修正正式來源、不開票、commit、PR、tag 或發布；設定變更與任何超出本表的續測均不在此授權範圍。
