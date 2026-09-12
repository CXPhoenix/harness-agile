# Codex／Claude Prompt 與 Skill 最佳化：來源與訪談起點

日期：2026-09-12。檢視基準：`26897cc3ca733714c541def5e2b520e497042ee0` 加上當時工作目錄。本文保留需求訪談時的官方摘要與待驗證假設；Q1–Q7 與執行授權見後文，修改結果另見維護歷程。初步假設不等同模型實測結果。

## 官方來源對照

| 來源 | 與本次維護相關的建議 |
| --- | --- |
| [OpenAI：Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) | 精準且精簡的 description；多分支 Skill 按需載入參考內容；依任務決定讀哪些文件；重看舊有確認邊界，明確定義任務完成條件。 |
| [Claude：Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) | 清楚描述輸出、限制與理由；順序或完整性重要時保留步驟；模型專屬建議轉用前須重新評估。 |
| [Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1) | 留意提早結束、進度資訊不足、擴張範圍與整檔重寫；只對實際出現的問題補充指令。API 的歷史訊息與 thinking block 管理屬於執行環境，不能靠 Skill 文字實作。 |
| [Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) | 明確界定工作範圍與文件篇幅；避免額外自我驗證提醒造成重複工作；限制小任務的 subagent 使用。 |
| [Claude Opus 4.8](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8) | 指令可能被字面解讀；工具使用與 effort 需依工作校準；既有固定頻率進度提醒可重新評估。 |
| [Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5) | 明確說明規則的適用範圍；工具使用更主動；effort 與 API thinking 設定有模型差異。 |

六個指定 HTML 頁面均可讀取，已檢視與本次工作相關的段落。OpenAI 與 Claude 通用頁面的 `.md` 版本嘗試失敗，研究依據為 HTML 頁面。這些來源說明模型建議，不能證明本專案已經得到效能改善。

## 本機已確認的起點

- `docs/agents/runtime.md` 已指定 `.agents/skills/` 為共用來源，Claude 使用相對 symlink 或同步副本，兩個執行環境保留原生工具轉接。
- `.codex/config.toml` 把模型選擇留在 host；不應把特定模型的 API 參數直接當成所有使用者的專案預設。
- `grilling` 目前要求整個可回答的問題集合在同一輪提出，環境事實交給 subagent 查找。這是本次訪談正在遵循的規則，也是可評估成本與互動負擔的候選。
- `writing-for-agents` 已有 context pointer、progressive disclosure 與檢查無效指令的概念；應先檢查實際技能是否遵循，避免新增另一套重複規範。
- 開始時已有 `docs/agents/skill-sources.json`、`tests/test_bootstrap.py`、`.agents/skills/archify/agents/` 與 `.tmpl.docs/history/2026-09-12-archify-validation.md` 的未提交變更。

## 待討論的判斷

### 唯讀盤點候選

| 位置 | 已看到的文字／流程 | 待驗證影響 |
| --- | --- | --- |
| `.agents/skills/code-review/SKILL.md:3,21,23`；`.agents/skills/implement/SKILL.md:13,15` | Review 宣告包含 WIP，卻指定 `git diff <fixed-point>...HEAD`，空 diff 即停止；implement 要先 review 再 commit。 | 可能漏掉未提交變更；需用 committed、staged、unstaged、untracked 情境驗證，這不是單純縮短文字。 |
| `.agents/skills/to-spec/SKILL.md:15,33,41` | 指定 ideal seam 數量為一，要求 LONG 與 extremely extensive。 | 可能使篇幅或架構偏好取代需求充分性；需比較 traceability 與遺漏情況。 |
| `.agents/skills/grilling/SKILL.md:8,26,28` | 全部 frontier 同輪問、環境事實派 subagent、每個分支皆需走訪。 | 問題數與探索成本缺乏依任務調整的邊界。 |
| `.agents/skills/implement/SKILL.md:11` | 要求定期 typechecking。 | 採用範本的產品不一定有 typecheck；需按實際工具鏈判定適用性。 |
| `docs/agents/workflow.md:119–120`；`docs/agents/runtime.md:120–121` | Stage 8 指定 accessibility plugin，runtime 又允許等價原生瀏覽器工具。 | 工具名稱要求與能力等價原則可能不一致，需確認可接受的驗收證據。 |
| `docs/agents/runtime.md:112–116` | 明示結構檢查不驗證模型品質。 | 最佳化成效需另有行為驗收；這是既有界線，不是缺陷。 |

此表由唯讀 subagent 盤點，未執行重現或跨模型實驗。行號對應本輪檢視時的工作目錄。

以下是工程推論，尚未經使用者確認或模型比較實驗驗證：

1. 共用層適合保存工作成果、治理邊界與證據要求；模型或執行環境特有的補充指令應有條件地載入。
2. 人工核准、獨立審查與必要驗收不能自動歸類為多餘的自我驗證。是否修改治理要求，需要明確決策。
3. 字數下降只能證明文件縮短；Skill 選擇、遵循邊界、完整交付、token 與等待時間需分別觀察。
4. API 文件中的參數、訊息歷史管理與模型行為建議需要分開處理；Claude Code 是否提供對應控制項，須另查其官方文件與實際環境。

## 第一輪決策，已確認

- Q1：執行效率與完成品質並重。使用者接受建議。
- Q2：保留治理要求，改善表達與載入方式。使用者接受建議。
- Q3：本次只針對 Codex 最佳化；Claude 文件用於注意共用 Skill 的相容性，Claude 相關設定先不碰。不再要求指定日常 Claude 模型，也不把 Claude 模型實測列為本次驗收。

後續問題依上述決策展開；尚未建立已核准 ADR、修改 Skill，或執行模型評測。

## 使用者提出的術語定義

以下保留使用者提出的定義。第二輪已確認適用邊界，見本節末尾。

| 名詞 | 定義 |
| --- | --- |
| Skill | 維護者提供給開發助理、可按需載入的可重用工作指引；可由 Codex 或 Claude Code 使用。 |
| Playbook | 出題者提供給關卡內 Agent 的能力組合，保留現有定義。 |
| Coding assistant（開發助理） | 協助維護者處理專案工作的 Codex 或 Claude Code。 |
| Agent | 繼續專指關卡內的 Agent，避免與開發助理混淆。 |
| CC Skill | 供 Claude Code 使用的 Skill。可與 Codex Skill 共用同一份核心指引。 |
| Codex Skill | 供 Codex 使用的 Skill。可與 CC Skill 共用同一份核心指引。 |
| CC Plugin | 供 Claude Code 安裝與管理的擴充套件，可封裝 Skill 或其他擴充能力。 |
| Codex Plugin | 供 Codex 安裝與管理的擴充套件，可封裝 Skill 或其他擴充能力。 |
| CC Agent | 為 Claude Code 定義、具有特定職責與執行限制的開發代理角色。 |
| Codex Agent | 為 Codex 定義、具有特定職責與執行限制的開發代理角色。 |

第二輪新增詞彙表前的本機檢查：checkout 未找到 `CONTEXT.md` 或 `CONTEXT-MAP.md`；`docs/`、`.tmpl.docs/`、根目錄 `AGENTS.md` 與 `README.md` 也未找到 Playbook 或關卡定義。因此「保留現有定義」只有使用者提供的描述，尚未核對產品原始文件。不能將特定產品的關卡用語直接視為通用範本既有領域。

## 第二輪決策，已確認

- Q4：開發助理相關術語留在範本；Playbook 與未加前綴 Agent 的關卡專用定義留在有關卡概念的產品專案，不作為通用範本的產品預設。
- Q5：CC／Codex 前綴只表示使用環境，不要求維護兩份 Skill。核心指引維持一份；Codex 專屬差異使用條件式參考文件或 Codex 設定。開發代理角色使用完整 CC Agent／Codex Agent 名稱；工具名稱、設定欄位與官方原文保留原名。

已將八個範本維護術語寫入 `.tmpl.docs/CONTEXT.md`，遵循範本維護資料存放原則。未建立產品根目錄詞彙表，未修改另一個產品的文件。這是訪談中已確認的術語紀錄，不代表已開始最佳化 Skill。

## 第三輪決策，已確認

- Q6：使用者接受全面盤點、聚焦修改。盤點全部專案 Skill 的 description 與共用入口，首批修改聚焦 `AGENTS.md`、runtime 文件、Codex Agent 指令及需求到實作／審查的核心 Skill；其他專用 Skill 有具體問題才列入。
- Q7：使用者接受以固定案例比較修改前後的 Codex 表現，涵蓋小幅文件修改、需求訪談、spec、含未提交變更的 review、實作驗證及能力等價工具替代。治理遵循與交付完整性為必要條件；工具呼叫、讀檔、重複確認與可取得的 token／時間資料用來評估效率。結構檢查另行報告，不代替模型實測。

完整共識與驗收方向整理於 [維護計畫](../plans/2026-09-12-codex-prompt-skill-optimization.md)。Q1–Q7 已確認，使用者接著以「開始修改」確認整體共識並授權執行。前述「尚未修改」描述的是訪談當時狀態；實際修改與驗收見維護歷程。
