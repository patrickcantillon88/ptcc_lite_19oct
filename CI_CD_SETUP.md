# CI/CD Pipeline Setup Guide

## Overview

This document describes the continuous integration and deployment (CI/CD) pipeline for the Privacy-Preserving Safeguarding System.

---

## GitHub Actions Workflows

### 1. Test Suite CI/CD (`.github/workflows/test.yml`)

**Triggered**: On every push and pull request to `main` or `develop` branches

**Jobs**:

#### `test` Job
- **Python Version**: 3.11
- **Runner**: macOS latest

**Steps**:
1. Checkout code
2. Set up Python 3.11
3. Install dependencies (pytest, coverage)
4. Run unit tests with coverage
5. Run integration tests with coverage
6. Run API tests (non-blocking)
7. Upload coverage reports to Codecov
8. Generate coverage badges
9. Publish test results

**Coverage Reporting**:
- XML format for Codecov integration
- Term-missing format for terminal output
- HTML reports generated locally
- Badge SVG for README

#### `lint` Job
- **Runner**: macOS latest

**Steps**:
1. Checkout code
2. Set up Python
3. Install linting tools (flake8, black, isort)
4. Check code formatting with Black
5. Check imports with isort
6. Lint with flake8

**Lint Rules**:
- Syntax errors and undefined names block build
- Style issues are warnings only
- Max complexity: 10
- Max line length: 127 characters

---

### 2. Deploy Workflow (`.github/workflows/deploy.yml`)

**Triggered**: 
- Manual trigger (`workflow_dispatch`)
- Pushes to `main` branch
- Tag pushes matching `v*`

**Jobs**:

#### `build` Job
**Output**: Version string (YYYY.MM.DD)

**Steps**:
1. Checkout code
2. Generate version from date
3. Set up Python
4. Install dependencies
5. Run full test suite
6. Build artifacts (tar.gz)
7. Upload build artifacts

#### `quality-check` Job
**Depends**: build job

**Steps**:
1. Checkout code
2. Set up Python
3. Install quality tools (pylint, black, isort, bandit)
4. Security scan with Bandit
5. Code style checks
6. Upload quality reports

#### `deploy` Job
**Depends**: build and quality-check jobs
**Condition**: Only runs if previous jobs succeed

**Steps**:
1. Download build artifacts
2. Create deployment package
3. Generate deployment summary
4. Upload deployment summary
5. Create GitHub Release (on tags)

---

## Configuration Files

### `pytest.ini`
Pytest configuration with:
- Test discovery patterns
- Test markers (unit, integration, api, privacy, performance)
- Output options
- Coverage configuration
- Asyncio settings
- Logging configuration
- 300-second timeout
- Minimum Python 3.11

### `.coveragerc`
Coverage.py configuration with:
- Source paths: `core/`, `api/`
- Branch coverage enabled
- Exclusion patterns for tests, cache, venv
- HTML report generation
- XML report for CI/CD
- Coverage precision: 2 decimal places

---

## Local Development

### Run All Tests Locally

```bash
cd backend
pytest -v --tb=short
```

### Run With Coverage

```bash
pytest --cov=core --cov-report=html --cov-report=term-missing
```

### View HTML Coverage Report

```bash
open htmlcov/index.html
```

### Run Specific Test File

```bash
pytest tests/test_privacy_components.py -v
```

### Run Linting Locally

```bash
# Check formatting
black --check .

# Check imports
isort --check-only .

# Lint code
flake8 . --max-complexity=10
```

---

## Coverage Reports

### Viewing Coverage

1. **Terminal Output**: See coverage percentage after each test run
2. **HTML Report**: Open `backend/htmlcov/index.html` in browser
3. **Codecov**: View on Codecov dashboard (when integrated)

### Coverage Thresholds

- **Unit Tests**: Target 90%+ coverage
- **Integration Tests**: Target 70%+ coverage
- **Overall**: Target 85%+ coverage

---

## Deployment Process

### Manual Deployment

```bash
# 1. Tag a release
git tag -a v1.0.0 -m "Release v1.0.0"

# 2. Push tag to trigger deployment
git push origin v1.0.0

# 3. GitHub Actions will:
#    - Run tests
#    - Build artifacts
#    - Create release
#    - Upload artifacts
```

### Deployment Checklist

- [ ] All tests passing
- [ ] Code review completed
- [ ] Coverage maintained or improved
- [ ] Security scan clean
- [ ] No lint warnings
- [ ] Documentation updated
- [ ] Release notes prepared
- [ ] Version tagged

---

## Monitoring & Troubleshooting

### View Workflow Runs

1. Go to GitHub repository
2. Click "Actions" tab
3. Select workflow to view
4. Click on specific run to see details

### Common Issues

#### Tests Failing
- Check test output in GitHub Actions
- Run locally with: `pytest -v --tb=long`
- Review recent code changes

#### Coverage Dropping
- Check which files lost coverage
- Add tests for uncovered lines
- Review `.coveragerc` exclusions

#### Lint Failures
- Run `black .` to auto-format
- Run `isort .` to auto-organize imports
- Check flake8 output for manual fixes

#### Deployment Blocked
- Review test failures
- Check quality scan results
- Ensure all prerequisites met

---

## Integration Points

### Codecov Integration
- Requires: Codecov account and token
- Configuration: Set `CODECOV_TOKEN` in GitHub Secrets
- Benefits: Coverage trend tracking, PR badges

### GitHub Releases
- Triggered on version tags (v*)
- Automatically generates release notes
- Attaches build artifacts
- Creates GitHub Release entry

---

## Best Practices

1. **Run tests locally before pushing**
   ```bash
   pytest tests/
   ```

2. **Keep coverage high**
   - Add tests for new code
   - Maintain 85%+ coverage

3. **Follow code style**
   - Run `black` before commit
   - Run `isort` before commit
   - Check flake8 warnings

4. **Meaningful commit messages**
   - Reference issues: "Fixes #123"
   - Describe changes clearly
   - Keep commits atomic

5. **Use feature branches**
   - Branch off `develop`
   - Create PR for review
   - Merge after CI passes

6. **Tag releases properly**
   - Use semantic versioning: v1.0.0
   - Tag after merge to main
   - Include release notes

---

## Environment Variables

### Required Secrets (GitHub)
- `CODECOV_TOKEN`: For Codecov integration
- `GITHUB_TOKEN`: Automatically provided by GitHub

### Optional Environment Variables
- `PYTHON_VERSION`: Python version to use (default: 3.11)
- `COVERAGE_THRESHOLD`: Minimum coverage percentage
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING)

---

## Performance

### Typical Pipeline Times

| Stage | Duration |
|-------|----------|
| Checkout | < 1 min |
| Setup | 2-3 min |
| Tests | 1-2 min |
| Lint | 1 min |
| Deploy | 1 min |
| **Total** | **6-8 min** |

### Optimization Tips

1. Cache dependencies for faster installs
2. Run jobs in parallel (already configured)
3. Skip expensive checks for non-critical changes
4. Use shallow clones for faster checkout

---

## Troubleshooting Commands

```bash
# Run tests with maximum verbosity
pytest -vvv --tb=long tests/

# Run only failing tests
pytest --lf

# Run with print statements visible
pytest -s

# Run specific test by name
pytest -k test_name

# Generate coverage and open report
pytest --cov=core --cov-report=html && open htmlcov/index.html

# Check what linting would do
black --check --diff backend/

# Dry run isort
isort --check-only --diff backend/
```

---

## Next Steps

1. ✅ CI/CD pipelines configured
2. Next: Set up performance benchmarks
3. Then: Add compliance verification tests

---

## Support

For issues or questions:
1. Check GitHub Actions logs
2. Review test output locally
3. Check test documentation
4. Contact development team
