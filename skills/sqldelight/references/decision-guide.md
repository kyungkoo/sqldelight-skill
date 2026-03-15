# SQLDelight Decision Guide

Use this file when the user needs a recommendation, not just a link.

## Start Here

1. Identify the target runtime.
2. Decide whether the schema source of truth is fresh `.sq` files or ordered `.sqm` migrations.
3. Decide whether the project needs asynchronous generated APIs.
4. Use `config-matrix.generated.md` for exact artifacts and Gradle option names.

## Recommended Paths

| Situation | Recommend | Why | Verify |
| --- | --- | --- | --- |
| Android app using SQLite only | Follow the Android SQLite path first. | Android docs include the default setup flow and Android driver usage. | Android getting started, Gradle, migrations, coroutines. |
| KMP app with Android plus iOS or desktop | Follow the Multiplatform SQLite path first. | It documents target-specific driver split and shared `SqlDriver` factory patterns. | Multiplatform getting started and the driver rows in `config-matrix.generated.md`. |
| Browser JS target | Treat JS as async-first. | The browser path uses the web worker driver and requires async generation. | JS getting started, worker setup, `generateAsync` in `config-matrix.generated.md`. |
| JVM app storing SQLite files locally | Use the JVM SQLite path. | It uses the SQLite JDBC driver and the JDBC-style constructor. | JVM SQLite getting started and Gradle pages. |
| JVM server with MySQL or PostgreSQL | Use the dialect-specific JVM server path. | These guides compose the same server setup pattern with dialect selection. | MySQL or PostgreSQL getting started, Gradle, migrations. |
| Existing production database or shared migration history | Prefer migration-backed schema. | SQLDelight can derive schema from `.sqm` files and verify upgrades against schema outputs. | `checklists.md` migration sections and `config-matrix.generated.md` options. |
| New project with no deployed schema | Start with fresh `.sq` schema files unless there is a clear migration requirement. | It is the shortest path to generated APIs and is easier to reason about initially. | `checklists.md` initial adoption and schema strategy sections. |
| Adding Flow-based observation or browser async drivers | Re-evaluate whether generated async APIs are required. | Browser targets and non-blocking drivers change which generated API surface is compatible. | `checklists.md` async section and upgrade notes. |

## Schema Strategy Defaults

- Default to fresh `.sq` schema files for greenfield local databases.
- Default to `deriveSchemaFromMigrations` when the migration history is already a product requirement.
- Turn on migration verification only when the project also stores schema outputs for comparison.

## Escalate to Anti-Patterns

Open `anti-patterns.md` before answering if the request mentions any of these:

- `generateAsync`
- `ColumnAdapter`
- `verifyMigrations`
- `deriveSchemaFromMigrations`
- JS browser driver migration
- SQLDelight 1.x to 2.x upgrade
