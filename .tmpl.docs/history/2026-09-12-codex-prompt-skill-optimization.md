# Codex Prompt／Skill 最佳化結果

日期：2026-09-12。依使用者批准的 Q1–Q7 與「開始修改」執行。本次完成文件修改、結構驗證、Git 擷取情境驗證及六類 Codex 決策模擬；未宣稱端到端任務效能提升。

## 修改內容

- `AGENTS.md` 與 runtime：依工作選擇參考內容、重用已讀取的內容與既有 tracker 設定。新增 `docs/agents/codex.md`，限定 Codex 的載入、授權延續、完成邊界與委派原則。
- `code-review`：明確處理 committed、staged、unstaged、untracked 與最終工作目錄狀態。兩個 reviewer 使用同一份快照，報告前檢查漂移。Git 擷取及十二項 smell baseline 放入按需讀取的參考文件。
- `grilling`、`to-spec`、`tdd`、`implement`：沿用已核准決策與 seam；保留真正的新決策 gate。Spec 以需求與 traceability 決定完整性；typecheck 依現有工具鏈；review 涵蓋尚未 commit 的實作。
- `init-template`：初始化觸發條件改為使用者要求採用範本，不再單靠 placeholder 存在。
- `agent-browser` 與 workflow：保留瀏覽器、Electron、Slack、QA 與 cloud 分支，刪除重複觸發例子；允許提供等價證據的原生工具。使用者要求指定工具時仍須遵守；必要證據不足時不宣稱通過。
- Skill mechanics：manual-only 是使用者控制政策，不保證 metadata 不可見或零 context 成本。
- Codex Agent 角色：明確限定輸入、證據、輸出及停止條件，維持唯讀與禁止巢狀委派。

九階段流程、四軸審查、兩輪上限、既有人工 gate、TDD 與證據要求保留。未修改 Claude 角色或設定；共用 Skill 經既有 symlink 契約同步。未修改模型／effort 預設或全域 Skill。

## 範圍與快照

基準 HEAD：`26897cc3ca733714c541def5e2b520e497042ee0`。修改前另保存工作目錄的 43 份指令／來源檔與 SHA-256 manifest 至 `/tmp/codex-prompt-baseline-20260912`。審查 packet 位於 `/tmp/codex-prompt-review-20260912`，含本次 17 個執行指引／來源紀錄檔的差異與內容；這些暫存路徑不是永久交付依賴。

原有 `tests/test_bootstrap.py`、archify metadata 與 Claude 入口／角色共五個檔案的 hash 未改變。`skill-sources.json` 保留既有 archify 記錄，再加入本輪 adaptation；未覆蓋原有修改。完整入口盤點見 [32 個 Skill 清單](../research/2026-09-12-skill-inventory.md)。

## 驗證結果

| 驗證介面 | 修改前 | 修改後 | 能支持的結論 |
| --- | --- | --- | --- |
| `python3 scripts/verify-project.py` | PASS，32 Skills | PASS，32 Skills | 本機結構、metadata、manual policy、可攜性檢查通過。 |
| `python3 -m unittest discover -s tests -v` | 22／22，3.820 秒 | 22／22，3.534 秒 | 既有建立器、初始化、同步與封裝回歸檢查通過；時間不是模型效能量測。 |
| `python3 scripts/sync-skills.py --refresh` | 不適用 | symlink 同步成功 | 維持共用 Skill 來源；不是 Claude 模型實測。 |
| Git 擷取 fixture | 舊 `HEAD...HEAD` 對目前 WIP 為空 | 五個情境通過 | 新文件使用的 Git 指令可涵蓋對應狀態。 |
| 兩軸文件審查 | 不適用 | 同一項 P2 已修正，兩軸複核關閉 | 指定 packet 的已發現問題已處理。 |

Git fixture 在拋棄式本機 clone 執行，沒有 commit。五個情境：空範圍、空 committed diff 加 staged／unstaged／untracked、staged 修改在 worktree 抵銷、path filter、無效 ref。Untracked 檔名同時包含空白及換行，使用 NUL 分隔取得。腳本保留於本目錄的 `checks/prompt-review-surface.py`，不加入產品測試套件。

## 六類 Codex 比較

使用兩個新的 Codex 子情境執行：`baseline_eval` 與 `after_eval`，皆不繼承對話，繼承同一工作階段的模型／effort，傳入完全相同的六題、指定讀取檔案與唯讀限制。第二次只改變專案指令內容。題目見 [固定案例](../research/2026-09-12-prompt-eval-cases.md)。

這是「讀指令後決定怎麼做」的模擬，不是六個完整任務的工具執行。共同 harness 明令不委派且預先指定讀取 Skill，因此不能由此推估實際委派數、Skill 自動發現正確率或讀檔節省。未取得逐案例 token／延遲量測。

| 案例 | 修改前觀察 | 修改後觀察 |
| --- | --- | --- |
| README 錯字 | 已會遵守維護豁免；指出 initializer description 衝突。 | 維持正確維護範圍，沒有 placeholder 觸發矛盾。 |
| Timeout 訪談 | 已會沿用核准；指出查單檔仍要求委派的文字衝突。 | 明確採直接讀檔，只問未決行為並保留共識 gate。 |
| Spec | 依上層覆蓋要求處理，但仍須解釋 LONG／單一 seam 偏好。 | 依 traceability 決定 stories 與必要 seams，不補虛構需求。 |
| WIP review | 依使用者要求克服空 diff 中止規則；自行補充 pending 捕捉。 | 直接使用文件的分層捕捉與同一 packet，空 committed diff 不阻止 review。 |
| Python 實作 | 不新增 typechecker，但指出未滿足無條件 typecheck 指令。 | 明確把未設定 typecheck 列為不適用，完成既定 suite／coverage／review。 |
| a11y 工具 | 選等價原生工具，但指出 workflow 要求安裝的衝突。 | 明確區分等價工具、使用者指定工具，以及缺證據時的阻塞。 |

修改前多數決策已因上層指令而正確；不能把六個衝突解讀成六個原有行為失敗。修改後的觀察支持「降低文字衝突、讓決策有直接依據」，不支持成功率、成本或速度提升的量化宣稱。

## 指令長度

| Description | 修改前字元 | 修改後字元 |
| --- | ---: | ---: |
| agent-browser | 925 | 199 |
| code-review | 419 | 124 |
| init-template | 325 | 173 |

三項合計由 1,669 降為 496 字元。這是移除 YAML 外層引號後的文字長度，不是 token 量測。Review 入口由 6,559 降為 3,587 字元，另增加條件式參考；不把移出入口的內容計為全專案刪除量。

## 審查與限制

Standards 與 Spec 使用相同 17 檔 packet，各自找到 Skill mechanics 殘留的零 context 成本保證。已移除，兩軸均直接複核並關閉 P2。其餘未發現可行動問題；這不代表全專案無缺陷。Spec reviewer 重用先前唯讀盤點的 context，Standards reviewer 使用新 context；兩軸沒有互相讀取意見。

尚未完成六類完整 Codex 工具執行的端到端比較、逐模型／effort 掃描，以及新 host 工作階段的自動 discovery 驗證。Claude 本次僅做共用檔案／結構相容性檢查。這些限制保留，不能以 unittest 或決策模擬替代。
