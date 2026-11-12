# mattpocock/skills 上游同步：3cca18b → 4ae2317

日期：2026-11-12（Asia/Taipei）。分支：`claude/fervent-chebyshev-f86d09`，接在 `claude/glossary-rename`（`8e47844`）之後；尚未合併。

評估與計畫見 [研究文件](../research/2026-11-12-mattpocock-upstream-sync-plan.md)。使用者核准計畫，四項決定全部採用建議：

- D1：保留 resolving-merge-conflicts。
- D2：tdd 的註記寫進 Test intent 欄位。
- D3：Codex 樹的 fresh-context 規則寫在 `runtime.md`，並在各 skill 加上短句。
- D4：這次不納入新 skill。

詞彙表改名的同步另見 [glossary-rename 歷程](2026-11-12-glossary-rename.md)。

## 交付內容

| Commit | 批次 | 內容 |
|---|---|---|
| `d1fd84c` | 1 | setup-matt-pocock-skills 的 tracker 範本與 SKILL.md、diagnosing-bugs。兩棵樹原樣套用上游 patch；tracker 種子範本現在跟上游 `4ae2317` 逐位元組相同 |
| `322c184` | 2 | wizard `template.sh` 換成上游版本，另加兩個本機修正，見下方「計畫外的發現」 |
| `99e26df` | 3 | teach、to-tickets、grilling、wayfinder。Codex 樹直接套 patch（grilling 手動插入），Claude 樹手動放進 audit 改寫後的段落；`issue-tracker.md` 補上「`blocked_by` 就是原生 edge」 |
| `1a699aa` | 4 | code-review、implement、tdd 改寫成本機寫法；Codex 樹 6 個 skill 加上 fresh-context，`runtime.md` Codex 段落補上 stage 3 以外的隔離規則與 fallback |
| 本 commit | 收尾 | `skill-sources.json` 的 `upstream_syncs` 第二筆、`local_adaptations`（wizard、code-review、implement、tdd），以及本歷程 |

## 計畫外的發現

- **上游 wizard 範本有兩個問題，已在本機修正**：
  - `ask()` 的 `$e[Enter keeps current]` 會讓 shellcheck 0.11.0 回報 SC1087 error。這在計畫階段就已經發現。
  - 套用後才測出第二個問題：macOS 內建的 bash 3.2 執行 `${value//"$sq"/\'}` 時會保留反斜線。含 `'` 的 `.env` 值重跑後會從 `it's` 變成 `it\'s`。改為透過變數 `q="'"` 替換後，在 bash 3.2 測過 5 種值的寫入、讀回與 `source`，結果都正確。bash 4／5 沒有實測。
- **implement 段落順序**：ticket reference 那段原本插在「at those seams」之前，會讓「those」離它指的對象太遠。最後改放到開頭。

## 審查

依 prompt audit 的成本教訓，只對批次 4 派一位 `harness-reviewer`。第一次因為連不上 API 而中斷，重跑後完成，結果沒有 P0／P1，P2 共 12 項。

**採納的 P2**：
- `runtime.md`：補上 fallback（host 無法隔離時改在主 session 做），段落移到 stage 3 內容之後，並明確寫出 launch evidence 與 agent ID 規則只限 stage 3。
- code-review：「aggregate」改為收集報告後交給第 4 步，避免跟「不跨軸合併」的規則衝突。
- code-review：標準檔案限定為「規範這次改動」的範圍。
- tdd：「proposed」的主詞改成「When you propose seams」。

**沒有採納的 P2**：
- Codex 樹的 wayfinder step 5 與 research 跟 `issue-tracker.md` 的 research 規則不一致。這是既有問題，計畫已經列為範圍外。
- wayfinder 第 76 行、improve-codebase-architecture 的 brief 內容：上游本身就是這樣寫，維持跟上游一致。
- implement 沒有處理 ticket 找不到的情況，也沒有在開始時把 ticket 設成 `processing`。後者是既有缺口。
- Codex 樹內 skill 叫用寫法不一致：只是風格問題，兩種寫法依 `runtime.md` 都有效。

## 驗證

- 每批都跑了 `python3 scripts/verify-project.py`（PASS，34 個 skill）與 `python3 -m unittest discover -s tests`（61 個測試，OK）。
- wizard：兩棵樹 `bash -n` 通過；`shellcheck -S warning` 沒有任何項目；在 bash 3.2 做了 `.env` 往返測試，也確認權限 0600、symlink 保留。
- 套用 patch 後逐檔對照上游 `4ae2317`。差異只剩已記錄的本機改編，以及這次刻意不同步的句子。
- **尚未驗證**：
  - 實際執行 skill 時的行為，例如 code-review 是否真的等兩份報告都回來才繼續、Codex 是否以 `fork_turns: "none"` 啟動 subagent。
  - wizard 在 bash 4／5 的表現。

## 後續

- Codex 樹的 wayfinder／research 跟 `issue-tracker.md` 的 research 規則要對齊，這屬於 audit 暫緩的「Codex 樹是否移植行為修正」。
- `retro` 可以另外評估是否配合 epic close-out。
