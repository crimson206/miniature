# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Miniature is a Python package for managing local git repositories and publishing packages with version tagging. It provides functions to load packages from local git repositories with version control and publish packages with automatic tagging.

## Essential Commands

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_load.py

# Run with verbose output
pytest -v
```

### Development
```bash
# Install package in development mode
pip install -e .

# Install with dependencies (pyshell and packaging are required but not in pyproject.toml)
pip install pyshell packaging
```

## Architecture

### Core Modules
- **`src/miniature/load.py`**: Package loading functionality
  - `load_pkg()`: Load single package from local git repo
  - `load_pkgs_from_file()`: Batch load packages from config
  
- **`src/miniature/publish.py`**: Package publishing functionality  
  - `publish_pkg()`: Publish package with optional tagging/pushing
  
- **`src/miniature/push.py`**: Git push operations
  - `push_pkg()`: Push package changes to repository
  
- **`src/miniature/tag.py`**: Git tagging functionality
  - `tag_pkg()`: Create and manage version tags

### Configuration Files
1. **`.miniature/gitdbs.json`**: Maps repository URLs to local paths
2. **`pkg.json`**: Package metadata (name, version, db-repo, root-dir, branch)

### Key Design Patterns
- All functions return structured dictionaries with `success`, `message`, and relevant data
- Local repository paths are resolved through gitdbs.json configuration
- Version specifications support exact versions, "latest", and semantic version constraints
- Shell commands are executed through pyshell library (not standard subprocess)

## Important Notes
- Dependencies `pyshell` and `packaging` are used but not listed in pyproject.toml
- Test files were recently deleted (shown in git status)
- No linting or formatting configuration currently exists
- Current branch is `dev`, main branch is `main`