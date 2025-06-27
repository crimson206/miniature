# miniature

A Python package for managing local git repositories and publishing packages with version tagging.

## Features

- **Load packages** from local git repositories with version control
- **Publish packages** with automatic tagging and pushing
- **Local repository management** with gitdbs configuration
- **Version specification** support (semantic versioning, latest tags, etc.)

## Installation

```bash
pip install miniature
```

## Quick Start

### 1. Setup Local Repository

First, configure a local repository in your `.miniature/gitdbs.json`:

```json
[
  {
    "name": "my-repo",
    "description": "My package repository",
    "db-repo": "https://github.com/user/my-repo",
    "local_path": "~/repos/my-repo"
  }
]
```

### 2. Load a Package

```python
from miniature.load import load_pkg

# Load a specific version
result = load_pkg(
    repo="https://github.com/user/my-repo",
    path="example_pkg",
    version="v1.0.0",
    target_dir="my_package"
)

# Load latest version
result = load_pkg(
    repo="https://github.com/user/my-repo",
    path="example_pkg",
    version="latest"
)

# Load from branch
result = load_pkg(
    repo="https://github.com/user/my-repo",
    path="example_pkg",
    branch="develop"
)
```

### 3. Publish a Package

Create a `pkg.json` file in your package directory:

```json
{
  "name": "my-package",
  "version": "1.2.3",
  "db-repo": "https://github.com/user/my-repo",
  "root-dir": "packages/my-package",
  "branch": "main"
}
```

Then publish:

```python
from miniature.publish import publish_pkg

result = publish_pkg(
    pkg_dir=".",
    tag=True,  # Create version tag
    push=True  # Push to remote
)
```

## API Reference

### Load Functions

#### `load_pkg(repo, path, version=None, target_dir=None, branch="main", clean=False, gitdbs_config=".miniature/gitdbs.json")`

Load a package from a local git repository.

**Parameters:**
- `repo` (str): Repository URL
- `path` (str): Path within the repository
- `version` (str, optional): Version/tag to load (e.g., "v1.0.0", ">=0.3.2", "latest")
- `target_dir` (str, optional): Directory to copy to (default: {path})
- `branch` (str): Branch to use if no version specified (default: "main")
- `clean` (bool): Whether to clean existing target directory (default: False)
- `gitdbs_config` (str): Path to gitdbs config file

**Returns:**
```python
{
    "success": True,
    "target_dir": "my_package",
    "repo": "https://github.com/user/my-repo",
    "path": "example_pkg",
    "version": "v1.0.0",
    "message": "Successfully loaded package from local https://github.com/user/my-repo/example_pkg"
}
```

#### `load_pkgs_from_file(config_file, package_names=None, clean=False, gitdbs_config=".miniature/gitdbs.json")`

Load multiple packages from a configuration file.

**Parameters:**
- `config_file` (str): Path to config file (JSON)
- `package_names` (list, optional): List of package names to load (None = load all)
- `clean` (bool): Whether to clean existing target directories
- `gitdbs_config` (str): Path to gitdbs config file

**Config file format:**
```json
{
  "packages": {
    "package1": {
      "db-repo": "https://github.com/user/repo1",
      "root-dir": "packages/pkg1",
      "version": "v1.0.0",
      "branch": "main",
      "target-dir": "local/pkg1"
    },
    "package2": {
      "db-repo": "https://github.com/user/repo2",
      "root-dir": "packages/pkg2",
      "version": "latest"
    }
  }
}
```

### Publish Functions

#### `publish_pkg(pkg_dir=".", meta_file="pkg.json", commit_message=None, push=True, tag=True, force_tag=False, gitdbs_config=".miniature/gitdbs.json")`

Publish a package with push and optional tagging.

**Parameters:**
- `pkg_dir` (str): Directory containing the package to publish
- `meta_file` (str): Name of the meta file (default: "pkg.json")
- `commit_message` (str, optional): Custom commit message
- `push` (bool): Whether to push changes to remote (default: True)
- `tag` (bool): Whether to create a tag (default: True)
- `force_tag` (bool): Whether to force overwrite existing tag (default: False)
- `gitdbs_config` (str): Path to gitdbs config file

**Returns:**
```python
{
    "success": True,
    "repo_path": "/home/user/repos/my-repo",
    "commit_message": "Update from my-package",
    "pushed": True,
    "tag_result": {
        "action": "pushed",
        "tag_name": "packages/my-package/1.2.3",
        "message": "Tag 'packages/my-package/1.2.3' pushed"
    },
    "message": "Successfully published to repository, Tag 'packages/my-package/1.2.3' pushed"
}
```

## Version Specification

The `version` parameter supports various formats:

- **Exact version**: `"v1.0.0"` or `"1.0.0"`
- **Latest tag**: `"latest"`
- **Version specifiers**: `">=0.3.2"`, `"~1.0"`, `"^2.0"`
- **Direct tag names**: `"packages/my-pkg/1.0.0"`

## Examples

### Load Examples

```python
from miniature.load import load_pkg, load_pkgs_from_file

# Load specific version
load_pkg(
    repo="https://github.com/user/repo",
    path="packages/my-pkg",
    version="v1.2.3"
)

# Load latest version
load_pkg(
    repo="https://github.com/user/repo",
    path="packages/my-pkg",
    version="latest"
)

# Load with version constraint
load_pkg(
    repo="https://github.com/user/repo",
    path="packages/my-pkg",
    version=">=1.0.0"
)

# Load multiple packages
load_pkgs_from_file("packages.json", clean=True)
```

### Publish Examples

```python
from miniature.publish import publish_pkg

# Basic publish
publish_pkg()

# Publish without tagging
publish_pkg(tag=False)

# Publish with custom commit message
publish_pkg(commit_message="Fix critical bug")

# Force overwrite existing tag
publish_pkg(force_tag=True)

# Commit only (no push)
publish_pkg(push=False)
```

## Configuration

### Gitdbs Configuration

Create `.miniature/gitdbs.json` to manage local repositories:

```json
[
  {
    "name": "repo1",
    "description": "First repository",
    "db-repo": "https://github.com/user/repo1",
    "local_path": "~/repos/repo1"
  },
  {
    "name": "repo2", 
    "description": "Second repository",
    "db-repo": "https://github.com/user/repo2",
    "local_path": "~/repos/repo2"
  }
]
```

### Package Configuration

Each package should have a `pkg.json` file:

```json
{
  "name": "my-package",
  "version": "1.2.3",
  "description": "My awesome package",
  "db-repo": "https://github.com/user/my-repo",
  "root-dir": "packages/my-package",
  "branch": "main"
}
```

## Error Handling

All functions return structured results with success status and error messages:

```python
result = load_pkg(repo="https://github.com/user/nonexistent", path="pkg")

if not result["success"]:
    print(f"Error: {result['message']}")
    # Handle error appropriately
```

## Requirements

- Python 3.7+
- Git
- `packaging` library (for version parsing)
- `pyshell` library (for shell operations)