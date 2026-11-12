# 領域詞彙表改名：CONTEXT.md → GLOSSARY.md

日期：2026-11-12（Asia/Taipei）。分支：`claude/glossary-rename`，從 `claude/template-migration`（`301fd18`）切出，因為 migrate step 必須和 migrate 本身一起出貨；尚未發布。

## 為什麼改

上游 [mattpocock/skills](https://github.com/mattpocock/skills) 在 v1.3.0（PR #876，`d80fa0f`）把領域詞彙表慣例 `CONTEXT.md`／`CONTEXT-MAP.md` 改成 `GLOSSARY.md`／`GLOSSARY-MAP.md`，`domain-modeling/CONTEXT-FORMAT.md` 也改為 `GLOSSARY-FORMAT.md`。改名後上游 skill 執行時只認新名稱，CHANGELOG 要求使用者自行 `git mv`。v1.3.2（`ed0de59`）的 `setup-matt-pocock-skills` 開始偵測舊檔並提議改名。

本範本的副本取自 `3cca18b`，早於這次改名。2026-11-12 以 GitHub API 查證：上游 main（`4ae2317`）的檔案樹已沒有含 `CONTEXT` 的路徑。

## 決策

決策經 `/grill-with-docs` 逐題確認：

| 題目 | 決定 |
|---|---|
| 同步範圍 | 只同步改名（`d80fa0f`）與 setup 的舊檔偵測（`ed0de59`）；其餘上游變更另行處理 |
| `CONTEXT-MAP.md`、`CONTEXT-FORMAT.md` | 照上游改為 `GLOSSARY-MAP.md`、`GLOSSARY-FORMAT.md` |
| 執行時回退舊名 | 不做，與上游一致 |
| 已採用範本的專案 | migrate 新增 `rename` 操作與 `glossary-rename` step（0.5.0）：改名根目錄的 `CONTEXT.md`／`CONTEXT-MAP.md`，降級時改回；新檔名已存在時不動並列為 `by hand`；子目錄的 `CONTEXT.md` 只列出不移動 |
| 與 `teach` 撞名 | `teach` 會在執行目錄寫自己的 `GLOSSARY.md`；`docs/agents/domain.md` 加一句：不要在 repo 根目錄執行 `/teach` |
| `.tmpl.docs/CONTEXT.md` | 一起改為 `.tmpl.docs/GLOSSARY.md` |
| 歷史紀錄 | `.tmpl.docs/` 的 research、plans、patch 與 drift report 保持原樣，作為當時狀態的證據 |
| 來源紀錄 | `docs/agents/skill-sources.json` 的 `licensing.groups.mattpocock-skills.upstream_syncs` |

這次沒有寫 ADR：改名跟隨上游，理由記在這裡與 `skill-sources.json`。

## 交付內容

- 兩套 skill 樹（`.claude/skills/`、`.agents/skills/`）、`AGENTS.md`、`docs/agents/domain.md`、`docs/agents/review.md` 的引用全面換成新名稱；兩份 `domain-modeling/CONTEXT-FORMAT.md` 以 `git mv` 改名；`tune-skills` 的「CONTEXT templates」改為「GLOSSARY templates」。
- 兩份 `setup-matt-pocock-skills/SKILL.md` 加入上游的舊檔偵測句。
- `harness_agile/migrate.py`：`rename`、`report_nested` 兩種 step 操作，`rename` 有對應的 undo 並納入 journal 驗證；計畫報告新增 `notices`（文字輸出為 `by hand`）。`docs/guide.md`〈升級或降級範本〉的表格補上這一列。
