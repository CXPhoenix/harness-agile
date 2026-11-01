# 全新上下文四軸規格審查

日期：2026-11-01。使用者已核准[計畫與測試表](../plans/2026-11-01-fresh-context-spec-review.md)，在 `codex/fresh-context-spec-review` 隔離 worktree 實作；原 checkout 與三份未提交研究／計畫保留。本紀錄保存驗證完成時、commit 前的狀態；當時尚未 commit、push、合併或發布套件。

## 實作

- `review.md` 保存 fresh-context、版本封包及有效完成契約；runtime 說明兩個宿主的派工方式。
- 每軸、每輪使用新對話；缺少能力、缺檔、失敗或 stale 維持未完成，不當作零 findings。
- 保留四軸、frozen prompt、最多兩輪、P0 gate 與使用者裁決；技術補跑不容許繞過內容輪數。
- 兩套 reviewer 角色分開列出 spec packet 與 code/security 的 Git 輸入；Stage 6／7 fallback、模型、權限、Charter 與 placeholders 保留。
- 新增 ADR-0004 與使用者說明，沒有新增 plugin、skill 或 Python engine。

## 證據與限制

完整 [執行證據與 coverage](../research/2026-11-01-fresh-context-review/evidence.md)、[變更 review](../research/2026-11-01-fresh-context-review/code-review.md)、[安全審查](../research/2026-11-01-fresh-context-review/security-review.md)。

Codex desktop 原生 1 次基線加 8 次兩輪四軸，第一輪發現 seeded 缺口，第二輪四軸零 findings；prompt hash 相同，沒有第三輪。兩輪合計 72 個必要檔案讀取/hash 回報均符合 manifest，parent 驗證 packet 未變。10 個注入 gate 案例只驗證主助理決策，不冒充實際工具故障。

Claude Code 未登入，live 未執行。有效 host sandbox 是 workspace-write，工具層強制唯讀未驗證；MEMORY_SUMMARY 仍會注入。完整底層 child raw read／memory trace、真實 timeout／停用能力的故障注入及跨平台遠端 CI 尚未驗證。這些限制不以結構檢查或兩輪 fixture 成功替代。

## 最終本機檢查

結構檢查通過，既有 22 項測試通過；來源初始化的 default／keep 模式通過。Wheel 與 npm snapshot 相同，uvx／npx／pnpx 預設初始化及 wheel 的保留範本模式通過，最終 9 份正式規範／role／guide 與測試套件 bytes 一致。變更 review 的唯一 P2 已修正並獲原 reviewer 定點 closure；安全候選為 0。詳見上方 evidence 的 coverage table 與 package source digest。

驗證完成時，工作保留於隔離 worktree、尚未 commit；原本 main 的未提交研究／計畫保持原樣。後續 commit 與 PR 以 Git 紀錄為準；套件發布與合併不在這次交付範圍。
