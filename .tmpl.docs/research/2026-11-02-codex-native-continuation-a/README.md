# Codex 原生續測 A 批：受預算停止

A 批已停止並交付證據；R01／R02 沒有啟動，未建立有效可寫控制組。執行日期為 2026-11-02（Asia/Taipei）。核准範圍來自本次啟動指示；原計畫的「待核准」歷史文字保留。

- 實際 CLI 模型測試：**0／3**；只執行 R00 無模型查核與新 fixture 建置。
- 已確認：CLI 0.161.0；新 fixture 的 project config 因未取得 trust 而被原生載入器停用。
- 未確認：codex exec 最終 sandbox、managed policy、CLI 實際寫入／拒絕，以及上一批無法落盤的完整根因。
- 停止原因：控制對話首次可見累計 input 741,189，超過 700,000 配置；結案用量與截止後缺失見 budget.md。

## 證據入口

- [coverage](coverage.md)：R00–R02 的結果與範圍。
- [設定與根因界線](capabilities.md)：已知／未知、實際 argv/cwd 與下一步。
- [fixture 依賴](fixture-dependencies.md)／[逐檔 hashes](fixture-dependencies.json)／[輸入封存](fixture-inputs.tar.gz)。
- [用量](budget.md)／[原生用量節錄](controller-usage-cutoff.json)。
- [原生無模型 stderr 與設定介面結果](app-server-config-selected.json)、[prompt-input 結果](prompt-input-selected.json)、[設定來源選定欄位](settings-files-selected.json)。
- [完整性查核](checks.json)、source-before.json、fixture-before.json、fixture-after.json 與 manifest.json。

新暫存複本：`/private/tmp/codex-continuation-a-b_xd1q1u`。預定輸出父目錄：`.tmpl.docs/research/drift-reports/`。只保存控制端無害探針；沒有模型報告或原生模型 trace，原因是沒有啟動模型。原生無模型訊息按實際結果保存，不將控制端寫入當 CLI 證據。

原正式來源、既有未提交草稿、原計畫與上一批證據的 hashes 均核對；結果見 checks.json。本次只新增此證據目錄及暫存複本，未執行無關整套測試，沒有變更正式程式或 gates。沒有延伸 B／C 或 Claude。
