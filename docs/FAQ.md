# SessionIntent - FAQ

## General Questions

### What is SessionIntent?

SessionIntent is a session orchestration system for GNOME Wayland. It lets you switch between different "modes" (work, gaming, browsing, etc.) that automatically launch and organize your applications across workspaces.

### Why create another session manager?

Existing tools either:
- Are too complex (window manager configurations)
- Don't integrate well with GNOME
- Lack hardware awareness
- Are destructive (kill processes)

SessionIntent focuses on simplicity, safety, and GNOME integration.

### Is SessionIntent production-ready?

Yes! We have:
- Stable core functionality
- Extensive testing (unit + integration)
- Documentation
- Active development

### Is SessionIntent distro-agnostic?

Designed for Linux with GNOME Wayland. It should work on any Linux distribution running GNOME.
- Python 3.10+
- PyYAML
- GNOME Wayland session

## Configuration

### How do I add a new app to app registry?

Edit `~/.config/sessionintent/apps.yaml`:

```yaml
myapp:
  cmd: ["myapp"]
  check: "myapp"
```

### Can I have the same app in multiple modes?

Yes! Use different profiles:

```yaml
# In browsing mode
firefox:
  profile: chill

# In work mode
firefox:
  profile: work
```

### How do I reset to defaults?

```bash
sessionintent --panic  # Clear current state
rm ~/.config/sessionintent/config.yaml
sessionintent --init   # Recreate defaults
```

### Where are configs stored?

- User configs: `~/.config/sessionintent/`
- System configs: `/usr/share/sessionintent/`
- State: `$XDG_STATE_HOME/sessionintent/`

## Troubleshooting

### App not launching?

1. Check if app is in `apps.yaml`
2. Verify app name matches `pgrep` output
3. Try `sessionintent --dev --mode work` to see dry-run

### App launching multiple times?

Set `internal_reuse: true` in `apps.yaml`:

```yaml
firefox:
  internal_reuse: true
```

### Wrong workspace?

Workspaces switch *before* app launches. Ensure you launch while focused on the target workspace.

### Mode not showing in selector?

Check:
- Hardware profile (battery mode disabled?)
- Mode name in `modes:` section
- YAML syntax (use `sessionintent --dev` to check)

### UI (wofi/rofi) not working?

Install one:

```bash
# Fedora
sudo dnf install wofi

# Ubuntu/Debian
sudo apt install rofi
```

## Usage

### Can I use SessionIntent without wofi/rofi?

Yes, use `--mode` directly:

```bash
sessionintent --mode work
```

### How do I check current session?

```bash
sessionintent --status
# or
cat ~/.local/state/sessionintent/current
```

### Can I bind to keyboard shortcut?

Yes! In GNOME Settings → Keyboard → Custom Shortcuts:

```
Name: Session Intent
Command: sessionintent
Shortcut: Super+M
```
Name: Session Intent
Command: sessionintent
Shortcut: Super+M
```

### Does SessionIntent kill apps?

No! SessionIntent:
- Never kills processes by default
- Only reuses or launches apps
- Has separate commands for different behaviors:
  - `--panic`: Clear state only (no app termination)
  - `--quit`: Gracefully close managed apps (SIGTERM)
  - `--kill`: Force kill managed apps (SIGKILL)

## Advanced

### How does template resolution work?

Use `{param|default}` syntax:

```yaml
cmd: ["firefox", "-P", "{profile|default}"]
```

With params:
```yaml
firefox:
  profile: work  # -> "firefox -P work"
```

### Can I use environment variables?

Not directly, but use absolute paths:

```yaml
cmd: ["code", "--workspace", "/home/user/${MY_VAR}/project.code-workspace"]
```

### How fast is mode switching?

Typically <500ms on modern hardware.Factors:
- Number of apps
- App launch times
- System load

## Development

### How do I test changes?

Use dev mode:

```bash
python3 sessionintent.py --dev --mode work
```

### How do I run tests?

```bash
python3 -m pytest tests/
```

### How do I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md)

## Distribution

### How do I package for Fedora?

See `packaging/fedora/sessionintent.spec`

### How do I build from source?

```bash
git clone https://github.com/fazrigading/SessionIntent.git
cd SessionIntent
./INSTALL.sh
```

## Future

### Will SessionIntent support other window managers?

Possibly, though it's currently GNOME-specific (uses GNOME D-Bus API).

### Will there be a GUI configurator?

Not planned. SessionIntent stays CLI-based for simplicity and Git-trackability.

### Can I extend SessionIntent?

Yes! Support is planned for:
- Plugins
- Custom app controllers
- Hooks/scripts

## Community

### Where can I get help?

- GitHub Issues
- Project Discord
- Fedora Forums

### How do I report bugs?

1. Check existing issues
2. Include your config
3. Use `--dev` mode output
4. Describe steps to reproduce

### Can I request features?

Yes! Open an issue with:
- Use case
- Proposed solution
- Example config
