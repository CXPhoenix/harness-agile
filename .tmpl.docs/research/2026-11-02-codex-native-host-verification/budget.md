# 實際預算與用量

日期：2026-11-02，Asia/Taipei。資料截止 UTC 2026-11-01T17:40:09.993Z；原生 usage 快照見 [usage-final-snapshot.json](usage-final-snapshot.json)。

## 啟動與時間

| 批次 | 實際 | 核准含預留上限 |
| --- | ---: | ---: |
| A．Desktop reviewer | 7（S01×4、S04×1、S07×2） | 19 |
| B．CLI EGM | 1（D01） | 7 |
| C．Desktop EGM | 0 | 7 |
| 合計 | **8** | **33** |
| 技術補跑 | **0** | **4，已包含在33內** |
| Claude | **0** | **0，延後** |

父任務開始 UTC 2026-11-01T17:31:53.504Z，結案量測 UTC 2026-11-01T17:40:42.739199+00:00；可量測經過時間約 **8.8 分鐘**（含準備、等待及整理，非純模型時間）。沒有達 6 小時上限。單一 CLI session 約 58.845 秒；desktop 每例起訖見 desktop-results.json，均在 6 分鐘內。沒有單例 deadline 後持續執行的測試程序。

## 可見原生 token 統計

| 範圍 | Input（含 cached） | Cached input | Output | Reasoning output（另列） |
| --- | ---: | ---: | ---: | ---: |
| 主助理本次任務的可見累計差額 | 5,438,806 | 5,389,184 | 34,009 | 13,140 |
| 6 個已完成 desktop reviewer | 660,106 | 577,024 | 10,517 | 1,438 |
| 1 個 CLI session | 238,294 | 206,720 | 4,476 | 1,122 |
| 已知合計下限 | 6,337,206 | 6,172,928 | 49,002 | 15,700 |

**這是可核對下限，不是精確總帳或金額。** S04 已取消，原生 token_count 沒有可用 usage，未當成 0；最後回覆及截止後事件也尚未計入。主助理以同一任務開始前的最後 total_token_usage 為基準，取本次累計差額，沒有把先前 release 工作的歷史總量直接算入。每個 child 僅取最後累計值一次；reasoning output 依原欄位另列，不額外加到 output。

觀測警戒將 cached input 也納入。首次檢查已知 input 達 **5,169,791**（cached **5,008,512**）、output **34,201**，因此停止新案例，沒有再啟動 S07 餘兩軸或 S08。結案用量仍計入上表；警戒不是工具強制 token 限額，也不代表最後統計停在 500 萬。

長控制對話的重複 context 是本次 input 的主要來源，因此 33 次啟動額度遠未用完就觸及 token 警戒。沒有以「尚有次數」繼續執行；也沒有為通過結果換模型、改權限或續跑。

Desktop parent／reviewer 的原生 turn context 為 gpt-6.1-sol／high；CLI 實際模型／effort unknown，沒有 override。沒有建立付費資源、切換登入或計費方式。缺少可核對的費率與帳務計量，不提供金額推估。
