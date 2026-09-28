# Claude／Codex skills 分離

日期：2026-09-26

## 背景

`.claude/skills/` 原本是指向 `.agents/skills/` 的相對 symlink，或經驗證完全一致的副本。Anthropic 與 OpenAI 的 prompt engineering 官方建議差異很大，共用同一份內容會讓兩邊的調整互相干擾。維護者決定改成兩份獨立副本，之後分別依官方建議微調 Claude 版本。

## 決策

| 問題 | 決定 |
| --- | --- |
| 跨工具 metadata | 各樹只留自己的：Claude 副本移除 `agents/`（含 `openai.yaml`）；Codex 版本移除 `disable-model-invocation` |
| 名稱集合 | 允許單邊專屬 skill；pipeline 與 hard rules 用到的必要 skills 兩邊都要有 |
| `--skill-mode` | 保留為無作用旗標並印出 deprecation 警告；CLI JSON 的 `skills` 與 `skill_mode` 欄位維持相容，另加 `codex_skills` |

## 變更

- `.claude/skills/` 改為 `.agents/skills/` 已追蹤檔案的實體副本；sanitizer 路徑說明改指向各自目錄。
- 移除 `scripts/skill_links.py`、`scripts/sync-skills.py`、`tests/test_skill_links.py` 與 CI 中的同步步驟。
- `verify-project.py` 分別檢查兩棵樹：必要 skills、frontmatter、不含連結、不含對方工具的 metadata，以及同名 skill 的觸發政策一致。
- 建立器 bundle 直接打包 `.claude/skills/`；初始化不再同步 skills。
- 新增 `tests/test_verify_project.py`（範本專用，初始化時移除）。
- `AGENTS.md`、`CLAUDE.md`、`docs/agents/`、`docs/guide.md`、`INSTALL.md`、README 與採用文件改為描述兩套獨立目錄。

## 取捨

- archify 約 8.5 MB 的程式與測試會存在兩份，套件體積約增加一倍 skills 部分；CI 只對 `.agents/skills/archify` 跑測試。
- 行為層面的修改（流程、gate、輸出位置）不再自動同步，需要手動移植到另一棵樹。

## 驗證

- `python3 -m unittest discover -s tests -v`：21 項通過（本機，macOS）。
- `verify-project.py` 在排除 `.DS_Store` 的乾淨副本中通過（由 `test_verify_project` 覆蓋）；本機工作目錄因既有、被 Git 忽略的 `.agents/skills/.DS_Store` 失敗，與本次變更無關。
- 未執行：wheel／npm 套件建置與 `verify-distributions.py`、遠端 CI、新 session 中的 skill discovery 實測。
