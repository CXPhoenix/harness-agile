# PR #11：修正 fast-uri 安全掃描失敗

日期：2026-11-01。使用者要求查明 CI 失敗、修正後驗證、使用專案 tw-emoji-commit 提交並推送；不合併。修正前 HEAD：`dbe12aeeb043edcff62942988af4847a35343d11`。

## 根因與重現

[PR workflow run 41288034206](https://github.com/CXPhoenix/harness-agile/actions/runs/41288034206) 的 Ubuntu、macOS、Windows 三個 job 都在 `npm audit --package-lock-only --ignore-scripts` 失敗，先前的結構、單元、portable／preview 測試已通過。Node.js 20 棄用訊息是另一項 warning，並非本次 exit 1 的來源。

本機在 `.agents/skills/archify` 執行同一命令加上 `--json`，重現 exit 1。`fast-uri 3.1.8` 被四則 2026-10-19 公告涵蓋，3.x 修正版為 3.1.9；兩套 runtime 的 override 與 lockfile 都仍固定 3.1.8。公告及適用範圍列在 [依賴文件](../../docs/security/archify-dependencies.md)。

## 修正

- 兩套 Archify 的 override 固定 3.1.9，以 `npm install --package-lock-only --ignore-scripts --no-audit --no-fund` 更新 lockfile。
- 逐項比對確認只有 fast-uri 的 lock entry 改變；兩套 lockfile 仍相同，registry integrity 與 `npm view fast-uri@3.1.9` 一致。
- 保留所有 CI gate 與既有模型／權限／四軸 review 政策，沒有忽略 moderate 公告或更改 audit 門檻。
- 更新來源調整紀錄及依賴說明，過去 3.1.8 的驗證結果仍保留原日期。

## 驗證

兩套 lockfile 的原始 audit 命令均已回到 exit 0、0 vulnerabilities。本機後續驗證結果如下；推送後 CI 以 PR 最新修正 commit 的 Actions 結果為準，不將舊的本機測試結果視為這次掃描證據。

本機確認：完整乾淨副本 `npm ci --ignore-scripts` 成功、portable 54／54、preview 11／11；validators freshness 通過且生成產物無改動。範本結構檢查與 22 項單元測試通過。沒有新增逐字比對相依版本的測試，直接沿用 CI 既有 audit／支援子集作為 red → green 的公開 seam。

| 公開驗證介面 | 修正前／後的觀察 |
|---|---|
| 既有 npm audit gate | 修正前 exit 1、fast-uri 3.1.8 受影響；修正後兩棵樹 exit 0、零 vulnerabilities |
| Archify 支援測試 | portable 54／54、preview 11／11；validators freshness 通過 |
| 範本驗證 | 結構檢查與既有 22 項測試通過 |
| 套件初始化 | wheel／npm snapshot 一致，uvx／npx／pnpx 三入口通過；source digest `f6602d88f7e1d9cf9c6198ccdaeabee6bc5ffd784dace5b804d393657530a116` |
| 變更 review | Standards 與需求軸各 0 findings；適用固定的 7 檔案 snapshot。後續僅追加本機驗證結果。原始 registry／CI log 未附在 review packet，parent 已另查原始輸出與上游公告。 |

本輪沒有執行 Claude live、模型隔離或額外的瀏覽器視覺驗收；不改變先前紀錄的這些證據界線。套件未發布，PR 不合併。
