# 範本維護文件

要建立新專案，先讀[採用指引](adoption.md)；要修改母範本，先讀[貢獻與維護](contributing.md)。這裡保存範本的設計背景與演變，採用後需要遵守的規範則放在 `AGENTS.md` 與 `docs/`。

## 現行入口

- [evidence-report 來源查核](research/2026-09-13-evidence-report-upstream-search.md)：網路查詢、同名候選排除與設計段落的新線索。

- [Windows 自動開啟已停用](../docs/security/windows-opener.md)：兩個入口、自行驗證與暫緩實驗的範圍。

- [公開準備：MIT 與第三方授權](history/2026-09-13-license-restoration.md)；[Windows opener 風險識別](research/2026-09-13-windows-opener-risk.md)。
- [採用指引](adoption.md)：建立新目錄、初始化既有副本，以及保留範本的選項。
- [貢獻與維護](contributing.md)：文件與程式放置位置、驗證方式、交付紀錄。
- [範本維護術語](CONTEXT.md)：開發助理、Skill、Plugin 與代理角色的共用詞彙。
- [Banner 設計與生成](assets/banner/README.md)：視覺概念、生成方法與重製方式。
- [本輪文件整理紀錄](history/2026-09-13-docs-refresh.md)：閱讀入口、中英文 README 與 banner 的變更及驗證。

## 設計與歷史證據

以下記錄保留當時的決策與實測範圍；查閱目前操作方式時，使用上方現行入口。

| 主題 | 研究與計畫 | 結果 |
| --- | --- | --- |
| Codex Prompt／Skill 最佳化 | [討論](research/2026-09-12-prompt-skill-optimization.md) · [計畫](plans/2026-09-12-codex-prompt-skill-optimization.md) | [改造結果](history/2026-09-12-codex-prompt-skill-optimization.md) |
| Claude Code／Codex 整合 | [研究](research/2026-09-08-claude-code-codex.md) · [計畫](plans/2026-09-08-dual-agent-template.md) | [建立器與發布歷程](history/2026-09-08-bootstrap-cli.md) |
| 多入口建立器 | [研究](research/2026-09-08-template-distribution-bootstrap.md) · [計畫](plans/2026-09-08-bootstrap-cli.md) | [實作與驗證](history/2026-09-08-bootstrap-cli.md) |
| 範本文件分離 | — | [搬移歷程](history/2026-09-08-template-docs-relocation.md) |

## 保存與初始化

此隱藏目錄隨母範本納入 Git。列出檔案使用 `rg --files --hidden .tmpl.docs/`；文件中的程式碼路徑若未另註，皆以 repository 根目錄為準。新計畫放 `plans/`、研究放 `research/`、完成紀錄放 `history/`。

預設初始化會移除此目錄與範本英文 README，並將根目錄 README 改成產品入口。`--keep-template-files` 會保留範本文件及素材。歷史內容中的 placeholders 不會被替換。

採用後的執行規範只連結會保留的文件，避免新專案依賴已移除的範本歷史。
