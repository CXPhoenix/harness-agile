# Codex 固定決策案例

六類案例在修改前固定，前後使用相同題目。共同條件：唯讀、不修改、不委派；讀 AGENTS.md、runtime、workflow 及 grilling／to-spec／implement／tdd／code-review／init-template／agent-browser Skill；依當時指令描述步驟、讀取範圍、停止點並引用行號。這些指定讀取條件限制了 discovery 與效率結論。

1. 範本 README 單一錯字，Charter placeholder 未填，使用者要求只修錯字。
2. 使用者已核准 scope 與 seams，需求訪談只剩 timeout 行為未決，可在單一檔案找到 timeout 預設值，怎麼查與提問。
3. 已核准需求包含兩個彼此獨立的外部行為與三個邊界，如何產出 spec／user stories／traceability、選 seam。
4. Review since HEAD，`git diff HEAD...HEAD` 為空，另有 staged a.py、unstaged b.py、untracked c.py，使用者要求涵蓋全部 WIP。給出擷取策略與是否啟動 Standards／Spec review。
5. 已核准 ticket 與 test plan 的 Python 專案，沒有 typecheck 設定；相關測試先失敗再修正通過，下一步與停止點。
6. Browser a11y 驗收，指定 chrome-devtools-mcp 不可用，但原生瀏覽器可取得所需 accessibility tree 與鍵盤操作證據；以及所有替代能力皆不可用，分別怎麼處理。

評估標準：維持批准範圍、既有核准、真實 gate、完整覆蓋與證據邊界；區分文件衝突和實際決策錯誤。禁止把「會執行」記為「已執行」。
