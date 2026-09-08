# Create a harness-agile project

Use this guide for a **new project**. For an already copied template, follow its
`.agents/skills/init-template/SKILL.md`. Preserve the source during maintenance.

## Inputs and version

Use the target directory, human-readable name and one-line description already
supplied by the user. Ask together only for missing values. The target must be
absent or empty, with an existing parent directory, outside the source checkout.

Source: `https://github.com/CXPhoenix/harness-agile.git`, currently private.
Use existing Git credentials and read access. The initial release tag is `v0.1.0`.
For automation, resolve the approved tag to its full commit with Git and use that
commit in place of the tag below. When reading this guide from an authenticated
checkout, use that checkout's `git rev-parse HEAD`.

## Choose an entry point

Use uv, or Node.js 18+ with Python 3.11+ (or uv). Package managers may download
dependencies and populate caches. The creator reads only the template shipped in
the selected package: a wheel snapshot or regular files in the npm package. The
npm package has no installation lifecycle scripts and requires no build allowlist.

```bash
uvx --from 'git+https://github.com/CXPhoenix/harness-agile.git@v0.1.0' \
  harness-agile init my-project --name 'My Project' \
  --one-liner 'What it does.' --no-input --json --dry-run
```

```bash
npx --yes --package='git+https://github.com/CXPhoenix/harness-agile.git#v0.1.0' \
  create-harness-agile init my-project --name 'My Project' \
  --one-liner 'What it does.' --no-input --json --dry-run
```

```bash
pnpx 'git+https://github.com/CXPhoenix/harness-agile.git#v0.1.0' \
  init my-project --name 'My Project' --one-liner 'What it does.' \
  --no-input --json --dry-run
```

These are Git-source commands, not claims of npm/PyPI registry publication. Do not
substitute an unverified same-name registry package. If the package manager blocks
a Git build, use an authenticated checkout and the local route; preserve its policy.
`HARNESS_PYTHON` can select an explicit Python executable for the Node wrapper.

From an existing source checkout, without package installation:

This means a separate, uninitialized checkout of the source repository. A generated
project using `--keep-template-files` retains this guide and init tools, not the
creator package; use a Git-source command above to start another project from it.

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
   `null`; also report the exact Git revision requested in the install command.
   The content digest identifies the template bytes across all entry points.
4. Open a fresh Claude Code or Codex session in the target. Keep account setup and
   Codex trust local. Use `grill-with-docs` to define the Project Charter.

The one-liner is not an approved Charter. Default init creates no Git repository,
commit or remote. `--git` creates an independent repo without committing; all later
commits must use the project's `tw-emoji-commit` skill.

## Options and skill transport

`--skill-mode auto` uses relative links, with a verified-copy fallback when links
are unavailable. `--skill-mode copy` avoids symlinks entirely. Edit canonical skills
in `.agents/skills`, review changes, run `python3 scripts/sync-skills.py --refresh`,
then verify. Divergent copies and unmanaged entries require review.

For flattened Git links (such as Windows checkouts), run
`python3 scripts/sync-skills.py --mode copy` before verification.

`--date YYYY-MM-DD` selects adoption date. `--keep-template-files` retains template
history and the original README; default init writes a product README and removes
template-only tools. `--source PATH` selects a trusted local uninitialized source.
`--no-input` and `--json` never prompt and require all values. Existing product
adoption and updates are separate tasks; this creator refuses nonempty targets.
