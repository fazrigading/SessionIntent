# SessionIntent - CI/CD Pipeline

This directory contains GitHub Actions workflows for SessionIntent.

## Workflows

### CI Pipeline (.github/workflows/ci.yml)

Runs on every push/PR:
- Python linting (ruff)
- Type checking (mypy)
- _unit tests
- Test config parsing

### Release Workflow (.github/workflows/release.yml)

Runs on tag creation:
- Build Python package
- Create GitHub release
- Upload artifacts
- Trigger COPR build

## Local Development CI

### Run linting
```bash
ruff check .
```

### Run type checks
```bash
mypy sessionintent.py
```

### Run tests
```bash
pytest
```

### Run all checks
```bash
make test
```
