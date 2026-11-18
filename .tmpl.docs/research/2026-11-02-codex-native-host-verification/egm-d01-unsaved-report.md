已顯式使用本專案的 `$egm-drift-report`。**靜態診斷確認 1 項漂移；主機為唯讀權限，報告未儲存。** 以下為本次新報告內容。

原定路徑：`.tmpl.docs/research/drift-reports/2026-11-02-ops-src.md`

日期時間：2026-11-02 01:35:05，Asia/Taipei。  
診斷狀態：`complete`，限本次要求的靜態來源比對；檔案交付未完成。  
Runtime：Codex，目前對話循序執行；未推測模型設定。  
Checkout：`/private/tmp/harness-native-20261102-e1rmy3p6/egm-d01`。沒有 Git repository，無法取得 branch、base、HEAD 或 staged／unstaged 狀態。

| 文件及有效狀態 | 比對結果 | 證據、影響與信心 |
|---|---|---|
| `ops/01-quota.md`：current | **確認漂移** | 第 2 行宣稱 quota 為 **37**；`src/options.py:1` 設為 **29**。`src/exporter.py:1,3–4` 匯入並回傳該值。來源所表達的上限比文件少 8 筆；高信心，雙方數值及引用關係明確。 |
| `ops/02-timeout.md`：current | 已檢查範圍未發現差異 | 第 2 行宣稱 12 秒，與 `src/options.py:2` 的 `TIMEOUT_SECONDS = 12` 一致。設定值比對為高信心；實際 timeout 是否生效仍需執行證據。 |
| `ops/03-planned.md`：planned | 預期差異／排除 | 第 2 行明示 quota 73 為未實作提案，沒有宣稱目前適用，因此不與目前的 29 判為漂移。高信心。 |
| `ops/04-history.md`：historical | 預期差異／排除 | 第 2 行明示 quota 19 屬 synthetic version H1，非目前狀態。不與目前來源直接判為漂移；H1 歷史內容本身未驗證。高信心。 |

實際覆蓋為 `ops/` 遞迴列舉所得全部 4 份 Markdown，以及 `src/` 全部 2 個實作檔，包含隱藏路徑檢查。已逐檔讀取，並在這兩個目錄內搜尋 quota、timeout、設定及匯出介面。實作盤點涵蓋 `QUOTA`、`TIMEOUT_SECONDS` 與 `export_limit()`；未發現其他需要補充記載的對外行為。這不構成整個專案或執行結果的正確性保證。

缺口與排除如下：

- `.tmpl.docs/` 存在但為空，無法讀取契約要求的 README；`docs/agents/language.md`、`domain.md` 也不存在。本次依已提供的語言規則及診斷契約處理。
- 未執行、匯入被檢查的程式，未驗證實際匯出流程或計時行為。
- 未讀取 checkout 外來源、oracle、其他案例、過去答案或既有診斷報告；未呼叫子代理、安裝套件或外部服務。
- 未修正、開票、commit 或變更任何來源與追蹤狀態。

首次讀取診斷來源時記錄以下 SHA-256；結束前重新計算，全部一致，輸入檔案清單也未變：

```text
ops/01-quota.md
2a83c3ef0492161bafbaf041d225c6b8a524ff742fc8d87a41a24c219b67eae8
ops/02-timeout.md
5c25045d36c028e7d9941a7ed84f802947f2ccd9b76821bebf86fcac650cb6bc
ops/03-planned.md
e06adbef64831bdf646684e44172329f7cc1a81d1f55f6b5f309718f0a054cb4
ops/04-history.md
b5720ffa843c33eb7d3f86174e3cd2844e759731f57f97046d18e241956e48ba
src/exporter.py
cc0aef6dbc81205ec006dae0fdda2eb1a6a83f2ae5bf8071659fd4484a2f441f
src/options.py
dd6311693dddc838fc5876f1fcfadb688cf3dd6d0129592ed1a32275703c638a
```

已讀取並於結束前核對一致的契約檔案：

```text
AGENTS.md
d90eba47efbd06424eecc9c811068f2a9996717ca5c9acaae887ab4255e53950
.agents/skills/egm-drift-report/SKILL.md
a340b35f51d80f91a4e90ec67284cc6a72c77c48877920b12c43a447f4a9d1ca
docs/agents/runtime.md
1088214a9ae85f345251ce1b0c08382bddaaf604eda48287f3ada0f7557e4b15
docs/agents/drift-report.md
407d225e1d551ed14ecc6d0291ec491b442b82424ab7fd624d1eae4abbf62cd3
docs/agents/codex.md
20ab3a45cf34c28f7f4973c4c978aaba188674add1ecb2a585b1667605db1929
```

可選後續是確認目前 quota 應採 37 或 29，再依既有流程決定如何調整；本次未選定修正方向。
