# 逐例原生紀錄

日期：2026-11-02，Asia/Taipei。模型與 effort 的 parent 核驗值見 desktop-results.json；reviewer 自評 unknown 仍完整保留於原生結果，未改寫原答覆。

## S01

| 軸 | Session UUID | 結果 |
| --- | --- | --- |
| Completeness | 01a1982b-ff81-7001-b68d-210c9f3211e5 | complete；9／9 hash/read；P0/P1/P2=0 |
| Verifiability | 01a1982c-0996-7832-834e-a085997ef88c | complete；9／9 hash/read；P0/P1/P2=0 |
| Contract conflict | 01a1982c-7f92-7742-a056-1729e259d239 | complete；9／9 hash/read；P0/P1/P2=0 |
| Red team | 01a1982c-8a33-7930-9b49-d3401f2d86dd | complete；9／9 hash/read；P0/P1/P2=0 |

主助理逐項核對原生工具輸出與 stage3-s01-manifest.json：36／36 必要 hash 出現於實際讀取輸出。封包全部 bytes 在四軸結束後不變。結論僅為這份合成 fixture 的有效第一輪零 P0，不為任何真實產品開票。

## S04

原生啟動 `/root/native_s04_cancel` 後立即 interrupt，工具回傳 previous_status=running。目標原生事件時序：17:35:44.467Z task_started；17:35:46.945Z turn_aborted。沒有 task_complete、有效 findings 或可用 usage，沒有把此軸當成零 P0。僅測得取消生命週期；未證明必要來源已讀，也沒有宣稱 crash／timeout。

## S07

首次受檢 contract SHA-256：`3c98b6bbe3090544fdda65efd6999a1d6681304735060fa4ccd05739d70aa21c`。

- 17:36:01.820Z：`/root/native_s07_completeness` 的實際工具輸出已包含上述 contract bytes/hash。
- 17:36:01.883849Z：控制端只修改 S07 fixture 的 contract，追加上限由 99 改為 49 的 revision；當時沒有該 child 的 task_complete。
- 新 SHA-256：`8bc8cc5fe04c0b5928ef25c3b145d4405b861cd6c3d088628c70dff83c377f6e`。
- Completeness 回報舊 hash；Verifiability 回報新 hash。它們各自的零 findings 不足以證明同一個 snapshot 通過。

主助理：**stale／incomplete，不計 P0 總數、不通過 gate、不自動補跑。** 預算警戒後沒有啟動剩餘 Contract conflict／Red team。故本例有真實的讀取後變動及拒收證據，但原表要求的四軸執行未完成，不列完整 pass。

## D01

原生 CLI 新 session 的完整事件、用量與 final message 已保存。`ops/01-quota.md` 宣稱 37，`src/options.py` 實際為 29；timeout=12 相符，planned=73 與 historical=19 均未被誤判為 current drift。未執行被檢查的 Python，也沒有子代理。

約 58.845 秒正常完成，exit code=0。**退出成功不等於案例成功**：沒有新增報告或任何檔案，session 明示未保存；模型輸出的診斷狀態 complete 與測試 blocked 分開記錄。egm-d01-unsaved-report.md 是控制端從 final message 保存的證據副本，不能宣稱是 skill 成功落盤的報告。

## S09：G1–G10 決策 replay

對照既有 gate-cases 與目前 review.md，本次主助理採以下決策。這是整理既有契約，不是新增模型案例、兩輪 live 執行或 mock runner。

| G | 本次判斷 |
| --- | --- |
| G1 R1 四軸有效、hash 一致、P0=0 | pass；S01 有當次原生證據，不要求第二輪 |
| G2 R2 P0=1 | split 回 Stage 1；本次未 live 注入此內容結果 |
| G3 要求第三個修訂版 | 不派第三輪；不能用 retry 重新計輪 |
| G4 fresh 不可用 | incomplete；本次沒有原生能力停用證據 |
| G5 一軸 timeout | incomplete、P0 count 未知；S04 是取消，不能抵用 timeout |
| G6 必要檔缺少 | incomplete；S08 本次因預算未啟動 |
| G7 來源 hash 改變 | stale／incomplete；S07 有當次讀取後注入證據 |
| G8 同 bytes 新 ID 技術補跑 | 同輪補跑；本次沒有執行 S03，不聲稱已補跑通過 |
| G9 prompt hash 改變 | frozen procedure invalid；不宣稱原流程通過 |
| G10 P0／P1 爭議 | 保留兩方交使用者裁決；不投票、不增派第五軸 |

未執行項目及其依賴、能力、預算原因逐列保留在 coverage.md，沒有將未執行寫成 clean。
