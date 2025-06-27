# %%
import sys
import os
from pprint import pprint
from miniature.load import (
    load_pkg, 
    load_pkg_from_config, 
    load_pkgs_from_file, 
    setup_local_repository
)
from miniature.push import push_pkg
from miniature.tag import create_tag
from utils import (
    create_test_repository, 
    create_test_package, 
    get_repository_info, 
    delete_all_tags,
    cleanup_test_repository
)

# %%
"""Cleanup existing test repository
Remove any existing test repository to start fresh
"""

cleanup_result = cleanup_test_repository(
    repo_name="test-miniature",
    delete_remote=True
)
pprint(cleanup_result)

# %%
"""Setup test repository
Create a fresh test repository for load examples
"""

repo_result = create_test_repository(
    repo_name="test-miniature",
    description="Test repository for miniature examples"
)
pprint(repo_result)

if not repo_result["success"]:
    print("Repository setup failed!")
    sys.exit(1)

# %%
"""Cleanup existing tags
Delete all existing tags to start fresh
"""

local_repo_path = os.path.expanduser("~/miniature/test-miniature")
tag_cleanup_result = delete_all_tags(local_repo_path)
pprint(tag_cleanup_result)

# %%
"""Create and push test packages
Create multiple test packages with different versions for loading
"""

os.makedirs("load_output", exist_ok=True)

# Create package 1 with multiple versions
versions = ["0.1.0", "0.1.1", "0.2.0"]
for version in versions:
    pkg_dir = f"load_output/test_pkg_{version.replace('.', '_')}"
    pkg_result = create_test_package(
        pkg_name="example_pkg",
        version=version,
        repo_url="https://github.com/crimson206/test-miniature",
        root_dir="packages/example_pkg",
        target_dir=pkg_dir
    )
    
    if pkg_result["success"]:
        # Push the package
        push_result = push_pkg(
            pkg_dir=pkg_dir,
            meta_file="pkg.json",
            commit_message=f"Add example_pkg v{version}",
            push=True
        )
        
        # Create tag
        tag_result = create_tag(
            repo_url="https://github.com/crimson206/test-miniature",
            tag_name=f"example_pkg/{version}",
            tag_message=f"Release example_pkg version {version}",
            push=True
        )
        
        print(f"Created and pushed example_pkg v{version}")
    else:
        print(f"Failed to create example_pkg v{version}")

# Create package 2
pkg_dir2 = "load_output/test_pkg_utils"
pkg_result2 = create_test_package(
    pkg_name="utils_pkg",
    version="1.0.0",
    repo_url="https://github.com/crimson206/test-miniature",
    root_dir="packages/utils_pkg",
    target_dir=pkg_dir2
)

if pkg_result2["success"]:
    push_result = push_pkg(
        pkg_dir=pkg_dir2,
        meta_file="pkg.json",
        commit_message="Add utils_pkg v1.0.0",
        push=True
    )
    
    tag_result = create_tag(
        repo_url="https://github.com/crimson206/test-miniature",
        tag_name="utils_pkg/1.0.0",
        tag_message="Release utils_pkg version 1.0.0",
        push=True
    )
    
    print("Created and pushed utils_pkg v1.0.0")

# %%
"""Setup local repository
Setup the local git repository for package loading
"""

repo_url = "https://github.com/crimson206/test-miniature"
local_path = "~/miniature/test-miniature"

setup_result = setup_local_repository(repo_url, local_path)
pprint(setup_result)

# %%
"""Load specific version
Load a specific version using tag name
"""

result = load_pkg(
    repo="https://github.com/crimson206/test-miniature",
    path="packages/example_pkg",
    version="example_pkg/0.1.1",
    target_dir="load_output/specific_version"
)
pprint(result)

# %%
"""Load latest version
Load the latest version of a package
"""

result = load_pkg(
    repo="https://github.com/crimson206/test-miniature",
    path="packages/example_pkg",
    version="latest",
    target_dir="load_output/latest_version"
)
pprint(result)

# %%
"""Load version range
Load package with version range specification
"""

result = load_pkg(
    repo="https://github.com/crimson206/test-miniature",
    path="packages/example_pkg",
    version=">=0.1.0",
    target_dir="load_output/version_range"
)
pprint(result)

# %%
"""Load from branch
Load package from specific branch
"""

result = load_pkg(
    repo="https://github.com/crimson206/test-miniature",
    path="packages/example_pkg",
    branch="main",
    target_dir="load_output/from_branch"
)
pprint(result)

# %%
"""Load from config dictionary
Load package using configuration dictionary
"""

config = {
    "repo": "https://github.com/crimson206/test-miniature",
    "path": "packages/example_pkg",
    "version": "example_pkg/0.1.1",
    "branch": "main"
}

result = load_pkg_from_config(
    config=config,
    target_dir="load_output/from_config"
)
pprint(result)

# %%
"""Load with default path
Load package using default target directory
"""

result = load_pkg(
    repo="https://github.com/crimson206/test-miniature",
    path="packages/example_pkg",
    version="example_pkg/0.1.1"
    # target_dir not specified - will use "example_pkg"
)
pprint(result)

# %%
"""Load all from config file
Load all packages from configuration file
"""

config_file = ".miniature/load.pkg.json"

result = load_pkgs_from_file(config_file)
pprint(result)

# %%
"""Load specific from config file
Load only specific packages from configuration file
"""

config_file = ".miniature/load.pkg.json"
package_names = ["example_pkg_0_1_1"]  # Only load this one

result = load_pkgs_from_file(config_file, package_names)
pprint(result)

# %%
"""Clean load
Load package with clean option
"""

result = load_pkg(
    repo="https://github.com/crimson206/test-miniature",
    path="packages/example_pkg",
    version="example_pkg/0.1.1",
    target_dir="load_output/clean_load",
    clean=True
)
pprint(result)

# %%
"""Check loaded files
List all downloaded directories and their contents
"""

import glob

downloaded_dirs = glob.glob("load_output/*")
for dir_path in downloaded_dirs:
    if os.path.isdir(dir_path):
        files = os.listdir(dir_path)
        pprint({os.path.basename(dir_path): files})

# %%
"""Check repository status
Check the current status of the local repository
"""

repo_info = get_repository_info("test-miniature")
pprint(repo_info)
