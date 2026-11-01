# elephant-goldfish-model 與 harness-agile 的整合研究

日期：2026-11-01。範圍：母範本維護的可行性研究與整合提案，未核准為實作計畫。

- 本機基準：`72677d5f04cfa9ace6658181d1317dacc1118305`，`main`，harness-agile 0.3.0。
- 上游基準：`google/elephant-goldfish-model` 的 `403d8881d62022490637d740657b33f01e321ea8`。
- 上游細節與逐項來源：[一手來源調查](2026-11-01-elephant-goldfish-upstream.md)。
- 證據分工：背景研究代理查上游原始文件與程式；主助理查本機規範、角色與打包程式，再提出整合建議。

## 建議

**先把 EGM 的「全新對話上下文審查」接入既有 Stage 3，再評估選用文件漂移檢查。** 目前範本已具備「主助理整理需求與規格、獨立代理挑戰規格、使用者裁決」的結構，最值得補強的是審查者究竟能看見哪些上下文，以及無法建立獨立上下文時 gate 如何處理。

這是根據兩邊規範的整合判斷，尚無比較實驗證明能改善缺陷發現率或節省成本。EGM 也提供完整 plugin 路線，但原樣執行會帶入另一套文件結構、審查階段與停止條件，需要專案 adapter。

## EGM 提供的能力

EGM 是協助 AI 開發助理進行設計與審查的 skills/plugin。Elephant 代表熟悉專案、保有前面討論的設計者；Goldfish 代表沒有前面對話的審查者，依文件與其引用的來源找出未寫清楚的假設。主線涵蓋需求探索、規格草擬、審查與議題處理，另有既有專案文件整理及文件漂移報告。它的定位與本專案的需求到規格階段相近。[上游 README](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/README.md)

上游要求完整 plugin bundle，因為 skills 會讀取同套件的 reviewers 與文件標準；僅複製 `SKILL.md` 無法代表完整整合。具體相依關係、runtime 宣告及驗證界線見[上游調查](2026-11-01-elephant-goldfish-upstream.md)。

它也提供值得獨立評估的內容：Comprehension 讓新讀者先轉述設計，以暴露文件的隱含知識；Zoom Out 則檢查問題本身、重用機會與過度設計。這些檢查可強化文件品質，但不能替代本機四軸中的 traceability 完整性或可驗證性。完整五階段每階段僅走一次，reviewer 派工數即為 1＋1＋3＋1＋3＝9，未含 synthesizer、重試及重審；不能視為比目前四軸便宜的既成事實。[EGM review](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review/SKILL.md)

## 與既有流程的對應

| 目前 harness-agile | EGM 能力 | 可整合方式 | 必須保留的本機規則 |
|---|---|---|---|
| Stage 1：`grill-with-docs`、ADR、詞彙表 | `egm-brainstorm` | 採用對假設與取捨的挑戰方式；官方 skill 可作選用工具 | 需求共識由使用者確認；決策回寫既有 ADR／詞彙表 |
| Stage 2：`to-spec`、traceability | `egm-draft` | 將有價值的設計章節映射到現行 spec，補足文件本身的完整性 | `spec.en.md` 為準；每個 matrix row 對應驗收條件；翻譯時機維持現行規則 |
| Stage 3：四軸、兩輪、frozen prompt | `egm-review`、`egm-review-loop` | 採用 fresh-context 執行條件與資料封包，維持既有四軸 | P0／P1／P2 定義、兩輪上限、使用者裁決 |
| Review findings 的裁決與修訂 | `egm-resolve` | 改善議題清單及取捨記錄的呈現 | 不以代理投票或代理自行決定取代使用者裁決 |
| `CONTEXT.md`、ADR、專案文件 | `egm-bootstrap` | 選用的既有專案文件盤點／遷移工具 | 不覆寫 Charter、初始化流程或另建權威文件副本 |
| 文件與程式的一致性維護 | `egm-drift-report` | 顯式觸發的診斷工具；輸出到專案既有位置 | 診斷報告不等於通過 spec、測試或交付 gate |
| Stage 4–9：tickets、TDD、code/security review、e2e、合併 | 非 EGM 的主要交付範圍 | 延用現有流程 | 不因規格審查完成而跳過後續 gates |

本機依據：[workflow](../../docs/agents/workflow.md)、[review](../../docs/agents/review.md)、[to-spec](../../.agents/skills/to-spec/SKILL.md)、[language](../../docs/agents/language.md)。EGM 各 skill 行為及來源見[上游調查](2026-11-01-elephant-goldfish-upstream.md)。

## 需要明確處理的衝突

### 1. 「獨立審查」尚未定義為「不繼承對話」

目前 `docs/agents/review.md:9–13` 要求四位獨立審查者及相同 snapshot，`runtime.md:85–95` 說明角色、並行數與退路，但未明定不得繼承主對話。`.codex/agents/harness-reviewer.toml` 也只有審查範圍與唯讀要求。這只能證明文件契約有缺口，不能反推過去每次 review 都曾洩入主對話。

提案是在 runtime adapter 明定每個軸、每一輪都建立新的對話上下文。本次宿主 API 提供 `fork_turns: "none"`；它是目前宿主可用的參數，不應當作所有 Codex 版本的通用名稱。Claude 及其他宿主須分別確認等效能力。模型設定的繼承與對話內容的繼承是兩件事，不必為了 fresh context 強制換模型。

Fresh context 只處理前面的對話，不會自動隔離共用 filesystem、AGENTS 指令、其他記憶服務或工具權限。審查資料的可見範圍與唯讀能力需要另外記錄；上游也將這些界線分開說明，見[上游調查](2026-11-01-elephant-goldfish-upstream.md)。

Claude adapter 還使用 `omitClaudeMd` 減少父層指令帶入；它與本機 reviewer 主動讀取 AGENTS／runtime／review 的習慣不同。不能只移植該開關，卻忘記在 reviewer 封包提供必要的權威規則與分級，也不能宣稱這會建立 filesystem sandbox。需先依實際 Claude 版本確認支援。[EGM Claude integration](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/claude.md)

### 2. 無子代理時的處理方式不同

本機 `runtime.md:92–95` 允許無子代理時採隔離檢閱並揭露限制；EGM 則要求 fresh subagent，不能建立時停止 Goldfish review。[本機 runtime](../../docs/agents/runtime.md)、[EGM README](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/README.md)

建議將單一主對話的檢閱標記為「診斷，未完成獨立審查 gate」。若採納，這是對現行 fallback 的政策變更，需要明文決定，不能宣稱現行規範已如此要求。

### 3. 輪次、分級及停止條件不同

本機要求 frozen prompt、最多兩輪；第二輪仍有 P0 時拆分 epic。上游通用 `egm-review-loop` 使用兩次連續 clean rounds、預設五輪上限，另允許詢問是否繼續；`egm-review` 又有分階段的 re-audit 與剩餘議題處理。因此不能直接把 `egm-review` 當成現有 Stage 3 的同義詞。[本機 review](../../docs/agents/review.md)、[EGM review-loop](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review-loop/SKILL.md)、[EGM review](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review/SKILL.md)

建議沿用本機分級及停止條件。EGM 的 reviewers 可提供分析素材，但必須逐項依本機定義裁定 P0／P1／P2，不能只對換標籤；不同 reviewer 分工也不能被當作現有四軸已完成。第二輪使用新的審查者及同一份 frozen prompt；前輪 findings 由主助理追蹤，不靠重用 reviewer 對話維持記憶。

### 4. 文件路徑及權威來源不同

EGM 的預設文件產物包括 concept brief、design draft 與 `docs/designs/` 下的核准設計；本機則使用 `.proj.specs/<epic>/spec.en.md`、`traceability.md` 及 `.proj.tickets/`。[EGM README](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/README.md)、[本機 tracker](../../docs/agents/issue-tracker.md)

建議維持一份權威 spec。若試用官方 drafting，草稿必須明確標為非權威輸入，再由 adapter 產生現行 spec 與 matrix；不能讓 `docs/designs/` 和 `.proj.specs/` 各自維護同一個功能的核准狀態。Bootstrap 產生的導覽／詞彙文件也需要映射現有 CONTEXT／ADR，不能自動重組目前專案。

上游可用 `EGM artifact directory: <path>` 改 brief／draft／report 的位置，但這不會一併改寫設計文件慣例或本機 tracker。`egm-bootstrap` 排除 hidden／non-code 等目錄，本專案的 skills 與 specs 卻大量位於隱藏目錄且以 Markdown 為主，所以不能用它直接取代初始化器或認定全專案已被盤點。`egm-drift-report` 是模型輔助比對，試行時應先選已實作的規範性文件與對應程式；未實作 spec、歷史研究及非規範文件的差異不一定是缺失。[EGM harnesses](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/harnesses.md)、[bootstrap](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-bootstrap/SKILL.md)、[drift-report](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-drift-report/SKILL.md)

### 5. Plugin bundle 與可攜 skills 的配置不同

本機兩套 skill 樹各自保存實體副本，Codex 要求 `agents/openai.yaml`、Claude 排除該設定；同名 skill 的顯式觸發政策必須一致。現有 verifier 會檢查這些條件。[runtime](../../docs/agents/runtime.md)、[verify-project.py](../../scripts/verify-project.py)

若選擇內附上游完整 plugin，需確認其 `skills/`、`agents/`、`resources/`、`docs/` 的相對路徑解析，不能把七個 skill 目錄直接放進兩棵樹就視為完成。本機 wheel snapshot 採明確的 PATHS 清單，npm 也有 `files` 清單；新放在其他根目錄的 plugin 資源不會自動隨兩種套件發布。[bundle.py](../../harness_agile/bundle.py)、[package.json](../../package.json)

### 6. 人工確認的頻率與決策權不同

EGM drafting 逐 section 暫停，review-loop 每輪需要明確確認；drafting 對多個合理架構選項還要求交回使用者決定。完整引入可能增加目前流程之外的確認點。[EGM draft](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-draft/SKILL.md)、[review-loop](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review-loop/SKILL.md)

建議 adapter 明確保留本專案既有的需求／拆票／test plan／爭議裁決 gates，延續使用者已核准的選擇與授權。例行分析及可逆整理可持續進行，不因引用上游 skill 而一律重新確認。這需要 deliberate adaptation；不是原樣執行上游流程就能得到的行為。

## 三種整合方式

| 方式 | 實際交付 | 優點 | 代價與適用時機 |
|---|---|---|---|
| A．採納 EGM 審查機制（建議先做） | 補 runtime 與 reviewer 契約、審查封包及行為驗證；不增加 plugin 依賴 | 重用既有流程，可攜範本的變動較小 | 需要自行維護 adapter；這不等於安裝官方 EGM，也不能宣稱已完整相容 |
| B．官方 plugin 作為選用工具 | 使用者在自己的宿主安裝完整 plugin，專案文件提供路徑與 gate 對應 | 上游功能可個別探索，維護 fork 較少 | 宿主安裝狀態不會因複製 repository 自動還原；與內建流程衝突須明訂，固定版本的安裝方式待驗證 |
| C．內附／分支維護完整 bundle | 固定上游 commit、完整資源、兩個 runtime adapter、來源與授權紀錄、打包驗證 | 有機會支援離線、可重現的新專案建立 | 維護成本最大；須處理 helper 路徑、host metadata、套件清單及每次上游更新的移植 |

A 適合本專案目前已有完整流程的狀態；B 適合先看 drafting／drift 工具的實際效果；只有確定每份生成專案都需要完整 EGM 時，才值得投入 C。這是依本機配置作出的建議，並非上游推薦的官方整合方式。

若未來複製或改寫上游材料，需依其 Apache-2.0 授權保存適用聲明、標記修改並檢查 NOTICE；根目錄 MIT 不會取代第三方條件。此輪只寫原創研究，沒有複製上游套件。[上游 LICENSE](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/LICENSE)、[本機第三方聲明](../../THIRD_PARTY_NOTICES.md)

## 建議的最小試行

以下是待決定的試行提案，尚未新增 ticket、測試或行為變更。

1. **固定試行面。** 在暫存副本保存上游 commit 與本機基準，先驗證上下文邊界，不執行完整五階段審查。Claude 與 Codex 分別記錄結果。
2. **準備足以獨立判斷的審查封包。** 放入當輪 spec、traceability、frozen prompt、必要 ADR／詞彙及實際介面證據；記錄檔案版本、範圍、引用及軸。避免把主助理的說服文字和整段需求對話一起交給 reviewer。權威規則仍需提供；fresh context 不代表刪除專案規範。
3. **四軸分別啟動 fresh reviewer。** 主助理保持唯讀審查面穩定；子代理不能修改 spec。任一軸失敗或缺少 fresh-context 能力時，報告未完成，不以其他軸投票補足。
4. **收集結構化 findings，交由使用者裁決。** 每項記錄位置、問題、依據、影響、信心與本機分級；主助理整理重複項目但保存不同意見。至多兩輪，依現行 P0 gate 停止或拆分。
5. **再試文件漂移診斷。** 用已知文件與程式差異評估 `egm-drift-report` 的結果。若有價值，再決定採用官方 plugin 或將必要能力移植成兩套 runtime skills；維持顯式觸發，不先增加每個 ticket 的必跑流程。

對應的變更接點以 `docs/agents/review.md`、`runtime.md`、`codex.md`、`.codex/agents/harness-reviewer.toml`、`.claude/agents/harness-reviewer.md` 為主；如增加新 skill／helper，再擴及兩套 skill 樹、`skill-sources.json`、授權與打包清單。不預先新增另一位總裁決代理，也不需要新增記憶資料庫或背景服務。

## 試行必須回答的驗證問題

| 驗證 | 可觀察的結果 | 目前狀態 |
|---|---|---|
| 對話隔離 | 主對話提供、封包未提供的唯一測試標記，fresh reviewer 無法從父對話取得；同時檢查實際啟動設定 | 未執行；標記未被回覆不能單獨證明隔離 |
| 規格自足性 | 把僅在對話中確認的設計決策故意漏出 spec，reviewer 能指出該處缺少可判斷資訊 | 未執行 |
| 引用與程式一致性 | 文件刻意引用過時介面，reviewer／drift 工具能以當前來源回報差異 | 未執行 |
| Gate 與輪次 | 無 fresh 能力、某軸失敗、第二輪仍有 P0 時，均不回報 gate 通過或自動啟動第三輪 | 未執行 |
| 唯讀與裁決 | Review 不修改受檢內容；互相衝突的 findings 保留，交使用者裁決 | 未執行 |
| 成本 | 記錄代理數、輪次、耗時與可取得的 token 使用量，不以代理數推算收益 | 未量測 |
| 模板可攜性（若內附） | 兩套 metadata／相對資源可用，預設初始化與保留範本模式均可用，wheel 與 npm 產物均有相依檔案 | 未做 EGM 整合測試 |

行為試行成功也只能證明當次宿主／版本與指定案例；不能保證每個缺陷都會被發現。結構檢查與初始化單元測試不會驗證模型真的使用 fresh context。

## 本輪範圍與後續決策

本輪只保存研究文件，沒有安裝 plugin、執行上游程式、變更 pipeline／skills、初始化產品、建立票券或 commit。上游調查依原始文件與程式進行；尚未在 Claude Code 或 Codex 實跑 EGM。上游仍為 0.1.0／pre-1.0，未將目前行為當作穩定版本契約；其測試紀錄是上游執行證據，不能推論本機整合可用。[EGM release contract](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/releases.md)、[TESTING](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/TESTING.md)

進入實作前最重要的決策是採 A／B／C 哪種交付方式，以及是否把「缺少 fresh subagent 時不得完成 Stage 3」改為正式規則。文件漂移檢查可留作獨立的第二步，不影響先驗證四軸審查的上下文隔離。
