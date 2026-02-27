# SessionIntent - Architecture Documentation

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
│                      sessionintent.py                       │
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

## Data Flow

```tree
1. User invokes sessionintent
   │
   ├─> --prompt
   │   └─> Load modes -> Show UI -> User selects -> Apply mode
   │
   ├─> --mode <name>
   │   └─> Load modes -> Validate -> Apply mode
   │
   ├─> --panic
   │   └─> Clear state file
   │
   └─> --init
       └─> Create default configs

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

**File**: `sessionintent.py:72-96`

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

**File**: `sessionintent.py:110-117`

Reads from `/sys/class/power_supply/AC/online`:

- `1` = AC power (plug in)
- `0` = Battery power
- Missing file = Assume AC (fail-safe)

### 3. App Launcher

**File**: `sessionintent.py:214-260`

Launch sequence:

1. Check if app is already running
2. If running + `internal_reuse: true` -> Reuse
3. If running + `internal_reuse: false` -> Skip
4. If not running -> Launch

### 4. Workspace Manager

**File**: `sessionintent.py:171-190`

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

### Template Resolution

App command templates use `{param|default}` syntax:

```python
def _resolve_template(template: str, params: Dict[str, Any]) -> str:
    def replace(match):
        parts = match.group(1).split('|', 1)
        key = parts[0]
        default = parts[1] if len(parts) > 1 else ""
        val = params.get(key, default)
        return str(val)
    return re.sub(r"\{([^}]+)\}", replace, template)
```

## State Management

### State File

Location: `$XDG_STATE_HOME/sessionintent/current`

Content: Mode name (e.g., "work")

Purpose: Track current session for potential recovery

## Extensibility Points

### Adding New App Types

1. Define in `apps.yaml`:

```yaml
newapp:
  cmd: ["newapp", "--flags"]
  check: "newapp"
```

2. Use in mode:

```yaml
modes:
  mymode:
    workspaces:
      1:
        - newapp
```

### Adding Hardware Profiles

1. Define in config:

```yaml
hardware_profiles:
  myprofile:
    disable_modes: []
    allow_all: true
```

2. Detect current hardware status in `is_on_AC()`

## Performance Considerations

- Config parsed on every invocation (acceptable - YAML is fast)
- App checking uses `pgrep -f` (efficient for most cases)
- Workspace switches are sequential (expected behavior)
- Dev mode skips actual launches/checks (for speed)

## Future Enhancements

- Async app launching for faster mode switches
- In-memory cache of config files
- Background watcher for config changes
- Session snapshots before mode switches
