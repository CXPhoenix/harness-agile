# 貢獻與維護

修改母範本時，先確認變更要改善哪一段採用或協作流程，再在分支中完成修改與驗證。保留 Project Charter 與專案 placeholders，讓下一個採用者可以填入自己的產品。

## 把修改放對地方

| 內容 | 位置 |
| --- | --- |
| 使用者第一次接觸專案 | 根目錄 `README.md` 與 `README.en.md` |
| 採用後仍需要的操作說明 | `docs/guide.md` |
| 開發助理共用規範 | `AGENTS.md` 與 `docs/agents/` |
| Skills 正本 | `.agents/skills/` |
| 範本研究、計畫與歷程 | `.tmpl.docs/research/`、`plans/`、`history/` |
| 範本視覺素材 | `.tmpl.docs/assets/` |

使用者文件依 Quill & Grill 的讀者優先原則撰寫：先交代讀者要完成的事，再給必要步驟、預期結果與限制。中英文 README 同次更新，指令、數字與行為說明保持一致。歷史研究保留當時的證據與日期；新的結論另記歷程。

開發助理文件以英文維護。`CLAUDE.md` 保持匯入入口，skills 的共用規則見 [runtime.md](../docs/agents/runtime.md)。改動正本後，檢閱差異，再執行 `python3 scripts/sync-skills.py --refresh`。

## 驗證修改

使用 Python 3.11+：

```bash
python3 scripts/verify-project.py
python3 -m unittest discover -s tests -v
```

結構檢查涵蓋 skills、來源紀錄與工具設定；測試涵蓋範本初始化與建立器行為。若改動影響套件內容，再依 [CI workflow](https://github.com/CXPhoenix/harness-agile/blob/main/.github/workflows/verify.yml) 建置 wheel 與 npm tarball，執行 `scripts/verify-distributions.py`。

新增範本專用檔案時，確認預設初始化會清理它們，而 `--keep-template-files` 會保留可用入口。新增文件也要檢查連結，包含初始化後的成品。用暫存副本驗證，保留母範本本身。

## 提出變更

說明解決的問題、改動後的行為，以及實際執行的驗證。每次 commit 使用專案 `tw-emoji-commit`，PR 描述使用 `tw-emoji-pr-note`；缺少對應 skill 時停止該動作並回報。

本機測試、套件驗證、遠端 CI 與模型執行結果是不同證據。只回報實際完成的項目，讓下一位維護者知道哪些部分仍待確認。
