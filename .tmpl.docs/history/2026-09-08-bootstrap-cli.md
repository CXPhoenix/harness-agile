# GitHub 發布與多入口建立器歷程

日期：2026-09-08。依據：[核准後實作計畫](../plans/2026-09-08-bootstrap-cli.md)、[官方來源研究](../research/2026-09-08-template-distribution-bootstrap.md)。

## 發布起點

使用者指定 `https://github.com/CXPhoenix/harness-agile.git`，並要求依研究建議實作，包含 npx／pnpx 與 symlink 問題處理。初次檢查遠端為空且 private，保留可見性；先提交研究為 `a819bb6`，推送 main 並設為 GitHub template。

## 完成內容

- Python 3.11+ 標準函式庫核心，提供新目錄建立、完整引數／互動補值、dry-run、JSON、本機來源、採用日期與 Git opt-in。
- hatchling 產生 wheel／sdist，npm prepare／prepack 產生相同內容的範本 bundle。Node wrapper 以 argv 呼叫 Python 或 uv，沒有另一套初始化引擎。
- 套件只攜帶正本資料；初始化時選擇相對 symlink 或完整副本。verifier 比對副本內容；sync 修復 Git 的連結文字檔，偏離副本需檢閱後明確 refresh。
- 模式切換先建妥所有新 entry 再交換；交換失敗可還原。initializer 先確認技能同步，再替換內容與清理。
- `.gitattributes` 固定文字 LF；檔案與子程序採 UTF-8，降低 Windows／locale 差異。
- 成品 README 改成專案名稱與後續工作指引。keep 模式保留原 README、INSTALL 與 bootstrap 指引，明示它不是完整建立器 checkout。
- `INSTALL.md` 與獨立 `bootstrap/create-harness-project` skill 共用 CLI；既有 init skill 直接採用已提供的值。
- `.github/workflows/verify.yml` 定義 Linux／macOS／Windows Python 3.11 的測試、實際套件建置及 uvx／npx／pnpx 執行。

## 審查與本機驗證

Standards 與 Spec 各一個獨立 agent，審查基準 `a819bb6` 加本次工作目錄。確認並修正：初始化失敗後過早刪除資料、symlink 切換失敗遺失舊副本、CRLF checksum、非 UTF-8 locale，以及 keep 模式指引資源缺漏。審查修正均有 regression；保留原始 upstream security-review checksum。

| 檢查 | 本機結果 |
| --- | --- |
| Python unit／CLI regression | 20 項通過 |
| 正本結構 verifier | 31 個 skills 通過 |
| wheel 與 npm tarball 資料 | 範本 content digest 相同，npm 不含 symlink |
| uvx 實際 wheel 啟動 | 建立 30 個 skills、成品 verifier 通過 |
| npx 實際 tarball 啟動 | copy 模式 30 個 skills、成品 verifier 通過 |
| pnpx 實際 tarball 啟動 | copy 模式 30 個 skills、成品 verifier 通過 |
| 非空目錄／無效輸入／dry-run | 不覆蓋既有內容、不留下成品 |
| 無 symlink 權限 | auto fallback；強制 symlink 失敗保留舊副本 |

本機環境：macOS、Python 3.14.3、Node.js 24.13.0、npm 11.6.2、pnpm 11.14.0、uv 0.11.21。上述套件測試在 checkout 外的暫存目錄執行，包含繁中與空白路徑及字面 `$()`／反引號。這些不是模型行為或產品功能測試。

## 發行界線

第一版透過 Git URL 與版本 tag 提供套件入口，未發布 npm／PyPI registry，也未將 repo 改成 public。Git URL 的 prepare 流程與 GitHub Actions 原生跨平台結果，於推送後另記確認結果；不得把本機 wheel／tarball 測試誤稱為這兩項已通過。
