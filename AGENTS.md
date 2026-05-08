# SessionIntent Agent Guidelines

This file provides guidelines for AI agents working on the SessionIntent codebase.

## Project Overview

SessionIntent is a declarative session orchestration system for GNOME Wayland written in Python 3.10+. The codebase is organized as a modular package under `src/`.

## Build, Lint, and Test Commands

### Prerequisites

```bash
pip install pytest ruff mypy PyYAML
```

### Lint and Typecheck

```bash
# Lint with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/
```

**Order**: lint → typecheck → test (as used in CI)

### Running Tests

```bash
# Run all tests
python3 -m pytest

# Run tests with coverage
python3 -m pytest --cov=src --cov-report=term-missing

# Run a single test file
python3 -m pytest tests/test_config/test_loader.py

# Run a single test class
python3 -m pytest tests/test_config/test_loader.py::TestLoadYamlFile

# Run a single test function
python3 -m pytest tests/test_config/test_loader.py::TestLoadYamlFile::test_load_valid_yaml

# Run tests in dev mode (verbose)
python3 -m pytest -v --tb=short
```

### Running the Application

```bash
# Via Python module
sessionintent --help

# Select mode via UI (default)
sessionintent

# Apply specific mode directly
sessionintent --mode browsing
sessionintent -m browsing

# Dev mode (dry-run)
sessionintent --dev --mode browsing
sessionintent -d -m browsing

# Status and listing
sessionintent --status
sessionintent -s
sessionintent --list
sessionintent -l

# Session control
sessionintent --panic          # Clear state (no app termination)
sessionintent -P
sessionintent --quit          # Gracefully close managed apps
sessionintent -q
sessionintent --clear         # Clear state files only
sessionintent --kill          # Force kill managed apps
sessionintent -k
sessionintent --suspend       # Suspend session

# Configuration
sessionintent --init / -i      # Initialize default configs and extension
sessionintent --setup          # Set up SessionIntent (scan apps)
sessionintent --reload        # Reload configuration
sessionintent -r
sessionintent --config <path> # Custom config file
sessionintent -c <path>
```

## Code Style Guidelines

### General Principles

- **PEP 8** compliance is required
- **Python 3.10+** compatibility
- Use **type hints** everywhere possible
- Write **docstrings** for all public functions
- Keep functions **small and focused** (under 50 lines)

### Naming Conventions

```python
# Variables and functions: snake_case
def get_available_modes():
    pass

# Classes: PascalCase
class SessionManager:
    pass

# Constants: UPPER_SNAKE_CASE
CONFIG_PATH = Path.home() / ".config" / "sessionintent"

# Private: leading underscore
def _build_command():
    pass
```

### Import Order

```python
# 1. Standard library
from __future__ import annotations

import os
import subprocess
from typing import Any

# 2. Third-party libraries
import yaml
import pytest

# 3. Local application imports (relative)
from .constants import CONFIG_PATH
from .config import load_config
from ..hardware import is_on_ac
```

### Type Hints

```python
# Use built-in types for Python 3.10+
from __future__ import annotations

from typing import Any

def launch_app(
    app_key: str,
    params: dict[str, Any],
    apps: dict[str, dict[str, Any]],
    dev_mode: bool = False,
) -> None:
    """Launch or reuse an application based on its definition."""
    pass
```

### Docstrings

```python
def is_on_ac() -> bool:
    """
    Check if the system is running on AC power.

    Returns:
        True if on AC power (plugged in), False if on battery.
        Defaults to True if power detection fails.
    """
    pass
```

### Error Handling

```python
# Use specific exception handling
try:
    subprocess.run(cmd, capture_output=True, check=True)
    return True
except subprocess.CalledProcessError:
    return False

# Raise descriptive errors
def load_yaml_file(file_path: Path) -> dict[str, Any]:
    if not file_path.exists():
        return {}
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {e}")
```

### File Organization

```
src/
├── __init__.py          # Package exports only
├── __main__.py          # CLI entry point
├── constants/           # Configuration constants
├── config/              # Configuration management
├── hardware/            # Hardware detection
├── app/                 # Application management
├── workspace/           # Workspace management
├── extensions/          # GNOME Shell extensions
├── ui/                  # User interface
├── session/             # Session orchestration
│   ├── manager.py      # Main orchestrator class
│   └── state.py        # State persistence
└── cli/                 # CLI utilities
```

### Test Organization

```python
# Test file naming: test_<module>.py
tests/
├── test_config/
│   ├── __init__.py
│   └── test_loader.py
├── test_hardware/
│   └── test_power.py
├── test_app/
├── test_extensions/
│   └── test_manager.py
├── test_workspace/
├── test_ui/
└── test_session/
    └── test_manager.py
```

### Module Exports

```python
# __init__.py should re-export public API
from .session import SessionManager
from .config import load_config, load_apps, init_default_configs
from .hardware import is_on_ac
from .ui import select_mode
from .workspace import switch_workspace
from .app import launch_app, is_running
from .extensions import apply_extensions, resolve_extension_id

__all__ = [
    "SessionManager",
    "load_config",
    "load_apps",
    "init_default_configs",
    "is_on_ac",
    "select_mode",
    "switch_workspace",
    "launch_app",
    "is_running",
    "apply_extensions",
    "resolve_extension_id",
]
```
