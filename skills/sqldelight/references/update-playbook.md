# SQLDelight Skill Update Playbook

Use this file when official SQLDelight docs change and the generated references need to be refreshed.

## Goal

Keep runtime behavior static for users while refreshing only generated facts for maintainers.

## Inputs

- A local SQLDelight repo checkout with `mkdocs.yml` and `docs/`
- This skill directory
- The `skill-creator` validator script for final structure validation

## Refresh Steps

1. Work from the root of this repository.
2. Regenerate the doc catalog:
   - `python3 skills/sqldelight/scripts/build_doc_catalog.py --repo-root /path/to/sqldelight --skill-dir skills/sqldelight`
3. Regenerate the config matrix and sync status:
   - `python3 skills/sqldelight/scripts/build_config_matrix.py --repo-root /path/to/sqldelight --skill-dir skills/sqldelight`
4. Validate generated and curated references:
   - `python3 skills/sqldelight/scripts/validate_refs.py --repo-root /path/to/sqldelight --skill-dir skills/sqldelight`
5. Validate the skill folder itself:
   - `python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sqldelight`

## When Curated Files Need Manual Updates

Update curated references only if the docs change the meaning of guidance, not just links.

- Update `decision-guide.md` if a platform path or default recommendation changes.
- Update `checklists.md` if setup steps, migration requirements, or async expectations change.
- Update `anti-patterns.md` if a former pitfall is removed or a new one appears.
- Update `SKILL.md` only if the workflow itself changes.

## Typical Change Boundaries

- Nav or link changes:
  - Regenerate `doc-catalog.generated.md`
- Artifact names, constructor examples, or Gradle option facts change:
  - Regenerate `config-matrix.generated.md`
  - Review `checklists.md` and `anti-patterns.md`
- Upgrade or breaking-change guidance changes:
  - Review `checklists.md` and `anti-patterns.md`
  - Regenerate `config-matrix.generated.md` if coordinates or options changed

## Expected Outputs

- `doc-catalog.generated.md`
- `config-matrix.generated.md`
- `sync-status.generated.md`

If validation fails after regeneration, fix the generated scripts first. Only edit generated files by rerunning the scripts.
