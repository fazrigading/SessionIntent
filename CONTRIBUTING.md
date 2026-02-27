# SessionIntent - CONTRIBUTING Guide

Thank you for your interest in contributing to SessionIntent! This document explains how to contribute to the project.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributions from everyone regardless of experience level.

## How Can I Contribute?

### 1. Reporting Bugs

Before reporting a bug:
- Check if it's already reported in [Issues](https://github.com/fazrigading/SessionIntent/issues)
- Ensure you're using the latest version

To report a bug:
1. Use the bug report template
2. Describe the issue clearly
3. Include steps to reproduce
4. Attach config files (remove sensitive data)
5. Include output with `--dev` flag

### 2. Suggesting Features

Feature requests should:
- Clearly describe the use case
- Explain the proposed implementation
- Include example config
- Consider backward compatibility

### 3. Pull Requests

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
pytest

# Run specific test file
pytest tests/test_sessionintent.py

# Run with coverage
pytest --cov=sessionintent
```

### Running in Dev Mode

```bash
# Test dry-run
python3 sessionintent.py --dev --mode work

# Test with custom config
python3 sessionintent.py --dev --mode work --config tests/test_configs/valid.yaml
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

## Project Structure

```
SessionIntent/
├── sessionintent.py          # Main orchestrator
├── requirements.txt          # Dependencies
├── pyproject.toml           # Package configuration
├── tests/                   # Test files
│   ├── test_sessionintent.py
│   └── test_configs/        # Test configuration files
├── docs/                    # Documentation
│   ├── README.md
│   ├── configuration-guide.md
│   └── ...
└── scripts/                 # Utility scripts
    └── install.sh
```

## Documentation

All documentation is in the `docs/` directory:

- `README.md` - Main project overview
- `configuration-guide.md` - Config tutorial
- `modes.md` - Mode examples
- `FAQ.md` - Common questions

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
4. Push to main
5. Create GitHub release

## Questions?

- Open an issue
<!-- - Join our Discord
- Email project maintainers -->

Thank you for having interest to contribute on SessionIntent project!
