# A 批 coverage

| 案例 | Surface | 結果與證據 |
| --- | --- | --- |
| R00 | 控制端／CLI 無模型介面 | partial：version/help、argv/cwd/profile、選定設定、trust 停用訊息、fixture 依賴與 hashes 已保存；CLI 有效 sandbox 與 managed policy 未取得。 |
| R01 | CLI 模型 | not run：控制對話 input 已達配置，啟動數 0；沒有 CLI 寫入或拒絕事件。 |
| R02 | CLI 顯式 EGM | not run：缺同條件有效寫入證據，且預算停止。沒有診斷報告。 |

fixture 的必要來源與合成比較範圍已靜態補齊；未經模型讀取驗證，不宣稱控制組成功。B／C、Claude、desktop EGM 均未啟動。
