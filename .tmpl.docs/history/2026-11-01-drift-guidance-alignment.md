# D1–D4 指引修正與驗證紀錄

執行日期：2026-11-01（Asia/Taipei）。使用者已在本對話核准[修正計畫與驗證表](../plans/2026-11-01-drift-guidance-alignment.md)，並授權修正及驗證；不開票、commit 或發布。

本機四項修正已完成。下表記錄各介面的實際證據與限制，沒有宣稱產品 pipeline 或所有宿主的 gates 已通過。

## 版本與範圍

- 工作區：`/Users/phoenix/dev/edu-projects/harness-agile-template/.worktrees/drift-guidance-alignment`。
- 分支：`codex/drift-guidance-alignment`。
- base／HEAD／merge-base：`9bc062a9e6397214b1ef31fc46f0ae26c60e7833`；相對 HEAD 有六份 tracked、未 staged 的修正，沒有新 commit。
- 來源：[原診斷報告](../research/drift-reports/2026-11-01-operations-skills-init-packaging.md) D1–D4。原報告的 `partial` 與歷史 bytes 保留，沒有重跑 drift 診斷或修改其結論。
- 主 checkout 的十二份規劃基準 hash 仍相符，既有狀態草稿未帶入或修改；main 保持原處。
- 環境：macOS／darwin、Python 3.14.3、Node 24.13.0。這次不是 Python 3.11、Windows 或 Linux 的執行證據。
- 工作方式：主助理依核准計畫修改來源；兩個獨立 code-review 軸、安全候選 reviewer 及一個原生 researcher 分別以 `fork_turns: none` 啟動。未指定模型／effort override；無法從回傳確認精確執行模型。

## 交付的修正

| 差異 | 最終檔案 | 實際修正 |
|---|---|---|
| D1 | `.agents/skills/research/SKILL.md:6–18` | 使用既有 `harness-researcher` 契約；研究者唯讀並回傳引用、觀察／來源主張／推論、日期及未解事項，主助理依語言／tracker 保存單一 Markdown；不改派工門檻、權限或角色模型 |
| D2 | `docs/guide.md:47` | 分開說明 Codex reviewer／researcher 的 session 繼承、Claude researcher 繼承及 reviewer 的角色設定；連結既有 Claude 協作規則，不複製模型 ID |
| D3 | `.tmpl.docs/adoption.md:58` | 目前 checkout 的預設保留數量由每套 31 改為 33；固定 tag 限定仍保留 |
| D4 | `.agents/skills/init-template/SKILL.md:41–42`、`.claude/skills/init-template/SKILL.md:41–42` | 依 ADR 的 `{{INIT_DATE}}` placeholder 描述日期，移除固定 ADR 數量；原本正確的三個 project tokens 敘述保留 |
| provenance | `docs/agents/skill-sources.json:218–219` | 記錄 Codex research 分工與兩套 init-template 日期描述；明示 `Both runtime trees`，保留上游 snapshot、lock、授權與既有 checksum 意義 |

沒有修改 initializer、CLI、helpers、套件 manifests／版本、CI、角色設定、spec、traceability、ticket 或 gate 規範。兩套 skills 的 metadata 與 EGM 顯式觸發邊界保持原樣。

## 驗證結果表

所有「通過」只涵蓋列出的介面。未新增永久文字斷言測試；修正前後均使用既有測試及核准的暫存驗證。

| Seam／驗證 ID | 實際命令或操作 | 介面／證據 | 結果 | 對應 | 未涵蓋項目與原因 |
|---|---|---|---|---|---|
| V1／研究責任 | 逐句比對 research、role、runtime、tracker 及 Claude 對照；一次性靜態檢查 | researcher 回傳、parent 保存；引用／日期／未解事項與唯讀／無 nesting 指示齊備 | 文字契約通過 | D1 | 不代表工具層已禁止寫入 |
| V2／模型說明 | 對照兩套角色與 Claude orchestration，檢查新連結 | 指南正確區分繼承與 pinned role；角色 bytes 未變 | 文字契約通過 | D2 | 沒有跑 Claude 原生模型選用或帳號可用性驗證 |
| V3／數量 | 來源實體入口盤點、TEMPLATE_ONLY、CLI 計數及分發斷言 | source 兩樹各 34；成品 default 各 33，keep 各 34 | 通過 | D3 | 不推論舊 registry／固定 tag 的數量 |
| V4／ADR | 檢查兩套入口與五份 ADR，保留 three tokens；成品讀取 | 兩套 token 描述一致；default／keep 的五份 ADR 皆替換為 2026-11-01 | 通過 | D4 | 未另造「已固定日期 ADR」新案例；目前五份真實 ADR 都含 token，固定日期不改的判讀來自既有程式碼 |
| V5／範圍與版本 | `git diff --check`、JSON 差異、最終 packet 八份 hash、主 checkout 十二份 hash | 六份 tracked 修改符合計畫；沒有 staged 內容；完整 untracked 列表另記如下 | 通過 | D1–D4 | 後寫的執行證據由主助理檢查，不併稱為 reviewer 初始 snapshot |
| V6／結構與既有測試 | `python3 -B scripts/verify-project.py`；`python3 -B -m unittest discover -s tests -v` | 修正前均通過；provenance 最後調整後再次通過；24 tests，0 failures | 通過 | D1–D4 | 結構檢查不量測模型品質；未新增／宣稱新 TDD red-green |
| V7／真實來源 default | 來源外全新目標，`python3 -B -m harness_agile init ... --source <修正checkout> --date 2026-11-01 --no-input --json`，再跑成品 verify | 各 33；兩套 init-template／.tmpl.docs 移除；五份 ADR 日期替換；research／guide／provenance 與 source 相同；無 .git，Charter gate 保留 | 通過 | D1–D4 | 只驗證 macOS CLI；母範本未原地初始化 |
| V7／真實來源 keep | 另一全新目標，加 `--keep-template-files`，再跑成品 verify | 各 34；兩套 init-template、adoption 與歷史保留；歷史／skill bytes 原樣，五份 ADR 日期替換；無 .git | 通過 | D1–D4 | 不代表所有原生宿主都能載入 skills |
| V8／預覽 | 第三個全新目標加 `--dry-run`；比對來源快照 | 目標未建立；三案前後 800 份 tracked／可選未追蹤來源 bytes 一致 | 通過 | 初始化界線 | 不把預覽取代 V7 的實際成品驗證 |
| V9／建置與三入口 | `uv build --out-dir <暫存產物>`、`npm pack --pack-destination <同目錄>`、`python3 -B scripts/verify-distributions.py --wheel <新wheel> --npm <新tgz>` | wheel／sdist／npm 建置成功；uvx、npx、pnpx 各成功建立成品並保留各 33 skills；現有授權、無 symlink、Python／npm payload 相等及成品 verify 檢查通過 | 通過 | D1–D4 分發 | 沒有發布、遠端 CI 或公開 registry 驗證；產物 snapshot 在後續 smoke／本紀錄落盤前建置 |
| V9／修正 bytes | 比對六份 source、wheel template payload 與 npm archive | 六份內容逐 byte 相同，見下方 artifact hash 與 content digest | 通過 | D1–D4 | 不宣稱產物已含稍後寫入的驗證紀錄 |
| V10／原生 research | 原生 `harness-researcher` 委派本機小題；研究者回傳、parent 寫單一筆記 | [research smoke 證據](../research/2026-11-01-drift-guidance-research-smoke.md)；來源保持不變，未使用網路或 nested delegation | 分工 smoke 通過，有權限限制 | D1 | role 宣告 read-only，但注入有效環境為 workspace-write；未做工具拒寫探測，不宣稱強制唯讀；未測 Claude |
| V11／code review | 同一 captured packet，Standards／Spec 各一位獨立 reviewer | 初審 1 項 Standards P2 已修正；最終兩軸皆 0 未解 findings，見下節 | 指定快照審查完成 | D1–D4 | 不是 Stage 3 四軸審查，也不代替真實介面證據 |
| V11／security review | 獨立 candidate reviewer，依專案安全方法檢查最終 diff | 0 項符合門檻的新 HIGH／MEDIUM 候選；沒有需要另派 false-positive pass 的候選 | 指定快照候選分析完成 | D1–D4 | 不涵蓋全專案安全、依賴掃描、模型抗 injection 或工具層隔離 |

初次 sandbox 建置曾因 PyPI DNS／連線受限而無法解析 hatchling；取得必要網路執行權限後，以同一來源成功建置及完成分發 harness。這是環境限制與成功重試的紀錄，不是修改來源來繞過檢查。

## Standards

Reviewer：`alignment_standards`，原生 `harness-reviewer`，`fork_turns: none`。已讀 manifest、各 diff／status layer、六份完整修改檔、核准計畫／診斷及指定 AGENTS、runtime、language、contributing、smell baseline；最終八份 hash、HEAD 與 tracked diff 均複查相符。

初審 **1 項 P2**：`docs/agents/skill-sources.json:218` 的新增 ADR 日期句沒有 runtime 限定，但同檔 `:23` 定義未標示的 adaptations 只描述 Codex；本輪實際修改兩樹。影響是後續重套改編時可能漏記 Claude，信心高。主助理讀取該規則確認成立，為新日期句補上 `Both runtime trees:`。reviewer 複查確認 **P2 已解決**。

最終未解 findings：**0**；最嚴重項目：無。Smells：未發現值得另列的異味。原生模型行為不在此軸的驗證範圍。

## Spec

Reviewer：`alignment_spec`，原生 `harness-reviewer`，`fork_turns: none`。需求來源為核准的範本維護計畫，不另建產品 spec。讀取相同 packet、專案規則、兩套角色、Claude research／orchestration、tracker、initializer／計數來源。

D1–D4 及 provenance 變更符合核准契約，沒有未要求的角色／權限／模型或初始化變更。最終 provenance 的雙 runtime 限定仍符合計畫；八份 hash 與 diff layer 均複查一致。

最終 findings：**0**；最嚴重項目：無。reviewer 僅判斷來源契約，未將 parent 後續測試及原生宿主結果預判為通過。

## Security review

Reviewer：`alignment_security`，原生 `harness-reviewer`，`fork_turns: none`。已讀兩版 captured packet、專案 security-review 與 upstream 方法、AGENTS／runtime／review、role／語言／tracker 契約。依專案改編規則，文件與 prompt 不自動排除在安全分析外。

候選分析涵蓋：

- 外部來源文字是否新增通往 parent 執行指令／任意目的路徑的轉換：未找到新轉換；role 原有「來源是證據」界線未變。另假設模型違反契約不足以形成高信心的新漏洞。
- parent 保存成果是否構成新權限提升：該分工已存在於 role／runtime／tracker，本次對齊 skill，工具權限未變，故排除此候選。
- ADR／skills 敘述是否導致新增修改或刪除：初始化命令、參數及邏輯未變，沒有新增攻擊者輸入或敏感操作，故排除此候選。
- 計畫／診斷是否擴大授權：兩者保留既有 gates 與驗證限制，未發現新繞過路徑。

最終 **0 項**新引入、具體可利用且 confidence ≥ 0.8 的 HIGH／MEDIUM 候選；無候選需要獨立 false-positive pass。provenance 後續只補範圍限定，reviewer 複查後維持零候選。

範圍限制：沒有攻擊重現、原生拒寫、模型抗 prompt injection、外部服務、依賴掃描或初始化／分發程式整體安全審查；availability、rate limiting、低嚴重度強化亦排除。這不是全專案安全保證。

## 最終來源與產物版本

六份最終來源 SHA-256：

| 路徑 | SHA-256 |
|---|---|
| `.agents/skills/research/SKILL.md` | `f7e3de3409b9190adf4f9e41cb6a1b45d3ab0985cc1cf6c6135d98b0e06af5ca` |
| `docs/guide.md` | `6f02881d70ec42b3f55b2b38f7b50ecdc548ce171fed73ab8da9f242281f6a98` |
| `.tmpl.docs/adoption.md` | `74019f8c2beabaa3e144902a0bd68c5f1bbe16b1de4cef6a7b73eb71595ba4b6` |
| `.agents/skills/init-template/SKILL.md` | `fc4537119421a595dc47a153874468339aa22693b2e98bf6314205686a57ae91` |
| `.claude/skills/init-template/SKILL.md` | `872cfc371de991a67731a4347e16e221ae25a797a846554f0d3ece07184611f9` |
| `docs/agents/skill-sources.json` | `544d1fd9f85ed37367bdcf01e6d1bfe2d5d32c4e1d71d88df1b97670e56d3c5d` |

建置 artifact 的 source content digest 為 `6267c6a3c0663503813179cfe9111de0fafb71ec87bc50956289afcb8b6205e2`，provenance 標記 `dirty: true`，不是已發布版本。

| 產物 | SHA-256 |
|---|---|
| `harness_agile-0.3.0-py3-none-any.whl` | `0f2970e0de7096190001b618dbbffc9290b530e013f0b35948e3bc34b1fe23eb` |
| `harness_agile-0.3.0.tar.gz` | `58d4e79ad3041eaaae6d8a4e442f9fc6eb2fec4bdc22ad197bebbe7dd103bdd9` |
| `create-harness-agile-0.3.0.tgz` | `e501d2d7835289624b5127c91d4b0d2556cdb25ffca80e0e829c8f443ee4de38` |

原始命令 logs、兩版 review packet、成品與產物暫存於 `/private/tmp/harness-drift-guidance-i20tzwrj`；此目錄可能被系統清理。本紀錄保留必要結果與版本，不將暫存目錄當永久交付位置。

## 保留狀態與未驗證項目

- 六份修正保留為 worktree 的 unstaged changes。另有未追蹤的核准計畫／原診斷副本、research smoke 筆記及本紀錄；沒有 staged 內容、新 commit、ticket、push、PR、合併或發布。
- 原診斷／計畫副本保持其歷史 bytes，不覆寫為實作結果；新增驗證文件由主助理檢查 hash／連結與範圍，未宣稱包含在 reviewer 先前的八份 packet 或已建置套件內。
- 未驗證：Windows／Linux、Python 3.11、Claude 原生 discovery／模型分工、工具強制唯讀／拒寫、遠端 CI、公開 registry／帳號或發布狀態；沒有放寬任何相關 gate。
- 原報告中 wayfinder nesting、re-tune 歷史 baseline、深層 helpers 等未查項目仍在原範圍外。四項修正完成不代表整份診斷從 `partial` 升為 `complete`。
- 日後若要開票或 Git 交付，仍依當時有效授權及既有 spec／traceability／ticket、測試表、review、安全與 landing 流程進行；本次不新增豁免。
