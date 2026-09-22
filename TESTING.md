# Testing SessionIntent

## Developer Mode

SessionIntent includes a **Developer Mode** for safe testing without side effects.
Global flags (`--dev`, `--config`, `--backend`) come before the command.

### How to Test

#### 1. Test a specific mode

```bash
sessionintent --dev apply browsing
```

This simulates switching workspaces and launching apps defined in the "browsing" mode.

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
sessionintent --dev select
```

> Note: UI still shows, but actions are dry-run. Without `wofi`/`rofi`,
> selection falls back to the terminal (TUI).

#### 5. Test status, listing, and preview

```bash
sessionintent status   # Show status
sessionintent list     # List modes
sessionintent preview work  # Show what apply would do
sessionintent reload   # Reload configuration
```

#### 6. Test another backend

```bash
sessionintent --dev --backend ewmh apply browsing
sessionintent --dev --backend sway list
```

## Unit Tests

### Running Tests

```bash
# Install test dependencies (creates .venv with pytest, pytest-cov, ruff, mypy)
uv sync

# Run all tests
uv run pytest

# Run with verbosity
uv run pytest -v --tb=short

# Run a single test file
uv run pytest tests/test_session/test_manager.py

# Run with coverage
uv run pytest --cov=sessionintent --cov-report=term-missing
```

### Quality Gates

Every change must pass, in order:

```bash
uv run ruff check src/ tests/
uv run mypy src/
uv run pytest
uv build && uv run sessionintent version
```

See `.github/workflows/ci.yml` — CI runs the same checks.

### Test Structure

```
tests/
├── test_app/          # App launching, templates, detection, setup, cache
├── test_cli/          # Subcommand parsing
├── test_config/       # Loading, validation, v1→v2 migration
├── test_constants/    # Paths (incl. XDG) and defaults
├── test_extensions/   # GNOME extension management
├── test_hardware/     # Power detection
├── test_plugins/      # Plugin system and manager wiring
├── test_providers/    # Detection, factory, TUI, per-desktop providers
├── test_session/      # SessionManager, state, notifications
├── test_ui/           # Selector and display formatting
└── test_workspace/    # GNOME workspace manager
```

Provider and detection tests mock `subprocess` and the environment —
no desktop session is needed. Anything requiring real hardware
(River/Labwc runs, multi-DE matrix) is a manual checklist, see
`plans/05-testing-and-ci.md`.

### Writing Tests

1. **Unit Tests**: Test individual functions; mock `subprocess` and I/O.
2. **Provider Tests**: Assert command construction, not execution.
3. **Config Tests**: Validate YAML parsing and schema errors.

Example:

```python
def test_config_loading(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("version: 2\nmodes:\n  work:\n    workspaces: {}\n")
    manager = SessionManager(config_path=str(config_path), dev_mode=True)
    assert manager.config.get("version") == 2
```

---

## Manual Testing

### Step-by-Step Testing

1. **Initialize Config**
   ```bash
   sessionintent init
   ```

2. **Edit config** (add test mode)
   ```bash
   nano ~/.config/sessionintent/config.yaml
   ```

3. **Test dry-run**
   ```bash
   sessionintent --dev apply test-mode
   ```

4. **Test selection** (if UI available)
   ```bash
   sessionintent
   ```

5. **Verify state**
   ```bash
   sessionintent status
   # or
   cat ~/.local/state/sessionintent/current
   ```

---

## Debugging

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

### Logs

SessionIntent logs to `~/.local/state/sessionintent/sessionintent.log`.

---

## Testing Scenarios

### Scenario 1: App Not Launching

1. Test in dev mode
2. Check pgrep pattern
3. Verify `internal_reuse` setting

### Scenario 2: Wrong Workspace

1. Check workspace numbers in config
2. Verify backend with `sessionintent --dev --backend <name> apply <mode>`
3. Test with `--dev` to see output

### Scenario 3: Template Not Resolving

1. Check YAML syntax
2. Verify parameter in mode config
3. Test with simple example
