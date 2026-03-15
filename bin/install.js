#!/usr/bin/env node

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

function usage() {
  console.log(`sqldelight-skill

Install the bundled sqldelight Codex skill into a Codex skills directory.

Usage:
  npx sqldelight-skill [--dest <skills-dir>] [--name <skill-name>] [--force] [--dry-run]

Options:
  --dest     Destination skills directory. Defaults to $CODEX_HOME/skills or ~/.codex/skills
  --name     Installed skill folder name. Defaults to sqldelight
  --force    Replace an existing destination skill directory
  --dry-run  Print the install plan without copying files
  --help     Show this help
`);
}

function parseArgs(argv) {
  const options = {
    dest: null,
    name: "sqldelight",
    force: false,
    dryRun: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--dest") {
      options.dest = argv[i + 1];
      i += 1;
    } else if (arg === "--name") {
      options.name = argv[i + 1];
      i += 1;
    } else if (arg === "--force") {
      options.force = true;
    } else if (arg === "--dry-run") {
      options.dryRun = true;
    } else if (arg === "--help" || arg === "-h") {
      usage();
      process.exit(0);
    } else {
      console.error(`Unknown argument: ${arg}`);
      usage();
      process.exit(1);
    }
  }

  if (!options.name) {
    console.error("--name must not be empty");
    process.exit(1);
  }

  return options;
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  const repoRoot = path.resolve(__dirname, "..");
  const sourceDir = path.join(repoRoot, "skills", "sqldelight");
  const codexHome = process.env.CODEX_HOME || path.join(os.homedir(), ".codex");
  const skillsDir = options.dest ? path.resolve(options.dest) : path.join(codexHome, "skills");
  const destinationDir = path.join(skillsDir, options.name);

  if (!fs.existsSync(sourceDir)) {
    console.error(`Skill source not found: ${sourceDir}`);
    process.exit(1);
  }

  if (options.dryRun) {
    console.log(`[DRY RUN] Source: ${sourceDir}`);
    console.log(`[DRY RUN] Destination: ${destinationDir}`);
    if (fs.existsSync(destinationDir)) {
      console.log(`[DRY RUN] Existing destination present${options.force ? " and would be replaced" : ""}`);
    }
    return;
  }

  fs.mkdirSync(skillsDir, { recursive: true });

  if (fs.existsSync(destinationDir)) {
    if (!options.force) {
      console.error(`Destination already exists: ${destinationDir}`);
      console.error("Re-run with --force to replace it.");
      process.exit(1);
    }
    fs.rmSync(destinationDir, { recursive: true, force: true });
  }

  fs.cpSync(sourceDir, destinationDir, { recursive: true });
  console.log(`Installed sqldelight skill to ${destinationDir}`);
  console.log("Restart Codex to pick up the new skill.");
}

main();
