# Fixture 依賴

21 份正式來源以原始 bytes 複製，逐檔 SHA-256 見 fixture-dependencies.json。包含 AGENTS、runtime／codex／drift-report／language／domain／workflow／review／issue-tracker、skill-sources、適用 ADR、.tmpl.docs/README／contributing／CONTEXT、EGM SKILL／metadata／LICENSE，以及原始 project config。

8 份新合成比較資料是 ops 下 5 份 Markdown 與 src 下 3 份 Python，涵蓋 current／planned／history／match。未執行合成原始碼。輸入封存為 fixture-inputs.tar.gz，排除 .git；測試 oracle 位於證據根，未進入 fixture 或任何模型 prompt。

歷史導覽連結只是可選來源，不遞迴複製舊報告。Stage 3 role／spec／matrix／frozen prompt 屬 C 批，明確不適用；產品規格及票單 gate 不適用此次母範本證據維護。若後續模型發現真正必要依賴缺漏，仍須標記 fixture_invalid，不能據此靜態清單推定有效。

控制端 I/O 探針保留於預定報告父目錄並納入前後 inventory；它不是模型產生的 EGM 報告。
