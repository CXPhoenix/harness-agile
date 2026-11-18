# 用量與停止點

A 批 input 配置 700,000，含 cached；結案另可用最多 200,000 input。這是觀測配置，沒有工具強制 token 硬上限。

首次取得的控制對話累計為 input 741,189、cached 665,984、output 6,015、reasoning output 1,185，因此停止所有新 CLI 模型測試。不是把之前 cumulative events 相加。控制對話自身反覆帶入宿主／工具脈絡，短啟動文字沒有保證短有效 context；此次沒有在更早階段取到累計，是預算控管缺失。

本次結案計量截止：2026-11-02T02:49:09.343765+08:00。最新可見控制對話累計：input **916348**、cached **839680**、output **7546**、reasoning output **1923**。cached 已含於 input，reasoning 已含於 output，不重複加總。

從停止查核快照至截止的可見 input 差額：175159；結案額度為 200,000。截止後處理與最終回覆用量未知，不當零，也不能宣稱最終一定在額度內。原生 session 起始時間與去重用量事件見 controller-usage-cutoff.json。

CLI 模型啟動 **0** 次，沒有取消案例或缺失的 CLI usage。未觀察到 CLI 實際 model／effort；全域設定值為 gpt-6.1-sol／high，控制對話原生值另有 turn_context 證據。無模型 help／schema／debug／app-server 查核不算測試 session。CLI token 欄不以未執行值冒充模型測量。
