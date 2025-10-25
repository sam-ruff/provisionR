# Contributing to provisionR

Thank you for your interest in contributing to provisionR!

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/sam-ruff/provisionR.git
   cd provisionR
   ```

2. **Install dependencies**
   ```bash
   uv sync --dev
   ```

3. **Run tests**
   ```bash
   uv run pytest -v
   ```

## Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for semantic versioning.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature (triggers minor version bump)
- **fix**: A bug fix (triggers patch version bump)
- **docs**: Documentation only changes (triggers patch version bump)
- **style**: Changes that don't affect code meaning (whitespace, formatting)
- **refactor**: Code change that neither fixes a bug nor adds a feature (triggers patch version bump)
- **perf**: Performance improvement (triggers patch version bump)
- **test**: Adding or updating tests
- **build**: Changes to build system or dependencies (triggers patch version bump)
- **ci**: Changes to CI configuration
- **chore**: Other changes that don't modify src or test files

### Breaking Changes

Add `BREAKING CHANGE:` in the footer or append `!` after the type to trigger a major version bump:

```
feat!: change API endpoint structure

BREAKING CHANGE: The /api/ks endpoint has been renamed to /api/v1/ks
```

### Examples

```bash
# Feature (minor version bump: 1.0.0 -> 1.1.0)
git commit -m "feat(api): add CSV export endpoint for machine passwords"

# Bug fix (patch version bump: 1.0.0 -> 1.0.1)
git commit -m "fix(auth): resolve password generation for special characters"

# Breaking change (major version bump: 1.0.0 -> 2.0.0)
git commit -m "feat!: restructure API endpoints

BREAKING CHANGE: All API endpoints now require /v1/ prefix"

# Documentation (patch version bump)
git commit -m "docs: add API usage examples to README"

# No version bump
git commit -m "test: add integration tests for export service"
git commit -m "ci: update GitHub Actions workflow"
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feat/my-new-feature
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Ensure tests pass**
   ```bash
   uv run pytest -v
   ```

4. **Commit using conventional commits**
   ```bash
   git commit -m "feat(service): add new kickstart template support"
   ```

5. **Push and create pull request**
   ```bash
   git push origin feat/my-new-feature
   ```

6. **Wait for CI to pass**
   - Tests must pass
   - Code coverage should not decrease

## Code Style

- Use type hints
- Write docstrings for public functions
- Follow existing patterns (service layer, dependency injection)
- Keep routes focused on HTTP concerns
- Put business logic in services

## Release Process

Releases are automated via semantic-release:

1. Commits to `main` branch trigger CI/CD
2. semantic-release analyzes commit messages
3. Version is bumped automatically based on commit types
4. CHANGELOG.md is updated
5. GitHub release is created
6. Version in pyproject.toml is updated

**You don't need to manually update versions!**

## Questions?

Open an issue for discussion or reach out to maintainers.
