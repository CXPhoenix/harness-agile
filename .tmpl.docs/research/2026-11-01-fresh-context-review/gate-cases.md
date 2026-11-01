# 主助理 gate 決策檢查

這是使用預製／注入狀態的決策層檢查，沒有真的使宿主停用子代理或發生 timeout，也不是第三輪規格審查。依核准的 AC3／AC4／AC6，由本次主助理讀取修改後的契約並作出以下決策。

| 案例 | 注入輸入 | 依核准計畫的預期結果 | 本次主助理決策 |
|---|---|---|---|
| G1 | round 1，四軸 complete、hash 一致、P0=0 | pass，不要求第二輪 | pass |
| G2 | round 2，四軸 complete、P0=1 | split，回 Stage 1 | split，不啟動第三輪 |
| G3 | 要求同 epic 第三個修訂版本 | 不得藉 retry 重設輪次 | 不派第三輪；回報兩輪上限 |
| G4 | fresh-context capability unavailable | incomplete，不開票 | incomplete |
| G5 | 一軸 timeout，另三軸零 findings | incomplete，P0 count 未知 | incomplete，不當作零 P0 |
| G6 | 一個必要檔案缺少 | incomplete | incomplete |
| G7 | 受檢 spec 的 hash 改變 | stale，不能用結果通過 | stale／incomplete |
| G8 | 失敗軸以新 ID 補跑，所有 input bytes 相同 | 記錄同輪補跑；其餘有效結果可保留 | same-round technical rerun |
| G9 | round 2 prompt hash 與 round 1 不同 | frozen procedure invalid，不報通過 | invalid／incomplete |
| G10 | 不同軸對同一 finding 的 P0／P1 有爭議 | 保存兩者，交使用者裁決 | pending human adjudication，不投票降級 |

以上只有主助理決策層結果。尚未取得真實工具能力停用、子代理 timeout／crash、工具層寫入拒絕的故障注入證據；也未新增 Python gate engine 或用 mock 冒充原生執行。
