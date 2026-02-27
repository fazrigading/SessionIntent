# SessionIntent Architecture

This document provides a high-level overview of SessionIntent's architecture.

## Overview

SessionIntent is a CLI tool that orchestrates GNOME session states based on user-defined "modes". Each mode declaratively specifies:
- Which applications to launch
- Which workspaces to use
- Application-specific parameters (profiles, workspaces, URLs)
- Hardware constraints (battery vs AC)

## System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                       User Interface                        │
│                        (rofi/wofi)                          │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              │ Mode selection
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        Orchestrator                         │
│                      SessionManager                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Config Loader                                        │  │
│  │  - Parse YAML configs                                 │  │
│  │  - Merge system + user configs                        │  │
│  │  - Validate schema                                    │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Hardware Detector                                    │  │
│  │  - AC/Battery detection                               │  │
│  │  - Apply hardware profiles                            │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Mode Selector                                        │  │
│  │  - Present options                                    │  │
│  │  - Handle user input                                  │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Workspace Manager                                    │  │
│  │  - Switch GNOME workspaces                            │  │
│  │  - Track current workspace state                      │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  App Controller                                       │  │
│  │  - Launch applications                                │  │
│  │  - Reuse existing instances                           │  │
│  │  - Handle app-specific parameters                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      System Services                        │
│  GNOME Shell (gdbus)                                        │
│  Process Manager (pgrep)                                    │
│  Power Supply (/sys/class/power_supply/)                    │
│  XDG Directories (~/.config/sessionintent/)                 │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Layers

### 1. User Interface Layer

**Tools**: `wofi` or `rofi`

**Responsibilities**:
- Present selectable session modes
- Keyboard-only interaction
- Number-based selection (no arrow keys required)

**Input**: User selects a mode from menu

**Output**: Selected mode name to orchestrator

### 2. Orchestrator Layer

**Main Class**: `SessionManager`

**Responsibilities**:
- Load and merge configurations
- Detect hardware state (battery/AC)
- Filter available modes
- Switch workspaces
- Launch/reuse applications
- State management

**Components**:
- Config Loader
- Hardware Detector
- Mode Selector
- Workspace Manager
- App Controller

### 3. System Integration Layer

**GNOME Shell (D-Bus)**:
- Workspace switching
- Method: `org.gnome.Shell.Eval`

**Process Manager**:
- `pgrep` for app detection
- `subprocess.Popen` for launching

**Power Supply**:
- `/sys/class/power_supply/AC/online`

**File System**:
- `~/.config/sessionintent/` (config)
- `~/.local/state/sessionintent/` (state)

## Data Flow

```tree
1. User invokes sessionintent
   │
   ├─> (no args) - Default
   │   └─> Load modes -> Show UI -> User selects -> Apply mode
   │
   ├─> --prompt
   │   └─> Load modes -> Show UI -> User selects -> Apply mode
   │
   ├─> --mode <name>
   │   └─> Load modes -> Validate -> Apply mode
   │
   ├─> --panic (-P)
   │   └─> Clear state file (no app termination)
   │
   ├─> --quit (-q)
   │   └─> Get current mode -> Find apps -> SIGTERM apps -> Clear state
   │
   ├─> --clear
   │   └─> Clear state file only
   │
   ├─> --kill (-k)
   │   └─> Get current mode -> Find apps -> SIGKILL apps
   │
   ├─> --suspend (-S)
   │   └─> Save suspend:<mode> to state
   │
   ├─> --status (-s)
   │   └─> Show current mode, power state, dev mode
   │
   ├─> --list (-l)
   │   └─> List available modes (hardware-aware)
   │
   ├─> --reload (-r)
   │   └─> Reload config from disk
   │
   ├─> --init (-i)
   │   └─> Create default configs
   │
   └─> --dev (-d)
       └─> Print commands instead of executing

2. Mode Application
   │
   ├─> Identify hardware profile (battery/AC)
   ├─> Filter available modes
   ├─> Switch to each workspace in order
   ├─> Launch/or reuse each app
   └─> Save state
```

## Key Components

### 1. Config Loader

Handles loading configuration from multiple sources:

```text
System config (/usr/share/sessionintent/)
                  ↓
                Merge
                  ↓
 User config (~/.config/sessionintent/)
                  ↓
          Final config used
```

### 2. Hardware Detector

Reads from `/sys/class/power_supply/AC/online`:

- `1` = AC power (plugged in)
- `0` = Battery power
- Missing file = Assume AC (fail-safe)

### 3. App Launcher

Launch sequence:

1. Check if app is already running
2. If running + `internal_reuse: true` -> Reuse
3. If running + `internal_reuse: false` -> Skip
4. If not running -> Launch

### 4. Workspace Manager

Uses GNOME shell D-Bus API:

```bash
gdbus call --session \
  --dest org.gnome.Shell \
  --object-path /org/gnome/Shell \
  --method org.gnome.Shell.Eval \
  "Main.wm.actionMoveWorkspace(Main.wm.get_workspace_by_index(N))"
```

## Configuration Loading

### Priority Order

1. System apps (`/usr/share/sessionintent/apps.yaml`)
2. Local dev apps (`./apps.yaml` in dev mode)
3. User apps (`~/.config/sessionintent/apps.yaml`)

Later sources override earlier ones.

### Config Merging

```python
# System + User = Final
self.apps = {**bundled_apps, **user_apps}
```

## Template Resolution

App commands support variable substitution:

```yaml
cmd: ["firefox", "-P", "{profile|default}"]
```

**Format**: `{variable|default}`
- `variable`: Key from params
- `default`: Fallback value (optional)

**Example resolution**:

```yaml
# Mode config
modes:
  work:
    firefox:
      profile: work
      urls:
        - https://example.com
```

Results in: `firefox -P work https://example.com`

## State Management

### State File

**Location**: `$XDG_STATE_HOME/sessionintent/current`

**Content**: Mode name (e.g., "work")

**Purpose**: Track current session state for recovery

**Initialization**: Created after mode application

## Error Handling

### Safety First

- Never kill user data
- Never force process termination
- Graceful degradation if UI missing
- Fallback to AC if power detection fails

### Validation

- YAML syntax errors
- Mode existence checks
- App registry existence
- Template resolution

## Extensibility

### Custom App Controllers

Add new app types in `apps.yaml`:

```yaml
newapp:
  cmd: ["newapp"]
  check: "newapp"
```

### Hardware Profile Extension

```yaml
hardware_profiles:
  custom:
    disable_modes: []
```

### Command Hooks (Future)

```yaml
modes:
  work:
    hooks:
      before: ["script.sh"]
      after: ["notify.sh"]
```

## Performance Characteristics

- Config load: <10ms (YAML is fast)
- App check: ~5ms (pgrep overhead)
- Workspace switch: ~200ms (GNOME D-Bus)
- App launch: Variable (depends on app)

Total mode switch: <500ms (typical)

## Security Considerations

- Runs as user (no sudo)
- No hardcoded secrets
- Template sanitization
- File permission checks

## Troubleshooting

### Debug Mode

```bash
sessionintent --dev --mode work
```

Shows dry-run output without side effects.

### Log Output

```bash
# Enable verbose logging (future)
sessionintent --verbose --mode work
```

### Common Issues

1. App not launching: Check `pgrep` pattern
2. Wrong workspace: Verify workspace numbers
3. Template not resolving: Check YAML syntax

## Future Enhancements

- Async app launching
- Config caching
- Live reload (SIGHUP)
- Plugin system
- Session snapshots
- Window state persistence
