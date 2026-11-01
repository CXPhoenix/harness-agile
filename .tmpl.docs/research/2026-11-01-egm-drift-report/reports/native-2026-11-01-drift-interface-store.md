# 文件與實作漂移診斷：Storage interface

- 診斷目的：比較已宣告為目前實作規範的 `docs/interface.md` 與 `src/store.py`，辨識規範矛盾及文件缺口。
- 狀態：**complete**。兩個指定檔案的全部內容及實作可觀察介面均已完成靜態檢查；complete 表示本次比較完成，不表示沒有漂移或已完成執行驗證。
- 當地時間：2026-11-01T16:55:16+08:00；時區 `Asia/Taipei`（UTC+08:00）。使用者指定診斷日期為 2026-11-01。
- 專案情境：採用後、沒有 epic 的隔離測試專案，依使用者提供的情境選用 `.proj.specs/_reports/`。
- 實際觀察的工具環境：Python 3.14.3，`sys.platform=darwin`，zsh（runtime 提供）；模型設定未觀察，不推測。

## 範圍、版本與文件效力

Checkout 實體路徑：`/private/tmp/harness-drift-native`。本次僅診斷 `docs/interface.md` 與 `src/store.py`。另外只讀取使用者明示的 skill 及該 skill 必讀的共用契約；沿用對話已載入的 AGENTS.md 規則，未額外讀取專案規則檔。

`docs/interface.md:3` 明示「Current implemented contract」，同檔第 4 行明示「The documented limit is normative」。使用者也指定文件宣告目前已實作規範。因此本次以目前適用的規範判讀，沒有證據可將 64 bytes 上限視為計畫、歷史快照或刻意取捨。第 5 行唯一直接引用為 `src/store.py`，已完整讀取。未引用翻譯規範、traceability 或 ticket，亦未擴大搜尋其他來源。

此目錄的 Git 查詢均回報 `fatal: not a git repository (or any of the parent directories): .git`，故無法取得 base、branch、HEAD、tracked/untracked 分類、ignored 狀態或 staged/unstaged 差異。兩個診斷檔案均為明確指定的常規檔案，非 symlink，以目前磁碟內容及 SHA-256 識別版本。未將 Git 資訊不可得誤判為工作目錄乾淨。

首次讀取來源時間：2026-11-01T16:54:28+08:00。以下為實際依據的檔案；skill 與契約屬流程依據，另外兩個檔案屬診斷證據。

| 路徑 | 首次版本 SHA-256 | 最終重查 SHA-256 |
| --- | --- | --- |
| `.agents/skills/egm-drift-report/SKILL.md` | `a340b35f51d80f91a4e90ec67284cc6a72c77c48877920b12c43a447f4a9d1ca` | `a340b35f51d80f91a4e90ec67284cc6a72c77c48877920b12c43a447f4a9d1ca` |
| `docs/agents/drift-report.md` | `407d225e1d551ed14ecc6d0291ec491b442b82424ab7fd624d1eae4abbf62cd3` | `407d225e1d551ed14ecc6d0291ec491b442b82424ab7fd624d1eae4abbf62cd3` |
| `docs/interface.md` | `b4becc853a6e2be16670e40e1fa85cf95870d6376b8b7b9ee53f60103a0ede10` | `b4becc853a6e2be16670e40e1fa85cf95870d6376b8b7b9ee53f60103a0ede10` |
| `src/store.py` | `7986cc8463d114c79d260aa209518ea1bb9c393a33c699fcf006f5c5dfe798a6` | `7986cc8463d114c79d260aa209518ea1bb9c393a33c699fcf006f5c5dfe798a6` |

## 診斷結論

**確認一項漂移：規範上限是 64 bytes，程式實際使用 128 bytes。** 依原始碼靜態邏輯，65–128 bytes 的 UTF-8 文字會得到成功回傳，而規範要求回傳 `{"error": "too_large"}`。兩邊皆採 UTF-8 編碼後的 byte 數；矛盾在數值上限。

另有一項已觀察的文件缺口：成功回傳 `{"saved": True}` 未記載於指定文件。這是可確認的未記載介面資訊；文件沒有宣告成功回傳格式，也沒有完整列舉所有回傳值的要求，因此本報告不將此缺口另算為已確認的規範矛盾。

## 逐項主張與雙側證據

| 項目 | 文件主張與位置 | 實作觀察與位置 | 結果與信心 |
| --- | --- | --- | --- |
| UTF-8 byte 計量 | `docs/interface.md:3`：`save(value) accepts UTF-8 text up to 64 bytes.` | `src/store.py:2`：`len(value.encode("utf-8"))`，計算編碼後的 byte 數。 | 已檢查範圍內未發現計量方式差異；高信心，直接可見編碼及長度運算。 |
| 允許長度上限 | `docs/interface.md:3-4`：上限 64 bytes，且此上限為 normative。 | `src/store.py:2`：`> 128` 才進入錯誤分支；第 4 行為其他輸入回傳成功。 | **Confirmed drift**；高信心，規範與分支常數直接矛盾。 |
| 超量時的回傳內容 | `docs/interface.md:4`：`On overflow, save returns {"error": "too_large"}.` | `src/store.py:3`：`return {"error": "too_large"}`。 | 錯誤內容一致；觸發範圍受上述上限漂移影響，並非完整符合規範。高信心。 |
| 對應介面 | `docs/interface.md:3,5`：介面為 `save(value)`，實作為 `src/store.py`。 | `src/store.py:1`：`def save(value):`。 | 已檢查範圍內未發現名稱、參數或引用位置差異；高信心。 |

### D1：65–128 bytes 被當作成功

- 文件側：`docs/interface.md:3` 設定 64 bytes 上限；`docs/interface.md:4` 指定超量回傳錯誤，並明示上限具規範效力。
- 程式側：`src/store.py:2-4` 只在 byte 數大於 128 時回傳錯誤，其餘回傳 `{"saved": True}`。
- 影響：呼叫端若依文件以 64 bytes 為界判斷成功與失敗，會在 65–128 bytes 區間取得與規範不符的成功結果。此結論僅涉及回傳與限制；沒有證據可推論實際儲存、持久化或下游資料流。
- 信心：高。兩個檔案短小且已完整讀取，無其他分支、委派呼叫或動態設定出現在指定實作中。結論由原始碼推導，未執行 fixture。
- 未解事實：目前證據未說明為何使用 128，也無法認定應改文件或改程式；後續修正需另行決策。

下表為靜態推導的邊界，並非測試執行結果。前提為可正常編碼為 UTF-8 的文字。

| UTF-8 byte 長度 | 文件規範 | 原始碼回傳 | 判定 |
| --- | --- | --- | --- |
| 0–64 | 接受；成功回傳格式未指定 | `{"saved": True}` | 接受範圍一致 |
| 65–128 | `{"error": "too_large"}` | `{"saved": True}` | 確認漂移，包含 65 及 128 邊界 |
| 129 以上 | `{"error": "too_large"}` | `{"error": "too_large"}` | 錯誤行為一致 |

### G1：成功回傳格式未記載

完整檢查 `docs/interface.md:1-5`，其中只描述超量錯誤，沒有成功回傳格式；`src/store.py:4` 明確回傳 `{"saved": True}`。此處的缺少證據來自指定文件的完整內容檢查，沒有虛構不存在的行號，也不主張整個專案沒有其他說明。

影響：僅依此文件的介面使用者無法確定成功回傳資料的形狀。對「指定文件未記載」的信心為高；是否必須補上仍需確認文件涵蓋政策，本次未發現可用來要求完整回傳規格的額外規範。

## 實作盤點、搜尋及實際涵蓋

採用穩定順序完整讀取兩個指定檔案並逐行對照；未做全專案搜尋。搜尋範圍僅為 `docs/interface.md:1-5` 與 `src/store.py:1-4` 的完整內容，足以盤點該函式在文字輸入範圍內的所有分支。

| 實作可觀察項目 | 涵蓋情形 |
| --- | --- |
| 公開函式 `save(value)` 與單一參數 | 已對照文件。 |
| UTF-8 編碼及 byte 長度判斷 | 已檢查，計量方式一致，門檻不一致。 |
| 超量錯誤 dictionary | 已檢查回傳內容及觸發條件。 |
| 非超量成功 dictionary | 已盤點，記錄為文件缺口。 |
| 動態上限、其他函式或委派呼叫 | 指定實作全文未見；未推論專案其他路徑不存在。 |
| 非文字輸入的例外行為 | 文件僅涵蓋 UTF-8 文字，未建立非文字輸入的驗收要求；不判定為漂移。 |
| 執行時、整合或服務行為 | 未執行、未驗證；不是本次靜態比較的完成宣稱。 |

排除：其他測試提示檔、測試程式、設定、其他文件及來源、過往報告、Git 內部內容、憑證、`.env`、cache、依賴及建置產物均未讀取或搜尋。沒有 epic 查找或 tracker 變更。只使用本地檔案讀取與版本查詢，未安裝套件、呼叫外部服務、執行 fixture 程式或派子代理。

## 最終版本檢查與限制

寫入前於 2026-11-01T16:55:16+08:00 重新計算四個已讀依據檔案的 SHA-256。全部與首次版本相同，無 stale 證據。

最終 Git 重查結果：

- `git rev-parse --show-toplevel`：exit 128；fatal: not a git repository (or any of the parent directories): .git
- `git branch --show-current`：exit 128；fatal: not a git repository (or any of the parent directories): .git
- `git rev-parse HEAD`：exit 128；fatal: not a git repository (or any of the parent directories): .git
- `git status --porcelain=v1 --untracked-files=all -- docs/interface.md src/store.py`：exit 128；fatal: not a git repository (or any of the parent directories): .git

初次與最終 Git 查詢皆無法取得 repository 資訊；可核對的是已讀來源內容沒有變動，不能宣稱整個目錄或 tracker 狀態均經 Git 驗證。報告只代表這兩個檔案的靜態診斷，不證明整體正確性、儲存持久性、實際呼叫端行為或驗收完成，也不授予 Stage 3 或安全審查裁定。

可選後續：先確認 64 或 128 bytes 哪一個應保留為正式規範，再依既有流程調整對應來源；若需要執行驗證，可另行授權針對 64、65、128、129 bytes 及多 byte 文字設計邊界測試。成功回傳格式也可另行確認是否納入文件。此次不修改來源、不建立 ticket、不 commit、不發布或觸發 CI。
