# Migrating to the Subcommand CLI and `version: 2` Configs

Phase 4 replaces the flat flag soup with subcommands and enforces a
`version: 2` config schema. This guide covers both changes.

## CLI: flag-to-command table

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
| `--clear-cache` | `scan --clear-cache` |
| (new) | `preview <mode>` — show apps/workspaces without applying |

Global flags come before the command:

```bash
sessionintent --dev apply work
sessionintent --backend sway apply work
sessionintent --config ~/other.yaml list
```

## Config: `version: 1` → `version: 2`

1. Add `version: 2` at the top of `config.yaml`.
2. Delete retired keys (unwired features removed in Phase 1):
   - mode-level `schedule`, `settings`, `time_schedules`
   - mode-level `hardware.battery_only`
   - top-level `time_schedules`, `settings`
3. Keep everything else: `modes`, `workspaces`, per-mode app params,
   `hardware_profiles`, `defaults`, and the `{var|default}` template
   syntax are unchanged. `apps.yaml` is unchanged.

A `version: 1` config still loads: SessionIntent migrates it in memory
and prints a notice naming the dropped keys. Add `version: 2` to
silence the notice.

## Examples

```bash
# Before
sessionintent --dev --mode work
sessionintent --scan-apps --force

# After
sessionintent --dev apply work
sessionintent scan --force
```
