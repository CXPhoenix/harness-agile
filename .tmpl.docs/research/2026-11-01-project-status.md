# 專案進度與狀態查核

查核日期：2026-11-01（Asia/Taipei）。對象為 `harness-agile` 母範本，查核基準為 `main` 的 `110a6224773d69b792b840e2a94c9966ed3ea110`。本報告完成前，主 checkout 與既有功能 worktree 都沒有未提交變更。本次僅新增此研究紀錄，未修改實作、commit、push、清理分支或發布套件。

## 判斷

目前可接續母範本維護：PR #11 已合併，本機與 GitHub `main` 相同；合併後三平台 CI 及本次本機範本檢查均通過。全新上下文四軸審查的規範與 adapter 已交付到原始碼，但 Claude live、真實故障情境及新版套件發布仍有待完成。[S1][S2][S3][S7]

## 已確認的目前狀態

| 項目 | 查核結果 | 來源／證據 |
|---|---|---|
| 專案定位 | 仍是母範本；Charter 保留 `{{PROJECT_NAME}}` 等 placeholders，沒有採用為特定產品 | [AGENTS.md](../../AGENTS.md) |
| 主分支 | 本機 HEAD、既有 `origin/main` 與 GitHub API 的 `main` 均為 `110a622` | `git status --short --branch`、`git rev-parse HEAD`、[S1] |
| 最近交付 | PR #11 已合併；包含全新上下文四軸審查與兩套 Archify 的 fast-uri 3.1.9 修正 | [S2]、[修正紀錄](../history/2026-11-01-pr11-ci-fast-uri.md) |
| 開啟中的協作項目 | GitHub open issues API 回傳空陣列，當下沒有 open issue 或 PR | [S4] |
| 功能分支 | `.worktrees/fresh-context-spec-review` 與 `codex/fresh-context-spec-review` 仍保留，HEAD 為 `b366cda`，工作目錄乾淨；已包含於 main 歷史 | `git worktree list --porcelain`、`git branch -avv`、功能 worktree 的 `git status`；[S2] |
| 追蹤文件 | `.proj.specs/` 只有 OPEN-QUESTIONS 範本、`.proj.tickets/` 只有 `.gitkeep`；未登錄產品 spec、ticket 或 OQ | `git ls-files .proj.specs .proj.tickets`、[OPEN-QUESTIONS.md](../../.proj.specs/OPEN-QUESTIONS.md) |
| 版本號 | Python 與 npm manifest 均為 0.3.0；本機 v0.3.0 指向 `72677d5`，main 在其後有 3 個 commits（含 merge commit） | [pyproject.toml](../../pyproject.toml)、[package.json](../../package.json)、`git rev-list -n 1 v0.3.0`、`git rev-list --count v0.3.0..HEAD` |
| 公開版本 | 最新正式 GitHub Release、PyPI 與 npm latest 都是 0.3.0；尚無包含 PR #11 的新版公開套件 | [S5][S6][S8] |

沒有已登錄的產品 ticket，不代表沒有維護待辦；未完成的驗證主要記錄於 `.tmpl.docs/`。

## 本次驗證與既有證據

| 驗證介面 | 本次查核結果 | 範圍與限制 |
|---|---|---|
| 本機範本結構 | `python3 scripts/verify-project.py` exit 0；33 種 skills、兩套 runtime 樹與角色設定通過 | 靜態／離線檢查，不等於模型行為通過 |
| 本機建立器與初始化 | `python3 -m unittest discover -s tests -v` exit 0；22/22，9.822 秒，Python 3.14.3 | CLI、範本初始化、封裝與結構檢查相關測試；不涵蓋產品功能 |
| 合併後 CI | run `41288885481` 對應 main `110a622`；Ubuntu、Windows、macOS 三個 packages jobs 全部 completed／success | [S3]；workflow 包含 Archify portable／preview、npm audit、wheel／npm 建置與分發驗證。這些是 GitHub 執行結果，本次未於本機重跑全部 CI 步驟 |
| Codex 全新上下文審查 | 既有執行紀錄：1 次基線＋8 次正式 reviewer；第一輪發現預埋缺陷，第二輪四軸零 P0，72/72 必要檔案 hash/read 回報吻合 | [既有 evidence](2026-11-01-fresh-context-review/evidence.md)；僅為合成 fixture 的 Stage 3 gate，未在本次重跑，也不代表某個產品 epic 已通過 |

現行四軸規範仍保留 frozen prompt、最多兩輪、P0 gate。缺少 fresh 能力、缺檔、失敗、timeout 或 stale 都屬未完成；不能以零 findings 代替完成證據。[review.md](../../docs/agents/review.md)

## 尚未完成與證據界線

1. **Claude 全新上下文審查 live 驗證。** 先前測試時未登入 Claude，因此只完成 adapter／可攜性檢查。本次沒有檢查目前登入狀態，也沒有執行 Claude 模型審查。[S7]
2. **真實故障與隔離驗證。** 10 個 gate cases 是預製結果的決策檢查；timeout／crash、能力停用、stale 競態尚無原生注入證據。先前有效 sandbox 為 workspace-write，仍注入 MEMORY_SUMMARY，缺少完整 child raw read／memory trace；fresh context 不保證檔案系統或外部記憶隔離。live suite 後的 Claude 摘要釐清只做定點 review 與靜態／套件驗證，未重跑完整 live suite。[S7]
3. **Codex tune-skills 流程實測與重新調校。** 計畫仍標示待測；provenance 的 Codex 目標仍是 GPT-6 前、模型未記錄的最佳化。現有 skill 已實作，但未登錄 GPT-6 調校完成。[調校計畫](../plans/2026-09-28-runtime-skill-tuning.md)、[provenance](../../docs/agents/skill-sources.json)
4. **Claude Sonnet 5.5 patch。** Opus 5.5 曾以 Sonnet 5.5 為目標測試流程、產出 7 項修改，沒有正式套用或更新調校紀錄；也沒有 Sonnet 行為前後比較。流程缺口的修正與套用 Sonnet patch 是不同工作。[實測報告](2026-10-16-tune-skills-test/README.md)
5. **新版套件交付。** PR #11 已進 main，但版本號、CHANGELOG 與固定安裝入口仍為 0.3.0。PyPI provenance 指向 `72677d5`；npm 官方 registry latest 為 0.3.0，公開 versions 只有 0.2.0、0.2.1、0.3.0，未提供 gitHead。本次未重新安裝 registry 套件或逐檔核對 npm 產物。[S5][S6][S8]、[INSTALL.md](../../INSTALL.md)
6. **既有暫緩項目。** Windows Archify 自動開啟維持停用；原生 Windows 風險實驗／替代 opener 不在這次交付中。三平台 CI 通過不能取代該實驗。[停用說明](../../docs/security/windows-opener.md)

本次採納的是 EGM 的全新上下文審查機制；不將它描述成已安裝或完整整合 EGM plugin，也不宣稱 token／成本或一般產品規格缺陷發現率已有改善。[實作計畫](../plans/2026-11-01-fresh-context-spec-review.md)、[S7]

## 建議接續順序

使用者於本次查核後指出，先前介面推薦的下一步是：「接下來請規劃 egm-drift-report 的整合，先擬定實作計畫與測試表，保留現有的 spec／ticket 流程，先不要實作。」這與[原整合研究](2026-11-01-elephant-goldfish-integration.md)第 5 個試行步驟及獨立第二步的安排一致。此處據此修正先前將驗證缺口排為下一步的建議；並未把該推薦視為計畫已核准或已開始實作。

1. **承接 EGM 路線：規劃 egm-drift-report。** 下一階段先產出整合實作計畫與待核准的測試表，保留現有 `.proj.specs/`、traceability、`.proj.tickets/` 及交付 gates。維持顯式觸發的診斷工具定位，報告不代替 spec／ticket 流程，也不先新增每張 ticket 的必跑步驟。本次確認範圍不包含撰寫該計畫或實作。
2. **其餘驗證缺口獨立追蹤。** Claude live、真實故障情境、Codex tune-skills、Sonnet patch 與新版發布仍保留為待辦；目前沒有證據要求它們全部完成後才能規劃 drift-report。發布仍依[既有規範](../registry-publishing.md)辦理。
3. **清理另行安排。** 已合併 worktree／分支與原稿備份本次未刪除。原稿備份 manifest 位於 `.proj.handoffs/2026-11-01-pr11-pre-sync-files/backup-manifest.json`，目前仍被 Git 忽略。

## 來源與歷史判讀

- [S1：GitHub main API](https://api.github.com/repos/CXPhoenix/harness-agile/branches/main)
- [S2：PR #11](https://github.com/CXPhoenix/harness-agile/pull/11)，API 確認 `state=closed`、`merged=true`、merge SHA `110a6224773d69b792b840e2a94c9966ed3ea110`。
- [S3：合併後 Actions run](https://github.com/CXPhoenix/harness-agile/actions/runs/41288885481)，另查同一 run 的 jobs API 確認 3/3 success。
- [S4：GitHub open issues API（包含 PR）](https://api.github.com/repos/CXPhoenix/harness-agile/issues?state=open&per_page=100)
- [S5：GitHub Releases](https://github.com/CXPhoenix/harness-agile/releases)，API 回傳的最新正式版本為 v0.3.0，另保留一筆未公開的 v0.2.0 草稿；草稿不列為正式版本。
- [S6：PyPI 專案與 provenance](https://pypi.org/project/harness-agile/)，0.3.0 的發布來源為 `72677d5f04cfa9ace6658181d1317dacc1118305`。
- [S7：全新上下文審查執行證據](2026-11-01-fresh-context-review/evidence.md)，其中「未合併／未跑遠端 CI」描述的是 commit 前快照；目前合併與 CI 狀態以 S1–S3 為準。
- [S8：npm 官方 registry](https://registry.npmjs.org/create-harness-agile)，唯讀 JSON 查詢確認 `dist-tags.latest=0.3.0`，發布時間為 `2026-10-15T18:22:19.529Z`（台灣時間 10 月 16 日）。一般 npm 網頁在本次查詢回傳 403，改查官方 registry。
- 上一個聊天 `01a19617-43bb-79c1-97f2-9b30125b0b2d` 已透過 `read_thread` 讀取，提供研究、核准、實作、修正 CI 與同步 main 的脈絡；目前狀態另以 Git／GitHub／registry 重新核對。

原有歷史文件保留當時狀態，不覆寫成今日狀態；本報告是查核時點的快照，也不保證後續遠端狀態不變。
