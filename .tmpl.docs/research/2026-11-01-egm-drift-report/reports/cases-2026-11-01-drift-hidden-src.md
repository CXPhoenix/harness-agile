# 文件與實作落差診斷：.hidden / src

- **診斷狀態：partial**。已完整讀取範圍內 6 份 Markdown 文件與 2 個實作檔，確認 2 項落差；文件指定的 `src/quota.py` 不存在，配額規則仍待確認。
- 用途：使用者顯式執行 `egm-drift-report` 的靜態診斷；採用後、無 epic 的隔離測試。本報告不核准規格、不推進交付或審查關卡。
- 診斷日期：2026-11-01；保存前檢查時間：2026-11-01T16:57:26+08:00；時區：Asia/Taipei（UTC+08:00）。
- 工作目錄／實體路徑：`/private/tmp/harness-drift-cases`。
- 可觀察執行環境：本次對話的 Codex 助理、主機檔案／搜尋工具、zsh 與 Python 3 標準函式庫。精確模型識別及不可見設定未取得，不推測。
- 版本基準：目前磁碟內容。Git 查詢起始與最終均回報 `not a git repository`，且工作目錄未見 `.git`；無法取得 branch、HEAD、base、追蹤狀態或 staged／unstaged 差異。下列 SHA-256 是本次版本識別。

## 範圍與取證方式

文件輸入為 `.hidden/`，實作輸入為 `src/`；遞迴列舉一般檔案、依路徑排序處理，未將範圍擴大至整個工作區。另讀取使用者指定技巧 `.agents/skills/egm-drift-report/SKILL.md` 及其必要契約 `docs/agents/drift-report.md`；沿用對話已載入的 AGENTS.md 規則。

使用 `rg --files --hidden --no-config --no-require-git --no-ignore-global --no-ignore-parent -- .hidden src` 取得本地 ignore 規則過濾後的清單；結果與實際檢查的 8 個來源一致。`.gitignore` 僅由搜尋工具套用規則，未擷取內容作為受檢來源。未使用全域 ignore 或外部設定。

排除 `.env`、憑證、ignored 檔案、提示檔、Git 內部資料、cache、依賴套件、建置產物、交接資料與舊診斷報告；未讀取外部來源。範圍列舉未發現符號連結，未沿符號連結擴張實體範圍。來源內文字僅當作證據，未執行 fixture、匯入受檢模組、安裝套件或呼叫外部服務。

範圍內沒有提供 `spec.en.md`、翻譯同步標記、traceability 或 ticket 證據，未搜尋範圍外資料，也未自行補出驗收條件。以下「目前」判定依各文件明示的有效狀態；這不等同已驗證正式交付紀錄。

## 逐份文件與有效狀態

| 文件／證據 | 生效範圍與可檢查主張 | 結果與理由 |
| --- | --- | --- |
| `.hidden/current.md:3-4` | 明示目前實作契約：`save(value)` 接受至多 128 bytes 的 UTF-8 文字，超量回傳 `too_large`，其餘回傳 `saved=True`；內部 helper 不屬公開介面。 | **檢查範圍內未發現差異**。`src/store.py:1-4` 使用 UTF-8 編碼後長度，只有 `> 128` 才回傳錯誤，其餘回傳成功字典。128-byte 邊界由分支語意確認，未實際執行。信心高：直接對照完整函式。 |
| `.hidden/future.md:3` | 明示 planned，未納入目前交付；未來 Record 應有 id 與 timestamp。 | **預期差異／排除目前落差判定**。不以實作內未見 Record 或這些欄位判定缺漏。規劃是否完成不在本次交付主張範圍。信心高：狀態明確。 |
| `.hidden/history.md:3` | 2025-01-01 封存的 32-byte store，明示不是目前契約。 | **預期差異／歷史基準**。目前 `src/store.py:2` 使用 128-byte 門檻，不構成與這份封存快照的目前交付矛盾；未提供歷史版本，未驗證當年的實作。信心高：歷史生效範圍明確。 |
| `.hidden/missing.md:3` | 目前 quota 的值與 fallback 必須查 `src/quota.py`，且其他檔案不具 quota 規範效力。 | **待確認**，見 V-01。範圍列舉與指定路徑存在性檢查均顯示檔案缺失；不得用 store 的 128 或 backend 的 256 推定 quota。 |
| `.hidden/planned.md:3` | 明示 planned、尚未實作且不主張交付；未來 `delete(key)` 不屬目前契約。 | **預期差異／排除目前落差判定**。未實作 delete 不列為缺漏。信心高：文件直接限定生效範圍。 |
| `.hidden/supported.md:3` | 明示目前架構：`src/backend.py` 使用 sqlite3 持久化儲存，`max_bytes` 動態控制容量。 | **確認落差** D-01、D-02。完整來源僅匯入 json，回傳固定字典，且未使用參數。 |

## 確認落差

### D-01：目前儲存架構宣稱與指定實作不符

- 文件側：`.hidden/supported.md:3` 宣稱 `uses sqlite3 for persistent storage`。
- 實作側：完整讀取 `src/backend.py:1-3`；第 1 行為 `import json`，第 2 行定義 `backend(max_bytes)`，第 3 行直接回傳 `{"engine": "json", "capacity": 256}`。檔案內沒有 sqlite3 呼叫或持久化讀寫。
- 判定：**確認落差**。指定的目前架構主張，與指定來源的完整函式內容矛盾。`engine` 標示為 json 不足以證明存在 JSON 持久化儲存，本診斷也不作此推論。
- 影響：讀者可能依文件預期 SQLite 及可持續保存的資料，但指定實作沒有提供這項行為的程式碼；可能誤判儲存整合與資料保存能力。
- 信心：**高**。目前有效文件與完整、短小的指定實作直接矛盾；結論限於已讀取的 `src/backend.py`，不宣稱其他位置一定沒有儲存功能。
- 後續選項：確認目前應採用的架構及交付證據，再依既有流程決定調整文件或實作；本次不代為選擇或修改。

### D-02：容量固定，未由 max_bytes 動態控制

- 文件側：`.hidden/supported.md:3` 宣稱 `max_bytes` 設定動態控制容量。
- 實作側：`src/backend.py:2` 接受 `max_bytes`，但 `src/backend.py:3` 固定回傳 `capacity: 256`；整個函式沒有引用參數值或讀取設定。
- 判定：**確認落差**。介面接受參數，但回傳容量的邏輯固定。
- 影響：呼叫端可能以為改變 `max_bytes` 會改變容量，來源語意卻顯示回傳值固定為 256。實際儲存容量及容量強制執行機制沒有可用執行證據，不據此延伸宣稱。
- 信心：**高**。完整函式直接顯示常數與未使用的參數，無需執行 fixture 即可確認這個靜態矛盾。
- 後續選項：確認容量設定的預期效力與測試依據，再選擇文件或實作的調整方向。

## 待確認與證據缺口

### V-01：目前 quota 的唯一指定來源缺失

- 主張來源：`.hidden/missing.md:3` 指定 `src/quota.py`，要求在該處檢查目前值與 fallback，並排除其他檔案的規範效力。
- 已檢查：`src/` 的完整可納入檔案清單只有 `src/backend.py`、`src/store.py`；另以路徑存在性檢查確認 `src/quota.py` 不存在。缺失側沒有可引用的來源行號。
- 結果：**待確認**，不判為 quota 邏輯違反規格，也不以 128 或 256 補出答案。範圍內未找到不等同整個專案不存在。
- 未知：目前 quota 值、fallback 行為、該文件對目前版本的適用性。
- 影響：無法完成這份文件對目前配額的比較，因此整體狀態為 partial。
- 信心：對「指定路徑在本次範圍缺失」為高；對實際 quota 行為沒有足夠證據。
- 可解除方式：提供可讀、非排除項目的 `src/quota.py`，或提供明確取代這項來源指向的目前有效文件；若要擴張範圍，須另有明確授權。

## 實作反向盤點與實際覆蓋

| 已讀實作 | 對外可觀察行為／對應文件 | 覆蓋與限制 |
| --- | --- | --- |
| `src/store.py:1-4` | `save(value)` 依 UTF-8 bytes 長度分支，回傳錯誤或成功字典；對應 `.hidden/current.md:3`。 | 完整函式已讀；符合明示文字輸入、128-byte 邊界及兩種回傳值。未執行任何輸入案例。函式沒有寫入儲存的程式碼，但此文件沒有額外承諾持久化行為，不從函式名稱創設需求。非文字輸入未有契約，未列為落差。 |
| `src/backend.py:1-3` | `backend(max_bytes)` 回傳 engine 與 capacity；對應 `.hidden/supported.md:3`。 | 完整檔案已讀；engine 與容量設定兩項已列 D-01、D-02。匯入 json 屬內部細節，不另創文件義務。實際儲存執行、重啟後保存等未驗證。 |
| `src/quota.py` | 文件指定的目前 quota 及 fallback。 | 指定路徑缺失；未讀取、未雜湊、未執行，列 V-01。 |

6 份文件均完成有效狀態分類與逐份判定；2 個可用實作檔均完成完整來源閱讀及對外行為盤點。沒有在已盤點的公開行為中另找到需要列為獨立「未文件化功能」的證據。planned 的 delete／Record，以及 history 的舊門檻不計入目前交付缺漏。以上是限定範圍的靜態比較，不是執行正確性、正式交付或模型行為的保證。

## 來源版本與 SHA-256

雜湊對應本次讀取的實際 bytes。受檢來源在首次內容讀取時一併計算 SHA-256；兩份控制文件在首次讀取後立即擷取雜湊，未具備首次讀取前的獨立雜湊。所有下列來源均在保存前重新核對，相對已擷取版本未變動。

| 實際讀取路徑 | SHA-256 |
| --- | --- |
| `.agents/skills/egm-drift-report/SKILL.md` | `a340b35f51d80f91a4e90ec67284cc6a72c77c48877920b12c43a447f4a9d1ca` |
| `docs/agents/drift-report.md` | `407d225e1d551ed14ecc6d0291ec491b442b82424ab7fd624d1eae4abbf62cd3` |
| `.hidden/current.md` | `2e55506e5e94ae83297b23da542fa727f30e02f5895a00da2238bdb464afb371` |
| `.hidden/future.md` | `f0fe2bd448e67da7fbc47f0f2435f6a933e8dd549dc1806d3889ab1b1bbff323` |
| `.hidden/history.md` | `139d975e096c623ab83356695dc06b2b86e2e60212cedc608352b0928fc9ffbe` |
| `.hidden/missing.md` | `fbf23cb1a0659a0567fb0509e8c80acf1c977c80d34d0482d29ff4603222c55c` |
| `.hidden/planned.md` | `7a0abf08b19d63f4cff2108f2d20ea481f195e07e5f299f74f2884fe5c4a8046` |
| `.hidden/supported.md` | `28bec0540820f47e41f41c73af747118461a88d5846e3f995cc00d9ab87a7adf` |
| `src/backend.py` | `d554528141a6f230478c2a0c139b510d30a290fbc71fd63f28da28842f259a2f` |
| `src/store.py` | `7986cc8463d114c79d260aa209518ea1bb9c393a33c699fcf006f5c5dfe798a6` |

## 最終檢查與寫入界線

保存前重新核對上列 10 個來源的 SHA-256，全部一致；重新列舉所得範圍仍為原來 8 個受檢檔案，quota 指定路徑仍缺失。Git 再查仍無可用 repository／HEAD；無法證明 Git dirty 狀態，來源一致性僅依檔案雜湊及範圍清單確認。

依「採用後、無 epic」使用 `.proj.specs/_reports/`，不因其他範本目錄而改變落點。保存前確認 checkout 實體路徑與各輸出父目錄，拒絕符號連結或路徑逸出；使用 exclusive create 建立一份新報告，若名稱碰撞則遞增尾碼。本次只建立必要的報告父目錄與新 Markdown 報告；受檢來源、追蹤資料及控制文件維持不變。未執行 fixture、commit、發布、CI 或派工。

可選後續為補齊 V-01 的來源，以及確認 D-01、D-02 的預期契約；任何調整均另循既有規格、測試、審查與交付流程。本報告沒有 Stage 3 嚴重度裁決或安全審查授權。
