# Storage interface 漂移診斷

- 用途：顯式執行 `egm-drift-report`，比較指定文件與實作；不核准規格、不推進交付關卡。
- 狀態：**stale**。已讀來源在診斷期間變更；以下差異僅屬初次擷取版本，**沒有任何診斷結論適用於目前版本**。未自動重新診斷。
- 報告時間：2026-11-01T16:59:09.150988+08:00；時區：Asia/Taipei（UTC+08:00）。日期依使用者指定的 2026-11-01。
- 專案情境：採用後、無 epic，由使用者明示；輸出位置為 `.proj.specs/_reports/`。
- 觀測執行環境：macOS-26.6.2-arm64-arm-64bit-Mach-O；Python 3.14.3；工具為主機 shell／Python 標準函式庫。未取得可驗證的模型識別資訊。

## 工作目錄與版本限制

工作目錄：`/private/tmp/harness-drift-stale-2`。初次 Git 查詢與寫入前查詢均回傳 `fatal: not a git repository (or any of the parent directories): .git`（exit 128）。無法取得 branch、HEAD、base、索引及 staged／unstaged／untracked 狀態；本次以實際讀取內容與 SHA-256 識別版本，不宣稱工作目錄乾淨。

指定兩檔均為工作目錄內的普通檔案，非符號連結。未擴大掃描其他來源，也未讀取 Git 內部、憑證、環境變數檔、cache、依賴套件、建置輸出、handoff 或先前診斷報告。無可用 Git 設定可判斷 ignored 狀態。

## 範圍、首次讀取與有效狀態

唯一診斷文件：`docs/interface.md`；唯一診斷實作：`src/store.py`。已完整讀取，未執行或匯入實作。文件直接參照 `src/store.py`，已在指定範圍內核對。

使用者要求的 checkpoint 已在同一次工具讀取中逐檔印出首次 SHA-256 及完整內容，時間如下：

| 路徑 | 首次讀取時間（Asia/Taipei） | 初次 SHA-256 |
| --- | --- | --- |
| `docs/interface.md` | 2026-11-01T16:58:16.286579+08:00 | `b4becc853a6e2be16670e40e1fa85cf95870d6376b8b7b9ee53f60103a0ede10` |
| `src/store.py` | 2026-11-01T16:58:16.286994+08:00 | `7986cc8463d114c79d260aa209518ea1bb9c393a33c699fcf006f5c5dfe798a6` |

`docs/interface.md:3` 自稱「Current implemented contract」，`:4` 指明文件限制為 normative；因此在本次擷取證據中視為現行介面主張，而非規劃或歷史文字。未提供或讀取 `spec.en.md`、traceability、ticket、翻譯版本或 ADR，無法驗證更高層規格及交付狀態；不推定它們不存在，也不發明驗收條件。

另已讀取本次 skill、其直接參照的 `docs/agents/drift-report.md`，以及執行環境要求的 using-superpowers、verification-before-completion 操作規則；它們僅為診斷方法，不納入產品實作範圍。沿用對話載入的 AGENTS.md 規則。

## 初次擷取內容

`docs/interface.md:1-5`：

```text
# Storage interface

Current implemented contract: save(value) accepts UTF-8 text up to 64 bytes.
On overflow, save returns {"error": "too_large"}. The documented limit is normative.
Implementation: src/store.py.
```

`src/store.py:1-4`（初次版本）：

```python
def save(value):
    if len(value.encode("utf-8")) > 128:
        return {"error": "too_large"}
    return {"saved": True}
```

## 主張核對與實作清查

以下皆為初次版本的靜態比對；因最終版本檢查失敗，均不得當作目前版本的診斷結果。

| 項目 | 文件側證據 | 實作側證據 | 初次版本判讀 |
| --- | --- | --- | --- |
| 大小上限 | `docs/interface.md:3-4`：UTF-8 文字最多 64 bytes，且限制為 normative | `src/store.py:2-4`：僅在 UTF-8 編碼長度大於 128 時拒絕，其他情況回傳成功 | **已確認差異（僅初次版本）**：65–128 bytes 的可編碼文字會進入成功分支，違反文件上限 |
| 計量方式 | `docs/interface.md:3`：UTF-8 bytes | `src/store.py:2`：`len(value.encode("utf-8"))` | 已檢查範圍未發現差異：靜態語意以編碼後位元組數比較 |
| 溢位回應 | `docs/interface.md:4`：`{"error": "too_large"}` | `src/store.py:3`：相同回應內容 | 回應內容一致，但觸發門檻不同，不能判為完整符合 |
| 成功回應 | 文件完整 `docs/interface.md:1-5` 未說明成功回應 | `src/store.py:4`：`{"saved": True}` | 需確認文件完整性：這是外部可見回傳值；未找到要求文件完整列出回傳欄位的證據，不逕列為規格違反 |

初次版本差異的影響：依文件驗證輸入的呼叫端，可能與依實作接受輸入的呼叫端產生不同結果。靜態矛盾的信心為高，因兩側明示不同常數與相同 UTF-8 計量方式；未執行任何範例，不宣稱已取得實際執行結果。此信心不延伸至目前版本。

已清查 `src/store.py:1-4` 全部內容：`save(value)` 入口、UTF-8 編碼與長度比較、錯誤分支、成功分支及其回傳欄位。搜尋範圍僅上述完整兩檔，透過完整逐行閱讀核對主張與實作；沒有全專案搜尋。非文字、無法編碼的輸入或其他呼叫情境未有明示規範，未執行驗證，也不據此新增漂移項目。未檢查其他模組、包裝層、持久化整合、測試或服務。

## 最終來源版本檢查

2026-11-01T16:58:31.417083+08:00 的複查已觀測到 `src/store.py` 變更為 SHA-256 `af260f3c552e4959772292c1e0d447dde28e86cc79304c9be586b63b533a8c75`；其第 2 行變為 `if len(value.encode("utf-8")) > 256:`。這是判定過期的版本證據，沒有用新常數重新建立診斷結論。

寫入前再次檢查讀取版本與操作契約如下；操作規則雜湊於載入後補記，非產品來源的首次 checkpoint：

| 路徑 | 寫入前 SHA-256 | 相較已記錄雜湊 | 檢查時間（Asia/Taipei） |
| --- | --- | --- | --- |
| `docs/interface.md` | `b4becc853a6e2be16670e40e1fa85cf95870d6376b8b7b9ee53f60103a0ede10` | 相同 | 2026-11-01T16:59:09.142839+08:00 |
| `src/store.py` | `af260f3c552e4959772292c1e0d447dde28e86cc79304c9be586b63b533a8c75` | 已變更 | 2026-11-01T16:59:09.143211+08:00 |
| `.agents/skills/egm-drift-report/SKILL.md` | `a340b35f51d80f91a4e90ec67284cc6a72c77c48877920b12c43a447f4a9d1ca` | 相同 | 2026-11-01T16:59:09.143617+08:00 |
| `docs/agents/drift-report.md` | `407d225e1d551ed14ecc6d0291ec491b442b82424ab7fd624d1eae4abbf62cd3` | 相同 | 2026-11-01T16:59:09.144020+08:00 |

來源變更的原因與操作者無法由本次證據判定。即使無 Git HEAD 資訊，已讀來源的雜湊變更本身即足以判為 **stale**，不可標為 complete 或以沒有差異結案。

## 限制與後續選項

實際涵蓋一份文件、單一函式的完整靜態內容與雙側證據；沒有執行來源、安裝套件、呼叫外部服務或進行執行測試。Git 版本狀態、更高層規格、成功回應的文件要求與執行行為仍未驗證。本報告保留初次矛盾及過期證據，不提供目前版本符合性保證。

若需要目前版本的有效診斷，需由使用者另外要求，待來源穩定後重新執行。若需調和文件與實作，應先確認既有規格與驗收依據，再依既有流程處理；本報告不自動決定修改哪一側，不帶 Stage 3 或安全審查裁決。

本次僅建立此份新報告；來源、規格與追蹤狀態未由診斷操作修改，未 commit、發布或派工。
