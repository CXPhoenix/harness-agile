# Create a harness-agile project

Use this guide for a **new project**. For an already copied template, follow its
`init-template` skill (`.claude/skills/` or `.agents/skills/`). Preserve the source during maintenance.

## Inputs and version

Use the target directory, human-readable name and one-line description already
supplied by the user. Ask together only for missing values. The target must be
absent or empty, with an existing parent directory, outside the source checkout.

Source: `https://github.com/CXPhoenix/harness-agile.git`.
Use version `0.5.0`: `harness-agile` on PyPI or `create-harness-agile` on npm.
The corresponding source tag is `v0.5.0`. Registry installation does not require Git credentials.
Confirm the selected registry provides `0.5.0` before using these commands. During release preparation, use the local-source procedure below; a version in this guide does not prove it has been published.

## Choose an entry point

Use uv, or Node.js 18+ with Python 3.11+ (or uv). Package managers may download
dependencies and populate caches. The creator reads only the template shipped in
the selected package: a wheel snapshot or regular files in the npm package. The
npm package has no installation lifecycle scripts and requires no build allowlist.

```bash
uvx --from 'harness-agile==0.5.0' \
  harness-agile init my-project --name 'My Project' \
  --one-liner 'What it does.' --no-input --json --dry-run
```

```bash
npx --yes --package='create-harness-agile@0.5.0' \
  create-harness-agile init my-project --name 'My Project' \
  --one-liner 'What it does.' --no-input --json --dry-run
```

```bash
pnpx 'create-harness-agile@0.5.0' \
  init my-project --name 'My Project' --one-liner 'What it does.' \
  --no-input --json --dry-run
```

These commands install fixed versions from the official PyPI and npm registries.
For a Git-source installation, replace the uvx source with
`git+https://github.com/CXPhoenix/harness-agile.git@v0.5.0`, or the npm package
specifier with `git+https://github.com/CXPhoenix/harness-agile.git#v0.5.0`.
`HARNESS_PYTHON` can select an explicit Python executable for the Node wrapper.

From an existing source checkout, without package installation:

This means a separate, uninitialized checkout of the source repository. A generated
project using `--keep-template-files` retains this guide and init tools, not the
creator package; use a registry command above to start another project from it.

```bash
python3 -m harness_agile init /absolute/path/my-project \
  --source . --name 'My Project' --one-liner 'What it does.' \
  --no-input --json --dry-run
```

Pass user values through argv; avoid constructing shell code from them.

## Apply and verify

1. Inspect the dry-run target and source. The creator writes no target files in
   dry-run. Execute the same command without `--dry-run` within the authorized scope.
2. Confirm exit 0 and JSON success. Run `python3 scripts/verify-project.py` from the
   generated directory, using Python 3.11+ (or the equivalent interpreter through uv).
3. Report the source commit/content digest, dirty-source status, target, skill mode
   and count. Provenance is saved in `docs/agents/template-source.json`.
   Exported npm packages have no Git metadata, so commit and dirty status can be
   `null`. For registry installs, report the package name and pinned version.
   Only Git-source installs should also report the requested Git revision;
   do not infer an unknown commit from the package version.
   The content digest identifies the template bytes across all entry points.
4. Open a fresh Claude Code or Codex session in the target. Keep account setup and
   Codex trust local. Use `grill-with-docs` to define the Project Charter.

The one-liner is not an approved Charter. Default init creates no Git repository,
commit or remote. `--git` creates an independent repo without committing; all later
commits must use the project's `tw-emoji-commit` skill.

## Options and skill trees

Claude Code skills live in `.claude/skills` and Codex skills in `.agents/skills`.
They are separate copies, so each can follow its vendor's prompting guidance; edit
the tree for the runtime you are tuning, then run `python3 scripts/verify-project.py`.
`--skill-mode` is deprecated and ignored.

`--date YYYY-MM-DD` selects adoption date. `--keep-template-files` retains template
history, both template READMEs, and the banner. Default init writes a product README,
removes the template English README and artwork, and retains `docs/guide.md` for
day-to-day collaboration. These documentation changes describe this checkout;
a fixed release tag may contain an earlier layout. `--source PATH` selects a trusted local uninitialized source.
`--no-input` and `--json` never prompt and require all values. This creator
refuses nonempty targets; to update an existing project, use `migrate` below.

## Move an existing project to another version

`migrate` moves a generated project to the template version of the package you
run: a newer package upgrades, an older one downgrades. Versions up to 0.4.0 lack it;
to reach one, run a newer package with `--source` set to that version's uninitialized checkout.
It reads `docs/agents/template-source.json`, which records the version, the
name/one-liner/date answers and a SHA-256 for every template-owned file.

```bash
uvx --from 'harness-agile==X.Y.Z' harness-agile migrate /path/to/project --json
```

1. Require a clean Git worktree; the command refuses otherwise (`--allow-no-git`
   skips the check for non-Git directories). It previews by default; add `--apply`
   to write. It never commits.
2. Unmodified template files take the target content; files the target dropped are
   deleted. A locally edited file is kept and the target content is written beside
   it as `<file>.harness-new` only when the target changed it; a locally deleted file
   is not recreated. `README.md`, `.gitignore`, `.gitattributes`, `.proj.*`, files
   Git did not track at creation, and source-checkout tooling (`pyproject.toml`,
   `package.json`, `.github/`, `bin/`, `harness_agile/`) are never synced; recorded,
   reversible steps make required structural edits. A symlink or junction on any
   synced path stops the run before writing.
3. Merge each `.harness-new` into its file and delete it; until then
   `scripts/verify-project.py` fails and `migrate` refuses to run again. Report the
   JSON categories, the steps applied or undone, and the verify status. If a write
   fails midway, inspect `git status` and return to the previous commit with
   `git restore` and `git clean` before retrying.

`--name`, `--one-liner`, `--date` and `--baseline-source` are accepted only with
`--adopt`. Projects without a schema 2 record need one `--adopt` run with `--name`,
`--one-liner` and the original `--date`; add `--baseline-source PATH` (an
uninitialized checkout of the version they were created from) to tell edited
files from unedited ones.
