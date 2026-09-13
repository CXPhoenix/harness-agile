# 2026-09-13：文件整理與專案 Banner

本輪依使用者要求，在 `codex/docs-refresh` 分支整理文件。使用者文件套用 Quill & Grill 的讀者優先寫法，README 採 OSS 常見閱讀結構，新增英文版本、badges 與 21:9 banner。

## 文件調整

README 先說明用途與適用情境，再提供快速開始、流程概覽、文件入口、驗證與授權現況。完整採用方式移到 `adoption.md`；日常 skills、交接與環境說明集中在 `docs/guide.md`。`docs/README.md` 提供規則查閱入口，`contributing.md` 說明母範本維護方式。

歷史研究與既有決策維持原文及證據狀態。現行文件修正過時的 skills 數量：此 checkout 的母範本為 32 個，初始化後為 31 個，包含新增的 `archify`。固定版本指令仍指向 `v0.1.0`，明示該 tag 的文件與 skills 可能不同。

未新增專案授權。README 如實說明缺少整體開源授權及 `UNLICENSED` 設定，第三方 skills 沿用各自授權。CI badge 連結遠端狀態，不將本機結果當成遠端通過。

## 素材與初始化

Banner 使用暖紙色、深綠與陶土橘，以多條路徑逐步收斂代表共用規範與交付。結合附件 canvas-design 的畫布設計方法與 algorithmic-art 的固定種子生成原則；成品為 2520 × 1080 PNG，原始生成器與設計說明放在 `assets/banner/`。

英文 README 納入 Python bundle 與 npm 檔案清單。預設初始化會移除範本英文 README 與素材，保留協作指南；`--keep-template-files` 保留中英文 README 及 banner。產品 README 樣板改為連結保留的操作指南，避免重複維護更新步驟。

## 驗證紀錄

本機 macOS、Python 3.14.3 的結果如下；完成後依 verification-before-completion 原則核對命令輸出。

| 檢查 | 結果 |
| --- | --- |
| `python3 scripts/verify-project.py` | 通過，母範本 32 個 skills |
| `python3 -m unittest discover -s tests -v` | 22 項通過 |
| 本輪現行文件的本機連結 | checkout 66 個、預設成品 18 個、保留模式 66 個，目標皆存在 |
| 預設初始化 | 31 個 skills；英文範本 README 與 banner 移除，協作指南保留 |
| 保留模式 | 32 個 skills；中英文 README 與 banner 保留，成品 verifier 通過 |
| Dry-run 與來源保存 | 不產生目標；來源 AGENTS、CLAUDE 與 README 的內容 hash 不變 |
| Banner | 2520 × 1080、733,318 bytes；重新生成逐 byte 一致，已目視檢查排版 |
| `uv build --offline`、`npm pack --ignore-scripts` | sdist、wheel、npm tarball 建置成功 |
| `scripts/verify-distributions.py` | wheel／npm 範本內容一致；uvx、npx、pnpx 皆成功建立並驗證 31 個 skills |
| `git diff --check` | 通過 |

套件驗證快照的 content digest 為 `9a06f4cbddf0da54661b10a18c8a13dfd20fc5141b42865413bcb6aa363f17f1`，來源標記為 dirty。這是補入本段驗證結果之前的快照，後續文件變動會改變 digest。字型 ZIP 由使用者提供，未隨 repository 散布；生成器需要另行提供該 ZIP。

驗證範圍為本機檔案、PNG 視覺、Python CLI 與套件介面；未執行遠端 CI、未發布套件，亦不代表產品行為或模型品質已驗證。
