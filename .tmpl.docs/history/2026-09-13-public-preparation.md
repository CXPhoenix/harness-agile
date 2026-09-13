# v0.2.0 公開準備紀錄

2026-09-13。維護者要求完成公開前準備；repository 可見性維持 private，切換 public 是獨立操作。

## 已處理

- 根目錄 MIT、第三方授權與 evidence-report 來源整理結案；32 份授權／聲明隨所有套件及初始化成品保留。
- Windows 圖表與 preview 自動開啟在程序啟動前停用；保留手動開啟、一般產圖與原呼叫政策。
- fast-uri 固定 3.1.6，依賴掃描 0 vulnerabilities，生成驗證器內容不變。
- 新增 Archify 可攜測試與 preview 測試，納入三平台 CI；封裝前清理開發依賴，並驗證實驗資料與 node_modules 不在套件內。
- 版本及安裝入口對齊 0.2.0；CHANGELOG 在預設初始化移除，保留範本模式則留下。
- 維護者明確接受歷史作者信箱公開，保留既有 Git 歷史，不改寫舊 tag。

## 本機證據

macOS／Python 3.14.3／Node.js 24.13.0。結構檢查通過；範本 22／22、Archify 65／65。sdist 可建置 wheel；uvx、npx、pnpx 真正初始化通過。32 份授權於 sdist、wheel metadata、wheel bundle、npm、預設初始化及保留範本模式逐 byte 相同。

獨立 code-review：Requirements 無發現；Standards 發現 CHANGELOG 未清理的 P2，修正並複核後無未結案發現。此為本輪變更審查，不宣稱完整上游 Archify 測試或原生 Windows 風險實驗通過。

敏感資訊：前輪已掃描全部本機 refs 的 14 個 commit、463 個歷史 blob，未確認到真實憑證。本輪再對最終來源做常見憑證／本機路徑／session 連結檢查，無命中；Detect Secrets 1.5.0 對本輪新增及修改檔案掃描，正控制成功，14 筆非控制警示均為來源 revision 或雜湊。完整來源的額外 Detect Secrets 重掃未在合理時間內完成，已中止，不列為成功；採前輪歷史掃描加本輪差異檢查。原始 session log 沒有放入專案。

第一方 Markdown 相對連結檢查無實際壞連結；scripts/project-readme.md 為生成根 README 的範本，須依生成位置解析。GitHub 查核當時仍為 PRIVATE，無 issue 或開啟中的 PR，Discussions 未啟用。

## 尚未納入完成宣告的項目

此檔寫入時，提交後的遠端 CI、發布 tag 與 release 草稿仍待執行；以最終 GitHub 結果為準。切換 public 後才可驗證匿名存取與 Git-source 安裝，不能在 private 階段先宣稱通過。

Windows VM 重現與本機實驗子目錄 standalone Git 暫緩，不作為此次公開的必要條件。SECURITY.md、分支保護與長期自動掃描可另行維護；本輪沒有把缺少這些設定視為已確認漏洞。
