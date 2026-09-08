# {{PROJECT_NAME}}

{{PROJECT_ONE_LINER}}

此專案採用 Claude Code 與 Codex 共用的開發流程。先從此目錄開啟工具，用 `grill-with-docs` 定義 `AGENTS.md` 的 Project Charter，再建立 walking skeleton。初始化不代表產品需求已確認。

| 操作 | Claude Code | Codex |
| --- | --- | --- |
| 定義 Charter | `/grill-with-docs` | `$grill-with-docs` |
| 查看 skills | `/skills` | `/skills` |
| 審查變更 | `/code-review` | `$code-review` |

共同規範見 [AGENTS.md](AGENTS.md)，工具分工與交接見 [runtime.md](docs/agents/runtime.md)，交付流程見 [workflow.md](docs/agents/workflow.md)。Codex 專案設定需要本機信任；帳號、憑證與信任設定由各自環境管理。

## 驗證協作設定

需要 Python 3.11+：

```bash
python3 scripts/verify-project.py
```

此命令檢查 skills、來源資料與工具設定；產品自己的 build／test 命令在 walking skeleton 完成後補上。

## 更新 skills

修改 `.agents/skills/` 正本。Claude 入口可能是相對 symlink，也可能是供不支援 symlink 環境使用的副本；verifier 會檢查副本是否一致。檢閱差異後同步：

```bash
python3 scripts/sync-skills.py --refresh
python3 scripts/verify-project.py
```

複製到另一台電腦後，可先執行 `python3 scripts/sync-skills.py`，修復 Git 留下的連結文字檔。更新完成後從新 session 確認原生 skills 清單。

每次 `git commit` 都需使用專案的 `tw-emoji-commit`，PR 與 release 文案分別使用對應的 `tw-emoji-*` skill。
