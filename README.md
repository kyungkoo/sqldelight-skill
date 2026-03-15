# SQLDelight Skill

Distribution repo for the Codex `sqldelight` skill.

## Layout

```text
skills/
  sqldelight/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
```

The actual installable skill lives under `skills/sqldelight/`. Root-level files exist only for repo management, CI, and release workflow.

## Install

Copy `skills/sqldelight` into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/sqldelight ~/.codex/skills/
```

If you want to install directly from GitHub with the Codex skill installer:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo <owner>/sqldelight-skill \
  --path skills/sqldelight
```

After installation, restart Codex to pick up the new skill.

## Install with npx

This repo also includes a small npm-based installer wrapper.

```bash
npx sqldelight-skill
```

Useful options:

```bash
npx sqldelight-skill --dest ~/.codex/skills
npx sqldelight-skill --dest ~/.codex/skills --force
npx sqldelight-skill --name sqldelight-preview --dest ~/.codex/skills
```

Notes:

- The npm package name is currently `sqldelight-skill`. If that name is unavailable on npm when you publish, rename it in `package.json` before release.
- The installer copies `skills/sqldelight` into the target Codex skills directory and does not generate files at runtime.

## Maintenance Model

- `SKILL.md` stays stable and focuses on runtime workflow.
- Curated references are edited manually.
- `*.generated.md` files are rebuilt from SQLDelight docs and committed.
- The generated references are meant to be static at runtime so all users get the same behavior.

## Refresh Generated References

You need a local checkout of the SQLDelight repo.

```bash
python3 skills/sqldelight/scripts/build_doc_catalog.py --repo-root /path/to/sqldelight --skill-dir skills/sqldelight
python3 skills/sqldelight/scripts/build_config_matrix.py --repo-root /path/to/sqldelight --skill-dir skills/sqldelight
python3 skills/sqldelight/scripts/validate_refs.py --repo-root /path/to/sqldelight --skill-dir skills/sqldelight
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sqldelight
```

The last command depends on the local Codex `skill-creator` installation.

## Release Guidance

- Commit generated reference updates together with any curated guidance changes.
- Tag versions for reproducible installs, for example `v0.1.0`.
- Use patch releases for doc refreshes and minor curated fixes.
- Use minor or major releases when workflow, trigger wording, or supported guidance scope changes.
- If you publish to npm, keep the npm package version aligned with the Git tag used for the skill release.
