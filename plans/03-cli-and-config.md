# 03 — CLI and Config Redesign

The rework allows breaking changes to both the CLI and the config format. This document
specifies the target surface and the migration path. The goal is not gratuitous churn —
it is to make the interface match what the code actually does, and to make it easier to
extend.

## 1. CLI target

Move from the current flat flag soup to a subcommand style:

```
sessionintent [--config PATH] [--dev] [--backend NAME] <command> [args]
```

### Global flags

| Flag | Purpose |
|------|---------|
| `--config PATH` | Custom config file. |
| `--dev` | Dry-run: print commands instead of executing. |
| `--backend NAME` | Manual backend override (replaces the unimplemented `--force-backend` idea). |

### Commands

| Command | Args | Purpose |
|---------|------|---------|
| `apply` | `<mode>` | Apply a mode directly. |
| `select` | — | Open the mode selector (default when no command is given). |
| `list` | — | List available modes. |
| `status` | — | Show current session status. |
| `panic` | — | Clear state without killing apps. |
| `quit` | — | Gracefully close managed apps (SIGTERM). |
| `clear` | — | Clear state files only. |
| `kill` | — | Force kill managed apps (SIGKILL). |
| `suspend` | — | Suspend the current session. |
| `init` | — | Initialize default configs and the workspace extension. |
| `setup` | — | Interactive setup wizard. |
| `scan` | `[--force] [--no-cache]` | Rescan installed apps. |
| `reload` | — | Reload configuration. |
| `version` | — | Print the version and exit. |

### Flag-to-command migration table

| Old flag | New command |
|----------|-------------|
| (no args) | `select` (default) |
| `-m` / `--mode <mode>` | `apply <mode>` |
| `-l` / `--list` | `list` |
| `-s` / `--status` | `status` |
| `-P` / `--panic` | `panic` |
| `-q` / `--quit` | `quit` |
| `--clear` | `clear` |
| `-k` / `--kill` | `kill` |
| `-S` / `--suspend` | `suspend` |
| `-i` / `--init` | `init` |
| `--setup` | `setup` |
| `--scan-apps` | `scan` |
| `-r` / `--reload` | `reload` |
| `--version` | `version` |
| `-c` / `--config PATH` | `--config PATH` (global) |
| `-d` / `--dev` | `--dev` (global) |
| `-f` / `--force` | `scan --force` |
| `--no-cache` | `scan --no-cache` |

### Fixes folded into the redesign

- `version` must actually print the version (single source of truth, see `02-vision.md`).
- `--force` and `--no-cache` must be wired through to the scanner.
- `--backend` gives manual control over provider selection, replacing the never-landed
  `--force-backend` from the compatibility plan.

## 2. Config target

Keep the parts that work and are already used:

- `modes` with workspaces and per-mode app params.
- `hardware_profiles` for battery/AC filtering.
- `apps.yaml` as a separate registry from `config.yaml`.

### 2.1 `config.yaml` schema (`version: 2`)

```yaml
version: 2

defaults:
  wait_window: 15
  reuse_workspaces: true

hardware_profiles:
  battery:
    disable_modes: [gaming]
  plugged:
    allow_all: true

modes:
  browsing:
    label: "Browsing / Chilling"
    firefox:
      profile: chill
      urls: [https://reddit.com, https://youtube.com]
    workspaces:
      1: [firefox]
      2: [discord]
```

### 2.2 `apps.yaml` schema

```yaml
firefox:
  cmd: ["firefox", "-P", "{profile|default}"]
  append_param: "urls"
  internal_reuse: true
```

App definition fields:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `cmd` | list[str] | `[app_key]` | Launch command. |
| `check` | str \| false | `app_key` | `pgrep -f` pattern, or `false` to always launch. |
| `flags` | dict[str, str] | `{}` | Conditional flags keyed by param name. |
| `append_param` | str \| null | `null` | Param whose list value is appended to the command. |
| `primary_param` | str | `value` | Param name used when a shorthand scalar value is given. |
| `internal_reuse` | bool | `true` | Whether to reuse a running instance. |

### 2.3 Changes and rationale

1. **Formal validation** — introduce a real schema (JSON Schema or an explicit validator
   that is actually invoked during load). The current `CONFIG_SCHEMA`/`APPS_SCHEMA` in
   `src/config/validator.py` exist but are never enforced in the load path.
2. **Clean split** — `config.yaml` defines modes; `apps.yaml` defines apps. This is
   already the de-facto split, but it is not codified.
3. **Version bump** — `version: 2`, with a documented migration from `version: 1`.
4. **Retire unwired keys** — remove `time_schedules`, `settings`, `hardware.battery_only`,
   and `schedule` from the documented schema until they are actually implemented. This
   keeps docs truthful (see `06-documentation.md`).
5. **Preserve template syntax** — `{var|default}` is retained because it is used across
   the code and tests.

### 2.4 Migration note

`version: 1` configs remain parseable in principle; the loader should detect the version
and either apply a simple migration or print a clear error pointing to the migration
guide. The subcommand CLI and `version: 2` schema land together in Phase 4 so users get
one coordinated breaking change instead of two.

See `04-phases.md` for when this lands and `07-decisions-and-risks.md` for why breaking
changes are acceptable.
