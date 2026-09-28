# 依使用者的主模型重新調校 skills（計畫）

日期：2026-09-28。狀態：已核准。Claude 版已完成（`.claude/skills/tune-skills`，2026-09-28）；Codex 版也已完成（`.agents/skills/tune-skills`），判準取自 OpenAI 的 GPT-6 Astra 文章，暫時當作 GPT-6 系列的通則（`references/gpt-6.md`）。

## 背景

範本附了兩棵已經調好的 skill 樹：Claude 樹以 Opus 5.5 為目標，Codex 樹依 OpenAI 的建議。但採用範本的人常用的主模型可能不同（例如 Sonnet 5），習慣也可能不同。[claude-orchestration.md](../../docs/agents/claude-orchestration.md) 已經寫了「主模型改變時要重跑 prompt audit」，只是沒有可以直接執行的步驟。

## 已決定

- **做 2 個 skill，各放在自己的樹**：`.claude/skills/tune-skills` 與 `.agents/skills/tune-skills`。每個只依自家廠商的判準，也只改自己那棵樹，避免兩家的建議混在一起。
- **範本仍附兩棵已經調好的樹**。採用範本時不一定要調校；主模型或習慣不同時再重調。

## 設計

**輸入分兩類，處理方式不同**

| 類別 | 例子 | 處理 |
| --- | --- | --- |
| 模型相關 | runtime、主模型、effort | 由 tune-skills 改寫 skill 本文 |
| 使用者習慣 | 語言、委派偏好、commit 風格 | 寫進 `AGENTS.md`／`CLAUDE.md` 或使用者設定，不改寫 skill |

調校結果記錄在 `docs/agents/skill-sources.json` 的 `runtime_trees`，內容是目標模型與日期，下次才知道該不該重調。

**Claude 版的流程**

1. **讀現況**：讀目前記錄的目標模型；和使用者現在的主模型相同就停止。
2. **跑 prompt audit**：用 Claude Code 內建的 `/claude-api prompt-audit`，判準依表面的實際讀者決定。
   - skill 本文用主模型的文章。
   - 角色檔依 `claude-orchestration.md`。
   - 不自己重寫一套審查規則。
3. **產出 patch 和報告**，給使用者核准後才套用。
4. **輕量驗證**，不使用多 agent × 多票反駁：
   - 先做確定性檢查：`verify-project.py`、單元測試、archify 測試，以及 grep 被修改句子在其他檔案的引用。
   - 只有會改變行為的高風險改動，才派一位 `harness-reviewer`，由主 session 裁決。
   - 事先設好預算上限；沒有 P1 就停止。
5. **更新紀錄**：provenance 記錄目標模型與日期；用 `/tw-emoji-commit` commit。

**Codex 版**：流程相同，判準改用 OpenAI 的官方 prompting 文件。Codex 沒有對應的 prompt-audit 工具，要先研究可以用什麼當作流程依據。

**接入點**

- `init-template` 在最後的 Hand over 階段詢問主模型；和目前記錄的目標不同時，建議執行 tune-skills，但不自動執行。
- `claude-orchestration.md` 的「主模型改變時重跑」改為指向 tune-skills。
- 兩棵樹都有這個 skill，`verify-project.py` 的 REQUIRED 清單要一起更新。

## 待確認

- Codex 版的流程依據：先研究 OpenAI 的官方文件，再決定。
- tune-skills 的 `disable-model-invocation`：建議設為 `true`，只由使用者或 init-template 叫用。

## 範圍外

- 暫緩的 P2 項目，見[稽核報告](../research/2026-09-26-claude-skill-prompt-audit.md)。
