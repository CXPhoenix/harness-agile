# 範本採用指引

這是尚未初始化的 harness-agile-template，支援 Claude Code 與 Codex。完整使用說明在 [根目錄 README.md](../README.md)，初始化後仍會保留。

1. 把完整 repository 複製到新專案，保留隱藏目錄與 symlink。
2. 執行 `python3 scripts/verify-project.py` 檢查可攜性。
3. Claude Code 使用 `/init-template`；Codex 使用 `$init-template`。提供專案名稱及一句話描述。
4. 使用 `grill-with-docs` 完成 `AGENTS.md` 的 Project Charter，接著建立 walking skeleton。

也可以直接執行腳本，先預覽再套用：

```bash
python3 scripts/init-project.py --dry-run --name "我的專案" --one-liner "它要解決的問題。"
python3 scripts/init-project.py --name "我的專案" --one-liner "它要解決的問題。"
```

初始化會刪除整個 `.tmpl.docs/`、README 的範本文件入口、初始化腳本、初始化專用測試及兩邊的 init skill 入口。加上 `--keep-template-files` 可完整保留；歷史文件中的 placeholder 不會被替換。它不會設定 Git remote、安裝產品依賴或建立產品功能。

若目前是在維護母範本，保留 placeholders，不要初始化這個目錄。共用規範只修改 `AGENTS.md`；`CLAUDE.md` 保持匯入入口。Skills 正本在 `.agents/skills/`，Claude 使用相對連結。
