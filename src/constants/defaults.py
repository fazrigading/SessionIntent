"""
SessionIntent Default Apps
Default applications configuration embedded as YAML string.
Parsed at runtime if no user config exists.
"""

DEFAULT_APPS = """firefox:
  cmd: ["firefox", "-P", "{profile|default}"]
  append_param: "urls"
  internal_reuse: true
vscode:
  cmd: ["code", "--reuse-window", "{workspace|}"]
  primary_param: "workspace"
  internal_reuse: true
discord:
  cmd: ["discord"]
  check: "discord"
  flags:
    background: "--start-minimized"
  internal_reuse: false
terminal:
  cmd: ["gnome-terminal"]
  check: false
  internal_reuse: true
"""

"""
SessionIntent Default Configuration
Default session configuration embedded as YAML string.
Parsed at runtime if no user config exists.
"""

DEFAULT_CONFIG = """version: 1
defaults:
  ask_before_kill: true
  reuse_workspaces: true
  wait_window: 15

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
"""
