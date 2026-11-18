# 設定來源與根因界線

- CLI 0.161.0；入口為 `/Users/phoenix/.local/bin/codex`，連至 `/Users/phoenix/.codex/packages/standalone/current/bin/codex`。
- 新 fixture cwd：`/private/tmp/codex-continuation-a-b_xd1q1u`。未選 profile，沒有 model／effort／sandbox／approval override。實際無模型 argv 見 prompt-input-selected.json 與 app-server-config-selected.json；沒有實際 codex exec 測試 argv。原預定條件是 `codex exec --ephemeral --json -`，cwd 與輸出父目錄固定於此複本。
- 全域設定選定值為 model=gpt-6.1-sol、effort=high；它們只是設定來源。因未啟動 CLI 模型，原生 CLI 實際 model／effort 皆未觀察。控制對話的原生 turn_context 另列於用量封包。
- 正式 checkout 的 trust 紀錄為 trusted；新 fixture 沒有適用紀錄。app-server stderr 明確說明新 fixture 的 project-local config、hooks 與 exec policies 因未取得 trust 而停用，skills 仍可載入。這證明此次設定層被略過，不證明最終 sandbox 為 read-only。
- fixture 的 config bytes 宣告 workspace-write；不能當作有效權限證據。父控制端的 UTF-8 exclusive-create／讀回成功，也不能證明 CLI 可寫。
- debug prompt-input 與 app-server 啟動均出現 Operation not permitted (os error 1)。app-server 未完成 initialize，未取得 config/read、configRequirements/read 回覆。此拒絕沒有指認報告寫入，不能抵用 R01 或 write-denial 測試。
- `/etc/codex/config.toml`、requirements.toml、managed_config.toml 均未發現；這不排除 MDM、雲端或宿主政策。managed policy 與 codex exec 最終有效 sandbox 仍為 unknown。
- 沒有修改 trust、sandbox、approval、正式或全域設定，沒有登入、模型 override、子代理、其他 chat、ticket、commit、PR、tag 或發布。

## 最小下一步選項

1. 先改善控制對話的可觀測用量與啟動封包，再另外核准新額度；此次不能自動續測。新對話仍可能包含大量宿主注入，不能只憑對話長度推算 token。
2. 維持原政策，在可取得有效設定與 managed requirements 的原生介面完成無模型查核；不以換 cwd／宿主掩蓋本次問題。
3. 只有未來證據證明需要 trust 變更時，另提供僅針對此暫存複本的最小差異及移除方式供審閱；本次沒有提出或實施設定寫入。

官方文件指出 project config 需要 trust，並記載 config/read 與 configRequirements/read 可查設定／限制；本機實測未取得這些回覆，文件不能替代有效政策證據。來源：[設定優先序](https://learn.chatgpt.com/docs/config-file/config-basic)、[App Server](https://learn.chatgpt.com/docs/app-server)。
