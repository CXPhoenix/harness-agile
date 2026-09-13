# evidence-report 建立日誌查核

> 目前狀態：來源與授權聲明已結案；完整聲明見根目錄 THIRD_PARTY_NOTICES.md 與 docs/agents/skill-sources.json。下方保留當時查核過程，「待確認」不代表現在仍待處理。

日期：2026-09-13。維護者明確授權查看建立本專案的 Claude Code session log。本報告只保存與 skill 來源相關的事實摘要，不複製完整對話或其他專案內容。

## 結論

已找到實際建立紀錄，取代先前僅依公開搜尋與維護者回憶的狀態。evidence-report 由 Claude Code 在維護者核准後寫入原始專案，再隨專案複製成此範本。寫入內容與目前檔案逐 byte 一致。

直接的設計來源紀錄指向 phoenix-design；同一段工作也曾呼叫 artifact-design。因此，不能簡化成「從某個網路同名 artifact-design repository 複製整份 skill」，也不能當成未受其他材料影響的純原創。

## 可稽核證據

原始 session 識別保留在維護者本機。它歸在原始專案的日誌目錄，並非以 harness-agile-template 命名的 session 目錄。以下時間為日誌 UTC；行號為原始 JSONL 行號。

| 行號 | 時間／紀錄 | 與來源的關係 |
| --- | --- | --- |
| 145、156、158 | 2026-08-29 14:08:36 起，呼叫 artifact-design、成功載入並提供 skill 內容 | 證明這個 skill 曾供當次工作使用；未提供可據以判定授權的官方發行版本。 |
| 219、221、231、233、236、238 | 14:26 起，讀取本機 phoenix-design 的 SKILL.md、目錄及指定段落 | 確認實際參考來源，而非只靠同名搜尋。 |
| 242 | 提議將 phoenix-design 的可攜設計原則精簡寫入 evidence-report，避免納入整套媒體與 references | 原始設計決策。 |
| 254 | 維護者同意 Round 3 建議，另排除一項無關 ADR | 該精簡方案獲准。 |
| 364、367 | 14:38:58 寫入 evidence-report；隨後工具回報建立成功 | 取得原始生成內容，與目前 skill 比對。 |
| 508 | 提交說明明列設計來源 phoenix-design、採精簡內嵌 | 與較早讀取及核准紀錄相互支持。 |
| 602 | 15:06:13 將原始專案複製為 harness-agile-template，排除原 Git | 確認進入範本的途徑。 |

原始寫入、初始 commit 與目前 SKILL.md 均為 4,932 bytes，SHA-256 為 `d3469822af2746394f7fcbd7629204f321bf295956fbffc20d1e0ddcad0d68bd`。

## 授權仍需分開確認

目前本機 phoenix-design 的 LICENSE 指向 alchaincyf／huashu-design，仍保存較早的 Personal Use License；這不是 2026-08-29 當時 LICENSE 的完整歷史快照。

本次即時核對 [huashu-design 官方 LICENSE](https://raw.githubusercontent.com/alchaincyf/huashu-design/master/LICENSE) 已為 MIT；[官方 README](https://github.com/alchaincyf/huashu-design/blob/master/README.en.md) 記載自 2026-05-14 改採 MIT。因此，不應僅依本機舊 LICENSE 宣稱上游目前禁止商用。

來源建立鏈已釐清；後續授權整理應針對實際使用的 phoenix-design／huashu-design 內容、版本及所需聲明進行，並區分 artifact-design 的實際使用與檔案內容沿用。此次沒有把網路上另一份 Apache-2.0 同名檔誤掛成直接來源，也未因找到建立日誌就宣稱全部第三方條款均已結案。

## 結案（2026-09-13）

依維護者指示，完成來源歸屬與聲明補齊後結案。evidence-report 內附 huashu-design 官方 MIT 全文，第三方聲明記錄 phoenix-design → huashu-design 的設計來源；版本與 SHA-256 記於 skill-sources.json。核對版本不冒充當時安裝版本。此結案範圍是來源及必要聲明整理，不是每一段生成文字的獨立法律鑑定。
