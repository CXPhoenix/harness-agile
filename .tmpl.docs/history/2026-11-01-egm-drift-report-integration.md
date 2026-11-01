# egm-drift-report 本機整合

日期：2026-11-01。使用者核准[計畫與測試表](../plans/2026-11-01-egm-drift-report-integration.md)
後，在 `codex/egm-drift-report` 隔離 worktree 實作；基準為 `110a622`。
本紀錄保存 commit 前的實作／驗證結果，原 checkout 的研究與計畫保留。使用者後續已另授權 commit、push 與 PR；交付狀態以 Git／PR 為準，仍不合併或發布。

## 行為與範圍

- 兩套 runtime 各有顯式入口，讀取共用 `docs/agents/drift-report.md` 契約。
- 依指定文件／實作範圍順序比對，分開確認差異、待確認、預期差異及已查未發現差異。
- 報告具有 complete／partial／blocked／stale 狀態、來源 hashes 與查核範圍，
  只在適用位置建立新 Markdown；重跑保留舊檔，拒絕輸出 symlink／路徑逸出。
- 原 spec、traceability、ticket、四軸／兩輪／P0 及交付 gates 保留。
- verifier 擋下缺 skill 及兩套同時退化為 implicit；初始化／分發斷言同步數量：
  產品各樹 33、母範本／keep 各樹 34。Apache-2.0 來源與授權隨兩套 skill 保留。

## 驗證證據

完整[執行證據與 coverage report](../research/2026-11-01-egm-drift-report/evidence.md)
列出 red → green、24 項 unittest、Codex CLI 原生正常／異常路徑、獨立 code／security
review、套件時序與限制。最終 wheel／npm snapshot 一致，三入口 default 與 wheel keep 模式通過；13 份正式檔案與產物 bytes 相同。這些是指定 fixture／宿主的證據，不保證一般偵測率。

Claude 未登入，未做 Claude live；實際 read-permission denial、context/time cutoff、
所有輸入邊界、Git dirty 分類、跨平台 CI 等未覆蓋項目保留，不冒稱通過。
正式兩套 adapter／授權／初始化可攜性與 Claude 模型行為分開回報。

本次沒有引入官方完整 EGM plugin、背景服務、production runner 或自動修正流程。
套件驗證使用本機 0.3.0 測試產物，不代表 registry 有任何更新。
