# Testing SessionIntent

## Developer Mode

SessionIntent includes a **Developer Mode** for safe testing without side effects.

### New Arguments

- `--dev` (-d): Enables "dry-run" mode. Prints commands instead of executing them.
- `--mode <name>` (-m): Directly apply a specific mode, bypassing the selection menu.
- `--config <path>` (-c): Specify a custom configuration file.
- `--panic` (-P): Clear current state (no app termination).
- `--quit` (-q): Gracefully close managed apps.
- `--clear`: Clear state files only.
- `--kill` (-k): Force kill managed apps.
- `--status` (-s): Show current session status.
- `--list` (-l): List available modes.
- `--reload` (-r): Reload configuration files.
- `--suspend` (-S): Suspend session.

### How to Test

#### 1. Test a specific mode

```bash
sessionintent -d -m browsing
# or
sessionintent --dev --mode browsing
```

This will simulate switching workspaces and launching apps defined in the "browsing" mode.

#### 2. Test with a custom config

```bash
sessionintent -d -m work -c tests/test_configs/valid.yaml
# or
sessionintent --dev --mode work --config tests/test_configs/valid.yaml
```

#### 3. Test the Panic reset

```bash
sessionintent -d -P
# or
sessionintent --dev --panic
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
sessionintent -s          # Show status
sessionintent -l          # List modes
sessionintent -s -l       # Show both
sessionintent -r -s       # Reload and show status
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
pytest tests/test_sessionintent.py::TestSessionManager::test_init_dev_mode

# Run with coverage
pytest --cov=sessionintent --cov-report=xml
```

### Test Structure

```
tests/
├── test_sessionintent.py      # Core functionality tests
├── test_configs/              # Valid and invalid test configs
│   ├── valid_config.yaml
│   └── invalid_config.yaml
└── test_app_controllers.py    # App controller tests (future)
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
