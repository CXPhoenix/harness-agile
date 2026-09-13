# PyPI 與 npm 發布

兩個流程都從 GitHub Actions 手動執行，選擇 `main`，輸入已存在的版本 tag。單純推送程式碼或 tag 不會發布套件。

| 平台 | Workflow filename | Environment | 套件 |
| --- | --- | --- | --- |
| PyPI | `publish-pypi.yml` | `pypi` | `harness-agile` |
| npm | `publish-npm.yml` | `npm` | `create-harness-agile` |

Trusted Publisher 的 GitHub Owner 填 `CXPhoenix`，Repository 填 `harness-agile`。Workflow filename 只填檔名，不含路徑；Environment 必須與上表一致。PyPI 可先建立 Pending Publisher；npm 首次手動發布後，在套件 Settings 設定 Trusted Publisher，並允許直接 `npm publish`。帳號驗證由維護者在官方網站完成，不把 token 放進專案。

共用 `build-release.yml` 會確認 tag 格式、版本一致性及 commit 已在 main 歷史內，再執行結構檢查、範本測試、Archify 支援子集、依賴掃描及實際套件初始化。建置工作不授予 OIDC 權限；發布工作只下載本次已驗證產物，再取得短效權限。npm 流程產生 provenance，PyPI 使用官方發布 Action。

發布前仍應確認該 tag 的三平台 CI 成功。相同版本不應重複發布；若 npm 已存在 0.2.0，就不要再對該版本執行 npm workflow，後續版本遞增後才執行。發布完成後，應從 registry 安裝固定版本並檢查生成專案；Git-source 安裝成功不等於 registry 安裝成功。

預設初始化會移除三個發布 workflows；`--keep-template-files` 才會保留。採用者若保留後要自行發布，必須先調整套件名稱、repository 與 Trusted Publisher 設定。

官方參考：[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/)、[npm Trusted Publishing](https://docs.npmjs.com/trusted-publishers/)。
