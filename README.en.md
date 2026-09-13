# harness-agile

![Exploration paths pass through checkpoints and converge into a deliverable.](.tmpl.docs/assets/banner/banner.png)

[![CI](https://github.com/CXPhoenix/harness-agile/actions/workflows/verify.yml/badge.svg)](https://github.com/CXPhoenix/harness-agile/actions/workflows/verify.yml)
[![Git tag](https://img.shields.io/badge/Git_tag-v0.2.1-476c63)](https://github.com/CXPhoenix/harness-agile/tree/v0.2.1)
[![PyPI](https://img.shields.io/pypi/v/harness-agile)](https://pypi.org/project/harness-agile/)
[![npm](https://img.shields.io/npm/v/create-harness-agile)](https://www.npmjs.com/package/create-harness-agile)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://github.com/CXPhoenix/harness-agile/blob/main/pyproject.toml)
[![Claude Code + Codex](https://img.shields.io/badge/Claude_Code_%2B_Codex-shared_workflow-d97757)](docs/agents/runtime.md)

**Give Claude Code and Codex the same requirements, specs, and delivery history.**

[繁體中文](README.md) · English

harness-agile is a portable template for AI-assisted development. Each step, from clarifying a requirement to merging a change, has working instructions, an expected output, and a gate. When you switch tools or hand off work, the next coding assistant can continue from the same record.

It is designed for individuals and teams who want their AI development workflow in Git and need to work across Claude Code and Codex. The template supplies the collaboration structure; you choose the product and its technology stack.

## What you get

- **One shared contract.** `AGENTS.md` holds the project purpose and workflow. Both tools use canonical skills while keeping their native tools and role configurations.
- **Traceable delivery.** Requirements become specs, acceptance criteria lead to tickets, and reviews, tests, and unresolved questions stay in the repository.
- **Portable projects.** The creator ships its template data, supports relative symlinks or full skill copies, and records the source and content digest.

## Quick start

With uv available, run this from the parent directory of your new project:

```bash
uvx --from 'harness-agile==0.2.1' \
  harness-agile init my-project --name 'My Project' \
  --one-liner 'The problem it solves.' --no-input
cd my-project
uv run --python 3.11 python scripts/verify-project.py
```

This creates a project directory, fills in its name and description, and checks the collaboration setup. The target must be absent or empty, and its parent must exist. The command installs a fixed version from PyPI; no GitHub account is required.

Next, open Claude Code or Codex in the new directory and run `grill-with-docs` to define the Project Charter in `AGENTS.md`: who the product serves, what problem it solves, and what it must do. A name and one-line description do not constitute approved requirements.

| Action | Claude Code | Codex |
| --- | --- | --- |
| Define the Project Charter | `/grill-with-docs` | `$grill-with-docs` |
| List available skills | `/skills` | `/skills` |
| Review a change | `/code-review` | `$code-review` |

<details>
<summary>Use npx or pnpx</summary>

Requires Node.js 18+ and either Python 3.11+ or uv.

```bash
npx --yes --package='create-harness-agile@0.2.1' \
  create-harness-agile init my-project --name 'My Project' \
  --one-liner 'The problem it solves.' --no-input
```

```bash
pnpx 'create-harness-agile@0.2.1' \
  init my-project --name 'My Project' --one-liner 'The problem it solves.' --no-input
```

You can replace `pnpx` with `pnpm dlx`. All three entry points use the same Python initializer. uvx installs `harness-agile` from PyPI; npx and pnpx install `create-harness-agile` from npm. The Node entry point looks for Python first, then uv; `HARNESS_PYTHON` selects an explicit Python executable.

</details>

For an existing template copy, local creation, previews, and all options, see the [adoption guide](.tmpl.docs/adoption.md) (Traditional Chinese). For an English setup procedure, see [INSTALL.md](INSTALL.md); you can give it to a coding assistant with your target directory, name, and description.

## From idea to delivery

Start with a **walking skeleton**: the thinnest product path that actually runs end to end and provides seams for further work. This is round 0, exempt from specs and spec review. Once it merges to `main`, subsequent work ships as epics, each delivering a demonstrable increment.

```text
Clarify → spec + traceability → four-axis review → tickets → TDD
        → code review → security review → real-surface verification → merge
```

The user confirms direction at gates such as shared requirements, ticket breakdown, and test planning. Each ticket gets its own branch. Verification must cover the surface where the behavior actually runs. See the [delivery workflow](docs/agents/workflow.md) for the rules and the [collaboration guide](docs/guide.md) (Traditional Chinese) for daily use.

## Documentation

| Your task | Start here |
| --- | --- |
| Create a project and choose an initialization route | [Adoption guide](.tmpl.docs/adoption.md) (Traditional Chinese) |
| Use skills, switch tools, and hand off work | [Collaboration guide](docs/guide.md) (Traditional Chinese) |
| Ask a coding assistant to create a project | [INSTALL.md](INSTALL.md) (English) |
| Find workflow, tracker, and review rules | [Shared contract](AGENTS.md) and [documentation index](docs/README.md) |
| Change and verify the source template | [Contributing and maintenance](.tmpl.docs/contributing.md) (Traditional Chinese) |

## Development and verification

In an uninitialized source checkout, with Python 3.11+:

```bash
python3 scripts/verify-project.py
python3 -m unittest discover -s tests -v
```

These checks cover template structure, skills, and initialization behavior. Product tests are established by the walking skeleton. The CI badge links to remote run status; it does not certify a new product's behavior.

## License

This project is licensed under the [MIT License](LICENSE). Bundled third-party skills, fonts, and brand assets retain their respective terms; see [third-party notices](THIRD_PARTY_NOTICES.md) and [source records](docs/agents/skill-sources.json).

<!-- TEMPLATE-DOCS:START -->
## Template design and history

The [maintenance index](.tmpl.docs/README.md) (Traditional Chinese) contains design context, research, plans, and historical verification. Default initialization removes that material, the template banner, and this English README, and replaces the main README with a product README. Use `--keep-template-files` to retain template documentation.
<!-- TEMPLATE-DOCS:END -->

Archify automatic opening is disabled on Windows. Generation and validation remain available; open artifacts manually. See the [restriction and verification guide](docs/security/windows-opener.md) (Traditional Chinese).
