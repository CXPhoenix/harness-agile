# 範本 migration（upgrade／downgrade）完成紀錄

日期：2026-11-02（Asia/Taipei）。分支：`claude/template-migration`，基準 `main`／`0fcd87f`（harness-agile 0.4.0）。依[計畫](../plans/2026-11-02-template-migration.md)實作，經 [PR #16](https://github.com/CXPhoenix/harness-agile/pull/16) 送審；尚未發布。

## 交付內容

- `harness-agile migrate`：依專案的 `docs/agents/template-source.json`（schema 2）把專案移到執行中 CLI 的範本版本。預設 dry-run，`--apply` 才寫入；要求乾淨 Git 工作區（`--allow-no-git` 例外）；本機修改以 `<file>.harness-new` 旁置；結構變更以可逆 step 記入 journal；`--adopt`（可加 `--baseline-source`）納管舊專案。
- 建立時寫入 state：CLI 與直接執行 `scripts/init-project.py` 兩條路線都記錄版本、答案、選項與逐檔 SHA-256；Git checkout 只記錄已追蹤檔案；填 token 的檔案改以 bytes 讀寫。
- `scripts/verify-project.py` 在 state 列出的檔案有未解決旁置檔時失敗。
- 文件：`docs/guide.md`〈升級或降級範本〉、`INSTALL.md`、中英文 README、產品 README 範本、`.tmpl.docs/adoption.md`。

## 驗證

| 項目 | 結果 | 涵蓋範圍 |
|---|---|---|
| `python3 scripts/verify-project.py` | PASS | 母範本結構 |
| `python3 -m unittest discover -s tests` | 54 項通過 | macOS 本機；含 T1–T12 與審查後新增的回歸測試 |
| `scripts/verify-distributions.py` | uvx、npx、pnpx 皆通過 | 從只含 tracked 檔與本次新增檔的乾淨副本建置 wheel／npm tarball；每個入口建立專案後執行 `migrate --json`，確認 up-to-date |
| Windows、Linux、macOS CI | 2026-11-09 全數通過（`c89b851`） | 經下節三次修正後通過；junction 偵測沒有專屬測試 |

工作區原有的未追蹤研究目錄 `.tmpl.docs/research/2026-11-02-codex-native-host-verification/` 含巢狀 LICENSE fixture，若在原 checkout 直接建置，會被打包並讓 `verify-distributions.py` 的授權檢查失敗。這與本次變更無關；提交前若要納入該目錄，需另行處理。

## PR CI 失敗與修正（2026-11-09）

| 失敗 | 原因 | 修正 |
|---|---|---|
| 三個平台的 `test_adopted_gitignore_step_is_undone_on_downgrade` | 測試的 `--adopt` 沒給 `--date`，改用執行當天的日期；11-02 本機剛好等於建立日，11-09 的 CI 就讓 ADR 內容不同而產生旁置檔 | `14154a7`：測試明確指定建立日期 |
| Windows 的初始化 banner 未移除 | 改以 bytes 讀檔後，CRLF 檔案不再正規化，banner regex 只認 `\n` | `14154a7`：regex 接受兩種換行並沿用原換行，新增 CRLF 測試 |
| Windows 的 Archify `deliver`／`preview` 測試隨機失敗 | Archify `output-path.mjs` 以 Number 比對 `dev`／`ino`；NTFS file ID 超過 2^53 後失去精度，不同的檔案或目錄被誤判成同一個。本 PR 的測試在 `%TEMP%` 大量建立又刪除檔案，因而觸發 | 根本修正在 [PR #17](https://github.com/CXPhoenix/harness-agile/pull/17)（bigint 比對），已合併進 `main` 並同步到本分支。`c89b851` 讓 migrate 測試改用精簡 bundle、共用 source，檔案量約少七成，本機 `test_migrate` 由約 45 秒降到 17 秒 |

更正：`c89b851` 的 commit 訊息推測原因是 Windows Defender 掃描新檔案；#17 的診斷證實原因是上表的檔案識別精度問題，該推測不正確。`c89b851` 減少檔案量只降低了撞上誤判的機率，本身不是修正；保留它是為了測試速度。

## Code review findings 與處理

`harness-reviewer` 對擷取的 diff 審查五個面向，回報 1 個 P0、4 個 P1、17 個 P2。主 session 逐項對照原始碼確認後處理如下。

| ID | 摘要 | 處理 |
|---|---|---|
| P0-1 | render 一律傳 `--template-version`，0.4.0 以前的初始化器失敗；`init --source <舊版>` 回歸 | 已修：先以 `--help` 偵測是否支援；舊 source 建立時寫回 legacy provenance。測試以改寫後的舊式初始化器驗證 baseline、降級與建立 |
| P1-1 | 本機改過、範本沒變的檔案每次都產生旁置檔 | 已修：新增矩陣 F14；同版本重跑為 up-to-date |
| P1-2 | GitHub 路線把 gitignored／未追蹤本機檔記成範本檔 | 已修：Git checkout 只記錄 `git ls-files` 的檔案（I2a） |
| P1-3 | Windows 以 CRLF 寫入填 token 的檔案 | 已修：bytes 讀寫（I4）；實際效果待 Windows CI |
| P1-4 | Windows 測試的 hash 預期寫死 LF | 已修：改以實際內容計算 |
| P2-1 | step 路徑與旁置目錄未檢查 symlink | 已修：step 路徑納入 blocked 檢查；旁置目錄也會被偵測 |
| P2-2 | 套用不具原子性 | 部分：state 改為暫存檔加 `os.replace`；文件說明以 Git 回復。檔案寫入本身仍非交易式 |
| P2-3 | state 可列入非範本檔；`.GIT` 大小寫繞過 | 已修：不屬範本擁有的路徑一律忽略；`.git` 比對不分大小寫。未來若把範本檔改為種子檔，需搭配 step，否則會被當成移除 |
| P2-4 | 沒裝 git 時 `--allow-no-git` 無效；dubious ownership 誤判 | 已修；未有自動測試 |
| P2-5 | 預發布版與 `v` 前綴的版本比較；未知目標版本被當成降級 | 已修：預發布排在正式版之前；目標版本無法判定時拒絕（P11） |
| P2-6 | state／journal 型別驗證不足 | 已修：載入時檢查結構與 undo 欄位型別 |
| P2-7 | 不分大小寫檔案系統上，僅大小寫不同的改名會刪檔 | 已修：F15；macOS 上有測試 |
| P2-8 | Windows junction 未偵測 | 已修：檢查解析後路徑是否仍在專案內；未在 Windows 驗證 |
| P2-9 | 範本把檔案改成目錄時一律 blocked | 未修：接受為限制，遇到時需在該版加入 step |
| P2-10 | verify 走訪整棵樹 | 已修：只檢查 state 列出的檔案 |
| P2-11 | 所有權常數重複且未鎖定一致 | 已修：測試比對兩邊常數；兩邊都排除 `.bak` |
| P2-12 | 文件遺漏 | 已修：舊版降級方式、blocked、不同步清單、`--adopt` 限定參數、中途失敗回復 |
| P2-13 | 計畫連結與調整未記錄 | 已修：本紀錄與〈實作調整〉 |
| P2-14 | AC8 字面比實作嚴格；T10 未含 step | AC8 改為排除 `source`、`generator_version`；step 往返由 StepTests 涵蓋，T10 未改 |
| P2-15 | AC5「每個路徑」與 T8 的比較是同一份計算 | AC5 改為「每個有動作的路徑」；實際寫入結果由 T3、T4 檢查 |
| P2-16 | 零星問題 | 已修：adopt 日期格式、CRLF 檔附加行、render 路徑檢查。未修：建立與 migrate 的版本後備值寫法不同（不影響行為）；「非 Git」測試假設暫存目錄不在 Git repo 內 |
| P2-17 | 測試缺口 | 已補：P13、F14、F15、P11、P12、旁置目錄、step symlink、結構驗證、常數一致、I2a。仍缺：F11、P8、state 內 Windows 保留名、A4 的 TTY 詢問、保留範本模式的 migrate、套件層的實際升級、中途失敗 |

## 已知限制

- 檔案與目錄互換、範本檔轉為種子檔，都需要在該版本加入專用 step。
- `AGENTS.md` 填入 Charter 後，只要範本更新它就會產生旁置檔；分區合併留待後續。
- 0.4.0 以前的版本沒有 `migrate`；降到這些版本需以較新 CLI 搭配 `--source`。
