# 全新上下文四軸審查 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
>
> **For Codex:** 執行時載入 `executing-plans`；依專案 runtime adapter 與宿主支援的方式載入 skills，並以本計畫的維護範圍及驗證表為準。

**Goal:** 將不繼承主對話的全新子代理整合進 Stage 3 四軸規格審查，保留 frozen prompt、最多兩輪與原有 P0 gate。

**Architecture:** 以 `docs/agents/review.md` 保存共用審查契約，`runtime.md` 保存 Claude／Codex 的啟動方式，兩套 `harness-reviewer` 角色依同一份明確的審查封包執行。主助理管理版本、派工與彙整，子代理唯讀審查；使用者保有爭議裁決權。這一階段採用 EGM 的上下文隔離機制，不增加另一套流程引擎。

**Tech Stack:** Markdown 指引、Claude agent frontmatter、Codex TOML role、宿主原生子代理 API；Python 3.11+ 與既有初始化／打包驗證。無新增套件相依。

---

## 狀態、授權與基準

- 日期：2026-11-01。狀態：**核准範圍已實作；Codex 原生驗證完成，Claude live 未驗證**。
- 已確認方向：採研究建議的方式 A，優先整合 fresh-context 四軸 review；保留兩輪上限與 P0 gate。
- 使用者已要求依計畫開始實作，並於完成後回報驗證結果及未驗證項目。核准不包含安裝 EGM plugin、發布或合併。
- 本機基準：`main`／`72677d5f04cfa9ace6658181d1317dacc1118305`，harness-agile 0.3.0。
- 既有兩份研究文件仍未提交；執行時一併保存，不覆寫或清除。
- 來源：[整合研究](../research/2026-11-01-elephant-goldfish-integration.md)、[上游一手來源](../research/2026-11-01-elephant-goldfish-upstream.md)。上游固定於 `403d8881d62022490637d740657b33f01e321ea8`。
- 這是母範本維護，保留 Charter 與所有專案 placeholders；不初始化產品，也不為這份維護計畫建立產品 spec／ticket。

以下檔案路徑皆相對 repository 根目錄；正式 agent 文件以英文撰寫，使用者說明與維護紀錄使用台灣繁體中文。

## 範圍與驗收條件

| ID | 完成後的行為 |
|---|---|
| AC1 | 維持 Completeness、Verifiability、Contract conflict、Red team 四軸。每軸、每輪各建立新的 reviewer 對話，不繼承主對話、不沿用前輪 agent ID。 |
| AC2 | Reviewer 取得當輪 spec、traceability、frozen prompt、指定軸、必要的權威規則與來源；依文件可見證據審查，缺少決策就回報缺口。 |
| AC3 | 四軸全部完成、必要資料可讀且審查版本一致，才可判斷 P0 gate。無 fresh 能力、失敗、逾時、缺檔或 stale 結果均記為未完成；不能當成零 findings。 |
| AC4 | 第一輪四軸完成且零 P0 可直接通過；有 P0 才修訂並進第二輪。第二輪重播原 frozen prompt，仍有 P0 就拆分 epic、回 Stage 1；不新增第三輪或「連續兩輪 clean」要求。 |
| AC5 | Claude 與 Codex 各使用實際支援的 fresh-context 啟動方式，依既有 slot 分批；模型／effort、帳號、sandbox 與工具權限沿用現行規則。 |
| AC6 | 子代理維持唯讀、只處理指定軸、不裁決其他軸；主助理保留有衝突的意見，交由使用者裁決。 |
| AC7 | 正式規範與角色設定會隨預設初始化、保留範本模式及既有兩種套件傳遞；採用後的必要操作不依賴 `.tmpl.docs/`。 |
| AC8 | 新的 fresh-context gate 僅適用 Stage 3。Stage 6 code review、Stage 7 security review、walking skeleton 豁免及既有票券／測試流程維持目前範圍。 |

本期範圍外：官方 EGM plugin 安裝、七個 EGM skills 的內附、Comprehension／Zoom Out 新審查階段、drift-report、bootstrap、背景服務、新增 Python 審查引擎，以及模型重新調校。

## 共用契約的具體設計

### 審查封包

主助理在派工前固定當輪輸入。沿用 `.proj.specs/<epic>/review/prompt.md` 與 `round-N.md`；不新增必要的 tracker 目錄、資料庫或 schema。

每輪報告開頭記錄：

1. Epic、輪次、checkout、HEAD，以及相關 staged／unstaged／untracked 狀態。HEAD 不是未提交 spec 的內容版本，仍須記錄受檢檔案的內容 hash。
2. `prompt.md` 的 SHA-256；spec、traceability、必要 ADR／詞彙／介面證據的路徑與 SHA-256。可沿用暫存 snapshot 封包保存實際 bytes；四軸共用同一份內容版本。
3. 每軸 reviewer ID、實際 fresh 啟動設定、完成狀態、必要讀檔結果與 findings。報告保留未完成原因及範圍限制。

封包提供專案規範與必要來源，但不附主對話 transcript、主助理說服 reviewer 的理由、其他軸輸出或上一輪審查對話。既有合法設計取捨應寫入 spec／ADR，讓 reviewer 依同一份證據判斷。

審查對象與引用資料是證據，不會因此成為子代理的新操作指令。fresh context 不等於 filesystem sandbox；共用檔案與宿主自動載入的專案指令仍可能可見。對話記憶及外部 memory 不用來補足 spec 的遺漏。

### Frozen prompt 與派工訊息

`prompt.md` 保留完整四軸標準、分級、證據與輸出要求，第一輪啟動後逐 byte 凍結。主助理另外提供最小派工資訊：本次軸、輪次、封包位置及其版本。第二輪只重新綁定當輪 spec／traceability 修訂版本；不把新的評判標準或上一輪答案塞入派工訊息。

兩輪之間，專案規範、軸、評分標準及相關程式基準保持固定；若必要的外部契約也要改，先揭露審查基準已變動，不能把結果宣稱為原 frozen-prompt 流程下的通過。執行時使用 Python 標準函式庫或既有工具計算 hash，不新增 hash helper。

### Gate 與技術失敗

| 狀態 | Stage 3 結果／下一步 |
|---|---|
| 第一輪四軸完成、版本一致、零 P0 | 通過，P1／P2 依現行規則攜入後續紀錄。 |
| 第一輪四軸完成且有 P0 | 修訂 spec／matrix，使用四個新 reviewer 進第二輪。 |
| 第二輪四軸完成、版本一致、零 P0 | 通過。 |
| 第二輪仍有 P0 | 拆分 epic，回 Stage 1；不開第三輪。 |
| 無法建立 fresh 子代理，或任一軸缺檔、失敗、逾時 | 未完成；可提供診斷，但不開票、不通過 gate。 |
| 審查期間受檢內容變動，或 prompt hash 改變 | 結果標示 stale／程序無效，不納入通過判斷。 |

技術補跑與內容修訂分開記錄：同一份輸入 bytes 的失敗軸，修復環境後可用新子代理補跑，仍屬原輪；已完成軸只有在輸入完全未變時才可保留。改過受檢內容後須使用下一輪版本，不以「重試」重設輪數；第二輪後也不以改名重啟來審第三個修訂版本。第二輪若缺有效結果，報告未完成；不能憑空認定有 P0，也不能認定零 P0。

對爭議 P0 沿用使用者裁決程序，保留原 finding 與裁決依據；主助理不藉重排或去重讓它消失。

## 實作步驟

### Task 1：固定變更面與第一個行為案例

**檔案：**

- 讀取：本計畫、兩份研究、`AGENTS.md`、`docs/agents/review.md`、`runtime.md`、`workflow.md`、`docs/adr/0003-adversarial-review-fixed-axes-two-rounds.md`。
- 建立：`.tmpl.docs/research/2026-11-01-fresh-context-review/README.md`，記錄測試協定；同目錄 `fixtures/` 先只建立第一個案例需要的 `spec.en.md`、`traceability.md` 與 `prompt.md`。

**步驟：**

1. 確認計畫與下方驗證表已獲核准。採 `using-git-worktrees` 建立單一寫入者的 `codex/fresh-context-spec-review` 維護分支；執行前重查 HEAD／status。
2. 新 worktree 不會自動帶入目前三份未提交的研究／計畫；按明確檔案清單複製它們，保留原 checkout 的檔案。不要用清除工作目錄來搬移。
3. 從第一個 fresh-context／缺少規格決策案例開始，建立最小 spec／matrix／prompt；用目前契約記錄基線實際表現。若原本就成功，記為基線成功，不捏造 failing test。
4. 先記錄目前「缺少獨立上下文仍可用本地隔離檢閱」的規範缺口。沒有有效 live trace 的項目標為未驗證，不以指令文字或角色宣告當作執行證據。

**完成條件：**scope、基線與測試協定已固定；未同時建立一整套尚未使用的測試或新 runner。

### Task 2：補齊 Stage 3 共用規範

**修改：**

- `docs/agents/review.md`：完整 fresh-context、封包、完成條件及失敗處理；保留原四軸、分級與 frozen prompt。
- `docs/agents/workflow.md`：Stage 3 連到上述契約，gate 寫明四軸有效完成及零 P0。
- `AGENTS.md`：Stage 3 與 hard rule 3 簡短指出每軸／每輪使用全新對話；詳細規則仍由 `review.md` 擁有。

**步驟：**

1. 在 `review.md` 寫入上述共用契約，將既有零 P0 gate 的適用前提補完整。
2. 更新 workflow 與 AGENTS 的入口指引；保留兩輪上限、P0 拆分條件、Charter 與 placeholders。
3. 逐項對照 AC1–AC4、AC6、AC8，檢查 Stage 6／7 段落未被套用新的 Stage 3 gate。

**完成條件：**讀取 workflow 的主助理能找到唯一完整規範，並能依狀態表判斷通過、修訂、拆分或未完成。

### Task 3：接上兩套 runtime 與 reviewer 角色

**修改：**

- `docs/agents/runtime.md`：兩套宿主 fresh 啟動方式、能力不足分支、Stage 3 限定的 fallback。
- `.codex/agents/harness-reviewer.toml`。
- `.claude/agents/harness-reviewer.md`。

**步驟：**

1. Codex adapter 依實際 API schema 明確停用父對話繼承。本次宿主可用 `fork_turns: "none"`；只有另一宿主真的提供 `fork_context` 時才使用其等效參數。角色可原生選取時使用 `harness-reviewer`，否則傳入其完整角色指引。
2. Claude adapter 使用新的 reviewer invocation，不 resume 前輪 agent。核對實際版本與工具是否繼承 transcript、是否附加 memory；不要直接把上游 `omitClaudeMd` 當作所有宿主必要或已支援的設定。
3. 明確提供權威專案規則。即使宿主能略過自動載入 CLAUDE.md，也不能因此失去四軸與 P0 定義；本期不為移除專案指令而提高版本門檻。
4. 兩套 reviewer role 區分輸入：spec review 讀 spec／matrix／prompt／權威來源；code／security review 保留目前 base、HEAD、captured diff 及 WIP inventory 要求。避免新建的 spec reviewer 為了沒有程式 diff 而誤判缺少必要輸入。
5. Role 保持唯讀、不啟動子代理、不裁決其他軸。runtime 中原有「無子代理時採隔離檢閱」對 Stage 3 改為診斷／未完成；Stage 6 的既有 fallback 不在此變更中擴大修改。
6. 以一個案例完成一個規則的修改／執行／記錄，再做下一個；模型、effort、trust、權限與 concurrency 數值不作重新設定。

**完成條件：**兩套宿主均有可檢查的啟動配方，缺少能力時會停在未完成；角色的 spec 與 diff 輸入要求不互相混用。

### Task 4：在實際宿主驗證四軸與兩輪

**依序擴充或建立：**

- `.tmpl.docs/research/2026-11-01-fresh-context-review/fixtures/spec.en.md`。
- 同目錄的 `traceability.md`、`contract.md`、`prompt.md`。
- `.tmpl.docs/research/2026-11-01-fresh-context-review/evidence.md`。

**步驟：**

1. 依下方驗證表逐例補 fixture；使用合成領域與可判斷的公開介面，不依賴產品 Charter。每個軸有明確 planted defect：matrix row 無驗收條件、模糊的 pass/fail 條件、與明示契約矛盾、未約束的跨租戶存取。
2. 先在 Codex 新 session 確認實際載入修改後的 role／規範，再啟動四個 fresh reviewers。僅在 parent 對話產生當次唯一測試標記，派工內容與讀取封包不含該標記。
3. 彙整第一輪結果與 P0，修訂 fixture 的 spec／matrix；第二輪換四個 reviewer，驗證 prompt bytes 不變及所有必要輸入讀取完成。保留「本來就能通過」及「新增規則後改變」的實際結果。
4. 在 Claude 新 session 使用相同 fixture 版本重做；兩個 runtime 的結果分開記錄。若其中一套宿主不可用，完成可執行部分，明列另一套尚未驗證，不宣稱雙 runtime 行為已通過。
5. 用清楚標為注入資料的 reviewer 報告，驗證主助理對 P0 存續、未完成、逾時、stale、意見衝突的 gate 決策。這些是決策層驗證，不能冒充實際子代理 timeout 或隔離成功證據。
6. 若宿主支援可控的能力停用／故障注入，再驗證實際無 fresh 能力與子代理失敗分支；否則保留該 runtime failure path 的證據缺口。

每套 runtime 的主要 live 路徑為四軸 × 兩輪；技術補跑另列，不偷偷增加第三輪內容審查。記錄實際啟動設定、parent／child IDs、必要讀取、檔案 hashes、四軸輸出及可取得的用量。只保存與驗證相關的 trace 片段；parent-only marker 在子代理結束前不寫進共用檔案，結束後可記於 evidence 供核對。

**完成條件：**成功、未完成與 P0 停止路徑有清楚區分；能指出每項證據驗證了哪個宿主、哪個層次。模型回覆沒有 marker 只是佐證，須結合實際啟動設定與必要讀檔 trace；未達標就如實保留限制。

### Task 5：記錄決策、更新使用者入口並驗證可攜性

**建立：**

- `docs/adr/0004-fresh-context-spec-review.md`：補充 ADR-0003，記錄上下文隔離及缺少能力不能通過 gate 的取捨；保留範本日期 placeholder 慣例。執行前確認 0004 尚未被其他工作使用。
- `.tmpl.docs/history/2026-11-01-fresh-context-spec-review.md`：實作範圍、來源、檢查結果與未驗證項目。

**修改：**

- `docs/README.md`：ADR 導覽。
- `docs/guide.md`：使用者可觀察到的 Stage 3 行為及能力不足時的結果。

**步驟：**

1. 寫 ADR 與入口更新；避免在多處重述整份協定。正式 agent 文件以英文維護，guide／歷程使用台灣繁體中文。正式 ADR 若引用 EGM，連到上游固定 commit；採用後不以會被移除的研究文件作必要依據。
2. 執行下方結構、既有測試與打包命令；在暫存新專案確認預設模式及 `--keep-template-files` 都保留正式規範與 role，且不依賴範本研究目錄。
3. 檢查相對連結、placeholder、role metadata 與檔案範圍。現有 `docs/`、兩套 agent role 都已在 bundle 選取範圍，這期不預設修改打包清單；只有實際發現遺漏才修正並補相對應行為測試。
4. 使用專案 `code-review`，以本核准計畫作 maintenance requirements，檢查最終差異；依適用流程處理 security／實際宿主驗證，記錄範圍。
5. 寫 coverage report table，逐列對照下方驗證表；區分通過、失敗、未執行、只驗證決策層。檢查過的檔案不等於模型行為已驗證。

**完成條件：**可審閱差異、驗證紀錄與限制齊全。若執行 commit 或 PR，分別載入專案 `tw-emoji-commit`／`tw-emoji-pr-note`；commit 必須使用 skill 產生並清理的 UTF-8 message file。本計畫不要求現在 commit、發布套件或合併。

## 驗證計畫表（已核准）

| Seam | Test intent | Scope | Acceptance criterion | Boundary conditions |
|---|---|---|---|---|
| 原生子代理啟動與回覆 | 不繼承 parent 對話；取得指定規範及封包 | Claude／Codex 各自的新 session／trace | AC1、AC2、AC5 | 每軸／每輪新 ID；parent-only marker 不寫入封包；專案規則可見不等於對話繼承 |
| 四軸 reviewer 輸出 | 發現 fixture 中四種各自有依據的規格缺口 | 第一輪合成 spec／matrix／契約 | AC1、AC2 | 不以知道 parent 隱含決策為正確答案；缺檔不得算無問題 |
| 主助理版本與 gate | 修訂後仍使用相同 frozen prompt，新 reviewer 可通過有效零 P0 的第二輪 | 兩輪 live fixture | AC3、AC4 | 第一輪已零 P0 可停止；不要求連續兩輪 clean |
| 主助理 gate 決策 | 第二輪仍有 P0 時拆分，不開第三輪 | 明確標記的 injected reviewer reports | AC4 | P1／P2 不升格為新 gate；沒有有效結果不能推論 P0 數量 |
| 主助理能力／完成判斷 | 無 fresh 能力、缺檔、軸失敗／逾時時維持未完成 | 決策層 fixtures；實際故障注入僅在宿主支援時執行 | AC3、AC5 | 分開記錄合成資料與真實 runtime failure；不以隔離自評取代子代理 |
| Snapshot 與派工內容 | 受檢內容／prompt 變動會使結果失效，補跑不得重設兩輪額度 | before／after hashes 與派工紀錄 | AC2、AC3、AC4 | 相同 bytes 技術補跑與修改後新版本分開；禁止附帶前輪答案改變標準 |
| Reviewer 工具與主助理裁決 | 受檢檔案維持不變；有衝突 findings 回到使用者 | 有效工具設定、fixture hashes、決策層對照 | AC6 | role 中的唯讀宣告不等於有效權限證據；實際工具權限另記 |
| 初始化與套件入口 | 正式契約與 role 隨新專案保留，範本文件清理符合設定 | 既有 CLI／bundle 測試與兩種初始化模式 | AC7 | 不把 `.tmpl.docs/` 當作採用後的必要來源；不改 skill 數量 |
| 最終差異與現有規範 | Stage 6／7 fallback、模型分工、walking skeleton 豁免保留 | scope diff、結構檢查、既有測試 | AC5、AC8 | 不新增內容逐字比對的 Python 測試來冒充上下文隔離驗證 |

這是以原生 agent／文件協定為介面的行為驗證。這期不新增只比對 Markdown 用字、mock 內部派工或重述實作的單元測試；若後續真的新增程式 helper，須另補其公開 seam 的 red → green 測試，並取得變更後的 test plan 核准。

## 命令與預期結果

在實作 worktree 執行；這些命令不會安裝 EGM 或發布套件。

```bash
python3 scripts/verify-project.py
python3 -m unittest discover -s tests -v
git diff --check
```

預期：結構檢查通過；現有 22 項測試通過（以執行時 inventory 為準）；無 whitespace error。這三項只覆蓋結構、初始化與既有行為，不能證明 fresh reviewer 的對話隔離。

因正式規範會進入發布套件，執行既有本機打包與初始化 smoke：

```bash
uv build --out-dir dist
npm pack --pack-destination dist
python3 scripts/verify-distributions.py --wheel dist/harness_agile-0.3.0-py3-none-any.whl --npm dist/create-harness-agile-0.3.0.tgz
```

若版本已變，先從現有 manifest 取得實際檔名，不為本機驗證額外 bump version。預期 wheel／npm snapshot 一致、uvx／npx／pnpx 的暫存專案初始化檢查成功；另確認保留範本模式。所需既有工具或網路若不可用，記為打包驗證未完成，不把它當成 agent 隔離失敗。

Live 測試以當次宿主提供的原生 API 執行，不在計畫中虛構通用 CLI 旗標；證據包含實際 API 參數及結果。沒有該宿主的 trace，就不宣稱該宿主的行為通過。

## 交付與停止點

交付內容為共用規範、兩套 runtime／reviewer adapter、ADR／使用者說明、fixtures 及真實驗證結果。驗證紀錄必須同時列出未覆蓋項目；雙 runtime 行為未驗證前不宣稱全面整合完成。

依核准範圍完成規範與 adapter，交付實際驗證及限制；不另行啟動 plugin 安裝、文件漂移功能或產品初始化。

## 執行紀錄

已依使用者核准進行；結果與 coverage 見[執行證據](../research/2026-11-01-fresh-context-review/evidence.md)及[維護歷程](../history/2026-11-01-fresh-context-spec-review.md)。Claude 未登入、實際故障注入及工具層強制唯讀等限制均明列，不宣稱全面驗證雙 runtime。
