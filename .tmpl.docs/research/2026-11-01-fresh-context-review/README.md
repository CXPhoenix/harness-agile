# 全新上下文審查驗證協定

計畫與測試表已於本次對話獲使用者核准。這裡保存合成 fixtures 與執行證據，不是產品規格。

先執行一個基線案例，再逐軸加入必要資料及缺陷；每輪凍結輸入 bytes，第二輪只改 spec／traceability。Reviewer 只讀指定封包，不讀 evidence 或本 README 的測試解答。Parent-only marker 在 reviewer 結束前不寫入共用檔案。

證據須區分原生子代理、決策層注入報告、靜態／初始化／打包檢查。未取得原生 trace 的宿主標為未驗證。
