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
- COPR build is a manual follow-up (see packaging/fedora/sessionintent.spec)

## Local Development CI

### Run linting
```bash
ruff check src/ tests/
```

### Run type checks
```bash
mypy src/
```

### Run tests
```bash
pytest
```

### Run all checks
```bash
make test
```
