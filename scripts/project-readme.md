# {{PROJECT_NAME}}

{{PROJECT_ONE_LINER}}

此專案採用 Claude Code 與 Codex 共用的開發流程。在這個目錄開啟開發助理，用 `grill-with-docs` 定義 Project Charter，確認產品服務誰、解決什麼問題，以及必須做到什麼，再建立 walking skeleton。

## 開始協作

| 操作 | Claude Code | Codex |
| --- | --- | --- |
| 定義 Charter | `/grill-with-docs` | `$grill-with-docs` |
| 查看 skills | `/skills` | `/skills` |
| 審查變更 | `/code-review` | `$code-review` |

名稱與一句話描述已填入，產品需求仍需確認。日常操作、skills 更新與工具交接見[協作指南](docs/guide.md)；完整規則見 [AGENTS.md](AGENTS.md) 與[文件導覽](docs/README.md)。

Codex 專案設定需要本機信任。帳號、憑證與信任設定由各自環境管理；更新設定後，從新 session 確認 skills 清單。

## 驗證協作設定

需要 Python 3.11+：

```bash
python3 scripts/verify-project.py
```

此命令檢查 skills、來源資料與工具設定。產品自己的 build／test 命令在 walking skeleton 完成後補上。

每次 `git commit` 都使用專案的 `tw-emoji-commit`；PR 與 release 文案分別使用對應的 `tw-emoji-*` skill。

## 範本授權

沿用的 harness-agile 範本內容採 [MIT License](LICENSE)，第三方內容依[原有條款](THIRD_PARTY_NOTICES.md)保留聲明。新增產品內容的授權由產品維護者決定。

Windows 的 Archify 自動開啟功能已停用；請手動開啟產物或預覽網址。詳見[停用範圍與驗證方式](docs/security/windows-opener.md)。
