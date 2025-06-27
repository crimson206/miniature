# %%
import sys
import os
from pprint import pprint
from miniature.push import push_pkg, push_pkg_from_json
from utils import create_test_repository, create_test_package, get_repository_info

# %%
"""Setup test repository
Create or ensure test repository exists
"""

repo_result = create_test_repository(
    repo_name="test-miniature",
    description="Test repository for miniature examples"
)
pprint(repo_result)

if not repo_result["success"]:
    print("Repository setup failed, but continuing with existing repository...")

# %%
"""Create test package
Create a simple test package for push examples
"""

pkg_result = create_test_package(
    pkg_name="test-package",
    version="0.1.0",
    repo_url="https://github.com/crimson206/test-miniature",
    root_dir="packages/test-package",
    target_dir="test_pkg"
)
pprint(pkg_result)

if not pkg_result["success"]:
    print("Package creation failed!")
    sys.exit(1)

# %%
"""Push package
Push the test package to the repository
"""

result = push_pkg(
    pkg_dir="test_pkg",
    meta_file="pkg.json",
    commit_message="Add test package v0.1.0",
    push=True
)
pprint(result)

# %%
"""Push with custom commit message
Push package with a custom commit message
"""

result = push_pkg(
    pkg_dir="test_pkg",
    meta_file="pkg.json",
    commit_message="Update test package with new features",
    push=True
)
pprint(result)

# %%
"""Push without pushing to remote
Commit changes but don't push to remote
"""

result = push_pkg(
    pkg_dir="test_pkg",
    meta_file="pkg.json",
    commit_message="Local commit only",
    push=False
)
pprint(result)

# %%
"""Push from JSON path
Push package using full path to pkg.json
"""

result = push_pkg_from_json(
    pkg_json_path=os.path.abspath("test_pkg/pkg.json"),
    commit_message="Push from JSON path",
    push=True
)
pprint(result)

# %%
"""Create another test package
Create a second test package for multiple package example
"""

pkg_result2 = create_test_package(
    pkg_name="test-package-2",
    version="0.2.0",
    repo_url="https://github.com/crimson206/test-miniature",
    root_dir="packages/test-package-2",
    target_dir="test_pkg2"
)
pprint(pkg_result2)

if not pkg_result2["success"]:
    print("Second package creation failed!")
    sys.exit(1)

# %%
"""Push second package
Push the second test package
"""

result = push_pkg(
    pkg_dir="test_pkg2",
    meta_file="pkg.json",
    commit_message="Add second test package v0.2.0",
    push=True
)
pprint(result)

# %%
"""Check repository status
Check the current status of the local repository
"""

repo_info = get_repository_info("test-miniature")
pprint(repo_info)
