# Archify 驗證修正

新增 archify 後，範本檢查因缺少 Codex metadata 失敗。補上 agents/openai.yaml，並在 docs/agents/skill-sources.json 記錄本機調整，保留上游的隱含呼叫政策。Claude 既有相對連結會共用這份 metadata。

清除未納入 Git 的 .agents/skills/.DS_Store；既有 .gitignore 已排除此檔案，驗證器仍維持禁止攜入本機暫存檔的檢查。若 Finder 再次產生此檔，仍需清除後驗證。

更新 tests/test_bootstrap.py 的三處固定數量：預設初始化為 31 個 skills，保留範本檔案時為 32 個。

驗證：python3 scripts/verify-project.py 通過；python3 -m unittest discover -s tests -v 的 22 項測試全數通過；git diff --check 通過。這些結果涵蓋本機範本結構與初始化流程，未驗證 archify 圖表功能或新工作階段的實際 skill 探索。
