# mattpocock/skills 上游同步評估與計畫

日期：2026-11-12（Asia/Taipei）。範圍：[mattpocock/skills](https://github.com/mattpocock/skills) 從本機副本基準 `3cca18b`（2026-09-04）到 main `4ae2317`（2026-10-31）之間的變更。狀態：**已核准並執行**（2026-11-12，D1–D4 全部採用建議）。以下保留評估當時的內容；實際交付、計畫外的發現與審查結果見 [同步歷程](../history/2026-11-12-upstream-sync.md)。

詞彙表改名（`d80fa0f`）與 setup 的舊檔偵測（`ed0de59` 的其中一段）已經同步，不在本次範圍內，紀錄見 [glossary-rename 歷程](../history/2026-11-12-glossary-rename.md) 與 `docs/agents/skill-sources.json` 的 `licensing.groups.mattpocock-skills.upstream_syncs`。

## 需要你決定的事

| # | 決定 | 建議 |
|---|---|---|
| D1 | 上游刪除了 `resolving-merge-conflicts`（`daa01d8`）。本機要不要跟著刪？ | **保留**。這個 skill 仍可使用，`docs/guide.md` 也列出了它。在 `skill-sources.json` 註記「上游已於 `daa01d8` 移除，本機保留 `3cca18b` 版本」 |
| D2 | `tdd` 要求每個 seam 註明「抓得到什麼、抓不到什麼」（`3f59913`）。本範本的 seam 已經記在 test plan table 裡，要放在哪裡？ | 寫進現有的 **Test intent** 欄位，`workflow.md` 的表格不新增欄位 |
| D3 | 「subagent 從全新 context 開始」（`7739eae`）在 Codex 樹要怎麼寫？ | 在 `runtime.md` 的 Codex 段落，把 stage 3 已有的 `fork_turns: "none"` 規則擴大到所有由 skill 啟動的 subagent；6 個 skill 各加一句短語指向這條規則 |
| D4 | 上游新增的 skill（`pr`、`retro`、`implement-spec`、`chief-of-staff`、`software-factory`）要不要納入？ | 這次不納入。其中 `retro` 可以配合 epic close-out，之後另外評估 |

核准這份計畫，就等於接受上表的建議；要改哪一項，直接指出編號即可。

## 方法

1. 把上游 clone 到 scratchpad。`git log 3cca18b..4ae2317` 共 94 個 commit，其中 46 個在 first-parent 線上。逐一列出每個 commit 改到的 `skills/<bucket>/<skill>/` 路徑，跟 `licensing.groups.mattpocock-skills.skills` 清單（23 個 skill）交叉比對。
2. 確認 CHANGELOG 1.3.0 的 patch 項目（`f02e2ed`、`4f28947`、`85f83d3`、`d419977`、`e6e9577`、`e3e547b`、`1dab982`、`594f0f8`）都已經是 `3cca18b` 的祖先，本機副本已經包含，不需要再同步。
3. 把每個相關 commit 的 patch 路徑改寫到 `.agents/skills/` 與 `.claude/skills/`，在兩棵樹的暫存副本上依時間順序執行 `git apply --reject`。哪些 hunk 能直接套用、哪些被拒絕，都以這次模擬的結果為準。
4. 被拒絕的 hunk 逐一閱讀本機檔案，判斷衝突是只差在 context，還是本機刻意改寫過（`runtime_trees.claude_prompt_audit`、`local_adaptations`、[Claude prompt audit](2026-09-26-claude-skill-prompt-audit.md)）。
5. 對 wizard 的 `template.sh` 在套用前後各跑一次 `bash -n` 與 `shellcheck` 0.11.0。

**上游 LICENSE 沒有變動**（`git diff 3cca18b 4ae2317 -- LICENSE` 為空），授權紀錄不需要更新。

## 逐項評估

分類：**同步**＝上游 hunk 原樣套用；**調整後同步**＝保留上游的意圖，改寫成符合本機改編的寫法；**不同步**＝不套用，理由見表中說明。「模擬」欄記錄 `git apply` 在該樹的結果。

### 影響已收錄 skill 的 commit

| 上游 commit | Skill／檔案 | Codex 樹 `.agents/skills/` | Claude 樹 `.claude/skills/` | 理由與衝突點 |
|---|---|---|---|---|
| `e0efb6e`、`8e67db2` | setup-matt-pocock-skills `issue-tracker-github.md` | 同步（模擬：乾淨） | 同步（模擬：乾淨） | 修正 `gh pr list --json authorAssociation` 一定失敗的 bug，改用 REST pulls endpoint。種子範本兩棵樹都跟上游基準完全相同 |
| `5b7cade` | setup-matt-pocock-skills `SKILL.md`、`issue-tracker-github.md`、`issue-tracker-gitlab.md`、`triage-labels.md` | 同步（乾淨） | 同步（乾淨） | 修正 `glab -F json`→`-O json`，`gh issue view` 改用 `--json` 讀取，並建立缺少的 triage label。本範本沒有安裝 `triage`，建立 label 的那段平常不會觸發，留著也無害 |
| `ed0de59`（舊檔偵測以外的部分） | setup-matt-pocock-skills `SKILL.md`、兩個 tracker 範本 | 同步（hunk 1 已同步，略過；其餘乾淨） | 同步（同左） | 寫入託管 tracker 之前先接好 remote、先留言再關閉 issue、讀取 PR body、**Blocking** 移到 Conventions、加上計算 open blocker 的指令、GitLab frontier 指令 |
| `59db609` | setup-matt-pocock-skills `issue-tracker-github.md` | 同步（乾淨） | 同步（乾淨） | 只在使用者自己的 repo 開 issue，避免 fork 預設把 issue 開到上游 |
| `cffab50`、`9e2abf8`（tracker 範本部分） | setup-matt-pocock-skills tracker 範本 | 同步（乾淨） | 同步（乾淨） | GitHub 範本補上 sub-issue 指令，wayfinder 的 child ticket 改為引用這條。GitLab 部分在 `9e2abf8` 已撤回，淨效果是零 |
| `cffab50`、`9e2abf8`（to-tickets 部分） | to-tickets `SKILL.md` | 同步（乾淨） | 調整後同步（模擬：hunk 1 被拒） | Claude 樹被拒，原因是 context 行已依 audit B7 改寫（frontier 那一行），只要手動放到同一段即可。「已用原生 edge 記錄 blocker 時，省略 `## Blocked by` 段落」與本機 `issue-tracker.md`「blocked 由 `blocked_by` 推導，不手寫第二份真相」的原則一致。建議在 `issue-tracker.md` 補一句：frontmatter 的 `blocked_by` 就是本 tracker 的原生 edge。sub-issue 在本機 markdown tracker 不會觸發 |
| `868c4cf`、`49dd158` | wizard `template.sh` | 調整後同步 | 調整後同步 | 兩棵樹都跟上游基準完全相同，模擬套用後與上游 HEAD 逐位元組一致，`bash -n` 也通過。但 `shellcheck` 會在 `ask()` 的 `$e[Enter keeps current]` 回報 **SC1087 error**；套用前只有一個 SC2034 warning。wizard 的 SKILL.md 要求對產生的腳本跑 `shellcheck`，所以同步時要改成 `${e}[Enter keeps current]`，並記入 `local_adaptations` |
| `f3fc563` | diagnosing-bugs `SKILL.md` | 同步（乾淨） | 同步（乾淨） | 用 mutation 製造紅燈時，先用 `diff` 證明 mutation 真的落地。不在 audit 改動範圍內 |
| `ad5400b` | teach `SKILL.md` | 同步（乾淨） | 調整後同步（hunk 1 被拒） | Claude 樹被拒，原因是 trailing context 的 `./reference/` 那行已依 audit 改寫，修改內容本身不衝突。workspace 根目錄的規則正好搭配 `domain.md`「不要在 repo 根目錄執行 `/teach`」的警告 |
| `95249b0` | grilling `SKILL.md` | 調整後同步（被拒） | 調整後同步（被拒） | 兩棵樹的 round 說明段都已改寫（Codex 批次與 audit B2），需要手動把「Word each question so "yes" accepts your recommended answer.」插在格式範例後面。跟 `➡️` 推薦答案的格式一致，沒有衝突 |
| `8295b8e` | wayfinder `SKILL.md` | 同步（乾淨） | 調整後同步（3 個 hunk 有 2 個被拒） | 共有三項：（1）map 與 ticket 不加 triage label；（2）交叉引用只用真實 id；（3）依 label 類型解決 ticket。這三項兩棵樹都適用。Claude 樹 step 5 已依 audit B4 改成透過 research skill 解決，沒有 throwaway branch，所以「push branch 但不開 PR」**不同步**；step 3 已有「依 ticket type 叫用 skill」，只補「從 type 欄位讀取，body 不會寫類型」。Codex 樹 step 5 仍是 throwaway branch，這跟 `issue-tracker.md`「research 結果存在 decision 旁」本來就不一致，這是既有問題，不在這次範圍 |
| `3da8c01` | code-review `SKILL.md` | 調整後同步（3 個 hunk 全拒） | 調整後同步（3 個 hunk 全拒） | 兩棵樹都已整份改寫。（a）tracker 改為「由 tracker doc 提供」：**不同步**，本機明確讀 `docs/agents/issue-tracker.md`，屬於專案設定。（b）搜尋所有記載程式碼規範的檔案，`CODING_STANDARDS.md`／`CONTRIBUTING.md` 存在時必須列入：調整後同步，改寫本機「Find applicable repository standards such as…」那一句。（c）兩個 subagent 同時發出、在前景等待回報後再彙整：調整後同步，Claude 樹寫成「同一則訊息啟動兩個 `harness-reviewer`，兩份報告都回來再彙整」 |
| `e48341a`、`04320ee` | implement `SKILL.md` | 調整後同步（被拒） | 調整後同步（被拒） | 本機已依 `local_adaptations.implement` 整份改寫。Claude 樹把「Use /tdd」「Use /code-review」改成「call the Skill tool with "tdd"／"code-review"」，兩者都是 model-invoked，可以這樣叫用。Codex 樹依 `runtime.md` 對照表寫成「load and follow the project `tdd`／`code-review` skill」 |
| `6d6a5b9` | implement `SKILL.md` | 調整後同步 | 調整後同步 | 改寫成：使用者給 ticket id 或路徑時，依 `issue-tracker.md`〈When a skill says "fetch the relevant ticket"〉讀取，開始前先說出標題；有歧義就問 |
| `3f59913` | tdd `SKILL.md` | 調整後同步（被拒） | 調整後同步（被拒） | 本機第 24 行是「For an unresolved seam, ask…」（`local_adaptations.tdd`）。依 D2，在問句後補上註記要求，並寫明註記放進 test plan table 的 Test intent 欄位 |
| `7739eae` | code-review、codebase-design `DESIGN-IT-TWICE.md`、improve-codebase-architecture、research、wayfinder、grilling | 調整後同步（依 D3） | **不同步** | 上游的理由是「部分 Codex 模型產生 subagent 時會 fork 父對話」。Codex 樹確實有這個風險，但 `runtime.md` 目前只在 stage 3 規定 `fork_turns: "none"`。Claude Code 的 Agent tool 預設從全新 context 開始，fork 要另外指定；而且 audit C2、C3、B3、B4 已經把 Claude 樹的委派縮到必要時才用，research 與 wayfinder 已經不再開 subagent。加這句在 Claude 樹只是多餘的文字 |
| `4f4e943`、`0f5e033` | handoff `SKILL.md` | **不同步** | **不同步** | 本機 handoff 寫入 `.proj.handoffs/`，並帶有 expires frontmatter（`runtime.md` 交接段），不使用 OS temp 目錄，所以上游的 temp 目錄解析規則用不到。可以考慮採用「告訴使用者檔案的絕對路徑」這一點，但不是必要 |
| `daa01d8` | resolving-merge-conflicts（整個刪除） | **不同步**（依 D1） | **不同步**（依 D1） | 上游的理由是 agent 不需要專用 skill 也能處理衝突。本機仍有 `docs/guide.md:30`、`THIRD_PARTY_NOTICES.md:26`、`skills-lock.json` 的引用，刪除的連動範圍比留著大 |

### 不影響已收錄 skill 的 commit

以下 commit 都**不同步**，原因是它們只改到本範本沒有收錄的 skill，或只改 repo 本身。

| 類別 | 上游 commit |
|---|---|
| 新 skill：`pr` | `d75dcf1` `4cfa4cd` `00cf26e` `1615268` `d2945f3` `73a3e94` `35f5926` `74ca5fe` `c55ee46` `a7d038f` |
| 新 skill：`retro` | `0243b6e` `6942bff` `ed975e9` `a7d038f` `389f5d2` `6b1cb1a` `8267225` |
| 新 skill：`implement-spec` | `153fc1b` `24f41cc` `a31f3f6` `c612def` `dc5cb3e` `a496f55` |
| in-progress：`chief-of-staff`、`software-factory`、`claude-handoff` | `e47c149` `4588b32` `7a030a8` `2b47ffc` `6fd9479` `5beb35b` `5ae4816` `4ae2317` `07b7105` `4ec00d9` |
| 未收錄的 `ask-matt`、`triage` | `9781ce1` `c5b9869` `954ee7f` `b645f47`（`d80fa0f` 也改到這兩個，但已排除） |
| repo 本身：文件、changeset、版本、issue 範本、CI、README | `006a52b` `b897f08` `93313df` `deb4a9c` `a600ef4` `b1f3390` `2aecca1` `984a2c0` `2629ffc` `d1478fc` `dfe7549` `423ed08` `f0588cd` `4d04daa` `542543a` `b0618bc` |

`pr` 跟 `tw-emoji-pr-note` 的職責重疊；`implement-spec` 一次跑完整份 spec、全部落在同一條 integration branch，跟 AGENTS.md「一張 ticket 一條 branch」的硬規則衝突。這兩個即使以後要評估，也需要先調整專案規則。

## 建議的同步批次

依 [Claude prompt audit](2026-09-26-claude-skill-prompt-audit.md) 的成本教訓，每批先跑確定性檢查，只有行為改動較大的批次才派一位 reviewer，最後由主 session 裁決，不跑多 agent 反駁。每批各用 `/tw-emoji-commit` 做一個 commit。

### 批次 1：上游 bug 修正，兩棵樹原樣套用

- 範圍：`e0efb6e` `8e67db2` `5b7cade` `ed0de59`（扣除已同步的 hunk）`59db609` `cffab50`／`9e2abf8` 的 tracker 範本部分，以及 `f3fc563`。
- 做法：用模擬時的路徑改寫 patch，依時間順序 `git apply`；`ed0de59` 的 setup `SKILL.md` hunk 1 已存在，排除。
- 檢查：兩棵樹對應檔案的 diff 應該完全相同（Claude 樹只多 `disable-model-invocation`）；`python3 scripts/verify-project.py`；`python3 -m unittest discover -s tests -v`。
- 不需要 reviewer。

### 批次 2：wizard 範本

- 範圍：`868c4cf` `49dd158`，加上本機的 `${e}` 修正。
- 檢查：兩棵樹 `bash -n`；`shellcheck` 不能有 error 等級的項目；用暫存 `.env` 手動跑一次 `write_env`／`_existing` 的往返（含空白、`'`、`$` 的值），確認 mode 為 0600。
- 紀錄：`local_adaptations` 新增 `wizard` 項目。

### 批次 3：只差 context 的手動定位

- 範圍：`ad5400b`（teach）、`cffab50`／`9e2abf8` 的 to-tickets 部分、`95249b0`（grilling），以及 `8295b8e`（wayfinder）的第 1、2 項與第 3 項的「讀 type」，兩棵樹都做。Codex 樹的 wayfinder 照上游原樣套用，含「不開 PR」。
- 另外在 `docs/agents/issue-tracker.md` 補一句：frontmatter 的 `blocked_by` 就是原生 edge。
- 檢查：verify-project；逐檔對照上游 hunk 與本機結果，確認沒有破壞 audit 的改寫。

### 批次 4：改寫成本機寫法

- 範圍：`3da8c01`（code-review 的 b、c 兩項）、`e48341a`／`04320ee`／`6d6a5b9`（implement）、`3f59913`（tdd，依 D2），以及 Codex 樹的 `7739eae`（依 D3，含 `runtime.md` Codex 段落）。
- 檢查：verify-project 與單元測試。派一位 `harness-reviewer`，檢查兩件事：意圖是否保留、跟 workflow gate 是否一致。在測試 repo 實際跑一次 `/code-review`，確認兩份報告都回來才彙整。
- 紀錄：更新 `local_adaptations` 的 `code-review`、`implement`、`tdd`；Claude 樹的改動補進 `runtime_trees.claude_prompt_audit` 的說明。

### 收尾（最後一個 commit）

- `skill-sources.json` 的 `upstream_syncs` 新增一筆：`on`、`checked_head: 4ae2317…`，`commits` 列出實際同步的 SHA，`not_synced` 列出 `4f4e943`、`0f5e033`、`daa01d8`，以及 Claude 樹的 `7739eae`，各附理由。如果 D1 決定保留，`resolving-merge-conflicts` 加註上游已移除。
- `skills-lock.json` 是 2026-09-08 安裝器的快照，維持不動。同步紀錄以 `upstream_syncs` 為準。
- `.tmpl.docs/history/` 新增同步歷程，連回本文件。

## 待確認與限制

- 模擬只證明 patch 的文字能不能套上，沒有驗證套用後的 agent 行為。批次 4 的行為檢查要在實際執行 skill 時才能確認。
- 評估時 `claude/glossary-rename` 還沒合併進 `main`。如果它在同步前被 rebase 或修改，批次 1 要重新跑一次模擬。
- Codex 樹的 wayfinder step 5 跟 `issue-tracker.md` 的 research 存放位置不一致。這是 audit 暫緩的「Codex 樹是否移植行為修正」的一部分，不在這次範圍。
