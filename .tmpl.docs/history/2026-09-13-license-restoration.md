# MIT 與第三方授權補齊

> 目前狀態：來源與授權聲明已結案；完整聲明見根目錄 THIRD_PARTY_NOTICES.md 與 docs/agents/skill-sources.json。下方保留當時查核過程，「待確認」不代表現在仍待處理。

使用者於 2026-09-13 指定本專案使用 MIT，並要求搜尋缺少的第三方授權。本次採用該決定，保留第三方原有條款；未修改 Windows opener、未 commit、未 push、未切換 public。

## 內容

- 根目錄新增 `LICENSE`（Copyright (c) 2026 CXPhoenix）及 `THIRD_PARTY_NOTICES.md`；中英文 README 與 npm／Python metadata 同步採 MIT。
- 23 個 `mattpocock/skills` 的各自目錄附上完整 MIT LICENSE，保留 Matt Pocock copyright。
- `i-have-adhd` 找到 ayghri/i-have-adhd 來源，附上 Ayoub Ghriss 的 MIT LICENSE。比對確認共同正文，保留本機 metadata 與舊版本規則差異，沒有趁補授權更新行為。
- `agent-browser` 與 vercel-labs 上游正文比對，附上 Apache-2.0 LICENSE，並在已修改的 SKILL.md 加上醒目的修改聲明。核對版本的上游根目錄沒有 NOTICE 檔案。
- Archify／security-review 既有 MIT、Archify 第三方 notices 及字型 OFL 原樣保留。
- 來源 URL、查核 revision 與授權檔 SHA-256 保存於 `docs/agents/skill-sources.json`。這些是授權查核版本，不冒充本機 skill 的原始安裝 revision。
- Python bundle、npm files 與 Python license-files／sdist 清單納入授權交付；產品 README 說明沿用範本的 MIT 與第三方條款，新增產品內容的授權由產品維護者決定。

## 尚待來源確認

`evidence-report` 只能追溯到初始 commit 501c8a2；公開網頁與 GitHub code 的獨特段落搜尋未找到上游。已詢問維護者是否為自行撰寫／本專案產生。搜尋沒有結果不能證明原創，故以待確認保存，不自行套用他人的名字或授權。

`tw-emoji-*`、`init-template` 沿用既有本機／專案來源紀錄；根 MIT 只授予維護者有權授予的部分，不將此視為所有本機來源都經過獨立著作權鑑定。

## 驗證

- skills 同步與結構檢查通過；22 項既有 Python tests 全數通過（本機 Python 3.14.3，macOS）。
- 暫存副本成功建置 sdist，並從 sdist 建置 wheel；npm tarball 成功。
- wheel metadata 宣告 `License-Expression: MIT`，另有 31 個可直接讀取的授權／聲明檔案。
- 31 個檔案逐 byte 比對：sdist、wheel metadata、wheel template bundle、npm tarball、預設初始化、`--keep-template-files` 初始化均保留一致內容。
- `scripts/verify-distributions.py` 的 uvx、npx、pnpx 入口全通過；兩種 skill transport 均有涵蓋。
- 本次沒有遠端 CI 新結果，既有 main 的 CI 不能當成本次未提交內容的 CI。

Windows 風險的操作矩陣、信任邊界與證據限制另見 [深入識別](../research/2026-09-13-windows-opener-risk.md)。授權補齊不代表該安全問題已修正，也不代表所有第三方素材均已取得不限用途的權利。

後續變更：同日已依使用者要求停用 Windows opener；上文「未修改」描述授權補齊當時的範圍。目前狀態見[停用公告](../../docs/security/windows-opener.md)。

後續來源確認（2026-09-13）：維護者確認 tw-emoji-* 與 init-template 由其使用 Claude Code 撰寫，記為專案自製 MIT；evidence-report 則回憶由 artifact-design 改寫，原始發行者、版本與條款仍待確認。此補充取代上文等待維護者說明的舊狀態。
