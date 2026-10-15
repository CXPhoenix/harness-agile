# 更新紀錄

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
