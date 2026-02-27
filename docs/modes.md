# SessionIntent - Modes Documentation

This document showcases various mode configurations for different workflows.

## Basic Modes

### Browsing / Chilling

```yaml
modes:
  browsing:
    label: "Browsing / Chilling"
    firefox:
      profile: chill
    workspaces:
      1:
        - firefox
      2:
        - ytmdesktop
```

**Use case**: Casual surfing, streaming music

### Work / Research

```yaml
modes:
  work:
    label: "Work / Research"
    firefox:
      profile: research
    workspaces:
      1:
        - firefox
        - obsidian
        - zotero
      2:
        - vscode: "~/Work/ResearchExperiment.code-workspace"
        - terminal
      3:
        - gnome-pomodoro
        - ytmdesktop
```

**Use case**: Coding, writing, research with multiple tools

### Gaming

```yaml
modes:
  gaming:
    label: "Gaming
    workspaces:
      1:
        - lutris
        - steam
      2:
        - discord:
            server: none
            background: true
```

**Use case**: Game sessions with Discord (background)

### Contributor

```yaml
modes:
  contributor:
    label: "Contributor Mode"
    firefox:
      profile: contributor
      urls:
        - https://github.com/fazrigading/repo
        - https://github.com/fazrigading/repo/issues
        - https://github.com/fazrigading/repo/pulls
    workspaces:
      1:
        - firefox
      2:
        - vscode: "~/Work/Repo.code-workspace"
      3:
        - discord:
            server: Repo
```

**Use case**: Open source contributions

### Tinkering

```yaml
modes:
  tinkering:
    label: "Linux Tweaking"
    workspaces:
      1:
        - firefox:
            urls:
              - https://www.youtube.com
              - https://archlinux.org
      2:
        - extension-manager
        - terminal
```

**Use case**: System administration, learning

## Advanced Modes

### Low-Power Mode

Optimized for battery life:

```yaml
modes:
  low-power:
    label: "Battery Saver"
    hardware:
      battery_only: true
    firefox:
      profile: minimal
      urls: []
    workspaces:
      1:
        - firefox
        - obsidian
```

**Features**:
- Disables media apps
- Uses minimal Firefox profile
- Single workspace

### Presentation Mode

Clean, distraction-free:

```yaml
modes:
  presentation:
    label: "Presentation"
    firefox:
      profile: presentation
      urls:
        - https://example.com/presentation
    workspaces:
      1:
        - firefox
    settings:
      notifications: "muted"
      background: "clear"
```

**Features**:
- Single focused app
- Muted notifications
- Minimal workspace

### Debug / Incident Mode

For troubleshooting:

```yaml
modes:
  debug:
    label: "Debug / Incident"
    workspaces:
      1:
        - terminal
        - firefox: {urls: ["https://localhost:8080"]}
      2:
        - gnome-system-log
        - wireshark
```

**Features**:
- Terminal ready
- Log viewers
- Network tools

## Time-Based Modes

You can create modes that auto-switch:

```yaml
modes:
  morning:
    label: "Morning Routine"
    schedule:
      time: "08:00"
      days: [monday, tuesday, wednesday, thursday, friday]
    firefox:
      profile: morning
      urls:
        - https://news.ycombinator.com
        - https://reddit.com
    workspaces:
      1:
        - firefox
        - terminal
```

## Custom Mode Template

Copy and customize:

```yaml
modes:
  your-mode-name:
    label: "Your Mode Label"
    firefox:
      profile: your-profile
      urls: []
    vscode:
      workspace: ""
    workspaces:
      1:
        - primary-app
      2:
        - secondary-app
      3:
        - tertiary-app
```

## Hardware-Aware Configuration

Use battery detection to disable heavy modes:

```yaml
hardware_profiles:
  battery:
    disable_modes: [gaming, video-editing, rendering]
  plugged:
    allow_all: true
```

Now gaming mode will only show when plugged in.

## Mode Priority

When multiple modes match, the first defined takes precedence. Order your modes by priority:

```yaml
modes:
  default: ...     # Lowest priority
  work: ...        # Medium priority
  gaming: ...      # Highest priority (if AC only)
```

## Mode Transitions

SessionIntent doesn't kill apps during transitions. Apps from previous mode stay running unless explicitly stopped.

### Best Practices

1. **Avoid conflicts** - Don't assign same app to multiple modes with different configs
2. **Use separate profiles** - Firefox profile per mode avoids conflicts
3. **Workspace cleanup** - Manually clear unused workspaces if needed
