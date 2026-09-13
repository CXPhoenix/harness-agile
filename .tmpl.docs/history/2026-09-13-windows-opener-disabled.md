# 暫停 Windows 自動開啟

依使用者要求，於 2026-09-13 移除 Windows PowerShell opener，在共用啟動入口直接回傳 `disabled`，涵蓋 `deliver --open` 與 `preview`。相關資安實驗暫緩；不預先承諾任何帳號方案或權限申請結果。

同步更新中英文 README、協作指南、文件導覽、初始化 README、Archify skill／delivery contract、來源調整紀錄與既有風險／授權歷史註記。公開使用說明見 [Windows 自動開啟已停用](../../docs/security/windows-opener.md)。

驗證：opener 4／4、範本 22／22、結構檢查與差異空白檢查通過。停用測試修改前失敗、修改後通過；驗證的是 macOS 上模擬 Windows 平台分支及程序啟動監測，並非原生 Windows 端到端結果。

停用前 opener 已存入被忽略的 `.proj.vuln.recur/windows-opener-command-injection/archive/`。Compose／Windows VM 實驗與該子目錄 standalone Git 建置尚未完成，不能視為已交付。此變更不代表專案所有公開前檢查均已結案。
