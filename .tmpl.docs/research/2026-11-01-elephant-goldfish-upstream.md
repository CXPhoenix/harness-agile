# Elephant-Goldfish Model 上游研究

查核日期：2026-11-01。固定來源 commit：[`403d8881d62022490637d740657b33f01e321ea8`](https://github.com/google/elephant-goldfish-model/commit/403d8881d62022490637d740657b33f01e321ea8)，提交日期 2026-10-30；當時 plugin 版本為 `0.1.0`。以下是來源閱讀結果，沒有安裝、執行模型或重跑上游測試。

## 定位與適合採用的部分

EGM 是以設計文件為中心的 skills、reviewer personas 與審查標準套件。Elephant 在主要對話中保留專案脈絡、撰寫設計並判斷審查意見；Goldfish 以新建且不繼承對話的子代理，僅依文件、標準及指定來源審查。設計取捨與核准由人負責。依資料處理說明，EGM 沒有自己的 hosted service、資料庫、外部記憶體服務或 telemetry endpoint，也不需要獨立帳號；宿主的模型與工具仍有其資料處理行為。來源：[README](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/README.md)、[資料處理說明](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/privacy.md)。

**研究判斷：**對既有 spec-driven template，最可分別採用的是 fresh-context 隔離契約、文件自足性檢查、Zoom Out 的 YAGNI／既有程式重用標準，以及審查完成證據。整套流程另有自己的產物位置、核准節點與收斂規則，不能只加入 skills 名稱就視為相容。

## Runtime bundle 依賴

上游明確要求安裝完整 plugin；只複製 `skills/` 會缺 reviewer personas 與 document standards。其依賴可整理為：

```text
Host marketplace／plugin manifest
└─ skills/egm-*/SKILL.md
   ├─ docs/codex.md 或 docs/claude.md：runtime 路徑與隔離契約
   ├─ agents/*.md：共用 reviewer persona／synthesizer
   ├─ resources/document_standards/*.md：審查標準
   ├─ resources/execution_instructions.md：draft 執行規則
   └─ skills/egm-*/references/*：該 skill 的範本／schema

Claude 額外使用：
.claude-plugin/plugin.json
└─ .claude-plugin/agents/*.md
   └─ agents/*.md：讀取共用 persona

Codex：
.codex-plugin/plugin.json / root plugin.json
└─ skills/；以 general-purpose 子代理讀取 agents/*.md
.agents/plugins/marketplace.json：探索目錄，不是 reviewer 目錄
```

上游共用一套 skill 文字，由 runtime 文件與 Claude adapters 調整宿主差異；不是各宿主各有一棵獨立 skill tree。完整發行還包含 README、LICENSE、介面 assets 與所需 docs。開發測試依賴為 Python 3.10+、pytest、PyYAML；這些不是使用 Markdown runtime 時必須安裝的獨立模型套件。來源：[宿主與目錄契約](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/harnesses.md)、[Codex integration](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/codex.md)、[Claude integration](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/claude.md)、[測試手冊](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/TESTING.md)。

## 五階段 review 與成本推算

`egm-review` 的 review stages 編號為 5–9，依序執行：

| Stage | 目的 | Reviewer |
|---|---|---|
| 5 | Initial Zoom Out：問題、簡化、重用與抽象層次 | zoom_out |
| 6 | Comprehension：新讀者能否完整理解文件 | comprehension |
| 7 | Critic：設計、結構與文字 | design、structural、style |
| 8 | Intermediate Zoom Out：重新檢查新增補救措施是否增加不必要複雜度 | zoom_out |
| 9 | Implementation Readiness：實作步驟、程式依據與文字 | implementation_readiness、codebase_details、style |

`FeatureRange` 與 `DetailedRange` 通常由 `Detailed Implementation Plan` 等標題分割；feature-spec-only 模式只執行 5–8。Comprehension 要保留 reviewer 的完整轉述，不能只經 synthesizer 留下 findings。各 stage 必須依序完成；只可在同一 stage 內平行執行 reviewers。來源：[egm-review 原始指引](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review/SKILL.md)。

**成本推算：**完整 review 一次基本需要 9 個 reviewer；brainstorm 另有 6 個 lenses。尚未計入 synthesizer、重試、重審或選擇每 persona 雙實例。這是派工數推算，不是 token 或金額測量。來源：[review](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review/SKILL.md)、[brainstorm](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-brainstorm/SKILL.md)、[synthesizer](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/agents/synthesizer.md)。

## Round、severity 與失敗處理

`egm-review-loop` 的契約：

- 每輪重新解析文件行範圍，派出新的 Goldfish，不繼承歷史對話。
- severity 為 **Blocker、Major、Nit**；沒有直接提供本專案 P0/P1/P2 對應。
- reviewer 失敗或 timeout 重試一次，再失敗記為 `not run`；不得算成零 findings。
- contested 或接受風險而不修的 finding 視為 settled；修過的 finding 若再次出現，必須重開。
- clean round：沒有新的未 settled Blocker／Major，且全部 reviewers 已完成；Nit 不阻擋。
- 連續兩輪 clean 才收斂，預設上限 **5 rounds**。
- 達 cap 或發生 churn，請人決定接受、越過 cap 繼續，或回到 drafting。
- 每輪修正後須等人明確確認下一輪。

來源：[review-loop](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review-loop/SKILL.md)。

另外，`egm-review` 本身規定每 stage 最多一次 re-audit；人工再次修改而達 cap 時，會將 residual findings 記為 accepted trade-offs 並前進。因此 orchestration 與通用 loop 有不同範圍的 cap，移植時需先決定採用哪一個，不能假設只有一套收斂契約。來源：[review checkpoint／pause-resume protocol](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review/SKILL.md)。

`egm-resolve` 要求 CONTEST 附 reviewer 能查閱的證據；只有對話或團隊習慣才知道的事要 ESCALATE 給人。不能以「原本就故意如此」當證據，也不能直接更改 reviewer severity。這一點適合移植成 finding 裁決規範。來源：[resolve](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-resolve/SKILL.md)。

## Claude Code／Codex 隔離限制

**Codex：**依實際 tool schema 使用 `fork_context: false`，或 `fork_turns: "none"`；必須把 persona、標準、target、reading list 的明確路徑交給 general-purpose 子代理，不傳 parent transcript。缺檔或漏讀不是 clean review；必須等實際 completion、傳遞 timeout／失敗。無法 nesting 時由 parent 直接派工，不能建立新 context 就停止 Goldfish review。來源：[Codex integration](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/codex.md)。

**Claude Code：**上游要求 2.1.271+ 才有 `omitClaudeMd`。review adapters 使用 `omitClaudeMd: true`、`model: inherit` 與 `Read/Grep/Glob`，禁止 shell 和寫入；未設定 persistent memory。synthesizer 的工具列表不同，可以派工與寫報告。來源：[Claude integration](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/claude.md)。

兩者都不是 filesystem 隔離。Codex fresh context 也不會自動排除 project instructions、已設定的 memory services；上游要求不要用歷史紀錄或 memory 補足設計文件缺失。應用 parent-only marker 並讀取實際 child output 驗證隔離。未完成原生 trace 查核時只能報告驗證界線。來源：[Codex integration](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/codex.md)、[測試證據標準](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/TESTING.md)。

## 文件產物與 bootstrap／drift

可用 `EGM artifact directory: <path>` 指定 brief、draft、reports 的產出目錄；這不會一起搬動設計文件及專案檔案。預設產物包含 `concepts_brief.md`、`design_draft.md`、多個固定名稱 report；長期設計慣例是 `docs/designs/`。來源：[宿主產物目錄](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/harnesses.md)、[review](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review/SKILL.md)。

`egm-bootstrap` 會自底向上建立或修正各目錄 README，整理 Interface、Invariants、Side Effects。它支援 `target_filename: EGM.md`，適合避開人工維護 README。發現超過 15 個目錄時要求核准；5 個以上會切子樹派工。來源中的「無人工 concurrency 限制」不能覆蓋宿主可用 slot 或專案預算。bootstrap 也會排除 hidden、test-only、non-code 目錄，故不應假設能完整盤點以隱藏 Markdown 目錄為主的 template skills／specs。最後這點是依篩選規則的整合推論。來源：[bootstrap](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-bootstrap/SKILL.md)。

`egm-drift-report` 是由模型逐份讀文件、搜尋並讀取現況程式的 workflow，產出 `{YYYY-MM-DD}_DRIFT_REPORT.md`。它會將文件有而程式無、程式有而文件無的情況都列為 drift；不是 parser 或 deterministic diff。對尚未實作的 spec、歷史研究、非規範性 README，需先指定 scope／status 才不會把預期差異算成缺失；後者是整合推論。來源：[drift-report](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-drift-report/SKILL.md)。

## 成熟度與證據界線

上游 `TESTING.md` 紀錄 Claude Code、Codex CLI 的 fixture workflow、原生隔離及必要讀檔證據。Codex 於 2026-10-29 以 CLI `0.164.0-alpha.11.1`、`gpt-6.1-sol` medium，對 v0.1.0 OpenAI ZIP 完成 live suite；紀錄 482.30 秒與 15 位 native reviewers。這是上游測試紀錄，本研究未重跑，也不能推論目前 Codex desktop 或修改後 template 已通過。來源：[固定版本測試紀錄](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/TESTING.md)。

上游明示 pre-1.0；版本 1.0 才要求 skill 名稱、參數、產物位置、report format 的穩定契約。採用時應固定 commit，不能只追蹤 `main`。來源：[release contract](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/releases.md)。

## 授權與待確認事項

LICENSE 為 Apache-2.0；README 明示不是 Google 官方支援產品。若複製或改寫來源，來源授權第 4 節要求保留授權及相關 notices，修改檔案應標示變更；不能把上游來源直接視為本專案 MIT 文字。來源：[LICENSE](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/LICENSE)、[README](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/README.md)。

整合前尚須決定：

1. 採完整 plugin 加 adapter，或僅移植隔離／rubrics；不能只安裝 `skills/`。
2. 明定本專案兩輪上限、frozen prompt、P0 gate 優先於上游 loop。
3. 為 spec、ticket plan、研究、歷史文件定義不同 review／drift scope。
4. 在實際 Claude Code／Codex surface 做最小隔離與必要讀檔驗證，再稱整合可用。
5. 評估逐 section 核准、每輪人工 gate 是否符合使用者希望的工作節奏；上游 drafting 還明文禁止 AI 在多個合理架構選項間代替人決定，即使人要求「幫我選」也要再次詢問。來源：[draft](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-draft/SKILL.md)。
