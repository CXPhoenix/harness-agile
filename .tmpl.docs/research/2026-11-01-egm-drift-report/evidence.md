# egm-drift-report 整合：驗證結果

日期：2026-11-01。分支 `codex/egm-drift-report`；base／HEAD
`110a6224773d69b792b840e2a94c9966ed3ea110`。這是母範本維護，
本報告保存實作完成、commit 前的驗證快照；當時使用者已核准實作並明定不 commit／發布。後續已另授權 commit、push 與 PR，交付狀態以 Git／PR 為準，仍不合併或發布。

## 實作與證據

兩套顯式入口及共用契約已實作，沒有新增 production runner、角色或套件相依。
Claude 使用 disable-model-invocation，Codex 使用 allow_implicit_invocation=false；
verifier 額外保證兩邊不能同時退化為 implicit。

未修改的基線結構檢查與 22 tests 通過。T10 的兩個新案例依序 red → green：
原 verifier 未檢出缺少新 skill，亦漏掉兩樹同時 implicit；最小修正後兩案通過。
既有 bootstrap 的固定 skill 數量在新增後先以 33≠32 失敗，更新為產品 33、
母範本／keep 34，並延伸既有 default／keep 案例核對 LICENSE 與相對契約入口。
本次完整 unittest 24/24 通過（Python 3.14.3，7.378 秒），結構檢查為 34 skills。

原生行為介面為 **Codex CLI 0.161.0**，每次新建 ephemeral session，沿用 CLI
預設模型、不指定另一模型／effort；未獨立觀察模型設定，故不推測。完整 stdout
JSONL 暫存在 /private/tmp，沒有將可能含帳號設定訊息的 stderr 納入專案。
[native-results.json](native-results.json) 保存 session ID、trace hash、指令數、
觀察到的 usage 與最終回覆；[reports/](reports/) 保存 6 份實際報告的原始副本。
沒有以代理自評取代 parent 的檔案／oracle 核對。

- 基線：測試目錄尚無 skill 時，Codex 找不到入口，停止診斷，沒有讀取兩個待診斷來源。
- 顯式入口：新 session 由名稱找到新 skill、讀共用契約並寫入報告；確認 64／128 bytes 漂移。
- hidden／混合文件：6 份文件、2 個實作；相符介面未誤報，planned/history 排除，
  找不到 quota 來源列待確認，架構與固定值兩項差異有來源，整體 partial。
- 缺漏行為／欄位：Record.timestamp、delete_record 缺漏均辨識，報告寫入既有 epic。
- 負向進度查詢：回覆 T-0001 ready，沒有執行 drift 或寫任何檔案。
- 同日重跑：原報告與所有原檔 hash 不變，只新增 -02 報告。
- 空目錄：blocked，不冒稱無差異。
- 輸出 symlink：拒絕 checkout 外寫入，未修正 symlink；只回覆摘要，外部 marker 不變。
- 真實版本變動：測試控制端在首次讀取完成後將暫存 store 的 128 改成 256；
  最終重查偵測 hash 不同，報告為 stale，沒有重試成 clean。

第一個 stale 試跑的控制端未辨識帶連字號的 SHA-256 標記，沒有注入變動；
此 run 只算未改動基線。控制端修正後另開 session，成功注入並核對原生 stale 報告。
這項失敗及兩個 trace 都保留在 run summary，不當作 production 缺陷。

## Coverage report

| Seam | Tests | Measured coverage | Acceptance criterion | Uncovered, and why |
|---|---|---|---|---|
| T01 原生入口 | 基線＋Codex 顯式新 session | 找到 skill／共用契約並落盤 | AC1、AC7、AC8 | Claude 2.1.283 auth status loggedIn=false，未跑 live；Codex desktop 亦未個別測試 |
| T02 主張／實作 | basic、hidden、models | 介面、缺漏 API／欄位、固定值、架構四類；原始報告／來源行號可核對 | AC2、AC3 | 單次小型 fixture，未量測一般偵測率或成本收益 |
| T03 相符／預期差異 | hidden 6 文件 | 相符、planned、history 正確分開；缺源未當成 drift | AC3、AC6 | 過期翻譯與已記錄取捨未另做模型案例 |
| T04 檔案列舉 | 單檔、hidden 遞迴、空目錄 | 指定範圍內順序讀取；空目錄 blocked | AC2、AC4 | 重複 aliases、缺輸入互動與廣大範圍未各別試跑 |
| T05 證據不足 | 缺 quota 來源、空集合 | partial／blocked 均有原生報告，非零差異 | AC3、AC4 | 真實權限拒絕、context/time cutoff 未注入 |
| T06 版本／dirty | 真實首次讀取後變更 | 128→256、hash 變更、stale；控制端事件與前後 hash 已保存 | AC2、AC4 | fixtures 無 Git，未實測 staged／unstaged／untracked 分類及 HEAD 固定的 dirty 工作樹 |
| T07 唯一寫入 | 首跑、重跑、symlink 拒絕 | 原來源／舊報告 unchanged，只新增報告或明示未保存 | AC5、AC6 | 沒有注入 disk-full／寫權限拒絕或同時競爭建立 |
| T08 輸出位置 | 專案層、既有 epic、範本 symlink | 兩個 adopted roots 成功，範本外連結被拒絕 | AC5、AC7 | 範本正常寫入、惡意 slug、原生 Windows symlink 未另作 live 案例 |
| T09 非顯式觸發 | 獨立 ticket 進度查詢 | 全部檔案 hash 與清單 unchanged，無報告 | AC1、AC6 | 未逐個執行其他 pipeline skill；靜態確認無新自動接點 |
| T10 政策退化 | 2 新 mutation tests | 每樹缺 skill、兩樹 implicit 都被擋下；完整 24 tests PASS | AC1、AC7 | 格式驗證不代表模型服從或 sandbox 強制唯讀 |
| T11 初始化 | 既有 source default／keep | 新 skill、LICENSE、相對契約入口與數量斷言 PASS | AC6、AC7 | 目前本機 macOS；沒有遠端 CI |
| T12 分發／授權 | wheel／npm／三入口與 keep | wheel／npm snapshot 一致、uvx／npx／pnpx 各樹 33、wheel keep 各樹 34 全通過 | AC7 | 本機套件驗證，不是 registry 發布或所有 OS live |

## Review 與流程保留

[code-review.md](code-review.md)：Standards 0、Spec 0。
[security-review.md](security-review.md)：0 個達 HIGH／MEDIUM 門檻的新增候選，
不宣稱整體安全。ADR-0005 依既有 Stage 8 記錄此非瀏覽器驗證介面；ADR 與 README 索引的兩檔增補另經定點 review，三位 reviewer 均回報 0。

兩個 code reviewers 與一個 security reviewer 各用新對話，
未繼承 parent transcript；診斷 skill 本身的執行沒有派子代理。
[review-manifest.json](review-manifest.json) 保存 captured inputs 與補充規則版本。

Parent 在原 review 後複查 23 個 captured inputs；後續 docs/README.md 的修改以兩檔 addendum hash 為準，最終原封包與增補合併核對皆相符。另確認 15 個權威流程／gate／角色檔案
與 HEAD 逐 byte 一致，包括 AGENTS、workflow、review、runtime、OPEN-QUESTIONS、
兩樹 to-spec／to-tickets／implement／tdd 及 reviewer roles。tracker 的新段落
只說明非權威診斷報告，不改 ticket frontmatter 或 gate。未建立產品 spec／ticket。

## 套件與證據時序

初次 wheel 建置後 oracle.json 又增加邊界案例，npm snapshot 因而與 wheel 不同；
分發驗證正確拒絕。已定位差異僅在研究 oracle；來源固定後重新建置並通過全部分發驗證。
最終打包結果檔與結案追加紀錄會在建置後產生，因此不宣稱套件已包含這些
事後產生的證據；正式 skill、共用契約與授權會另與已驗證產物逐 byte 核對。

最終結果見 [packaging-result.json](packaging-result.json)：Darwin／Python 3.14.3，
source digest `a33076ad30c01ebff931f4bfe8cc6e770fab993f770fec2f5e1f70baa6245e44`、
HEAD 仍為基準且 dirty=true；wheel／npm snapshot 完全一致。uvx／npx／pnpx
預設初始化皆 PASS，各樹 33 skills；同一 wheel keep 模式 PASS，各樹 34，
ADR-0005 日期 placeholder 正確替換，正式契約與入口保留。13 個受影響且隨
套件傳遞的正式檔案與本機最終 bytes 全部一致；產物 SHA-256 一併保存。
沒有新增 runtime 套件，因此未因這次純指引整合重跑 Archify 全套或依賴 audit。

本機 Codex skill-creator quick_validate 通過 Codex entry；其 validator 不支援
Claude 專屬 disable-model-invocation 欄位，Claude metadata 由專案 verifier 檢查，
沒有為迎合 Codex validator 移除合法 Claude 設定。

## 交付界線

實作已保留於隔離 worktree；所有變更未 commit。沒有 push、PR、合併、
發布、版本遞增或遠端 CI。沒有安裝官方 EGM plugin。未驗證部分如上表，
不將靜態指引當作工具強制隔離或雙 runtime live 完成。
