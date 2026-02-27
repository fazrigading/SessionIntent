# SessionIntent - CONTRIBUTING Guide

Thank you for your interest in contributing to SessionIntent! This document explains how to contribute to the project.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributions from everyone regardless of experience level.

## How Can I Contribute?

### 1. Following Project Roadmap

Check [ROADMAP.md](docs/ROADMAP.md) for planned features and areas where contributions are welcome. Pick an item that interests you and open a discussion issue before starting major work.

### 2. Reporting Bugs

Before reporting a bug:
- Check if it's already reported in [Issues](https://github.com/fazrigading/SessionIntent/issues)
- Ensure you're using the latest version

To report a bug:
1. Use the bug report template
2. Describe the issue clearly
3. Include steps to reproduce
4. Attach config files (remove sensitive data)
5. Include output with `--dev` flag

### 3. Suggesting Features

Feature requests should:
- Clearly describe the use case
- Explain the proposed implementation
- Include example config
- Consider backward compatibility

### 4. Pull Requests

#### Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Format code
6. Open a pull request

#### Guidelines

- Follow existing code style
- Write clear commit messages
- Keep PRs focused (one feature per PR)
- Update documentation
- Wait for CI checks to pass

## Development Setup

### Prerequisites

- Python 3.10+
- pip
- wofi or rofi (for UI testing)

### Local Installation

```bash
# Clone repository
git clone https://github.com/fazrigading/SessionIntent.git
cd SessionIntent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
python3 -m pytest

# Run specific test file
python3 -m pytest tests/test_config/

# Run with coverage
python3 -m pytest --cov=src --cov-report=term-missing
```

### Running in Dev Mode

```bash
# Test dry-run
sessionintent --dev --mode work

# Test with custom config
sessionintent --dev --mode work --config tests/test_configs/valid.yaml
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints
- Keep functions under 50 lines
- Use meaningful names

### YAML Style

- Use 2 spaces indentation
- Sort keys alphabetically
- Add comments for complex configs
- Use consistent formatting

## Documentation

All documentation is in the `docs/` directory:

- `README.md` - Main project overview
- `ARCHITECTURE.md` - System architecture
- `CONFIGURATION-GUIDE.md` - Config tutorial
- `FAQ.md` - Common questions
- `INSTALLATION.md` - Installation manual
- `MODES.md` - Mode examples
- `ROADMAP.md` - Project roadmap

## Testing

### Unit Tests

Test individual components:

```python
def test_config_loading():
    manager = SessionManager(dev_mode=True)
    assert manager.config is not None
```

### Integration Tests

Test full workflows:

```python
def test_mode_switching():
    manager = SessionManager(dev_mode=True)
    manager.apply_mode("work")
```

## Release Process

1. Update version in `pyproject.toml`
2. Update changelog in `CHANGELOG.md`
3. Create git tag
4. Push to master
5. Create GitHub release

## Questions?

- Open an issue
- Start a new discussion
<!-- - Join our Discord
- Email project maintainers -->

Thank you for having interest to contribute on SessionIntent project!
