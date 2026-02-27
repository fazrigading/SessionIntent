# SessionIntent - Project Suggestions

## Current Status

SessionIntent is a well-designed session orchestration system for GNOME Wayland on Fedora 43. It provides:
- Intent-based session control via YAML configuration
- Hardware-aware mode switching (battery/AC detection)
- Workspace orchestration with advisory placement
- Safe, non-destructive operation with panic reset

## Project Status: ✅ RESTRUCTURED

SessionIntent has now been restructured with:
- Complete project organization
- Full documentation suite
- Fedora COPR packaging setup
- Python packaging with pyproject.toml
- Installation script for all distros
- Unit tests and CI/CD pipeline

All issues from the original suggestions have been addressed.

## Structure Issues (RESOLVED)

1. ✅ **Project structure** - Organized into proper directories
2. ✅ **Essential files** - README.md, LICENSE, requirements.txt, pyproject.toml created
3. ✅ **Documentation** - Separate docs/ folder with comprehensive guides
4. ✅ **Packaging** - sessionintent.spec for Fedora COPR included
5. ✅ **Testing** - Unit tests and CI/CD configured

---

## Implementation Status

| Task | Status |
| ---- | ------ |
| Create proper project structure | ✅ Complete |
| Add README.md with quick start | ✅ Complete |
| Add LICENSE file | ✅ Complete (MIT) |
| Create requirements.txt | ✅ Complete |
| Convert to pyproject.toml package | ✅ Complete |
| Create sessionintent.spec for COPR | ✅ Complete |
| Write install.sh script | ✅ Complete |
| Add unit tests | ✅ Complete |
| Add CI/CD pipeline | ✅ Complete |
| Create man page | ✅ Complete |
| Write CONTRIBUTING.md | ✅ Complete |
| Add CHANGELOG.md | ✅ Complete |
| Create example configs | ✅ Complete |
| Add comprehensive docs | ✅ Complete |

## Suggested Project Structure

```
SessionIntent/
├── README.md                         # Main project documentation
├── LICENSE                           # MIT/Apache-2.0 or similar
├── requirements.txt                  # Python dependencies
├── pyproject.toml                    # Modern Python package config
├── src/                              # Main package
│   ├── __init__.py                   # Package exports
│   ├── __main__.py                   # CLI entry point
│   ├── constants/                    # Configuration constants
│   ├── config/                       # Configuration management
│   ├── hardware/                     # Hardware detection
│   ├── app/                          # Application management
│   ├── workspace/                    # Workspace management
│   ├── extensions/                   # GNOME Shell extensions
│   ├── ui/                           # User interface
│   ├── session/                      # Session orchestration
│   │   ├── manager.py                # Main orchestrator class
│   │   └── state.py                  # State persistence
│   └── cli/                          # CLI utilities
├── apps.yaml.example                 # Example apps registry
├── config.yaml.example               # Example config
├── man/                              # Manual pages
│   └── sessionintent.1
├── scripts/
│   ├── install.sh                    # Installation script for all distros
│   └── setup-autostart.sh            # Helper for autostart configuration
├── packaging/
│   ├── fedora/
│   │   └── sessionintent.spec        # RPM spec file (for COPR)
│   └── Arch/
│       └── PKGBUILD                  # AUR package build file
├── tests/                            # Unit tests
│   ├── test_config/
│   ├── test_hardware/
│   ├── test_app/
│   ├── test_extensions/
│   ├── test_workspace/
│   ├── test_ui/
│   └── test_session/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # CI/CD pipeline
│       └── release.yml               # Release automation
├── .gitignore                        # Exclude config files, build artifacts
├── .editorconfig                     # Consistent code style
├── CONTRIBUTING.md                   # Contribution guidelines
├── AGENTS.md                        # AI agent guidelines
└── docs/                             # Additional documentation
    ├── architecture.md               # Detailed architecture docs
    ├── configuration-guide.md        # Config tutorial
    ├── modes.md                      # Mode examples
    ├── installation.md               # Installation guide
    └── FAQ.md                        # Common questions
```

---

## Key Suggestions

### 1. Code Quality & Maintainability

**a. Add type hints throughout**
```python
# Currently partial, should be complete:
def launch_app(self, app_key: str, params: Dict[str, Any]) -> None:
```

**b. Add logging instead of print statements**
- Use Python's `logging` module
- Add `--verbose` flag
- Log to file for debugging

**c. Add error handling**
- Catch YAML parsing errors
- Handle missing dependencies gracefully
- Better error messages for all failure modes

**d. Separate concerns**
- Move app controllers to separate module
- Create dedicated config validator
- Isolate GNOME shell interaction

### 2. Configuration Improvements

**a. Schema validation**
- Add JSON Schema for config/apps files
- Validate at load time
- Provide helpful error messages

**b. Merge strategy for configs**
- System apps + User apps should merge cleanly
- Allow user to override system defaults
- Document override precedence

**c. Hot reload support**
- Watch config files for changes
- Reload without restart
- Signal-based reload (SIGHUP)

### 3. Feature Enhancements

**a. Session persistence**
- Persist window states
- Remember last active mode
- Auto-recover after crash

**b. Advanced workspace management**
- Support for multiple monitors
- Workspace naming
- Workspace cycling

**c. mode transitions**
- Smooth transitions between modes
- Pause/resume support
- Session snapshots

**d. Extensions system**
- Plugin architecture
- Custom app controllers
- hooks for external scripts

### 4. Distribution & Packaging

**a. RPM spec file (CRITICAL)**
- Missing despite COPR focus
- Should handle:
  - System-wide apps.yaml
  - Config file placement
  - Autostart desktop file
  - Man page installation

**b. Python packaging**
- Convert to proper package with `pyproject.toml`
- Use `setuptools` or `poetry`
- Provide `sessionintent` CLI entry point

**c. Installation options**
- `install.sh` for all distros
- Snap package (universal Linux)
- Flatpak (sandboxed)
- Distro-specific packages (Deb, Arch)

### 5. Testing & CI

**a. Unit tests**
- Test YAML parsing
- Test AC detection
- Test template resolution
- Test config validation

**b. Integration tests**
- Test full workflow in dev mode
- Test config loading from multiple sources
- Test mode switching

**c. CI/CD**
- Run tests on PR
- Linting (ruff, mypy)
- Auto-generate docs
- Release automation

### 6. Documentation

**a. README improvements**
- Quick start guide
- Installation instructions
- Basic configuration example
- Screenshot/GIF of UI in action

**b. Config examples**
- Multiple ready-to-use configs
- Mode-specific examples
- Common workflow patterns

**c. Troubleshooting guide**
- Common issues and fixes
- Debugging tips
- Log analysis

### 7. User Experience

**a. Better error messaging**
- Show which config file failed
- Indicate line numbers for YAML errors
- Suggest solutions

**b. CLI improvements**
- Tab completion support
- `--dry-run` (currently `--dev`)
- `--status` to show current mode
- `--list` to show available modes

**c. Visual feedback**
- Desktop notifications for mode changes
- Status indicator in panel
- Log viewer

### 8. Security & Safety

**a. Configsanity checks**
- Validate file permissions on config
- Warn about world-readable configs
- Sanitize template inputs

**b. privilege separation**
- Run as user (currently does)
- No sudo required
- Clear documentation on this

### 9. Performance

**a. Lazy loading**
- Load apps on demand
- Cache expensive operations
- Avoid redundant file reads

**b. async support**
- Use asyncio for.parallel app launches
- Faster mode switching
- Better resource utilization

### 10. Community & Growth

**a. Contribution guide**
- Clear how-to for beginners
- Good first issues
- Code of conduct

**b. changelog**
- Keep CHANGELOG.md
- Document breaking changes
- Version information

**c. Support channels**
- Matrix/Discord channel
- Forum category
- Issue templates

---

## Priority Implementation Order

### Critical (Project Must-Haves)
1. ✅ Create `README.md` with quick start
2. ✅ Add `LICENSE` file
3. ✅ Generate `requirements.txt`
4. ✅ Convert to proper Python package (`pyproject.toml`)
5. ✅ Create `sessionintent.spec` for COPR
6. ✅ Write `install.sh` script
7. ✅ Add unit tests (basic coverage)
8. ✅ Create `config.yaml.example` from `my_personal_config.yaml`

### High Priority
9. Add JSON Schema for config validation
10. Improve error messages throughout
11. Add `--status` CLI flag
12. Create man page
13. Write CONTRIBUTING.md
14. Add CI/CD pipeline

### Medium Priority
15. Add logging system
16. Create docs/ folder structure
17. Add more comprehensive tests
18. Implement window state persistence

### Low Priority (Nice to Have)
19. Plugin system
20. Time-based auto-switching
21. Desktop notifications
22. Theme support

---

## Quick Wins (Do First)

### 1. Create README.md (20 minutes)
```markdown
# SessionIntent
A declarative session orchestration system for GNOME Wayland

## Quick Start
1. Install: `./install.sh` or `pip install -e .`
2. Configure: `~/.config/sessionintent/config.yaml`
3. Launch: `python3 -m src --prompt`

## Features
- Intent-based session modes
- Hardware-aware (battery vs AC)
- Non-destructive operations
- ...etc
```

### 2. Add requirements.txt (5 minutes)
```
PyYAML>=6.0
```

### 3. Create pyproject.toml (15 minutes)
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "sessionintent"
version = "0.1.0"
description = "A declarative session orchestration system for GNOME Wayland"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "PyYAML>=6.0",
]

[project.scripts]
sessionintent = "src.__main__:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]
```

### 4. Add .gitignore (5 minutes)
```
*.py[cod]
__pycache__/
*.yaml.bak
*.pyc
.env/
.venv/
dist/
build/
*.egg-info/
*.log
```

### 5. Create example configs (30 minutes)
- Copy `config.yaml` → `config.yaml.example`
- Copy `apps.yaml` → `apps.yaml.example`
- Add comments explaining each option

---

## Conclusion

SessionIntent has a solid foundation but needs:
1. **Structure** - Proper project organization
2. **Packaging** - RPM spec for COPR (critical)
3. **Testing** - CI/CD and test suite
4. **Documentation** - Better guides and examples
5. **Distribution** - Multiple installation methods

Implementing these suggestions will transform SessionIntent from a working prototype into a production-ready tool ready for Fedora COPR distribution and community adoption.
