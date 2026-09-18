# Testing SessionIntent

## Developer Mode

SessionIntent includes a **Developer Mode** for safe testing without side effects.

### Commands

- `apply <name>`: Directly apply a specific mode, bypassing the selection menu.
- `--config <path>`: Specify a custom configuration file (global flag).
- `panic`: Clear current state (no app termination).
- `quit`: Gracefully close managed apps.
- `clear`: Clear state files only.
- `kill`: Force kill managed apps.
- `status`: Show current session status.
- `list`: List available modes.
- `reload`: Reload configuration files.
- `suspend`: Suspend session.

Global flags (`--dev`, `--config`, `--backend`) come before the command.

### How to Test

#### 1. Test a specific mode

```bash
sessionintent --dev apply browsing
```

This will simulate switching workspaces and launching apps defined in the "browsing" mode.

#### 2. Test with a custom config

```bash
sessionintent --dev --config examples/config.example.yaml apply work
```

#### 3. Test the Panic reset

```bash
sessionintent --dev panic
```

#### 4. Test the UI selector (default behavior)

```bash
sessionintent
# or with dev mode
sessionintent -d
```

> Note: UI still shows, but actions are dry-run.

#### 5. Test status and listing

```bash
sessionintent status   # Show status
sessionintent list     # List modes
sessionintent reload   # Reload configuration
```

---

## Unit Tests

### Running Tests

```bash
# Installpytest
pip install pytest

# Run all tests
pytest

# Run with verbosity
pytest -v

# Run specific test
pytest tests/test_session/test_manager.py -q

# Run with coverage
pytest --cov=sessionintent --cov-report=xml
```

### Test Structure

```
tests/
├── test_app/          # App launching, templates, detection, setup, cache
├── test_cli/          # Argument parsing
├── test_config/       # Config loading and validation
├── test_constants/    # Paths and defaults
├── test_extensions/   # GNOME extension management
├── test_hardware/     # Power detection
├── test_session/      # SessionManager and state
├── test_ui/           # Selector and display formatting
└── test_workspace/    # Workspace switching
```

### Writing Tests

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test full workflows
3. **Config Tests**: Validate YAML parsing

Example:

```python
def test_config_loading():
    manager = SessionManager(dev_mode=True)
    manager.load_config()
    assert manager.config is not None
```

---

## Manual Testing

### Step-by-Step Testing

1. **Initialize Config**
   ```bash
   sessionintent -i
   ```

2. **Edit config** (add test mode)
   ```bash
   nano ~/.config/sessionintent/config.yaml
   ```

3. **Test dry-run**
   ```bash
   sessionintent -d -m test-mode
   ```

4. **Test selection** (if UI available)
   ```bash
   sessionintent
   ```

5. **Verify state**
   ```bash
   sessionintent -s
   # or
   cat ~/.local/state/sessionintent/current
   ```

---

## Debugging

### Enable Verbose Output

```bash
# Add print statements or use logging
python3 -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

### Check Config Validation

```bash
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

### Test App Detection

```bash
# Check if app exists
which firefox

# Test pgrep pattern
pgrep -f firefox
```

---

##常见 Testing Scenarios

### Scenario 1: App Not Launching

1. Test in dev mode
2. Check pgrep pattern
3. Verify `internal_reuse` setting

### Scenario 2: Wrong Workspace

1. Check workspace numbers in config
2. Verify GNOME shell D-Bus commands
3. Test with `--dev` to see output

### Scenario 3: Template Not Resolving

1. Check YAML syntax
2. Verify parameter in mode config
3. Test with simple example

---

## CI Testing

SessionIntent uses GitHub Actions for CI:

```bash
# Run all checks locally
make test
```

See `.github/workflows/ci.yml` for details.
