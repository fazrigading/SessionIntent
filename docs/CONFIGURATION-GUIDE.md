# SessionIntent - Configuration Guide

This guide explains how to configure SessionIntent to match your workflow.

## Configuration Files

SessionIntent reads from two main configuration files:

1. **config.yaml** - Defines session modes and hardware profiles
2. **apps.yaml** - Defines available applications and their launch behavior

### Location

- **user config**: `~/.config/sessionintent/config.yaml`
- **user apps**: `~/.config/sessionintent/apps.yaml`
- **system apps**: `/usr/share/sessionintent/apps.yaml`

User configs override system configs.

## Config.yaml Structure

```yaml
version: 1

defaults:
  ask_before_kill: true
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
    workspaces:
      1:
        - firefox
      2:
        - discord
```

### Options

#### version

Optional. Current config version (for future migrations).

#### defaults

Global defaults for all modes:
- `ask_before_kill`: Prompt before killing processes (default: true)
- `reuse_workspaces`: Keep workspace state between mode switches (default: true)

#### hardware_profiles

Adjust behavior based on power state:

```yaml
hardware_profiles:
  battery:
    disable_modes: [gaming, video-editing]
  plugged:
    allow_all: true
```

#### modes

Define your session modes:

Each mode can have:
- `label`: Display name in selector
- `firefox`, `vscode`, etc.: App-specific settings
- `workspaces`: Workspace assignments

Workspaces are defined by number (1, 2, 3, ...):
```yaml
workspaces:
  1:
    - app1
    - app2
  2:
    - app3
```

### Mode-level App Settings

Set default parameters for an app in a mode:

```yaml
modes:
  work:
    firefox:
      profile: work
      urls:
        - https://example.com
        - https://another.com
    vscode:
      workspace: ~/Work.project.code-workspace
```

## Apps.yaml Structure

```yaml
firefox:
  cmd: ["firefox", "-P", "{profile|default}"]
  append_param: "urls"
  internal_reuse: true

vscode:
  cmd: ["code", "--reuse-window", "{workspace|}"]
  primary_param: "workspace"
  internal_reuse: true
```

### App Options

| Option | Description | Default |
|--------|-------------|---------|
| `cmd` | Command to launch app | `[app_key]` |
| `check` | Process pattern to check for running app | `app_key` |
| `flags` | Conditional command flags | `{}` |
| `append_param` | Param to append URL/list args | `null` |
| `primary_param` | Main parameter for app | `value` |
| `internal_reuse` | Reuse existing instance? | `true` |

### Template Variables

Use `{variable|default}` syntax in commands:

- `{profile}` - Firefox profile name
- `{workspace}` - VSCode workspace path
- `{urls}` - List of URLs
- `{server}` - Discord server name

### Advanced Examples

#### Firefox with multiple profiles

```yaml
firefox:
  cmd: ["firefox", "-P", "{profile|default}", "--new-window"]
  append_param: "urls"
  internal_reuse: true
```

Usage in mode:
```yaml
modes:
  work:
    firefox:
      profile: work
      urls:
        - https://github.com
        - https://example.com
```

#### VSCode with workspace

```yaml
vscode:
  cmd: ["code", "--reuse-window", "{workspace|}"]
  primary_param: "workspace"
  internal_reuse: true
```

Usage in mode:
```yaml
modes:
  work:
    workspaces:
      2:
        - vscode: "~/Work/Project.code-workspace"
```

#### Discord with flags

```yaml
discord:
  cmd: ["discord"]
  check: "discord"
  flags:
    background: "--start-minimized"
  internal_reuse: false
```

Usage in mode:
```yaml
modes:
  gaming:
    workspaces:
      2:
        - discord:
            background: true
```

## Mode Switching

### Use Multiple Workspaces

- **Workspace 1**: Primary app (browser, IDE)
- **Workspace 2**: Secondary apps (terminal, media)
- **Workspace 3**: Utilities (pomodoro, notes)

### Hardware-Aware Modes

```yaml
modes:
  low-power:
    label: "Battery Saver"
    # Light mode for battery
    
  gaming:
    label: "Gaming"
    # Heavy mode (disabled on battery)
```

## GNOME Extensions

SessionIntent can enable or disable GNOME Shell extensions per mode.

### Extension Configuration

```yaml
modes:
  gaming:
    label: "Gaming"
    extensions:
      enable:
        - dash-to-panel
        - caffeine
      disable:
        - workspace-indicator
    workspaces:
      1:
        - steam
      2:
        - discord
```

### Extension Names

You can reference extensions by:

- **Display name**: `Dash to Panel`, `Caffeine`, `Workspace Indicator`
- **Hyphenated name**: `dash-to-panel`, `caffeine`, `workspace-indicator`
- **UUID**: `dash-to-panel@jderose9.github.com`, `caffeine@patapon.info`

The resolver handles all these formats.

### Available Extensions

SessionIntent includes a registry of common GNOME extensions. You can use any of these names in your config:

- `dash to panel` - Dash to panel
- `caffeine` - Prevent auto-suspend
- `workspace indicator` - Show workspace number
- `hide top bar` - Auto-hide top bar
- And 80+ more...

### Error Handling

If an extension doesn't exist, SessionIntent will show:

```log
Error: Extension 'unknown-extension' does not exist
```

## Tips

1. **Start simple** - Define 2-3 basic modes first
2. **Test in dev mode** - `sessionintent --dev --mode work`
3. **Keep configs git-trackable** - Store in `~/.config/sessionintent/`
4. **Use labels** - Make mode names descriptive
5. **Profile per mode** - Separate Firefox profiles for cleaner sessions

## Troubleshooting

### App won't reused

Check `internal_reuse: false` or `check` pattern mismatch.

### Wrong workspace

Ensure workspace numbers match mode config. Switch happens *before* app launch.

### Mode not showing

Check `hardware_profiles` - battery mode might be disabled.

### Template not resolving

Verify format: `{param|default}` with pipe and braces.
