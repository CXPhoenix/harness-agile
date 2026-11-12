# 更新紀錄

## [Unreleased]

## ✨ [0.5.0] - 2026-11-12

> 新增 `harness-agile migrate`，讓已建立的專案可以升級或降級範本；領域詞彙表跟隨上游改名為 `GLOSSARY.md`，並同步 mattpocock/skills 至 `4ae2317`。

### ✨ 新增
- 新增 `harness-agile migrate`，把專案移到執行中 CLI 的範本版本，升級降級都可以。預設只預覽計畫，加 `--apply` 才寫入。本機改過的範本檔不會被覆寫，目標版本內容另存為 `<檔名>.harness-new`；結構調整以可還原的 migration step 記錄。0.4.0 以前建立的專案可用 `--adopt` 納入管理 ([#16])。
- 建立專案時在 `docs/agents/template-source.json` 記錄範本版本、建立參數與逐檔 SHA-256，供 migrate 判斷哪些檔案改過；`verify-project.py` 會在旁置檔未處理時失敗 ([#16])。
- migrate 新增 `glossary-rename` step：升級到 0.5.0 時，把根目錄的 `CONTEXT.md`／`CONTEXT-MAP.md` 改名為 `GLOSSARY.md`／`GLOSSARY-MAP.md`，降級時改回。新檔名已存在，或子目錄還有 `CONTEXT.md` 時不會移動，計畫會列在 `by hand` ([#18])。

### 🔄 變更
- 同步 mattpocock/skills 上游 `3cca18b..4ae2317`，涵蓋 setup-matt-pocock-skills 的 tracker 範本、diagnosing-bugs、teach、to-tickets、grilling、wayfinder、code-review、implement 與 tdd。兩套 runtime 各自保留既有的本機改編，來源與差異記錄在 `docs/agents/skill-sources.json` ([#18])。
- Codex 樹的 subagent 一律以全新 context 啟動，`docs/agents/runtime.md` 補上 Stage 3 以外的隔離規則與無法隔離時的 fallback ([#18])。
- `setup-matt-pocock-skills` 偵測到舊的 `CONTEXT.md`／`CONTEXT-MAP.md` 時，會提議以 `git mv` 改成新名稱 ([#18])。

### 🐛 修復
- Archify 改以 bigint 比對檔案 identity。先前 Windows NTFS 的 file ID 超過 2^53 會失去精度，不同的檔案或目錄被誤判成 output／input alias，導致 `deliver`／`preview` 隨機失敗 ([#17])。
- 初始化移除範本 banner 時接受 CRLF 換行，修正 Windows 上 banner 沒有移除的問題 ([#16])。
- wizard `template.sh` 改用上游版本，另修正 shellcheck SC1087，以及 macOS 內建 bash 3.2 重跑時把 `.env` 值中的 `'` 變成 `\'` 的問題 ([#18])。
- Codex 樹的 wayfinder 不再讓每張 research ticket 各開 subagent、push 永不合併的 `research/<name>` branch，改由 research skill 處理，並由主 session 把結果存到 tracker 指定的位置，與 Claude 樹及 `docs/agents/issue-tracker.md` 一致 ([#19])。

### 💥 Breaking Changes
- **領域詞彙表檔名**：`CONTEXT.md`／`CONTEXT-MAP.md` → `GLOSSARY.md`／`GLOSSARY-MAP.md`。domain-modeling 的格式檔也改名為 `GLOSSARY-FORMAT.md`。skill 執行時只讀新名稱，不會回頭找舊檔名 ([#18])。
  遷移方式：執行 0.5.0 的 `harness-agile migrate`（0.4.0 以前建立的專案先加 `--adopt`），根目錄的詞彙表會自動改名；計畫列在 `by hand` 的檔案請自行合併或 `git mv`。

### 使用注意
- migrate 不會 commit。套用後先檢查 `git diff` 並處理所有 `.harness-new`，再提交。
- `teach` 會在執行目錄寫自己的 `GLOSSARY.md`，請在另外的工作目錄執行 `/teach`，不要在 repo 根目錄執行。
- 同步後的 skill 只經過結構檢查與靜態審查，沒有在原生 Claude Code／Codex session 實際跑過；wizard 只在 bash 3.2 測試過。
- PyPI／npm 依既有手動流程發布；npm 候選需由維護者完成 2FA 核准後才公開。

[#16]: https://github.com/CXPhoenix/harness-agile/pull/16
[#17]: https://github.com/CXPhoenix/harness-agile/pull/17
[#18]: https://github.com/CXPhoenix/harness-agile/pull/18
[#19]: https://github.com/CXPhoenix/harness-agile/pull/19

## ✨ [0.4.0] - 2026-11-01

> 新增顯式 EGM 診斷，補齊 fresh-context 規格審查與研究分工，並修正操作指引及開發依賴。

### ✨ 新增
- 新增兩套 runtime 的 `egm-drift-report`，可明確指定文件與實作範圍，產出附來源位置、SHA-256、查核範圍與限制的 Markdown 診斷。區分確認差異、待確認與預期差異，並以 complete／partial／blocked／stale 表達診斷狀態；這是 EGM 的本機改編，不是完整上游 plugin 安裝 ([#12])。

### 🔄 變更
- Stage 3 規格審查改為每軸、每輪都使用不繼承父對話的全新 reviewer，主助理提供固定 prompt、spec、traceability 與必要專案規範，記錄版本與完成證據。四軸有效完成且零 P0 才能前進，最多兩輪；缺少輸入、無法取得 fresh context 或來源變動均不能算通過 ([#11])。
- 補齊跨 runtime 的角色、輸入封包與交接規則；不改使用者選定的角色模型、既有權限或 spec／ticket gates ([#11], [#13])。

### 🐛 修復
- Codex `research` 對齊唯讀角色分工：researcher 回傳證據、日期與未解事項，由主助理保存成果；協作指南分開說明 Codex 的 session 繼承與 Claude reviewer 的角色模型設定 ([#13])。
- 採用指引更新為預設每套保留 33 個 skills；兩套 `init-template` 改依 ADR 的 `INIT_DATE` placeholder 描述日期，避免固定數量落後實際內容 ([#13])。

### 🔒 安全性
- 兩套 Archify 的開發依賴 `fast-uri` 更新至 3.1.9，修正既有 audit gate 報告的四則安全公告；保留原有掃描門檻，沒有將開發依賴公告宣稱為已確認的產品執行期漏洞 ([#11])。

### 使用注意
- 使用 `/egm-drift-report`（Claude）或 `$egm-drift-report`（Codex）顯式叫用診斷。它只建立新報告，不自動修正、開票或推進 gates；報告標示 partial 或 stale 時不能解讀為沒有差異。
- 母範本與 `--keep-template-files` 各有 34 個 skills，預設初始化後各保留 33 個。既有採用專案不會自動更新，也不會自動重設 tracker。
- 靜態設定與 CLI／套件測試不證明模型行為或工具強制唯讀。無法取得合格 fresh context 時，Stage 3 仍維持未完成；既有 Claude 原生宿主與強制拒寫的驗證限制保留。
- Windows 的 Archify 自動開啟仍停用，請手動開啟產物。PyPI／npm 仍依既有手動發布流程；npm 候選需由維護者完成 2FA 核准後才公開。

[#11]: https://github.com/CXPhoenix/harness-agile/pull/11
[#12]: https://github.com/CXPhoenix/harness-agile/pull/12
[#13]: https://github.com/CXPhoenix/harness-agile/pull/13

## ✨ [0.3.0] - 2026-10-16

這一版把 Claude Code 與 Codex 的 skills 拆成兩份獨立副本，各自依自家模型的 prompting 指引調校，並新增 tune-skills，讓採用者可以依自己的主模型重新調校。

### ✨ 新增
- 新增 `tune-skills`，Claude 版與 Codex 版各一份，只能手動叫用。主模型和記錄的調校目標不同時，可以用它稽核自己 runtime 的 skills，產出報告與 patch，經使用者核准後才套用 ([#8], [#9])。
- 新增 Claude 的模型分工設定：`harness-reviewer`、`harness-challenger`、`harness-executor`、`harness-researcher` 四個角色各自指定模型，並附上委派時機與 findings 回報原則 ([#8])。
- handoff 改存到 repository 根目錄的 `.proj.handoffs/`，不進版控；文件開頭用 frontmatter 標註到期條件，接手時會先檢查有沒有過期 ([#8])。

### 🔄 變更
- `.claude/skills/` 不再是 `.agents/skills/` 的 symlink 或同步副本，改為兩份獨立目錄，各自調校。Claude 那份依 Opus 5.5 的 prompting 指引稽核並調整過 ([#8])。
- `--skill-mode` 保留為不再有作用的旗標，使用時會印出棄用警告。CLI JSON 的 `skills` 與 `skill_mode` 欄位維持相容，另新增 `codex_skills` ([#8])。

### 🐛 修復
- 補上拆成兩份副本後 wheel 缺少的 Claude 樹授權檔；Windows 上 skill 目錄若是 symlink，現在會正確回報「必須是實體目錄」([#8])。
- 明確指定 npm 發布產物的本機路徑 ([#6])。

### 🔒 安全性
- Archify 開發依賴 fast-uri 更新至 3.1.8，修正 GHSA-qw65-cvwx-89v3、GHSA-58mr-gqgx-xq4g（high）與 GHSA-hrr3-gc8f-f4qj（medium）。fast-uri 只在開發時用來產生驗證器，重新產生的驗證器內容不變 ([#9])。
- npm 改用 staged publishing：CI 只上傳待審版本，由維護者在 npm 完成 2FA 核准後才公開 ([#7])。

### 使用注意
- 用舊版範本建立的專案若要沿用新的 handoff 規則，請在 `.gitignore` 加入 `/.proj.handoffs/`，否則新版 `verify-project.py` 會失敗。跨機器交接不再透過 Git 傳遞，需要自行複製檔案。
- 兩份 skills 不再自動同步；修改流程、gate 或輸出位置時，需要手動移植到另一份。
- 套件內含兩份 Archify，安裝體積比 0.2.1 大。

[#6]: https://github.com/CXPhoenix/harness-agile/pull/6
[#7]: https://github.com/CXPhoenix/harness-agile/pull/7
[#8]: https://github.com/CXPhoenix/harness-agile/pull/8
[#9]: https://github.com/CXPhoenix/harness-agile/pull/9

## 🐛 [0.2.1] - 2026-09-13

更新正式套件安裝入口，並納入可驗證的 registry 發布流程。

### 🔄 變更
- 中英文 README 與 INSTALL 改用固定版本的 PyPI／npm 安裝指令，不再要求 GitHub 存取權限。
- 維護者可從 main 手動指定 tag，透過 Trusted Publishing 發布至 PyPI 與 npm。

### 🐛 修復
- 預設初始化移除母範本專用發布 workflows，避免新專案保留錯誤的發布目標；保留範本模式仍保留。

### 使用注意
- Windows 自動開啟維持停用，產圖與手動開啟不受影響。

## ✨ [0.2.0] - 2026-09-13

提供完整授權聲明與經驗證的 Claude Code／Codex 範本，新增 Archify 架構圖工具。

### ✨ 新增
- 內建 Archify，可產生與檢查架構、工作流程、循序、資料流及生命週期圖表。
- 新增中英文使用入口、協作指南，以及 Archify 可攜與本機預覽測試。

### 🔄 變更
- 專案採 MIT，補齊第三方授權、來源及字型／品牌素材條款，並隨安裝成品保留。
- 整理 Claude Code 與 Codex 的 skill 發現、呼叫及工具邊界。

### 🐛 修復
- 預覽監聽前解析真實目錄路徑，處理 Windows 短路徑可能導致 Node.js 中止的問題。

### 🔒 安全性
- 停用 Windows 圖表與 preview 自動開啟；仍可產生與驗證，請手動開啟產物或網址。
- 將 Archify 開發依賴 fast-uri 更新至 3.1.6；未將依賴公告誤報為已確認可利用的產品 SSRF。
- 本機重現實驗資料排除於 Git 與發布套件之外。

### 使用注意
- 第三方品牌圖示保留各自條款，根目錄 MIT 不取代其使用限制。
- 此版本不包含原生 Windows 風險重現證據；Windows 自動開啟維持停用。
- v0.1.0 是歷史快照，請使用 v0.2.0 取得本次內容。
