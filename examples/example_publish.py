# %%
import sys
import os
from pprint import pprint
from miniature.publish import publish_pkg, publish_pkg_from_json
from utils import create_test_repository, create_test_package, get_repository_info, delete_all_tags, cleanup_test_repository

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
Create a fresh test repository for publish examples
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
"""Create test package
Create a simple test package for publish examples
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
"""Publish package
Publish the test package (push + tag)
"""

result = publish_pkg(
    pkg_dir="test_pkg",
    meta_file="pkg.json",
    commit_message="Publish test package v0.1.0",
    push=True,
    tag=True
)
pprint(result)

# %%
"""Publish without tag
Push package without creating a tag
"""

result = publish_pkg(
    pkg_dir="test_pkg",
    meta_file="pkg.json",
    commit_message="Update test package without tag",
    push=True,
    tag=False
)
pprint(result)

# %%
"""Publish without pushing
Commit and tag locally but don't push to remote
"""

result = publish_pkg(
    pkg_dir="test_pkg",
    meta_file="pkg.json",
    commit_message="Local publish only",
    push=False,
    tag=True
)
pprint(result)

# %%
"""Publish from JSON path
Publish package using full path to pkg.json
"""

result = publish_pkg_from_json(
    pkg_json_path=os.path.abspath("test_pkg/pkg.json"),
    commit_message="Publish from JSON path",
    push=True,
    tag=True
)
pprint(result)

# %%
"""Create another test package
Create a second test package for multiple package publish example
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
"""Publish second package
Publish the second test package
"""

result = publish_pkg(
    pkg_dir="test_pkg2",
    meta_file="pkg.json",
    commit_message="Publish second test package v0.2.0",
    push=True,
    tag=True
)
pprint(result)

# %%
"""Publish with force tag
Force create a tag (overwrite if exists)
"""

result = publish_pkg(
    pkg_dir="test_pkg",
    meta_file="pkg.json",
    commit_message="Force publish with overwrite",
    push=True,
    tag=True,
    force_tag=True
)
pprint(result)

# %%
"""Check repository status
Check the current status of the local repository
"""

repo_info = get_repository_info("test-miniature")
pprint(repo_info)

# %%
"""Publish multiple versions
Publish the same package with different versions
"""

versions = ["0.3.0", "0.4.0", "0.5.0"]

results = []
for version in versions:
    # Update package version
    pkg_result = create_test_package(
        pkg_name="test-package",
        version=version,
        repo_url="https://github.com/crimson206/test-miniature",
        root_dir="packages/test-package",
        target_dir="test_pkg"
    )
    
    if pkg_result["success"]:
        result = publish_pkg(
            pkg_dir="test_pkg",
            meta_file="pkg.json",
            commit_message=f"Publish test package {version}",
            push=True,
            tag=True
        )
        results.append(result)
    else:
        results.append({"error": f"Failed to create package version {version}"})

pprint(results)

# %%
"""Final repository status
Check the final state after all publish operations
"""

final_repo_info = get_repository_info("test-miniature")
pprint(final_repo_info)
