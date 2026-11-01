# Archify 依賴與驗證範圍

2026-11-01：本範本將兩套 Archify 的 `fast-uri` override 與 lockfile 由 3.1.8 更新為 3.1.9，修正 PR #11 的安全掃描失敗。前次更新為 2026-10-16（3.1.6 → 3.1.8）及 2026-09-13（3.1.5 → 3.1.6）。保留 Archify 內建及既有呼叫政策；Windows 自動開啟繼續[停用](windows-opener.md)。

## 公告的適用範圍

[上游公告](https://github.com/fastify/fast-uri/security/advisories/GHSA-f65p-4m7j-42xc) 描述不受信任 URL 正規化後，用於網路請求或主機政策判斷時的風險，3.1.6 是 3.x 分支的修正版。

2026-09-28／29 又公布三則公告，風險類型相同，都是 authority 或 host 的解析與正規化：

| 公告 | 等級 | 3.x 修正版 |
| --- | --- | --- |
| [GHSA-qw65-cvwx-89v3](https://github.com/advisories/GHSA-qw65-cvwx-89v3)：port 未驗證，可在 serialize 時注入 authority | high | 3.1.7 |
| [GHSA-58mr-gqgx-xq4g](https://github.com/advisories/GHSA-58mr-gqgx-xq4g)：authority 中未閉合的中括號造成 host 混淆 | high | 3.1.7 |
| [GHSA-hrr3-gc8f-f4qj](https://github.com/advisories/GHSA-hrr3-gc8f-f4qj)：percent-encoded 字元造成 host 大小寫正規化不一致 | medium | 3.1.8 |

3.1.8 是同時涵蓋三則公告的 3.x 版本，落在 `ajv@8.20.0` 宣告的 `^3.0.1` 範圍內。

2026-10-19 又公布四則公告，3.1.8 仍在影響範圍；[3.1.9 security release](https://github.com/fastify/fast-uri/releases/tag/v3.1.9) 修正以下問題：

| 公告 | 等級 | 3.x 修正版 |
| --- | --- | --- |
| [GHSA-w74x-v6f9-j3xg](https://github.com/advisories/GHSA-w74x-v6f9-j3xg)：percent-encoded scheme 解碼後變成可執行 scheme | moderate | 3.1.9 |
| [GHSA-wjr9-j795-jxcr](https://github.com/advisories/GHSA-wjr9-j795-jxcr)：host canonicalization 靜默改寫有歧義的 host | moderate | 3.1.9 |
| [GHSA-xhq7-xmqj-769h](https://github.com/advisories/GHSA-xhq7-xmqj-769h)：相對路徑正規化改變原本的解析語意 | low | 3.1.9 |
| [GHSA-333x-w4r6-6crp](https://github.com/advisories/GHSA-333x-w4r6-6crp)：suffix reference 未跳脫首段冒號，可能被重新解析為 scheme | low | 3.1.9 |

3.1.9 仍在現有 AJV 宣告的 `^3.0.1` 範圍內。兩棵 runtime 樹都固定此 patch 版本並更新 registry integrity；其他套件版本不變。CI 的安全掃描維持啟用，沒有降低門檻或略過檢查。

目前程式碼僅在開發用的 `scripts/generate-validators.mjs` 經由 AJV 使用此依賴，讀取內附 schema，輸出無外部 require 的 standalone validators。一般產圖使用預先生成的驗證器；此次未確認公告描述的可利用 SSRF 路徑。即使沒有公開 endpoint，也不能單憑這點排除所有本機處理不受信任資料的風險。

改為只能由使用者呼叫屬操作政策，不能取代依賴修正。因此保留原有呼叫政策；一般產圖不啟動伺服器，明確選用 preview 才監聽 127.0.0.1，並依 skill 規則按使用者需求啟動。

## 在獨立 skill 副本自行驗證

需 Node.js 18+ 與 npm。在 `.agents/skills/archify/` 或其完整暫存副本執行：

```sh
npm ci --ignore-scripts
npm run test:portable
npm run test:preview
npm audit --package-lock-only --ignore-scripts
```

`test:portable` 涵蓋驗證器新鮮度及 schema、Windows opener 停用、交付規則、輸出路徑防護與 render 產物檢查。`test:preview` 需允許本機監聽，檢查最後有效產物保留、重複寫入、過期候選、停止行為與五種 renderer 的首次交付。

上游 `npm test` 保持原樣，其中部分指令依賴未隨 skill 附上的上游 README、scripts 與 examples。此處提供可獨立執行的明確子集，不宣稱通過整套上游測試、瀏覽器視覺驗收或原生 Windows 端到端測試。

## 2026-11-01 修正驗證

在 macOS、Node.js 24.13.0、npm 11.6.2，以完整的乾淨 Archify 暫存副本驗證 3.1.9：

- `npm ci --ignore-scripts` 成功，兩棵樹的 lockfile 安全掃描皆為 0 vulnerabilities。
- `test:portable` 54／54、`test:preview` 11／11 通過；驗證器 freshness 檢查通過，預先生成的驗證器沒有改動。
- 根目錄結構檢查及既有 22 項單元測試通過。

遠端三平台結果以 PR #11 最新 commit 的 CI 為準；詳細重現與修正紀錄見範本維護歷程。

## 本輪結果

2026-10-16，macOS、Node.js 24.13.0、npm 11.6.2，更新為 3.1.8 後：

- 乾淨暫存副本執行 `npm ci --ignore-scripts` 成功，npm 回報 0 vulnerabilities。
- 驗證器重新產生檢查通過，產物無須變更。
- `test:portable` 54／54、`test:preview` 11／11 通過。

2026-09-13（3.1.6）的結果：首次嘗試額外的上游 preview-contract 測試因缺少其父目錄 README 而失敗，未納入本範本支援子集；預覽測試首次受 sandbox 禁止監聽，允許 loopback 監聽後全數通過。

## Windows CI 追加修正

三平台 CI 首次揭露 preview 在 Windows libuv 檔案監聽層中止，與[上游 issue 310](https://github.com/tt-a1i/archify/issues/310) 描述的短路徑問題一致。監聽前改以 `fs.realpathSync.native` 取得真實目錄，既有回歸測試加入傳入路徑斷言。此為可靠性修正，與已停用的 PowerShell opener 是不同問題；原始失敗及修正後結果以 CI 紀錄為準。
