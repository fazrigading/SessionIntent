# Testing SessionIntent

## Developer Mode

SessionIntent includes a **Developer Mode** for safe testing without side effects.

### New Arguments

- `--dev`: Enables "dry-run" mode. Prints commands instead of executing them.
- `--mode <name>`: Directly apply a specific mode, bypassing the selection menu.
- `--config <path>`: Specify a custom configuration file.
- `--panic`: Clear current state (in dry-run).

### How to Test

#### 1. Test a specific mode

```bash
python3 sessionintent.py --dev --mode browsing
```

This will simulate switching workspaces and launching apps defined in the "browsing" mode.

#### 2. Test with a custom config

```bash
python3 sessionintent.py --dev --mode work --config tests/test_configs/valid.yaml
```

#### 3. Test the Panic reset

```bash
python3 sessionintent.py --dev --panic
```

#### 4. Test the UI selector

```bash
python3 sessionintent.py --dev --prompt
```

> Note: UI still shows, but actions are dry-run.

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
   python3 sessionintent.py --init
   ```

2. **Edit config** (add test mode)
   ```bash
   nano ~/.config/sessionintent/config.yaml
   ```

3. **Test dry-run**
   ```bash
   python3 sessionintent.py --dev --mode test-mode
   ```

4. **Test selection** (if UI available)
   ```bash
   python3 sessionintent.py --prompt
   ```

5. **Verify state**
   ```bash
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
