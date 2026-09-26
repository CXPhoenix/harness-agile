# Claude skills 行為驗證實驗計畫

日期：2026-09-26。狀態：**已執行**，結果見 [實驗結果](../research/2026-09-26-skill-behavior-experiment/README.md)。範圍經 challenger 審查後修訂為 S3、S4 各組 5 次（20 個 trial，預算上限 $30）。

> 更正：下文提到「使用 `--allowedTools` 白名單」，但實際執行時為 `permissionMode: auto`，白名單沒有生效，兩組條件相同。詳見結果文件。

## 修訂後的設計（實際執行版本）

`harness-challenger` 在執行前指出，原精簡版中多數指標無法區分兩組。修訂如下：

- **S1（commit）不跑**：D3a 的必要性由 shell 語意即可證成（雙引號中的 `$(...)` 會被執行）。「是否自行 commit」會被全域 CLAUDE.md 主導，而且這條政策使用者已經決定。
- **S5（to-tickets）不跑**：B6 在真實環境中是 no-op，因為 AGENTS.md 已要求先讀 issue-tracker.md；B7 會被 Charter gate 和 stage 4 gate 遮蔽。兩項改依文字清晰度決定是否採用。
- **S3 指標**改為「主 session 是否啟動 subagent」（頂層 `Agent`／`Task` tool call）。兩組都會寫出筆記檔，無法用來區分。
- **S4 改用中性 fixture**：一個小型 todo CLI，只有簡短的 `CLAUDE.md`，沒有 AGENTS.md，也就沒有 Charter gate。transcript 是已收斂的對話，最後使用者只說「確認」，並沒有授權實作。
- **排除個人層級 skills**：加上 `--disable-slash-commands`，模型只能讀取專案的 SKILL.md，無法叫出同名的個人 skill。
- **預先登記的判定規則**：patched 組在 5 次有效 trial 中至少 4 次出現目標行為，且 baseline 組至多 1 次出現，才算「行為上有支持」；其他結果一律為 inconclusive。
- **harness**：規格見 scratchpad 的 `exp/SPEC.md`，由 `harness-executor` 建立。主 session 審閱時修正了一個 bug：`transcript.jsonl` 和 `stderr.txt` 原本會被誤算為產品程式碼變更。

以下為原始計畫，保留作為紀錄。

## 目的

prompt-audit 的 Step 7 指出：每一項刪改都只是假設，需要實測行為才能確認。本實驗比較 `HEAD`（baseline）與套用 [audit patch](../research/2026-09-26-claude-skill-prompt-audit.patch) 後（patched）的 skill 行為。只挑選行為可以自動量測的 hunk；其餘 hunk 只做文字審閱，不在本實驗範圍內。

## 執行面與控制條件

- **執行方式**：在 scratchpad 建立兩份 fixture repo（baseline／patched），以 headless `claude -p --output-format stream-json` 執行，從 tool call 紀錄與產出檔案量測行為。
- **主 session 模型**：`claude-opus-5-5`，effort `high`（與你目前的 settings 相同），兩組一致。
- **排除個人層級 skills**：個人層級 skill 的優先權高於專案 skill，你的 `~/.claude/skills/` 有 7 個同名 skill。每個 trial 的 prompt 都寫成「讀取並遵循 `.claude/skills/<name>/SKILL.md`」，兩組一致。這是 AGENTS.md 要求的做法，也確保測到的是專案副本。
- **環境**：你的全域 `~/.claude/CLAUDE.md` 會被載入，兩組相同，視為真實環境的一部分。
- **權限**：使用 `--allowedTools` 白名單，不使用 `--dangerously-skip-permissions`；fixture 只放在 scratchpad。
- **預算**：每個 trial 設 `--max-budget-usd`，超過即中止並記錄。
- **重複次數**：每個情境、每一組各跑 3 次，以降低單次抽樣的雜訊。

## 情境與指標

| # | 情境 | 對應 hunk | Prompt 概要 | 指標（自動量測） |
|---|---|---|---|---|
| S1 | commit 訊息 | D2a、D2b、D3a | staged diff 內含反引號與 `$(...)`；只要求產生訊息 | sanitizer 是否以雙引號 argv 傳入草稿；是否產生執行副作用（偵測標記檔）；是否自行執行 `git commit` |
| S2 | code review 的 recall | A1、A2 | fixture diff 中埋入 5 個已知 bug（2 個高、3 個低嚴重度），依 `/code-review` 審查 | 回報中命中的已知 bug 數；誤報數；reviewer subagent 數 |
| S3 | research 的委派 | B3 | 一個只需讀幾頁的小問題 | 是否啟動 background agent；是否寫出筆記檔；總成本 |
| S4 | grilling 確認後的行為 | B2 | 附上已收斂的對話與使用者確認 | 是否開始實作（寫入產品程式碼）；是否停在交給 calling workflow |
| S5 | to-tickets 的發布 | B6、B7 | 已核准的 breakdown；要求發布 | ticket 路徑是 `.proj.tickets/` 還是 `.scratch/`；發布後是否開始實作 |
| S6 | 前端 prototype | C4、C6 | logic prototype 與 UI 變體 | 產出的 CSS 是否出現米白底、標題斜體、01/02/03、monospace 標籤、膠囊按鈕 |

## 預估成本

依可行性測試，最小一次呼叫約 $0.075（主要是約 45k token 的 context 成本）。Agentic trial 以每次 $0.5–3 估算：

| 範圍 | trial 數 | 估計成本 |
|---|---|---|
| 全部 S1–S6 | 36 | 約 $30–80 |
| 精簡版：S1、S3、S4、S5 | 24 | 約 $12–35 |
| 只跑 S2 | 6 | 約 $10–25（每次會啟動兩個 reviewer subagent） |

實際成本會在第一個情境跑完後回報；若超出估計，先停下來請你決定是否繼續。

## Orchestration

- **設計與分析**：主 session。
- **實驗設計挑戰**：`harness-challenger` 在花錢之前檢查設計的效度，例如指標能否區分兩組、樣本數是否足夠。
- **fixture 與 harness 腳本**：交給 `harness-executor`，依本計畫的規格建立。
- **結果審查**：`harness-reviewer` 檢查統計解讀與結論是否超出證據。

## 限制

- 每組 3 次只能看出方向，不足以做顯著性檢定。
- 只量測可自動判定的行為；文字品質類的 hunk（例如 A4、C11、C12）不在本實驗範圍。
- 巢狀執行的環境可能與你平常的互動 session 有差異，例如 hooks 和 MCP。

## 已知的附帶發現

- `disable-model-invocation: true` 會讓 description 不進入 context（Claude Code skills 文件）。C1 原本較強的寫法其實正確，可以恢復。
- 個人層級 skill 的優先權高於專案 skill。你的 7 個同名 skill（agent-browser、grilling、i-have-adhd、writing-for-agents、三個 tw-emoji）用 `/name` 叫出來時，執行的是個人版本。這也說明了 D5 的現象：agent-browser 的個人版本是指向 `~/.agents/skills` 的 symlink。
