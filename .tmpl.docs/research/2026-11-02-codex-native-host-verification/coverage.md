# Coverage report

執行日期：2026-11-02（Asia/Taipei）。`blocked` 是測試受阻；`stale／incomplete／complete` 是診斷或 gate 狀態，兩者不混用。S07 有局部證據，但整列未完成。

| 案例／surface | 實際新啟動 | 測試結果 | 可核對覆蓋與狀態 | 尚未覆蓋及原因 |
| --- | ---: | --- | --- | --- |
| S01 Desktop 四軸控制組 | 4 | pass | 原生 fresh 參數、4 個唯一 IDs、36／36 read hashes、來源 unchanged、有效零 P0 | 僅合成 fixture，不是一般缺陷發現率或全部 filesystem 隔離 |
| S02 Desktop timeout | 0 | blocked | 能力盤點，未啟動 | 無安全的原生指定軸 timeout／pause 注入；不能用取消冒充 |
| S03 Desktop 同 bytes 補跑 | 0 | skipped_dependency | S02 未成立，沒有補跑 | 沒有當次技術補跑證據 |
| S04 Desktop 取消 | 1 | pass | running→interrupt ack→turn_aborted；無完整回覆，不作零 findings | 未必已讀必要資料；用量 missing，不是 timeout／crash |
| S05 Desktop crash | 0 | blocked | 能力盤點 | 無可安全異常終止的獨立 worker 控制 |
| S06 Desktop fresh 停用 | 0 | blocked | 能力盤點 | 無隔離停用介面，不修改全域設定或耗盡槽位 |
| S07 Desktop stale | 2／原計畫4 | blocked（預算）；局部證據有效 | 真實首讀後 64 ms 注入，old／new hash 不同；parent 拒收同版四軸通過 | 剩餘兩軸未啟動；不列完整 pass |
| S08 Desktop 缺輸入 | 0 | blocked（預算） | 僅準備隔離 fixture，沒有模型呼叫 | 未驗證實際 missing-input 回覆 |
| S09 決策 replay | 0 | pass（決策層） | G1–G10 與既有四軸／兩輪／P0 規則對照 | 不代表所有狀態已原生注入 |
| D01 CLI 控制組 | 1 | blocked（落盤前提） | seeded drift、相符、planned／history 判讀有原生證據；來源 unchanged，無報告保存 | session 回報唯讀；fixture 部分規範脈絡缺漏；完整控制組未成立 |
| D02 Desktop 控制組 | 0 | blocked（能力） | 無當次模型證據 | 沒有使用者提供的新頂層測試 session |
| D03 CLI dirty | 0 | skipped_dependency | D01 未建立完整控制組，停止新 CLI 案例 | staged／unstaged／untracked／部分 staged 均未原生測試 |
| D03 Desktop dirty | 0 | blocked（能力） | 無當次模型證據 | 同 D02；不能借用 CLI 結果 |
| D04 CLI read denial | 0 | skipped_dependency | 控制端無模型 EACCES 探針成立 | 尚未由模型讀取不可讀來源，不列 partial 行為通過 |
| D05 CLI write denial | 0 | skipped_dependency | 控制端無模型 EACCES 探針成立 | D01 無落盤不抵用本列；沒有受控模型寫入拒絕證據 |
| D06 CLI exclusive-create 競爭 | 0 | skipped_dependency | 無模型／競態注入 | D01 前提未成立；建立前同步 hook 亦未確認 |
| D07 CLI 軟截止 | 0 | skipped_dependency | 無模型／steering 注入 | D01 前提未成立；exec 入口無已確認的進行中 steering |
| D08 Desktop 硬中止 | 0 | blocked（能力） | 無當次 EGM 證據 | 缺新頂層 session；S04 reviewer 取消不能抵用 |
| D09 Desktop 非顯式查詢 | 0 | blocked（能力） | 無當次 EGM 證據 | 缺新頂層 session；CLI 歷史結果不抵用 |
| D10 Desktop stale | 0 | blocked（能力） | 無當次 EGM 證據 | 缺新頂層 session；Stage 3 S07 與 CLI 歷史 stale 不抵用 |
| D11 Desktop write denial | 0 | blocked（能力） | 無當次 EGM 證據 | 缺新頂層 session／該身分的受控拒絕前提 |
| Claude 全部 | 0 | deferred_by_user | 僅保留延期紀錄，未查登入 | 另行授權後再按該宿主規劃、核准與執行 |

來源證據：desktop-results.json、desktop-launch-controls.json、各 native_* 原生 trace／result、stage3-s07-injection.json、egm-d01-trace.jsonl、permission-probe.json。所有未執行列都不計入有效零 findings，也不自行新增為交付 gate。
