# 能力盤點

此為本次實際可見能力，不是新增 gate。正式契約與模型設定均未修改。

| 能力 | 觀察與證據 | 本次決定 |
| --- | --- | --- |
| Desktop fresh reviewer | 原生 spawn 支援 harness-reviewer 與 fork_turns=none；取得新 session UUID、啟動與工具輸出 | S01、S04、S07 已使用；沒有 parent transcript 繼承的啟動選項省略問題 |
| 主助理是否 fresh | 本次沿用原對話作控制端，不宣稱它是新的頂層 session | Stage 3 的 fresh 單位是每個 reviewer；EGM desktop 另受新頂層 session 前提限制 |
| 原生讀取事件 | 本次 child 的本機 rollout 含 custom_tool_call_output，可獨立核對已讀來源 hash 與時間 | S07 可同步注入；事件與 controller 時序均保存 |
| 取消 | interrupt_agent 對 running 回傳 ack，目標 trace 有 turn_aborted | S04 成立，沒有殘留 running 測試代理 |
| 原生 timeout／pause | 可等待、可取消，但沒有可安全指定一軸必要讀取的原生 timeout／pause 注入介面 | S02 blocked；不以等待 deadline、sleep 指示或取消冒充 timeout |
| 獨立 worker crash | 未取得此 desktop reviewer 專用且可安全異常終止的 worker 控制 | S05 blocked；沒有終止 desktop app 或其他工作 |
| 停用 fresh 能力 | 現有 API 能 fresh spawn，未提供僅作用於隔離案例的安全能力停用控制 | S06 blocked；未改 concurrency、角色或 trust，也沒有刻意耗盡其他人的槽位 |
| 新頂層 desktop EGM session | 未有使用者另行提供的新測試工作階段；管理工具建立側欄 chat 不在本次操作範圍 | C 批 0 次，不以子代理代演 EGM、不另建立 chat |
| CLI 新 session／可停止 | exec help 確認 ephemeral／JSON／stdin 介面；控制端以獨立 process group 啟動，設定 600 秒 deadline 與 TERM→KILL 後備 | D01 約 58.845 秒正常退出，沒有用到強制停止 |
| CLI 有效寫入 | session 回報唯讀，沒有寫入命令／報告；stderr 有 filesystem sandbox violation 訊息，但 path=unknown，不能精確歸因報告寫入 | 只能確認沒有落盤，不能把它計為 D05 的受控 write-denial pass；完整 D01 blocked，停止後續 CLI 模型 |
| 同身分 I/O 拒絕 | UID 501 的無模型探針，read 000 與 write 0500 均得到 errno 13 | permission-probe.json 僅為控制端能力；D04／D05 模型案例未執行 |
| CLI 同步建立前 hook | JSONL 可以觀察事件，但未確認建立前可暫停且可保證先後的 hook | D06 未執行，不用預放同名檔或非同步猜測冒充競爭 |
| CLI 即時 steering | 此 exec 入口接受初始 stdin 後 EOF；未取得對進行中同一 session 的安全 steering 入口 | D07 未執行，不以硬中止代替軟截止 |
| 用量 | 6 個完成 reviewer 與 CLI 有 usage；S04 取消只有 token_count 空資訊，無可用 usage；父對話有累計計數 | 已知用量加總為下限；包含父對話的長 context cached input，不將 missing 填 0 |

沒有執行 Claude CLI、登入或模型檢查。沒有改動任何權限、sandbox、角色、fresh 規則或模型設定以繞過限制。
