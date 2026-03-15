---
name: sqldelight
description: Guide SQLDelight setup, dialect and driver selection, Gradle DSL, schema strategy, migrations, async and coroutines usage, custom column types, upgrade guidance, and troubleshooting for Kotlin, Android, KMP, JVM, and JS projects. Use when a user needs SQLDelight recommendations, wants the right official docs quickly, or needs help diagnosing SQLDelight configuration and migration issues.
---

# SQLDelight

Use this skill to route SQLDelight questions to the right official docs while keeping responses stable when the network is limited.

## Runtime Rules

1. Classify the request before answering.
   - Platform or dialect: Android SQLite, Multiplatform SQLite, Native SQLite, JVM SQLite, JS, MySQL, PostgreSQL, HSQL/H2.
   - Schema lifecycle: fresh schema, migration-backed schema, or existing production database.
   - Runtime model: synchronous or asynchronous.
   - Problem type: setup, Gradle DSL, generated APIs, migrations, adapters, coroutines, upgrade, or troubleshooting.
2. Prefer official `latest` SQLDelight docs for version-sensitive facts when online.
3. Use bundled references to keep answers consistent and useful offline.
4. If the official docs and repo implementation disagree, treat the official docs as the answer source and mention the repo only as implementation context.

## Answer Shape

Respond in this order:

1. Recommendation
2. Why that recommendation fits the user's situation
3. Exact docs or config points to verify
4. Relevant anti-patterns or migration risks
5. A staleness note if you are answering from bundled references without checking the latest docs

## Reference Map

Read these files directly from `references/` as needed:

- `decision-guide.md`: choose the right platform path, schema strategy, and async model.
- `checklists.md`: walk through setup, migration, adapter, and upgrade checks.
- `anti-patterns.md`: catch common mistakes before suggesting code changes.
- `update-playbook.md`: maintain this skill when SQLDelight docs change.
- `doc-catalog.generated.md`: map an intent to the right official docs page and local source page.
- `config-matrix.generated.md`: verify artifacts, constructors, dialect modules, and Gradle options.
- `sync-status.generated.md`: see when generated references were last refreshed and whether they may be stale.

## Maintenance Rules

- Do not run the bundled scripts during normal user help unless the task is explicitly about updating this skill.
- Generated files are maintenance artifacts, not runtime logic.
- Keep `SKILL.md` stable. Put changing facts in generated references whenever possible.
