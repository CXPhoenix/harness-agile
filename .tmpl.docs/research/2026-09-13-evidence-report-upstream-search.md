# evidence-report 公開來源查核

> 目前狀態：來源與授權聲明已結案；完整聲明見根目錄 THIRD_PARTY_NOTICES.md 與 docs/agents/skill-sources.json。下方保留當時查核過程，「待確認」不代表現在仍待處理。

日期：2026-09-13。範圍：`.agents/skills/evidence-report/SKILL.md` 的來源與授權線索。此次沒有修改 skill 本文或替未知作者新增授權。

## 日誌查核更新

後續已找到實際建立與複製紀錄，見[session 來源查核](2026-09-13-evidence-report-session-provenance.md)。下方保留搜尋當時的結果；「建立來源不明」已由日誌證據取代，授權整理則另行處理。

## 維護者後續補充

2026-09-13，維護者回憶 evidence-report 應是使用其他 skill 從 artifact-design 改寫而來。此說明與搜尋線索相容；目前可記為「維護者回憶的改寫來源」，尚不能指定是哪個發行者、版本或授權。下方搜尋結果保留為補充前的查核證據。

同時，維護者明確確認 tw-emoji-commit、tw-emoji-pr-note、tw-emoji-release-note 與 init-template 均由其使用 Claude Code 撰寫。這四項已依維護者聲明記為專案自製，適用其指定的根目錄 MIT，不再列為等待維護者確認來源。

## 結論

**未找到整份相符的公開上游；但找到較早公開版本中的相似設計段落。來源仍未確認，不能把「搜尋不到整份」改寫為「自行原創」，也不能由相似文字直接判定侵權或複製方向。**

- 已驗證：本機 skill 與 2026-08-29 初始 commit `501c8a295b552bdfdef1b352e8ae366a4dfe2de7` 的 `.claude/skills/evidence-report/SKILL.md` 逐 byte 一致，皆為 4,932 bytes。SHA-256：`d3469822af2746394f7fcbd7629204f321bf295956fbffc20d1e0ddcad0d68bd`。
- 已驗證：此 checkout 不是 shallow clone；`git log --follow` 可追溯到初始 commit 與後續目錄搬移。初始及目前 `skills-lock.json` 均沒有 evidence-report 的上游安裝紀錄。
- 已驗證：另外九份同名 skill 已取得全文比對，沒有逐 byte 相符，也沒有命中此次選取的五個特徵字串；這不是語意相似度或所有歷史版本的完整鑑定。
- 外部證據：`interface-built-right` 的 artifact-design 在本專案初始 commit 之前，已包含相近的中性色選擇、單一視覺重點及避免制式 AI 設計描述。見下節。
- 尚未知：本專案是否自行編寫、由 AI 依內建指引產生、改寫第三方文件，或另有未公開來源。Git 提交者身分不能單獨證明作者與授權。

## 重要的新線索：設計段落

[tyroneross/interface-built-right 的初始 artifact-design](https://github.com/tyroneross/interface-built-right/blob/cc8de6fdd51859314cf8b658de645f9104a75284/skills/artifact-design/SKILL.md) 已於其 Git 紀錄的 2026-08-14 加入，早於本專案 2026-08-29 的初始 commit。

| 本機內容位置 | 比對結果 |
| --- | --- |
| Design 的 Pick the neutral | 關於略偏向主色的灰色會顯得經過選擇的描述，有連續相同措辭；上下文及句序不同。 |
| Design 的 Spend boldness once | 與上游只在一處使用強烈視覺、其餘保持安靜的原則相近；不是整段逐字相同。 |
| Design 的 Avoid the generated look | 列舉奶油色搭襯線字／陶土色、深色搭酸綠色、紫藍漸層、字型及排版慣例，排列與內容相近，但存在增刪及改寫。 |

該 repository 的[根授權](https://github.com/tyroneross/interface-built-right/blob/main/LICENSE) 宣告 Apache-2.0。其[引入 commit](https://github.com/tyroneross/interface-built-right/commit/cc8de6fdd51859314cf8b658de645f9104a75284) 說明此功能參考 Claude Code 內建 artifact-design／artifact-diagramming 概念，並稱其為自行實作；這是作者的來源敘述，不是本專案的複製證據。

另在[非官方文字鏡像](https://github.com/amangly/claude-instruct-4-8/blob/c69625b4b818726e18381fd6ae9eb289d688bc29/system-prompts-opus-4-8/skill-artifact-design.md) 找到類似段落。該鏡像只能作為文字相似線索，不能當成 Anthropic 官方授權或正式產品內容的證明。對 Anthropic GitHub 組織搜尋相同片語沒有命中，亦不能由此推論其未存在於產品中。

**不能直接補上這個候選的 Apache-2.0 就結案：尚未證明本專案取自該 repository，也未確認共同來源與權利鏈。**

## GitHub 程式碼搜尋

以目前帳號可存取的 GitHub code search API 查詢，可能包含本專案私人 repository；以下命中數不等於公開來源數。沒有完整掃描整個 GitHub，亦沒有比對全部分支與歷史。總數超過 100 的查詢只取得第一頁 100 筆，僅用於探索線索，不宣稱排除所有候選。

| 查詢 | API 回報總數 | 實際取回 |
| --- | ---: | ---: |
| `"Tier claims, not sentences"` | 1 | 1 |
| `"Spend boldness once"` | 114 | 100 |
| `"A report the user can audit"` | 3 | 3 |
| `"q1-pipeline-cadence.html"` | 1 | 1 |
| `"evidence-report" in:path filename:SKILL.md` | 31 | 31 |
| `"A grey biased slightly"` | 6 | 6 |
| `"Cream grounds" "terracotta"` | 210 | 100 |
| `"Every factual claim carries its source"` | 45 | 45 |
| `"Spend boldness once" "recommendation"` | 43 | 43 |

`Tier claims, not sentences` 與 `q1-pipeline-cadence.html` 各只命中本專案。`A report the user can audit` 另外命中 rnwolfe/skills 與 OrgMentem/zotio，取得全文後確認是不同上下文中的短句，不足以認定上游。

## 同名候選全文比對

以下候選都不是整份相符來源；相同名稱或一般性「主張須附證據」原則，不足以確認來源。

| Repository | 本次取得版本 | bytes |
| --- | --- | ---: |
| GongShichen/LuminaCode | [檔案](https://github.com/GongShichen/LuminaCode/blob/08c22817eb641870088a068677058d304044dbaf/.Lumina/TEAM/product-development/research/skills/evidence-report/SKILL.md) | 536 |
| EvianEvans/rumor-checker | [檔案](https://github.com/EvianEvans/rumor-checker/blob/8bac2e0b8922cab1e20ff49d7b57cb431f851a2b/skills/evidence-report/SKILL.md) | 6947 |
| Gonglitian/agent-skills | [檔案](https://github.com/Gonglitian/agent-skills/blob/7e030c34f5ff6807106ff12e485f3a36486588e3/skills/evidence-report/SKILL.md) | 6223 |
| lost-rob0t/starintel-auto-research | [檔案](https://github.com/lost-rob0t/starintel-auto-research/blob/d49f1e6e56cdbddd0843ad2c1c962c3ff758075f/skills/evidence-report/SKILL.md) | 1238 |
| Anders-planck/orditra | [檔案](https://github.com/Anders-planck/orditra/blob/9e72dbbd6a66e09bfbbf51c4ad1ac501b2ce1aec/skills/evidence-report/SKILL.md) | 969 |
| Mingkai406/CreatorPal | [檔案](https://github.com/Mingkai406/CreatorPal/blob/77d63395b693cd4c1b9a8bd4e15720318a82c3ed/creatorpal_agent/skills/evidence-report/SKILL.md) | 705 |
| aliciaa-20/devflow | [檔案](https://github.com/aliciaa-20/devflow/blob/3b26b31865e665aa87df357bc9f1a8efc54e5c24/.bob/skills/evidence-report/SKILL.md) | 4877 |
| JordanForeman/pi-agent | [檔案](https://github.com/JordanForeman/pi-agent/blob/c575ead0db8ac62f6bbf6c404979fea383cb0a1f/agent/skills/formats/evidence-report/SKILL.md) | 1102 |
| workshop-gbb/awesome-copilot-adventures | [檔案](https://github.com/workshop-gbb/awesome-copilot-adventures/blob/3d77eae7fa3dd72f70f486eac6c4ea01b205b181/labs/algora-skills/starter/.github/skills/evidence-report/SKILL.md) | 117 |

比對的五個特徵為 `Tier claims, not sentences`、`Spend boldness once`、`A report the user can audit`、`q1-pipeline-cadence.html` 與 `grilling convergence`。

## 搜尋引擎與獨立複核

主代理使用一般網頁搜尋及 GitHub API；獨立研究代理另查 12 組名稱／獨特語句／目錄限定查詢，包括 skills.sh、SkillsMP、mattpocock 與繁體中文關鍵字。獨立搜尋沒有找到整份相符上游。

- [mattpocock/skills README](https://raw.githubusercontent.com/mattpocock/skills/main/README.md)：本次取得的技能清單未列 evidence-report。沒有全面排除上游歷史或改名來源。
- [zero-api-key-web-search](https://github.com/wd041216-bit/zero-api-key-web-search)：從 cross-validated-search 重新導向；evidence-report 是其舊版 CLI alias，與本機離線 HTML skill 不同。
- Skills.sh 查詢頁擷取與研究代理的 GitHub 搜尋頁擷取失敗，不能記為零筆結果。主代理後來另透過 GitHub API 成功取得上述結果。
- 搜尋引擎可能寬鬆匹配或未收錄私人／已刪除／新檔案。上述結果只能代表此次可見證據。

## 對公開判定的影響

維持「來源待確認」，並新增「設計段落有外部相似內容」的具體線索；不是已確認缺哪一份 LICENSE，也不是侵權判定。

可收斂的下一步是核對建立本 skill 當時的對話或匯入紀錄；若能確認來源，依實際來源補齊條款。若無法釐清，維護者可決定移除或另行撰寫可追溯的替代版本；本次尚未執行這些變更。
