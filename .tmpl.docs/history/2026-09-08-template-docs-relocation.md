# 範本文件分離歷程

日期：2026-09-08。範圍：harness-agile-template 的文件配置與初始化清除規則。

## 背景與決定

使用者先確認 `docs/` 目前存放的是範本規範與改造歷史，接著提出將範本專用內容移到 `.tmpl.docs/`。討論後決定：範本研究、改造計畫與維護說明集中管理，新專案仍需要的工作規範與已採用決策保留原位。使用者明確要求執行搬移並記錄歷程。

## 搬移範圍

| 原位置 | 新位置 | 用途 |
| --- | --- | --- |
| `docs/plans/2026-09-08-dual-agent-template.md` | `.tmpl.docs/plans/2026-09-08-dual-agent-template.md` | 前次雙工具整合計畫 |
| `docs/research/2026-09-08-claude-code-codex.md` | `.tmpl.docs/research/2026-09-08-claude-code-codex.md` | 前次研究依據與驗證紀錄 |
| `TEMPLATE.md` | `.tmpl.docs/adoption.md` | 範本採用說明 |

另建立 `.tmpl.docs/README.md` 作為維護入口，以及本篇歷程。`docs/agents/`、`docs/adr/`、skill 來源紀錄與授權保留；根目錄 README 繼續提供使用說明。

## 取捨

- 新專案的 `docs/` 更聚焦，但隱藏目錄較不容易被預設搜尋發現，因此根目錄 README 提供入口，維護指南提醒使用 `rg --hidden`。
- 新專案預設不保留母範本研究背景；母範本仍應將歷史納入 Git，需要攜帶時使用 `--keep-template-files`。
- 清除歷史也必須清除入口。README 的範本文件區塊使用成對標記，初始化只移除該區塊，其餘內容保留。runtime 文件維持自足，不再依賴研究報告連結。

## 實作

1. 搬移現有文件並修正引用，研究報告內容保留為當時的紀錄。
2. 把 `.tmpl.docs/` 加入初始化腳本的範本專用清單，使 token 掃描及替換略過整個目錄。
3. 預設初始化刪除該目錄及 README 入口；保留模式維持歷史檔案與入口原文。
4. 更新 init-template skill、共用維護規範、README 與採用指南，讓後續範本維護沿用新的位置。

## 驗證

新增兩項 CLI regression tests：預設初始化清除歷史與入口；保留模式不改寫歷史 token 或 README，且再次初始化仍會拒絕執行。修改前兩項皆失敗，修改後連同既有四項共六項通過。

完整副本另外檢查預覽、預設初始化、保留模式的本機 Markdown 連結，以及初始化前後的 skills 可攜性，結果如下：

| 驗證 | 結果 |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 6 項通過，包含新增的兩項 regression tests |
| 母範本 `python3 scripts/verify-project.py` | 31 個 skills、連結、觸發政策、腳本資源與角色設定通過 |
| 完整副本 dry-run | 檔案內容雜湊不變 |
| 完整副本預設初始化 | `.tmpl.docs/` 與 README 標記入口移除，剩餘文件連結及 skills 檢查通過 |
| 完整副本保留模式 | 歷史檔案內容雜湊不變，文件連結及 skills 檢查通過，再次初始化回傳拒絕狀態 |
| `git diff --check` | 通過 |

以上為本機檔案、初始化 CLI 與結構驗證；沒有重跑前次 Claude／Codex 原生載入或模型回合。副本測試前後另比對母範本檔案內容，確認測試沒有修改母範本。

母範本未執行初始化；本次工作不包含 commit、全域記憶更新或模型工作流程重跑。
