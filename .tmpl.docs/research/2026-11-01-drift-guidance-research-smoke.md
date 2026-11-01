# Codex research 分工 smoke 證據

驗證日期：2026-11-01（Asia/Taipei）。這是核准計畫 V10 的執行紀錄，由主助理保存；不是新一輪 drift 診斷。

## 問題、版本與實際操作

問題：此 checkout 的預設初始化與 `--keep-template-files`，對兩套 init-template skills、`.tmpl.docs` 歷史 placeholders、ADR `INIT_DATE` 各如何處理？

- Checkout：`/Users/phoenix/dev/edu-projects/harness-agile-template/.worktrees/drift-guidance-alignment`。
- Branch：`codex/drift-guidance-alignment`；HEAD：`9bc062a9e6397214b1ef31fc46f0ae26c60e7833`，包含本輪未提交修正。
- 主助理讀取修改後的 `.agents/skills/research/SKILL.md`，以原生 collaboration API 啟動 `alignment_research_smoke`；`agent_type: harness-researcher`、`fork_turns: none`，未指定模型或 effort。
- 派工限定讀取本機第一手來源、回傳證據，由 parent 保存單一 Markdown；研究者不執行受檢程式、不寫檔、不使用網路或啟動下一層代理。
- 研究者回傳附行號的觀察、來源主張、推論、驗證日期及未解事項；主助理將結果保存在本檔。期間工作區的受檢來源未被研究者修改。

## 研究者回傳的來源觀察

| 對象 | 預設初始化 | `--keep-template-files` | 來源 |
|---|---|---|---|
| `.agents/skills/init-template/`、`.claude/skills/init-template/` | 兩者均刪除 | 兩者均保留 | `scripts/init-project.py:29–40,148–173` |
| `.tmpl.docs/` 歷史與 placeholders | 目錄刪除；刪除前不替換其中 tokens | 歷史及其中 tokens 保留原值 | `scripts/init-project.py:61–90,148–173` |
| `docs/adr/` 中的 `{{INIT_DATE}}` | 換成採用日期 | 同樣換成採用日期 | `scripts/init-project.py:98,120–146` |

掃描器排除 `.agents`、`.claude` 及範本專用路徑，因此 keep 保留的 skill／歷史 tokens 不參與替換及殘留檢查；token 替換在可選刪除區塊前執行。日期預設取執行環境當日，也可用合法的 `--date YYYY-MM-DD` 指定。

目前五份 ADR 各在第 3 行含 `date: {{INIT_DATE}}`：`docs/adr/0001-walking-skeleton-then-epic-loop.md`、`0002-ticket-status-in-frontmatter.md`、`0003-adversarial-review-fixed-axes-two-rounds.md`、`0004-fresh-context-spec-review.md`、`0005-drift-diagnosis-native-host-verification.md`。

## 來源主張與推論

兩套 `init-template/SKILL.md:33–42` 的來源主張與上述程式碼一致：default 刪除兩套初始化入口、keep 保留歷史，ADR 日期以 token 說明。`.tmpl.docs/README.md:31–37` 亦記載範本歷史及採用時的保留／移除規則。

研究者的推論是：成功初始化時，兩種模式都應替換目前五份 ADR 日期；已有固定日期而不含 token 的 ADR，日期不會因這個選項重寫。這是研究者的靜態推論，不是研究者執行 initializer 的結果。主助理另行執行的真實成品驗證見[修正與驗證紀錄](../history/2026-11-01-drift-guidance-alignment.md)。

## 工具、權限與驗證限制

- 研究者回報使用 `functions.exec` 包裝 `exec_command`，讀取／搜尋指令為 `pwd`、`sed`、`cat`、`nl`、`rg`；回報沒有寫檔、執行受檢程式、網路存取或 nested delegation。此操作清單來自代理回覆，不是獨立工具稽核 log。
- role 檔 `.codex/agents/harness-researcher.toml:3–5` 宣告 `read-only`；研究者觀察到注入環境為 `workspace-write`。這次指派與操作維持唯讀，**不能宣稱工具層已強制唯讀**，也沒有執行拒絕寫入探測。
- 未從工具回傳取得精確模型 ID 或 reasoning effort；沒有猜測或覆寫模型設定。
- 本 smoke 僅涵蓋一次原生 Codex 研究委派、證據回傳及 parent 保存的工作分工。未驗證 Claude 宿主、全域 discovery、模型抗 prompt injection、所有輸入情境或強制權限隔離。

驗證結論：V10 的本機研究分工已觀察到；工具強制唯讀及其他宿主行為仍未驗證。
