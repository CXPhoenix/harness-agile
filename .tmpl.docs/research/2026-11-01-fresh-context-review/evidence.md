# 全新上下文四軸審查：執行證據

日期：2026-11-01。驗證時分支 `codex/fresh-context-spec-review`，base／HEAD `72677d5f04cfa9ace6658181d1317dacc1118305`；以下結果記錄於 commit 前，後續交付版本以 Git 紀錄為準。

## 基線

修改前啟動 `baseline_completeness`，`agent_type=harness-reviewer`、`fork_turns=none`。完成三份 fixture 與規範讀取，發現 unsupported format matrix row 無 AC，P0／高信心；marker probe 為 UNAVAILABLE。當前工具本來就能以新上下文發現此缺口，因此沒有把既有成功行為寫成 failing test。規範層的缺口是當時 fallback 容許非獨立的本地檢閱，尚未明定它無法通過 Stage 3。

基線 formal rule hashes：AGENTS `7788e8567b6a01946e8cd14c0e82dbd0b0aea9d3dc36b6efbe968ef4b8079b49`；runtime `0a386799cefea9966a12bf02d50061688facbd9650e2366b459e1c4c7a710122`；review `59986a988856af5eb70f1682ee136170b964e1bc7346020629c795a6e203529e`。

## Codex desktop 原生 collaboration API

每次皆為 `spawn_agent(agent_type="harness-reviewer", fork_turns="none", task_name=<下表>)`，未指定 model／effort，也未 resume 舊 agent。實際回傳的識別名稱是 canonical task name；宿主未向 parent 回傳底層 session UUID。更新後角色指引作為明確封包輸入提供，不宣稱長時間執行中的 host 自動重新載入 role cache。

每輪四軸讀同一個暫存 packet：`/private/tmp/harness-fresh-review-r1`／`r2`。當輪 manifest 與必要輸入 SHA-256 另存 [round-1-manifest.json](round-1-manifest.json)、[round-2-manifest.json](round-2-manifest.json)；兩輪只改 spec／matrix，prompt hash 同為 `80786acb836ad2d1b2779fd6c02a5696d4ec5133ef6132e805e3c2f82bd022c0`。原始及修訂 spec／matrix 位於 `fixtures/round-1/`、`fixtures/round-2/`。

### 第一輪

| Canonical reviewer ID | 軸 | 結果 | 讀取與探針 |
|---|---|---|---|
| /root/r1_completeness | Completeness | 1 P0：unsupported format 無 AC | 9/9 input hashes MATCH；UNAVAILABLE |
| /root/r1_verifiability | Verifiability | 1 P0：容量耗盡只寫 respond appropriately | 9/9 input hashes MATCH；UNAVAILABLE |
| /root/r1_contract | Contract conflict | 4 P0：授權、保留期限、不支援格式、容量結果與契約要求不合 | 9/9 input hashes MATCH；UNAVAILABLE |
| /root/r1_redteam | Red team | 2 P0：跨租戶建立／讀取、到期 artifact 仍可讀 | 9/9 input hashes MATCH；UNAVAILABLE |

共 8 筆 P0 回報，有跨軸重疊。沒有相互矛盾的裁決；修訂涵蓋 4 類缺陷。依原 gate，第一輪不得通過。Parent 在子代理完成後重新計算封包與原輸入 hashes，全部未變。第一輪 marker 僅在 parent 推理上下文產生，其缺席是弱佐證，主要可觀察證據是顯式 fork_turns=none。

### 第二輪

| Canonical reviewer ID | 軸 | 結果 | 讀取與探針 |
|---|---|---|---|
| /root/r2_completeness | Completeness | 無 findings，P0=0 | 9/9 input hashes MATCH；UNAVAILABLE |
| /root/r2_verifiability | Verifiability | 無 findings，P0=0 | 9/9 input hashes MATCH；UNAVAILABLE |
| /root/r2_contract | Contract conflict | 無 findings，P0=0 | 9/9 input hashes MATCH；UNAVAILABLE |
| /root/r2_redteam | Red team | 無 findings，P0=0 | 9/9 input hashes MATCH；UNAVAILABLE |

四軸有效完成，P0=0，這份合成 fixture 的 Stage 3 gate 通過；沒有第三輪。Parent 完成後重新比對 round 1／2 全部輸入 bytes/hash；封包均未變，當前正式規則及第二輪 fixture 與 round 2 manifest 相符。

本輪 parent-only marker `PARENT_ONLY_R2_A7F0_HERON_42` 在派工前寫於 parent commentary，未放入封包或派工訊息。四個 child 均回覆 UNAVAILABLE，與顯式 fork_turns=none 啟動控制相互佐證；不能延伸推論 filesystem 或外部 memory 已隔離。

9 個原生 reviewer invocation：1 次基線加 8 次正式四軸；正式兩輪合計 72 次必要檔案 hash/read 回報全部吻合 manifest。沒有技術補跑；沒有強制指定另一模型／effort。未取得 token／費用計量，因此不報告成本改善。

## 權限、記憶與 trace 界線

第一輪 reviewers 明確回報有效 host sandbox 為 workspace-write，存在可寫入工具；角色 read-only 並非工具層強制唯讀。Parent packet 的 before／after hashes 未變；這證明受檢檔案未被修改，不證明所有 filesystem 都不可寫。

Fresh 子代理仍收到宿主注入的 MEMORY_SUMMARY；未用於補足 fixture。這符合對話隔離不等於清除所有宿主指令／memory 的界線。Parent 可觀察啟動參數、completion 與完整 child 回報／hashes；未獨立取得全部底層 child raw read trace 或 memory 使用 trace，因此不宣稱完整隔離所有資訊來源。

## Claude

本機 Claude Code 2.1.283；`claude auth status` 回報 loggedIn=false、authMethod=none。未變更帳號或憑證，未執行 Claude 模型審查。因此 adapter／frontmatter 的檔案檢查與 Claude live behavior 必須分開回報。

## 決策層與其他驗證

[Gate cases](gate-cases.md) 保存 10 個預製狀態與本次主助理決策。它不是實際 timeout、故障或無 fresh 能力的原生重現。結構檢查通過（33 skills）；既有 unittest 22/22 通過（Python 3.14.3，5.817 秒）；`git diff --check` 通過。直接來源初始化的 default／keep 兩種模式均驗證 7 個必要檔案，role 與契約 bytes 保留，ADR placeholder 正確替換；default 移除 `.tmpl.docs/`、keep 保留。最終 runtime 摘要修正後重跑：結構檢查通過，22/22 unittest 通過（5.586 秒），diff whitespace 檢查通過。25 份當時變更／匯入 Markdown 的本機連結與 UTF-8／whitespace 檢查通過，Charter／project tokens 保留。

[變更 review](code-review.md)：Standards 0；Spec 唯一 P2 已修正並獲定點 closure。[安全審查](security-review.md)：0 個新增 HIGH／MEDIUM 候選。

Live 四軸測試固定的是當時 packet。完成後 Stage 6 指出 runtime 的 Claude role 摘要仍籠統要求 Git diff，已修正這個摘要；正式四軸／分級／P0／兩輪標準沒有改變。最終 runtime 檔案 hash 因摘要修正不同於 live manifest；不宣稱 live 測試曾讀到尚未存在的修訂，也沒有為這個文件釐清啟動第三輪合成 spec review。

## 最終套件驗證

- `uv build --out-dir dist`：sdist／wheel 成功。
- `npm pack --pack-destination dist --json`：本機 create-harness-agile 0.3.0 tgz 成功，747 entries。
- `python3 scripts/verify-distributions.py --wheel dist/harness_agile-0.3.0-py3-none-any.whl --npm dist/create-harness-agile-0.3.0.tgz`：wheel／npm snapshot 相同，uvx、npx、pnpx 三種 default 初始化全部 PASS，各有 32 個 Claude／Codex skills。
- 從同一 wheel 另執行 `uvx --offline --from <wheel> harness-agile init <temporary target> --keep-template-files --no-input ...`：PASS，必要文件、角色與 verifier 保留可用。
- 最終 9 份正式契約／role／guide bytes 與已驗證 wheel 逐一一致。結果見 [packaging-result.json](packaging-result.json)，source digest 為 `7ec76e8a5de342e7d5009dc290458106b1951855c7f6f7040c321a6ce424d4e8`，dirty=true／HEAD 仍為基準 commit。

初次受限 sandbox 的 uv build／額外 keep 驗證曾因全域 cache／tools 目錄寫入遭拒。已確認錯誤路徑並以核准權限重跑成功，沒有改動專案程式來繞過。驗證結果檔在建置後產生，故不宣稱套件內含這份最終結果；正式 runtime bytes 已核對。套件未發布，未重跑遠端 CI 或其他 OS。

## Coverage report

| Seam | Tests | Measured coverage | Acceptance criterion | Uncovered, and why |
|---|---|---|---|---|
| 原生子代理啟動／回覆 | 1 次基線＋8 次正式 invocation；fork_turns=none | Codex desktop 四軸×兩輪，唯一 IDs；R2 commentary marker 均 UNAVAILABLE | AC1、AC2、AC5 | Claude 無登入；未完整獨立取得 child raw trace；marker 本身不是完整隔離證明 |
| 四軸輸出 | 4 類 seeded 缺陷；R1 8 筆回報含重疊，R2 無 findings | 每個軸均有完成回報；72/72 必要檔案 hash/read 回報符合 manifest | AC1、AC2 | 未以其他產品 spec 衡量缺陷發現率；未量測成本改善 |
| 版本／P0 gate | R1 不能通過，R2 有效零 P0；同 prompt hash | 兩輪 packet before/after 完全相同；無第三輪 | AC3、AC4 | 最後 Claude 摘要釐清後僅定點 review／靜態／套件驗證，未宣稱重新執行完整 live suite |
| 停止與分歧決策 | G1–G10 注入案例 | 主助理依狀態表作決策，包含 R2 P0→split、timeout→incomplete、爭議→使用者 | AC3、AC4、AC6 | 這是決策層；真實停用能力、timeout/crash、stale 競態未原生注入 |
| 唯讀／記憶邊界 | Packet hashes、實際 host 權限回報 | 受檢檔案未改，沒有巢狀代理；workspace-write 與 memory 注入已揭露 | AC6 | 工具層寫入拒絕／完整 filesystem 與 memory 隔離未驗證，也不是 fresh context 本身的保證 |
| 初始化／可攜性 | 22 既有測試、2 種來源模式、3 種套件入口、wheel keep 模式 | Darwin／Python 3.14.3 通過，9 個正式檔案與 wheel 一致 | AC7 | 未重跑 Windows／Linux／遠端 CI；不宣稱跨 OS live agent 行為 |
| Scope／維護規範 | Standards、Spec、security review；links／tokens／diff checks | Standards 0；唯一 Spec P2 已 closure；HIGH/MEDIUM security candidates 0 | AC5、AC8 | review 適用 captured scope；dependency scanning、availability/rate limiting 不在安全審查內 |

本次修改的是文件／role 協定，程式碼覆蓋率不適用；沒有新增逐字比對文件的 Python 測試。對雙 runtime 的宣稱限於兩套 adapter 已實作、可攜性通過及上述實際可觀察證據，不宣稱 Claude live 已驗證。
