# CodeGraph code map

[CodeGraph](https://github.com/colbymchenry/codegraph) (MIT) indexes the repository
into a local graph of symbols, calls and imports in `.codegraph/`. The usage rule
lives in `AGENTS.md` (Code map): when `.codegraph/` exists, query it before grep or
broad file reads, and read a file directly before editing it or citing it. This page
covers setup, privacy and removal. Installing the CLI, building the index and
removing a registration are the user's call; an agent reports what it found and
leaves those steps to the user.

Verified 2026-11-18 with CodeGraph 1.6.2 on a local machine; the latest npm release on
that date was 1.6.3. Upgrade, daemon, worktree and `codegraph.json` behaviour was
re-checked 2026-11-19 against the installed 1.6.2 package. Re-check the sources below
before relying on newer versions.

## What ships

| File | Used by | Takes effect |
| --- | --- | --- |
| `.mcp.json` (`mcpServers.codegraph`) | Claude Code | After you approve the project server when Claude Code asks |
| `.codex/config.toml` (`[mcp_servers.codegraph]`) | Codex | After the project is trusted locally |
| `codegraph.json` | CodeGraph CLI and server | On the next `codegraph init`, `index` or `sync` |

Each runtime reads only its own registration. Both start `codegraph serve --mcp` over
stdio with `DO_NOT_TRACK=1` and `CODEGRAPH_TELEMETRY=0`.

`codegraph.json` excludes the two skill trees (`.claude/skills/`, `.agents/skills/`):
they are per-runtime copies of the same skills, and their helper scripts crowd
first-party code out of results (this template indexed 383 files without the
exclusion, 32 with it). `exclude` takes gitignore-style paths from the repository
root. The file is committed, so a change applies to every collaborator; re-run
`codegraph index` after editing it.

Migrating a project whose `.mcp.json` or `.codex/config.toml` differs from the
template leaves `<file>.harness-new` beside it: copy the `codegraph` entry into your
`mcpServers`, or the `[mcp_servers.codegraph]` table with its `env` into your
`config.toml`, then delete the sidecar.

## Install the CLI (per machine)

- Recommended: `npm install -g @colbymchenry/codegraph@<version>`, pinned to a tested
  version. The npm package is a launcher: the CLI and the MCP server run on a Node 24
  runtime bundled in a per-platform package, so the system Node only runs npm and
  the launcher.
- Before the first `codegraph init`, turn telemetry off for shell use: run
  `codegraph telemetry off` once, or `export DO_NOT_TRACK=1` in that shell. The
  shipped `env` covers only the MCP server; shell commands record telemetry, and
  `init`, `index`, `sync`, `uninit` and `upgrade` send it right away.
- Upgrade with the same `npm install -g @colbymchenry/codegraph@<version>`, then
  re-run `codegraph index`. Run `codegraph upgrade` and `codegraph install --refresh`
  only outside this repository: in 1.6.2, `codegraph upgrade` runs
  `codegraph install --refresh` in the current directory, which rewrites the
  CodeGraph entries in `.mcp.json` and `.codex/config.toml` without the shipped
  `env` and writes CodeGraph sections into `AGENTS.md` and `.claude/CLAUDE.md`.
  `CODEGRAPH_NO_INSTALL_REFRESH=1` skips that refresh. If it already ran here, check
  `git diff`, restore the files with
  `git checkout -- .mcp.json .codex/config.toml AGENTS.md` (this also discards your
  own uncommitted edits to them) and delete a `.claude/CLAUDE.md` it created.
- Upstream also offers a standalone `curl | sh` (PowerShell on Windows) installer.
  It runs a remote script, so using it is the user's call.
- Skip `codegraph install`. Its local mode rewrites the root `AGENTS.md`,
  `.claude/CLAUDE.md` and `.claude/settings.json` and adds a `UserPromptSubmit` hook,
  which conflicts with this project's file ownership. To compare its configuration
  with the shipped one, run
  `codegraph install --print-config <claude|codex> --location local`, which only
  prints; without `--location local` it names a global file. The printed snippet has
  no `env` (the Claude one adds `alwaysLoad: true`), so keep the shipped entry rather
  than pasting the snippet over it.

## Build and maintain the index

- With telemetry off (above), `codegraph init` at the repository root creates
  `.codegraph/`. The root `.gitignore` excludes `/.codegraph/`; never commit it. An
  index directory under another name, such as `.codegraph-wsl/` (a WSL project on a
  Windows drive) or a `CODEGRAPH_DIR` value, is not covered by that line; add it to
  `.gitignore` yourself.
- The MCP server starts one shared background daemon per project. The daemon watches
  files and keeps the index current. It runs detached from the client and exits about
  5 minutes after the last client disconnects. `codegraph daemon` lists running
  daemons with their pids and, in a terminal, stops the one you pick.
- In CI, sandboxes, or when the watcher is off, run `codegraph sync`. Check state with
  `codegraph status`.
- Worktrees: a git worktree's repository root is its own root. A nested worktree
  (`.claude/worktrees/`, `.worktrees/`) without its own `.codegraph/` gets the main
  checkout's index, files and line numbers, which can belong to another branch; the
  MCP result carries no warning. `codegraph status` run there reports that the index
  belongs to a different git working tree. Agents skip CodeGraph in such a worktree
  (`AGENTS.md`); a worktree-local index needs `codegraph init` at the worktree root.

## Privacy

- The index and every query stay on the local machine.
- Upstream telemetry is on by default. The shipped configs set `DO_NOT_TRACK=1` and
  `CODEGRAPH_TELEMETRY=0` for the MCP server; `DO_NOT_TRACK=1` also stops the daily
  GitHub update check.
- `codegraph telemetry off` saves the choice in the user's CodeGraph config, which
  every CodeGraph process on the machine reads unless one of these variables
  overrides it, including a project daemon that another MCP host started without
  them. An exported `DO_NOT_TRACK=1` covers only processes that inherit it.
- Keep telemetry control in `env`. CodeGraph 1.6.2 rejects `--no-telemetry` on
  `serve` (`unknown option`), and the server then fails to start.
- `scripts/verify-project.py` does not check these variables; keep them when you
  edit an entry.

## Subagents and tools

- Claude Code roles in `.claude/agents/` list only `mcp__codegraph__codegraph_explore`
  in `tools`.
- Codex subagents inherit the parent session's MCP servers.
- The server exposes only `codegraph_explore` by default; `CODEGRAPH_MCP_TOOLS` in the
  server's `env` enables more. When you enable one, also add its
  `mcp__codegraph__codegraph_<name>` entry to `tools` in `.claude/agents/*.md`;
  otherwise only the main Claude session can call it.

## When the code map is unavailable

- **CLI installed, no index.** The server connects and lists `codegraph_explore`; a
  call replies "No CodeGraph project is loaded for this session." Work with normal
  file reads and mention that the user can run `codegraph init`. Leave the shipped
  MCP config as it is: the reply suggests adding `--path`, which would commit a
  machine-local path.
- **CLI missing or not on the host's PATH** (a host started from a GUI may lack the
  shell's PATH). The server fails to start, and Claude Code lists it as failed. Work
  continues without the code map; mention the failed server once. Installing the CLI
  or removing the registration is the user's call.

## Remove CodeGraph

The user runs these steps; an agent describes them and leaves the registration in
place. Removing your runtime's registration is also how to decline CodeGraph: the
`AGENTS.md` reminder stops once it is gone.

1. Delete the `codegraph` entry from `.mcp.json` (or the whole file if it holds
   nothing else) and the `[mcp_servers.codegraph]` table from `.codex/config.toml`.
   `codegraph.json` can go too.
2. Close the Claude Code and Codex sessions that use the server. The daemon exits
   about 5 minutes after the last one disconnects; to stop it sooner, run
   `codegraph daemon` and pick this project, or stop the pid it lists.
3. Run `codegraph uninit` (it asks before deleting `.codegraph/`) or delete
   `.codegraph/` yourself. Neither stops a running daemon.
4. Optionally uninstall the CLI: `npm uninstall -g @colbymchenry/codegraph`.

Keep the `/.codegraph/` line in `.gitignore`; it is harmless without the server.

## Unverified

- Whether Codex `network_access = false` affects the MCP server process.
- Whether a sandboxed shell fallback (`codegraph explore` from a Codex shell) can
  write `~/.codegraph`.
- How Codex reports a registered server whose CLI is missing.
- Whether the bare `codegraph` command starts the server on native Windows, where an
  npm global install puts a `codegraph.cmd` shim on PATH. If it fails there, override
  the entry in a local or user-scope config (not the committed file) with
  `"command": "cmd", "args": ["/c", "codegraph", "serve", "--mcp"]`.
- Whether a Claude role starts while `mcp__codegraph__codegraph_explore` in its
  `tools` cannot resolve (server not approved, or failed). Read, Glob and Grep always
  resolve; roles without a shell fall back to them.

## Sources

Checked 2026-11-18, and the installed 1.6.2 package on 2026-11-19:

- README: https://github.com/colbymchenry/codegraph
- Telemetry: https://github.com/colbymchenry/codegraph/blob/main/TELEMETRY.md
- npm package: https://www.npmjs.com/package/@colbymchenry/codegraph
