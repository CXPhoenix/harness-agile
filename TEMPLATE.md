# harness-agile-template

一套給 Claude Code 用的專案工作流範本：**spec 驅動、adversarial review 把關、TDD 實作、每個 epic 交付一次可運作的軟體**。

複製這個目錄，跑一次 init，就可以開始。這份 `TEMPLATE.md` 在 init 之後會被刪除。

---

## 開始使用

```bash
cp -R harness-agile-template my-project    # 或 git clone
cd my-project
```

然後在 Claude Code 裡打：

```
/init-template
```

它會問你兩件事（專案名稱、一句話描述），填掉 placeholder，並刪除範本專用檔案。

不想透過 skill 的話，直接跑腳本：

```bash
python3 scripts/init-project.py --dry-run --name "My Project" --one-liner "它做什麼。"
python3 scripts/init-project.py           --name "My Project" --one-liner "它做什麼。"
```

init 完成後的下一步是 `/grill-with-docs`，把 `CLAUDE.md` 的 Project Charter 寫出來。**Charter 沒寫完之前，`CLAUDE.md` 的守門規則會擋住所有 spec、開票與實作**，只允許 walking skeleton。

---

## 這個範本給你什麼

**一條九階段管線**（`CLAUDE.md` 有總表，`docs/agents/workflow.md` 有全文）：

```
grill → spec → adversarial review → tickets → TDD 實作 → code review → security review → e2e → merge
```

**一個交付節奏**：以 **epic** 為單位，一個 epic = 一份 spec = 跑一次管線 = 一個可展示的增量。第 0 輪先做 **walking skeleton**（最薄的端到端貫穿），刻意不寫 spec、不做 review，因為兩者都需要 seam 當輸入，而空 repo 沒有 seam。

**四個關鍵閘門**，每個都有明確的通過條件：

| 閘門 | 通過條件 |
|---|---|
| spec | traceability matrix 每一列都對到一條 AC |
| adversarial review | P0 findings 歸零，最多兩輪 |
| 實作 | 測試計畫表經使用者確認後才動筆寫測試 |
| 收尾 | 涵蓋率報告表 + 跨票的漏洞鏈分析 |

**幾個防退化的機制**：adversarial review 用 frozen prompt（第二輪逐字重播第一輪，避免評分標尺逐輪升高）；ticket 狀態存 frontmatter 而非目錄（避免搬檔造成的引用斷裂與 merge conflict）；spec 雙語以 `synced_from_sha` 做可機檢的同步偵測。

理由都寫在 `docs/adr/` 的三份 ADR 裡。

---

## 目錄結構

```
CLAUDE.md                  管線總表、硬規則、Charter 守門
docs/agents/
  workflow.md              九階段全文
  issue-tracker.md         spec / ticket 的存放與格式
  review.md                adversarial 四軸 + security 兩段式
  language.md              en / zh-TW 分工與雙語同步
  domain.md                CONTEXT.md 與 ADR 的取用方式
docs/adr/                  三份工作流 ADR
.proj.specs/               spec、追溯矩陣、review 紀錄、證據報告
.proj.tickets/             ticket，狀態存 frontmatter
.claude/skills/            專案 skills
.agents/skills/            mattpocock/skills 的 21 個 engineering / productivity skills
```

---

## 隨附的 skills

**自動可呼叫**

- `evidence-report` — 產出 standalone HTML 證據報告，每條主張標註「已驗證 / 推論 / 外部」三級
- `init-template` — 這份範本的 init（跑完會自我刪除）
- `.agents/skills/` 底下的 `tdd`、`code-review`、`codebase-design`、`diagnosing-bugs`、`domain-modeling`、`prototype`、`resolving-merge-conflicts`、`wizard`、`writing-for-agents`

**需要你手動呼叫**（`disable-model-invocation`）

- `grill-with-docs`、`grilling`、`grill-me`、`to-spec`、`to-tickets`、`implement`、`handoff`、`teach`、`wayfinder` 等
- `i-have-adhd` — 輸出風格，會鎖定整個 session，刻意保留為手動觸發

`i-have-adhd` 與 `agent-browser` 是以 `skill-mirror` vendor 進來的複本，內容未修改。你機器上若有原始來源，`skill-mirror status` 會回報是否落後 upstream。

---

## 需要你自己補的東西

範本刻意不預設技術棧，以下幾處要依專案填：

1. **`CLAUDE.md` 的 Project Charter** —— 用 `/grill-with-docs` 寫。
2. **`CLAUDE.md` 的 Build and test commands** —— walking skeleton 建立工具鏈之後填。
3. **非瀏覽器 surface 的 e2e harness** —— `/agent-browser` 只能驅動 Chrome/Chromium 與 Electron。原生客戶端、daemon、CLI、遊戲 server 都需要專案自備 harness。決定之前先記進 `.proj.specs/OPEN-QUESTIONS.md`。
4. **領域特有的 security finding 分類** —— 若你的專案本身就會刻意包含漏洞（資安靶場、教學用脆弱環境、紅隊標的），必須在第一次 security review 之前，於 `docs/agents/review.md` 寫明「刻意的」與「意外的」如何區分，並記成 ADR。沒有這條規則，每張票都會被自己的標的擋住。

---

## 需要的外部工具

| 工具 | 用在哪 | 沒有的話 |
|---|---|---|
| `/tw-emoji-commit` `/tw-emoji-pr-note` `/tw-emoji-release-note` | commit / PR / release 文案 | 管線的硬規則 5 要求停下來回報，不得自行撰寫 |
| `agent-browser` CLI | 階段 8 的瀏覽器 e2e | 只能驗證非瀏覽器 surface |
| `chrome-devtools-mcp` | a11y 檢查 | 請使用者安裝，或跳過 a11y |
| `skill-mirror` | 追蹤 vendored skill 的 drift | vendored 複本仍可用，只是無法 sync |
