# 文件與實作漂移診斷：Storage interface

- 診斷狀態：**complete**。已完成指定兩個檔案的靜態逐項比對與實作行為盤點；此狀態不表示沒有漂移，也不代表執行驗證或交付核准。
- 目的：檢查宣告目前已實作的介面規範與指定實作是否一致。
- 診斷日期：2026-11-01；最終來源複核時間：2026-11-01T16:57:18+08:00；時區：Asia/Taipei（UTC+08:00）。
- 專案情境：使用者明確指定為採用後、沒有 epic 的隔離測試專案。
- 工作目錄／checkout：`/private/tmp/harness-drift-native`。
- 已觀測執行環境：Darwin 25.6.0；檔案讀取、雜湊與報告建立使用 Python 3.14.3 標準函式庫。未執行被診斷程式；未取得可驗證的模型識別字或設定。

## 來源版本與範圍

使用目前工作目錄的實際檔案內容。Git 查詢回覆 `fatal: not a git repository (or any of the parent directories): .git`；因此沒有可記錄的 branch、HEAD 或 Git base，亦無法判定 tracked／untracked、staged／unstaged、ignored 或相關 dirty state。兩個明確指定的普通檔案仍可用 SHA-256 定位。本次 base 為讀取時的檔案快照；沒有其他歷史版本比較。

診斷輸入只有 `docs/interface.md`（全文 5 行）與 `src/store.py`（全文 4 行）。實作檢查範圍只有 `src/store.py` 的全部內容，未擴大搜尋其他路徑。文件第 5 行直接指向的實作正是本次指定檔案。

另僅讀取作業所需的 `.agents/skills/egm-drift-report/SKILL.md` 與其明確要求的 `docs/agents/drift-report.md`；這兩者是診斷規則，並非額外診斷對象。適用的 AGENTS.md 規則沿用對話已提供內容，未另外搜尋規則檔。首次解析契約相對路徑時曾嘗試不存在的 `.agents/docs/agents/drift-report.md`，未讀取任何內容，隨即改用正確契約路徑。

| 實際讀取路徑 | SHA-256 | 最終複核 |
| --- | --- | --- |
| `.agents/skills/egm-drift-report/SKILL.md` | `a340b35f51d80f91a4e90ec67284cc6a72c77c48877920b12c43a447f4a9d1ca` | 未變更 |
| `docs/agents/drift-report.md` | `407d225e1d551ed14ecc6d0291ec491b442b82424ab7fd624d1eae4abbf62cd3` | 未變更 |
| `docs/interface.md` | `b4becc853a6e2be16670e40e1fa85cf95870d6376b8b7b9ee53f60103a0ede10` | 未變更 |
| `src/store.py` | `7986cc8463d114c79d260aa209518ea1bb9c393a33c699fcf006f5c5dfe798a6` | 未變更 |

所有實際讀取路徑均為本工作目錄內的普通檔案，未透過 symlink 跨越範圍。未讀取其他測試提示檔、其他規範、測試、tracker、epic、舊報告、憑證、環境設定或其他實作；未檢查其他介面、呼叫端或部署狀態。未呼叫外部服務，未安裝套件，未執行 fixture 程式、測試或匯入 `src/store.py`。

## 文件有效狀態

`docs/interface.md:3` 明示 `Current implemented contract`；第 4 行明示 `The documented limit is normative.`，且使用者明確確認文件宣告目前已實作規範。因此此次把 64 bytes 視為現行適用規範，不視為計畫或歷史快照。沒有使用翻譯副本、ticket 或其他文件替代這份指定規範；未檢查範圍外的 `spec.en.md` 或 traceability。

## 主張與結果

| 文件主張 | 實作證據 | 結果 |
| --- | --- | --- |
| `save(value)` 接受 UTF-8 文字（`docs/interface.md:3`）。 | `src/store.py:1` 定義相同函式；第 2 行以 `value.encode("utf-8")` 的結果計算長度。 | 指定範圍內未發現函式名稱或計量單位差異；大小限制另見 D-01。這不等於所有輸入型別皆經執行驗證。 |
| 現行上限為 64 bytes，超過上限回傳 `{"error": "too_large"}`（`docs/interface.md:3-4`）。 | `src/store.py:2-4` 僅在 UTF-8 編碼長度 `> 128` 時回傳該錯誤，其餘回傳 `{"saved": True}`。 | **Confirmed drift：D-01**。65–128 bytes 的可編碼文字會走成功回應分支，與文件矛盾。 |
| 文件指定實作為 `src/store.py`（`docs/interface.md:5`）。 | 已完整讀取指定路徑，函式位於 `src/store.py:1-4`。 | 指定範圍內未發現參照路徑差異。 |

### D-01：64 bytes 規範與 128 bytes 判斷不一致

- 文件側：`docs/interface.md:3` 的 `up to 64 bytes`，以及 `docs/interface.md:4` 的 overflow 錯誤規則。
- 實作側：`src/store.py:2` 為 `if len(value.encode("utf-8")) > 128:`；`src/store.py:3` 回傳 `{"error": "too_large"}`；`src/store.py:4` 回傳 `{"saved": True}`。
- 實際差異：對 UTF-8 編碼成功的文字，65–128 bytes（含兩端）按文件應回傳 `too_large`，卻按目前分支回傳成功。
- 影響：依文件採用 64 bytes 邊界的呼叫端，會觀察到與規範不同的成功／錯誤結果。此證據沒有證明資料實際寫入任何儲存媒介。
- 信心：**高**。現行且明示為 normative 的文件與直接常數比較互相矛盾，無須推測其他檔案或服務。

以下是依文字規範及程式分支推導的邊界表，**不是執行結果**：

| 可編碼文字的 UTF-8 長度 | 文件要求 | 實作分支推導 |
| --- | --- | --- |
| 0–64 bytes | 在允許範圍內；成功回傳格式未記載 | `{"saved": True}` |
| 65–128 bytes | `{"error": "too_large"}` | `{"saved": True}`，確認漂移 |
| 大於 128 bytes | `{"error": "too_large"}` | `{"error": "too_large"}`，這段行為一致 |

## 實作盤點與文件缺口

已檢查 `src/store.py:1-4` 的完整實作：函式入口、UTF-8 編碼、以 bytes 長度比較、溢位錯誤回傳，以及成功回傳；沒有尚未讀取的指定範圍內程式碼。

- **G-01：成功回傳格式未記載。** `src/store.py:4` 明確回傳 `{"saved": True}`，但完整的 `docs/interface.md:1-5` 僅記載錯誤格式，沒有成功回傳格式。這是已確認的介面文件覆蓋缺口；是否要求固定成功格式成為 normative 規範，仍**需要確認**，不另推定為已確認的違規。影響是呼叫端缺少成功回傳形狀的文字依據；缺漏觀察的信心為高，規範義務則無足夠證據。可由規範維護者確認成功回傳是否屬於公開介面承諾。
- UTF-8 編碼失敗或非文字輸入的處理方式沒有規範承諾；未把這些未指定的行為判為漂移。
- 函式名稱與文件標題不足以證明持久儲存承諾。讀取的函式本體只呈現編碼、比較與回傳，未據此推論整個專案是否具備儲存能力。

## 最終來源複核、限制與後續選項

寫入報告前已重新計算上述四個實際讀取檔案的 SHA-256，全部與捕捉值相同；再次查詢 Git 仍顯示此目錄不是 Git repository，未觀察到版本環境改變。因此結果不是 stale。無 Git 的限制使此次只能確認列出來源的位元組穩定，不能證明整個專案沒有其他變更。

本次靜態比對已完整涵蓋指定兩個檔案；未執行的項目為實際呼叫、測試、呼叫端相容性、服務及持久化驗證，這些均不在授權範圍。靜態程式分支足以確認 D-01，但不構成執行成功或全專案正確性保證。

後續可先由規範維護者確認要維持 64 bytes 或調整規範，再依既有流程處理程式或文件；另可確認成功回傳格式是否需寫入介面規範。本次未選擇修正方向，未變更來源、規範、tracker、ticket 或任何 gate，未 commit、merge、發布、觸發 CI 或派出子代理。唯一新增產物為本報告。
