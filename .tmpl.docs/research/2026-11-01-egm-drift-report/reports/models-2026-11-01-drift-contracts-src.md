# contracts／src 文件與實作落差診斷

- 狀態：**complete**。指定文件與實作清單均已完成靜態比對；確認 2 項落差，來源版本複查一致。
- 診斷時間：2026-11-01T16:58:58+08:00（Asia/Taipei，UTC+08:00）；首次診斷來源擷取時間：2026-11-01T16:58:06+08:00。
- 目的：依使用者顯式呼叫 `egm-drift-report`，診斷採用後專案之目前交付契約與實作；對應既有 epic `0001-records`。
- 工作目錄／實體根目錄：`/private/tmp/harness-drift-models`。
- 執行環境：本對話之 Codex，使用 host `exec_command`、zsh 與 Python 標準函式庫進行列舉、讀取、雜湊及報告寫入；未取得可獨立查證的後端模型版本。
- Git：初始與最終查詢均回傳 `fatal: not a git repository`（exit 128）。無法取得 base、branch、HEAD、staged／unstaged／untracked 或 dirty state；以目前磁碟內容與 SHA-256 作為版本依據，不將這些檔案標示成已追蹤或未追蹤。

## 範圍與有效狀態

文件範圍為 `contracts/` 下遞迴列舉的 Markdown 一般檔案，包含隱藏路徑；實作範圍為 `src/` 下的一般檔案。依穩定路徑順序完整讀取 2 份文件與 2 個實作檔，未發現隱藏檔案、symlink 或其他實作檔。文件沒有直接引用其他來源，僅明確指向已納入的兩個實作檔。

使用者明示「文件表示目前交付契約」；`contracts/model.md:1,3` 使用「Current model」「Current delivered」，`contracts/service.md:1,3` 使用「Current public service」「Current delivered」「Both are mandatory」，故本次視為現行交付要求，無證據可將缺項解釋成規劃中或歷史差異。

僅使用已載入的專案規則、指定 skill 及其明確要求的共用診斷契約。未讀取其他提示檔、epic 規格、traceability、翻譯或 tickets，也未擴大到其他目錄；epic 僅確認既有目錄與安全輸出位置。沒有以 tickets 取代需求，亦未虛構 acceptance criteria。本次結論僅針對使用者指定的現行 `contracts/`，不代表與未讀取之 `spec.en.md` 或其他規格完成一致性驗證。

排除範圍：Git internals、憑證與 `.env`、cache、node_modules、建置產物、handoffs、舊診斷報告，以及其餘未指定內容；未讀取上述內容。列舉所得四檔均為本次明示目錄範圍內的一般檔案，未見上述排除類別。因無 Git，`git check-ignore` 無法有效判定 ignore 狀態，不將其查詢失敗解讀為「未忽略」。

## 逐文件結果

| 文件／主張 | 實作證據 | 結果 |
| --- | --- | --- |
| `contracts/model.md:3`：`Record` 的 `id` 與 `timestamp` 都是必要欄位 | `src/model.py:1-5`：匯入 `dataclass`、套用 decorator，`Record` 僅宣告 `id: str`，沒有預設值 | `id` 的宣告及必要性在靜態來源層級未發現差異；`timestamp` 為 D-01 確認落差 |
| `contracts/service.md:3`：必須提供 `list_records()` 與 `delete_record(key)`，且沒有委由其他實作入口提供 | `src/service.py:1-2`：唯一函式為無參數的 `list_records()`，直接回傳 `[]` | `list_records()` 的存在及參數形式未發現差異；`delete_record(key)` 為 D-02 確認落差 |

### D-01：Record 缺少必要的 timestamp

- 結果：**Confirmed drift**。
- 文件側：`contracts/model.md:3` 明定「id and timestamp fields. Both are mandatory.」。
- 實作側：`src/model.py:3-5` 的完整 `Record` 定義僅有 `id: str`；`src/model.py:1-5` 為整個檔案。完整 `src/` 清單僅包含 `src/model.py` 與 `src/service.py`，後者也沒有欄位補充邏輯。
- 差異與影響：目前來源定義沒有契約要求的 `timestamp` 欄位及其必要性宣告，無法依此型別定義交付文件承諾的完整資料結構。未推定時間格式、型別、產生方式或時區規則，因文件沒有要求這些細節。
- 信心：高；現行文件主張明確，對應型別與整個指定實作範圍均已讀取。這是來源層級的缺項，未執行 constructor 或驗證外部執行時期行為。
- 後續選項：依既有需求與交付流程釐清應補齊欄位，或是否應正式修訂契約；本次不代為決定或修改。

### D-02：服務缺少必要的 delete_record(key)

- 結果：**Confirmed drift**。
- 文件側：`contracts/service.md:3` 明定必須提供 `list_records()` 與 `delete_record(key)`，並明確表示沒有委由其他實作入口提供。
- 實作側：`src/service.py:1-2` 為完整檔案，只定義 `list_records()` 並回傳空清單；沒有 `delete_record` 定義、匯入或轉接。另一個範圍內來源 `src/model.py:1-5` 也沒有此入口。
- 搜尋邊界：完整列舉與讀取 `src/` 兩檔，並於 `contracts/`、`src/` 執行 `rg -n --hidden 'Record|timestamp|id|list_records|delete_record|def |class |import'`；`delete_record` 僅命中文件 `contracts/service.md:3`。此結論是指定範圍內未提供該入口，不是全專案不存在的保證；缺少的一側不虛構行號。
- 差異與影響：依目前服務模組來源，呼叫端無法取得契約承諾的刪除入口。文件未定義刪除回傳值、錯誤處理或持久化方式，故不追加這些要求。
- 信心：高；服務檔案短且完整，沒有其他實作轉接，文件也排除委由其他入口提供的解釋。未呼叫服務或驗證任何外部系統。
- 後續選項：依既有流程確認刪除功能之交付要求與後續實作／契約調整；本次不開票、不改狀態。

## 實作反向盤點與實際覆蓋

| 來源 | 已檢查的可觀察介面或行為 | 文件對照與限制 |
| --- | --- | --- |
| `src/model.py:1-5` | `Record` 為套用 `dataclass` 的型別；唯一欄位 `id: str`，無預設值 | 對應 `contracts/model.md:3`；缺項見 D-01。匯入與 decorator 為實作機制，未另立文件義務 |
| `src/service.py:1-2` | `list_records()` 無參數且固定回傳 `[]`；無其他定義或轉接 | 對應 `contracts/service.md:3`；缺項見 D-02。文件只要求入口存在，沒有承諾資料來源或非空結果，故不將固定空清單額外判定成落差 |

指定範圍沒有尚未讀取的文件或實作檔，也沒有已確認的預期差異。動態測試、服務整合、資料持久化、部署現況與範圍外規格一致性均未驗證；這些限制不影響兩個明確來源缺項的判定。沒有執行、匯入或編譯 fixture 來源，沒有安裝套件、連線外部服務或派工。

## 來源版本與 SHA-256

診斷目標四檔在首次內容讀取時，以同一份讀取位元組同時計算 SHA-256；skill 與共用診斷契約在流程載入後重新讀取並擷取雜湊。以下六檔均在報告寫入前重新檢查，結果全部相同；`contracts/` 與 `src/` 檔案清單也再次確認一致。

| 實際讀取路徑 | SHA-256 |
| --- | --- |
| `.agents/skills/egm-drift-report/SKILL.md` | `a340b35f51d80f91a4e90ec67284cc6a72c77c48877920b12c43a447f4a9d1ca` |
| `docs/agents/drift-report.md` | `407d225e1d551ed14ecc6d0291ec491b442b82424ab7fd624d1eae4abbf62cd3` |
| `contracts/model.md` | `ef5695d55a60211696470992cb08c5152fa647c78a58726c77d4dcfab4aae877` |
| `contracts/service.md` | `ce15a7874d0c53a5405aac62909c34df9012e1560c0947195bc0638cacc3d320` |
| `src/model.py` | `6588a4002d3e45b211725cbaabf1f8d9976e2160813c5607f26dd253d9c92269` |
| `src/service.py` | `66b2231fd3834acd4d882ed4c31b16f2b7620dfd9850189d9b8d0c972d6ff566` |

最終來源檢查時間：2026-11-01T16:58:58+08:00（Asia/Taipei）。Git 可用性與初始一致，仍無法取得版本控制狀態；未因 Git 不可用宣稱工作目錄乾淨。來源雜湊與範圍清單未改變，故本次不是 stale。

## 寫入邊界與後續

本次只以獨佔建立模式新增此報告，檔名衝突則使用流水號；保留既有報告。輸出父路徑逐層檢查不得為 symlink，必須留在 checkout 內，且既有 epic 必須存在。未修改程式碼、契約、規格、追溯資料、翻譯、tickets、ADRs 或 gate 規則；未 commit、merge、發布或觸發 CI。

`complete` 表示此次指定靜態比對完整，不是 ticket 完成、Stage 3 判定、安全稽核、測試通過或交付核准。後續若要調整文件或實作，仍依既有需求／規格／ticket、核准測試計畫、TDD、review、安全檢查、實際介面驗證與 landing 流程處理。
