# %%
import sys
import os
from pprint import pprint
from miniature.tag import create_tag, clean_tag
from utils import create_test_repository, delete_all_tags, get_repository_info

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
"""Cleanup existing tags
Delete all existing tags to start fresh
"""

local_repo_path = os.path.expanduser("~/miniature/test-miniature")
tag_cleanup_result = delete_all_tags(local_repo_path)
pprint(tag_cleanup_result)

# %%
"""Create simple tag
Create a basic tag for the test repository
"""

result = create_tag(
    repo_url="https://github.com/crimson206/test-miniature",
    tag_name="v0.1.0",
    tag_message="Release version 0.1.0",
    push=True
)
pprint(result)

# %%
"""Create tag with custom message
Create a tag with a detailed custom message
"""

result = create_tag(
    repo_url="https://github.com/crimson206/test-miniature",
    tag_name="test-package/v0.1.0",
    tag_message="Release test-package version 0.1.0 with initial features",
    push=True
)
pprint(result)

# %%
"""Create tag without pushing
Create a tag locally but don't push to remote
"""

result = create_tag(
    repo_url="https://github.com/crimson206/test-miniature",
    tag_name="local-only/v0.1.0",
    tag_message="Local tag only",
    push=False
)
pprint(result)

# %%
"""Create tag with force
Force create a tag (overwrite if exists)
"""

result = create_tag(
    repo_url="https://github.com/crimson206/test-miniature",
    tag_name="v0.1.0",
    tag_message="Updated release version 0.1.0",
    force=True,
    push=True
)
pprint(result)

# %%
"""Cleanup before multiple tags
Delete existing tags before creating multiple ones
"""

local_repo_path = os.path.expanduser("~/miniature/test-miniature")
tag_cleanup_result = delete_all_tags(local_repo_path)
pprint(tag_cleanup_result)

# %%
"""Create multiple tags
Create several tags for different packages
"""

tags = [
    ("test-package/v0.1.0", "Test package version 0.1.0"),
    ("test-package/v0.2.0", "Test package version 0.2.0"),
    ("test-package-2/v0.1.0", "Test package 2 version 0.1.0"),
    ("test-package-2/v0.2.0", "Test package 2 version 0.2.0")
]

results = []
for tag_name, tag_message in tags:
    result = create_tag(
        repo_url="https://github.com/crimson206/test-miniature",
        tag_name=tag_name,
        tag_message=tag_message,
        push=True
    )
    results.append(result)

pprint(results)

# %%
"""List all tags
Check what tags exist in the repository
"""

repo_info = get_repository_info("test-miniature")
pprint(repo_info)

# %%
"""Clean tag
Delete a tag locally and from remote
"""

result = clean_tag(
    repo_url="https://github.com/crimson206/test-miniature",
    tag_name="local-only/v0.1.0",
    remote="origin"
)
pprint(result)

# %%
"""Clean multiple tags
Delete several tags
"""

tags_to_delete = ["test-package/v0.1.0", "test-package-2/v0.1.0"]

results = []
for tag_name in tags_to_delete:
    result = clean_tag(
        repo_url="https://github.com/crimson206/test-miniature",
        tag_name=tag_name,
        remote="origin"
    )
    results.append(result)

pprint(results)

# %%
"""Check final tag status
Verify the final state of tags after operations
"""

repo_info = get_repository_info("test-miniature")
pprint(repo_info)
