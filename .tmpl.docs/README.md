# 範本維護資料

這裡保存 harness-agile-template 的設計背景、研究、改造計畫與維護歷程。新專案採用後必須遵守的規範保留在根目錄 `AGENTS.md` 與 `docs/`，不依賴這個資料夾。

## 文件入口

- [範本採用指引](adoption.md)：複製範本、初始化及保留選項。
- [Claude Code／Codex 整合計畫](plans/2026-09-08-dual-agent-template.md)：雙工具設定、skills 攜入與驗收範圍。
- [Claude Code／Codex 研究](research/2026-09-08-claude-code-codex.md)：官方來源、工具差異、設定依據與當時的實測結果。
- [範本發布與快速建立研究](research/2026-09-08-template-distribution-bootstrap.md)：GitHub template、本機建立、npx／uvx 與 agent 安裝指引的官方依據、取捨與實測邊界。
- [多入口建立器計畫](plans/2026-09-08-bootstrap-cli.md)：GitHub 發布、共用 CLI、skill 副本模式及套件驗收範圍。
- [建立器實作與發布歷程](history/2026-09-08-bootstrap-cli.md)：實際改動、審查修正、套件驗證與發布範圍。
- [本次文件搬移歷程](history/2026-09-08-template-docs-relocation.md)：搬移理由、取捨、實作與驗證結果。

## 存放原則

「為什麼這個範本被做成這樣」放在這裡；「採用後要怎麼工作」放在 `docs/`。後續維護範本時，計畫放 `plans/`、研究放 `research/`、完成後的歷程放 `history/`。產品自己的文件仍依產品規範存放。

此目錄應隨母範本納入 Git，不加入 `.gitignore`。因為是隱藏目錄，列出檔案使用 `rg --files --hidden .tmpl.docs/`；文件中的程式碼路徑若未另註，皆以 repository 根目錄為基準。歷史報告記錄的是當時的狀態，後續變更另記歷程。

## 初始化行為

預設 init 會刪除整個 `.tmpl.docs/`，並移除根目錄 README 裡標記為 `TEMPLATE-DOCS` 的入口。加上 `--keep-template-files` 會保留兩者。

無論是否保留，初始化都不替換此目錄內的 placeholder。保留的研究範例或歷史記錄不會讓初始化誤判成尚未完成。新專案的執行規範不得連結到這些會被移除的檔案。
