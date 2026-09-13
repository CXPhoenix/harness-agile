# PyPI 與 npm 發布

兩個流程都從 GitHub Actions 手動執行，選擇 `main`，輸入已存在的版本 tag。單純推送程式碼或 tag 不會發布套件。PyPI workflow 會直接上架；npm workflow 只上傳待核准版本。

| 平台 | Workflow filename | Environment | 套件 |
| --- | --- | --- | --- |
| PyPI | `publish-pypi.yml` | `pypi` | `harness-agile` |
| npm | `publish-npm.yml` | `npm` | `create-harness-agile` |

Trusted Publisher 的 GitHub Owner 填 `CXPhoenix`，Repository 填 `harness-agile`。Workflow filename 只填檔名，不含路徑；Environment 必須與上表一致。PyPI 可先建立 Pending Publisher；npm 首次手動發布後，在套件 Settings 設定 Trusted Publisher，取消勾選 **Allow npm publish**，只允許 `npm stage publish`。帳號驗證由維護者在官方網站完成，不把 token 放進專案。

共用 `build-release.yml` 會確認 tag 格式、版本一致性及 commit 已在 main 歷史內，再執行結構檢查、範本測試、Archify 支援子集、依賴掃描及實際套件初始化。建置工作不授予 OIDC 權限；發布工作只下載本次已驗證產物，再取得短效權限。npm 使用支援 staged publishing 的 npm 11.19.1，產生 provenance，PyPI 使用官方發布 Action。

發布前仍應確認該 tag 的三平台 CI 成功。相同版本不應重複發布；若 npm 已存在該版本，就不要再對該版本執行 npm workflow，後續版本遞增後才執行。發布完成後，應從 registry 安裝固定版本並檢查生成專案；Git-source 安裝成功不等於 registry 安裝成功。

預設初始化會移除三個發布 workflows；`--keep-template-files` 才會保留。採用者若保留後要自行發布，必須先調整套件名稱、repository 與 Trusted Publisher 設定。

官方參考：[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/)、[npm Trusted Publishing](https://docs.npmjs.com/trusted-publishers/)。

## npm 的人工核准

1. 執行 `publish-npm.yml`，輸入尚未發布的版本 tag。CI 成功只代表候選版本已上傳，不代表正式上架。
2. 在 npm 套件頁的 staged releases 檢查套件名稱、版本、來源與產物；確認與該 tag 的 CI 證據一致。
3. 由維護者在 npm 完成 2FA 並核准。核准後才會公開；不採用的候選應拒絕。
4. 等 registry 處理完成，再從 registry 安裝該版本並驗證。已上架的 0.2.1 不重新上傳，也不為測試流程而新增版本。

核准不放進 GitHub workflow，也不使用 OIDC 自動核准。帳號與 token 限制保留；PyPI 流程不變。此次變更以 staged publish dry-run 與 workflow 檢查驗證；第一次實際待審上傳與 2FA 核准會在下一個版本驗證。

官方參考：[npm staged publishing](https://docs.npmjs.com/staged-publishing/)。
