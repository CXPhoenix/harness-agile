# Codex 原生宿主與失敗情境：驗證結果

日期：2026-11-02（Asia/Taipei）。依[核准計畫](../../plans/2026-11-02-codex-native-host-failure-verification.md)執行；Claude 依使用者要求延後。本次僅驗證、保存證據，未修正、開票、commit、推送或發布。

**本批已結束，整體為部分完成，不能宣稱全部通過。** 實際新建 7 個 desktop reviewer、1 個 CLI session，共 8／33 次啟動；沒有技術補跑。新案例在可見累計 input 達警戒後停止，後續只整理與核對證據。

| 項目 | 結果 |
| --- | --- |
| S01 四軸控制組 | **pass**。四個新 reviewer、顯式 `fork_turns: none`，36／36 必要檔案 hash/read 可由原生工具輸出核對；四軸零 findings，來源未變。僅此合成 fixture 可判第一輪有效零 P0。 |
| S04 原生取消 | **pass**。對 running reviewer 發出 interrupt，回傳 previous_status=running；其 trace 隨後出現 `turn_aborted`，沒有完成結果。這是取消，不能寫成 timeout 或 crash。 |
| S07 真實 stale | **部分原生證據成立，完整案例未完成**。原生工具輸出確認首軸已讀舊 contract，控制端約 64 ms 後修改；另一軸讀到新版。主助理核對來源變動並拒絕合併為有效同版四軸結果。僅完成 2／4 軸，餘兩軸因預算警戒未啟動。 |
| S09 gate replay | **pass，僅決策層**。對照現行規則及 G1–G10；沒有重新執行兩輪 live 或新增 gate engine。 |
| D01 CLI 控制組 | **blocked：完整落盤前提未成立**。診斷辨識 quota 37／29 差異，timeout 12 相符，planned／history 排除正確；session 回報唯讀，未保存報告。前後 inventory 完全相同；只保存對話輸出的證據副本。 |
| 其他案例 | 分別因能力不足、D01 依賴未成立、新 desktop 頂層 session 不可用或預算停止而未執行；見完整 coverage。 |

沒有確認需自動修正的 production 缺陷。D01 暴露的是本次 CLI 測試環境／控制組限制，S07 的來源變動由測試控制端刻意注入；不能把它們寫成已重現的專案程式缺陷。

## 實際宿主與證據

- Desktop 原生 trace 的 originator 為 `Codex Desktop`，其中 core/CLI version 欄位為 `0.166.0-alpha.5.1`；這不是另外查得的桌面 app 套件版本。
- 主助理及 7 個 desktop reviewer 的 turn context 可觀察到 `gpt-6.1-sol`、`high`。啟動時沒有指定 model／effort override；子代理自評 unknown 不取代主助理取得的原生設定證據。
- Codex CLI 為 `0.161.0`，使用 `exec --ephemeral --json --skip-git-repo-check -C <fixture> -`。沒有覆寫模型／effort／sandbox、修改 trust 或憑證。CLI 的實際模型／effort未取得可獨立核驗的值，保留 unknown。
- Desktop reviewer 的有效 sandbox 是 workspace-write，且有自動附加 memory；操作均唯讀，不能據此聲稱工具層唯讀或完整記憶隔離。
- 基準 main／origin/main／v0.4.0 peeled tag：`0fcd87f9053311c4372a8c6b4867f7ea30aa8d9e`。本次計畫及兩份 project-status 草稿保持原 bytes。

證據入口：[coverage](coverage.md)、[逐例紀錄](cases.md)、[能力盤點](capabilities.md)、[實際預算與用量](budget.md)、[desktop 結果與用量](desktop-results.json)、[原生啟動／取消控制](desktop-launch-controls.json)、[注入事件](stage3-s07-injection.json)、[CLI 未保存報告的對話副本](egm-d01-unsaved-report.md)、[CLI 原生事件](egm-d01-trace.jsonl)。

## 執行方式與限制

唯一測試暫存根目錄為 `/private/tmp/harness-native-20261102-e1rmy3p6`；沒有沿用、刪除舊驗證資料。Stage 3 在現有 desktop 控制對話建立新的 reviewer 對話；沒有宣稱主助理本身為新頂層 session。所有 reviewer 均使用 `harness-reviewer`、`fork_turns: none`，同時最多兩個。

必要規範與新合成 fixture 才提供給 reviewer／CLI，oracle 保存在其指定 scope 外。主助理另讀取這些測試 session 的本機原生 trace，核對實際工具輸出、用量及終止事件；沒有以歷史答案填補本次結果。保存的是必要節錄，未將完整父對話、memory 或可能包含帳號訊息的 CLI stderr 納入專案。

CLI fixture 有 4 份文件與 2 份實作，沒有 Git。它複製的 `.tmpl.docs/` 為空，且缺少 AGENTS 連結的部分輔助文件；D01 明列這些 fixture 脈絡限制。這也是本輪控制組準備不完整的因素，不能把結果包裝成完整成功。依使用者要求未修正該 fixture 後再跑，也沒有變更 CLI 權限來取得成功結果。

首次預算警戒快照記錄可見 input **5,169,791**、其中 cached **5,008,512**、output **34,201**；這含主助理，並非僅 8 個測試 session。之後沒有啟動新案例。結案整理本身仍產生用量，最後可核對下限、缺失及截止時間見 budget；不能把警戒值當成實際最終總量或金額。

既有 spec／traceability／ticket 流程與 gates 沒有變動。EGM 維持顯式觸發、順序、只診斷；沒有自動修正、開票或重試。本批未驗證項目不新增為全域 gate，亦不以局部通過推論 Claude、其他 OS 或全部宿主行為。

## 後續選項

若另行核准續測，先以較短的新控制對話降低重複 context 用量；明確確認 CLI 的既有有效寫入權限及完整 fixture 脈絡後，重做 D01，才恢復 CLI 邊界測試。這些是下一批的前置決策，不是本批已完成的修正。

desktop EGM 仍需要使用者提供可用的新頂層測試工作階段；不以 reviewer 子代理、CLI 或 source classification 偽裝。timeout、獨立 worker crash、fresh 能力停用、同步建立競爭與 steering 各自仍需宿主支援。Claude 維持 deferred_by_user，0 次啟動，沒有檢查或變更 Claude 登入。
