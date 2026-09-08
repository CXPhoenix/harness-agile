# 多入口專案建立器實作計畫

**目標：** 依使用者核准的研究建議，發布 GitHub template，提供 uvx、npx／pnpx 與 agent 指引；生成結果不依賴套件能保存 symlink。

**架構：** Python 標準函式庫建立器使用 build 時產生的固定範本 bundle，在目標父目錄的暫存位置呼叫既有 initializer，再同步 Claude skills、驗證與移交成品。Node 薄入口尋找 Python 3.11+ 或 uv，以 argv 轉送到同一核心。套件只攜帶技能正本；連結或一致性副本在成品建立。

**工具：** Python 3.11+、hatchling build backend、Node.js 18+、npm／pnpm、Git。保留母範本 placeholders。這是範本維護，使用既有核准範圍，不替母範本編造產品 Charter。

## 已確認範圍

- 遠端：`https://github.com/CXPhoenix/harness-agile.git`，private，保留可見性並設定 template。
- 先以 Git URL 提供執行入口，不在未設定帳號下宣稱 npm／PyPI registry 已發布。
- `init DIRECTORY`、`--name`、`--one-liner`、`--date`、`--keep-template-files`、`--no-input`、`--json`、`--dry-run`、`--source` 本機路徑、`--skill-mode auto|symlink|copy`、`--git`。
- 預設不建立 commit、remote 或 push；建立者可明確指定 `--git` 初始化獨立 repo。
- `auto` 能使用 symlink 時建立相對連結，無權限時使用完整副本；verifier 檢查副本是否與正本逐檔一致。`scripts/sync-skills.py` 用於日後同步。
- package 內含固定範本，不在每次 init 下載 main；來源紀錄含 commit、內容 digest 及是否由 dirty checkout 建置。

## 執行步驟與驗證表

| 步驟 | 檔案／行為 | 驗證 |
| --- | --- | --- |
| 1 | `scripts/skill_links.py`、`scripts/sync-skills.py`、verifier 支援副本 | 先測試副本驗證與偏離偵測失敗，再實作；測試 auto 無連結權限 fallback |
| 2 | `harness_agile/bundle.py`、`cli.py`、`__init__.py`／`__main__.py` | 先 CLI 測試失敗，再實作新目錄成功、已有資料不覆蓋、缺值／無效輸入不留成品、dry-run、JSON、來源保存 |
| 3 | initializer、README 成品標記及 init skill | 既有 6 項 regression；完成 init 不留下指向已刪工具的說明；副本同步不重複替換 skills |
| 4 | `pyproject.toml`、`hatch_build.py`、`package.json`、`bin/*.cjs` | 實際 wheel／npm pack 解包驗證；uvx、npx、pnpx 或 pnpm dlx 走同一組引數 |
| 5 | `INSTALL.md`、README、runtime 與 bootstrap skill | 只詢問缺值、明列 Python／uv 與 private repo 權限、連結有效 |
| 6 | `.github/workflows/verify.yml` | macOS／Linux／Windows job 定義，實際 GitHub Actions 結果回報；本機檢查不得冒充 Windows 驗證 |
| 7 | 來源與歷程、commit／push | 用 tw-emoji-commit；遠端 HEAD／工作目錄確認；記錄發布與 registry 差異 |

先驗證基本建立流程，後續每個邊界新增 regression 再修正。Python unit／CLI 測試用 `python3 -m unittest discover -s tests -v`；套件端到端驗證產物而非 source checkout，確保 hidden assets 完整。來源檔案、目標路徑或生成失敗不得刪除使用者既有內容。技能副本偏離需要明確同步，不靜默忽略。

## 不在第一版範圍

既有產品 overlay／升級合併、產品技術棧生成、全域 agent 設定與憑證管理。INSTALL 指引只設定新專案，後續 Charter 仍走既有流程。
