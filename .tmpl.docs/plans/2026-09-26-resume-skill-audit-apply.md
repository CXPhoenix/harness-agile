# 接續：套用 Claude skills audit patch（2026-09-26 凍結）

> **狀態：已於 2026-09-28 完成。** 沒有照原步驟接續審查 workflow，理由是成本；改由主 session 裁決 finding。結果見[稽核報告的「套用與審查」](../research/2026-09-26-claude-skill-prompt-audit.md)。

使用者要求暫停以控制消耗，預定週一接續。

## 目前狀態

- **分支**：`claude/split-runtime-skills`，最後一個 commit 是 `d68acc3`。
- **已套用、未 commit**：`.tmpl.docs/research/2026-09-26-claude-skill-prompt-audit.final.patch` 已套到工作目錄，共 44 項修改、26 個檔案。
  - 與舊版 `.patch` 的差異：拿掉 D5，C1 恢復較強的寫法（已由 Claude Code skills 文件確認）。
  - 用 `git status` 可看到 26 個 `.claude/skills/**` 修改。
- **結構檢查**：尚未確認。apply 階段的 executor 已在 workflow 內跑過 verify 與 unittest，但結果在 workflow 被停止前沒有取回。
- **修訂後 B3 的重測（S3 patched，5 次，$1.81）**：
  - 5/5 沒有派 subagent。
  - 5/5 筆記都有標示推論、列出未解問題並記錄驗證日期。
  - 筆記是英文，因為 fixture 沒有語言規則。
  - 結果存在 `.tmpl.docs/research/2026-09-26-skill-behavior-experiment/round2-b3-revised/`，尚未寫進實驗結果文件。
- **審查 workflow 被中途停止**：run ID `wf_d1bbcbff-9d6`。已完成的 agent 結果有 cache，但 cache 在原 session 的 transcript 目錄內。

## 接續步驟

1. 在原 session 中，用相同 script 加上 `resumeFromRunId: wf_d1bbcbff-9d6` 重跑審查 workflow，已完成的 agent 直接取用 cache。如果是新 session，就重跑審查（apply 階段要跳過，因為 patch 已經套用）。
2. 依確認成立的 findings 裁決修正方式；由 `harness-executor` 修改後再審一次。
3. 執行 `/opt/homebrew/bin/python3 -B scripts/verify-project.py` 與 `-m unittest discover -s tests`。
4. 把 round 2 結果補進實驗結果文件，並在稽核報告中標示 D5 排除、C1 恢復。
5. 用 `/tw-emoji-commit`（專案版本）commit。

## 放棄時

如果決定不套用，用 `git apply -R .tmpl.docs/research/2026-09-26-claude-skill-prompt-audit.final.patch` 還原。
