# 採用指引

先選擇起點：**要建立新的目錄**，使用建立器；**已複製完整範本**，在那份副本執行初始化。若正在維護母範本，請保留 placeholders，閱讀[維護指引](contributing.md)。

## 用建立器產生新專案

[README 快速開始](../README.md#快速開始)提供 uv、npx 與 pnpx 指令。建立器會使用所選版本隨附的範本，不依賴家目錄中的 skills。

需要先預覽時，在建立指令加上 `--dry-run`。它不寫入目標，但套件管理器仍可能下載來源與使用 cache。確認來源與目標後，移除該選項執行。

從另外取得的、尚未初始化的母範本 checkout，也可直接執行：

```bash
python3 -m harness_agile init /absolute/path/my-project \
  --source . --name '我的專案' --one-liner '它要解決的問題。' --no-input
```

這條路線需要 Python 3.11+。目標須在來源目錄之外、不存在或為空，父目錄須已存在。`--keep-template-files` 產生的專案保留說明與 init 工具，並非完整建立器 checkout；從成品再建立另一個專案時，使用 README 的 PyPI／npm 安裝入口。

| 選項 | 何時使用 |
| --- | --- |
| `--dry-run` | 預覽來源與目標，不寫入成品 |
| `--no-input` | 已提供必要值，不需要互動提問 |
| `--json` | 讓開發助理或 CI 讀取結果；缺少必要值時失敗、不詢問 |
| `--skill-mode copy` | 環境不使用 symlink；預設 `auto` 在連結不可用時改用副本 |
| `--date YYYY-MM-DD` | 指定採用日期 |
| `--keep-template-files` | 保留範本歷史、初始化工具、中英文 README 與 banner |
| `--source PATH` | 從指定的本機母範本建立 |
| `--git` | 建立獨立 Git repository；不自動 commit、建立 remote 或 push |

完整參數可非互動執行；省略參數時，只有互動終端機會詢問缺值。來源與內容 digest 記錄在新專案的 `docs/agents/template-source.json`。

## 初始化已複製的範本

可以透過 GitHub template 建立，或複製完整 repository。複製時保留隱藏目錄。

```bash
gh repo create MY_ACCOUNT/my-project \
  --template CXPhoenix/harness-agile --private --clone
cd my-project
python3 scripts/sync-skills.py
python3 scripts/verify-project.py
```

這條路線需要 Git、Python 3.11+；GitHub 指令另外需要已登入的 `gh` 與來源存取權限。同步與驗證成功後，在副本中開啟開發助理：

| Claude Code | Codex |
| --- | --- |
| `/init-template` | `$init-template` |

提供專案名稱與一句話描述，也可以直接執行腳本：

```bash
python3 scripts/init-project.py --dry-run --name '我的專案' --one-liner '它要解決的問題。'
python3 scripts/init-project.py --name '我的專案' --one-liner '它要解決的問題。'
```

## 初始化後會留下什麼

目前 checkout 預設會填入專案名稱、描述與 ADR 日期，將根目錄 README 改為產品入口，保留共用規範、31 個 skills、協作指南、同步與驗證工具。範本歷史、banner、英文範本 README、建立器、初始化工具及其專用測試則會移除。固定 tag 的內容可能不同，以該版本的驗證結果為準。

`--keep-template-files` 保留範本文件與初始化工具，包含中英文 README。歷史文件中的 placeholders 不會替換，因為它們記錄的是母範本的設計背景。

初始化完成後，在新 session 使用 `grill-with-docs` 定義 Project Charter，再建立 walking skeleton。初始化不會選擇技術棧、安裝產品依賴或建立產品功能。日常操作請接著讀[協作指南](../docs/guide.md)。
