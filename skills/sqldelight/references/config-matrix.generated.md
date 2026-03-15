# Config Matrix (Generated)

Generated from SQLDelight docs. Refresh this file with `scripts/build_config_matrix.py`.

## Driver Matrix

| Platform | Dialect module | Driver artifacts | Constructors | Async | Notes | Source docs |
| --- | --- | --- | --- | --- | --- | --- |
| SQLite (Android) | see dialect matrix | android-driver | AndroidSqliteDriver | false |  | docs/android_sqlite/index.md |
| SQLite (Multiplatform) | see dialect matrix | android-driver, native-driver, sqlite-driver | AndroidSqliteDriver, NativeSqliteDriver, JdbcSqliteDriver | false |  | docs/multiplatform_sqlite/index.md |
| SQLite (Native) | see dialect matrix | native-driver | NativeSqliteDriver | false | Native targets use the native driver path. | docs/native_sqlite/index.md |
| SQLite (JVM) | see dialect matrix | sqlite-driver | JdbcSqliteDriver | false |  | docs/jvm_sqlite/index.md |
| SQLite (JS) | see dialect matrix | web-worker-driver, @cashapp/sqldelight-sqljs-worker | WebWorkerDriver | true | Requires async generated APIs. Browser-only web worker driver path. | docs/js_sqlite/index.md |
| MySQL (JVM) | app.cash.sqldelight:mysql-dialect | jdbc-driver |  | false | Uses the server JDBC setup pattern. | docs/jvm_mysql/index.md |
| PostgreSQL (JVM) | app.cash.sqldelight:postgresql-dialect | jdbc-driver |  | false | Uses the server JDBC setup pattern. | docs/jvm_postgresql/index.md |
| HSQL / H2 (JVM) | app.cash.sqldelight:hsql-dialect | jdbc-driver |  | false | Uses the server JDBC setup pattern. | docs/jvm_h2/index.md |

## Dialect Modules

| Family | Module |
| --- | --- |
| HSQL | hsql-dialect |
| MySQL | mysql-dialect |
| PostgreSQL | postgresql-dialect |
| SQLite 3.18 | sqlite-3-18-dialect |
| SQLite 3.24 | sqlite-3-24-dialect |
| SQLite 3.25 | sqlite-3-25-dialect |
| SQLite 3.30 | sqlite-3-30-dialect |
| SQLite 3.33 | sqlite-3-33-dialect |
| SQLite 3.35 | sqlite-3-35-dialect |
| SQLite 3.38 | sqlite-3-38-dialect |

## Core Gradle Options

| Option | Type | Default | Summary |
| --- | --- | --- | --- |
| databases |  |  | Container for databases. Configures SQLDelight to create each database with the given name. |
| linkSqlite | Property<Boolean> | true | For native targets. Whether sqlite should be automatically linked. This adds the necessary metadata for linking sqlite when the project is compiled to a dynamic framework (which is the default in recent versions of KMP). Note that for a static framework, this flag has no effect. The XCode build that imports the project should add `-lsqlite3` to the linker flags. Alternatively [add a project dependency](https://kotlinlang.org/docs/native-cocoapods-libraries.html) on the [sqlite3](https://cocoapods.org/pods/sqlite3) pod via the cocoapods plugin. Another option that may work is adding `sqlite3` to the cocoapods [`spec.libraries` setting](https://guides.cocoapods.org/syntax/podspec.html#libraries) e.g. in Gradle Kotlin DSL: `extraSpecAttributes["libraries"] = "'c++', 'sqlite3'".` |
| packageName | Property<String> |  | Package name used for the database class. |
| srcDirs | ConfigurableFileCollection | src/[prefix]main/sqldelight | A collection of folders that the plugin will look in for your `.sq` and `.sqm` files. |
| schemaOutputDirectory | DirectoryProperty | null | The directory where `.db` schema files should be stored, relative to the project root. These files are used to verify that migrations yield a database with the latest schema. If `null`, the migration verification tasks will not be created. |
| dependency | Project |  | Optionally specify schema dependencies on other gradle projects [(see below)](#schema-dependencies). |
| dialect | String |  | The SQL dialect you would like to target. Dialects are selected using a gradle dependency. These dependencies can be specified as `app.cash.sqldelight:{dialect module}:{{ versions.sqldelight }}`. See below for available dialects. For Android projects, the SQLite version is automatically selected based on your `minSdk`. Otherwise defaults to SQLite 3.18. Available dialects: * HSQL: `hsql-dialect` * MySQL: `mysql-dialect` * PostgreSQL: `postgresql-dialect` * SQLite 3.18: `sqlite-3-18-dialect` * SQLite 3.24: `sqlite-3-24-dialect` * SQLite 3.25: `sqlite-3-25-dialect` * SQLite 3.30: `sqlite-3-30-dialect` * SQLite 3.33: `sqlite-3-33-dialect` * SQLite 3.35: `sqlite-3-35-dialect` * SQLite 3.38: `sqlite-3-38-dialect` |
| verifyMigrations | Property<Boolean> | false | If set to true, migration files will fail during the build process if there are any errors in them. |
| treatNullAsUnknownForEquality | Property<Boolean> | false | If set to true, SQLDelight will not replace an equality comparison with a nullable typed value when using `IS`. |
| generateAsync | Property<Boolean> | false | If set to true, SQLDelight will generate suspending query methods for use with asynchronous drivers. |
| deriveSchemaFromMigrations | Property<Boolean> | false | If set to true, the schema for your database will be derived from your `.sqm` files as if each migration had been applied. If false, your schema is defined in `.sq` files. |
| expandSelectStar | Property<Boolean> | true | If set to true, SQLDelight will rewrite `SELECT *` statements to explicitly reference each of the actual resulting columns. For example, the `getAll` query below |

## Upgrade Coordinate Replacements

| Old | New |
| --- | --- |
| id("com.squareup.sqldelight") version "{{ versions.sqldelight }}" | id("app.cash.sqldelight") version "{{ versions.sqldelight }}" |
| implementation("com.squareup.sqldelight:sqlite-driver:{{ versions.sqldelight }}") | implementation("app.cash.sqldelight:sqlite-driver:{{ versions.sqldelight }}") |
| implementation("com.squareup.sqldelight:android-driver:{{ versions.sqldelight }}") | implementation("app.cash.sqldelight:android-driver:{{ versions.sqldelight }}") |
| implementation("com.squareup.sqldelight:coroutines-extensions:{{ versions.sqldelight }}") | implementation("app.cash.sqldelight:coroutines-extensions-jvm:{{ versions.sqldelight }}") |
| import com.squareup.sqldelight.db.SqlDriver | import app.cash.sqldelight.db.SqlDriver |
