"""Version handling utilities for package loading."""

import re
from typing import Optional
from git import Repo
import packaging.version
import packaging.specifiers


def find_latest_tag(repo: Repo) -> Optional[str]:
    """Find the latest tag in a repository.

    Args:
        repo: Git repository object

    Returns:
        Latest tag name or None
    """
    try:
        tags = list(repo.tags)

        if not tags:
            return None

        # Get all tags
        package_tags = [str(tag.name) for tag in tags]

        # Sort by version
        version_tags = []

        for tag_name in package_tags:
            try:
                # Extract version part
                if "/" in tag_name:
                    version_part = tag_name.split("/")[-1]
                else:
                    version_part = tag_name

                # Remove 'v' prefix if present
                version_part = version_part.lstrip("v")

                ver = packaging.version.parse(version_part)
                version_tags.append((tag_name, ver))
            except packaging.version.InvalidVersion:
                continue

        if not version_tags:
            return package_tags[-1]  # Return last tag if no valid versions

        # Sort by version and return latest
        version_tags.sort(key=lambda x: x[1])
        return version_tags[-1][0]

    except Exception:
        return None


def find_matching_tag(repo: Repo, version_spec: str) -> Optional[str]:
    """Find a tag matching version specification.

    Args:
        repo: Git repository object
        version_spec: Version specification (e.g., ">=1.0.0")

    Returns:
        Matching tag name or None
    """
    try:
        tags = list(repo.tags)

        if not tags:
            return None

        # Create specifier set
        specifier_set = packaging.specifiers.SpecifierSet(version_spec)

        # Filter and match tags
        valid_tags = []

        for tag in tags:
            tag_name = str(tag.name)

            try:
                # Extract version part
                if "/" in tag_name:
                    version_part = tag_name.split("/")[-1]
                else:
                    version_part = tag_name

                # Remove 'v' prefix if present
                version_part = version_part.lstrip("v")

                ver = packaging.version.parse(version_part)

                # Check if version matches specifier
                if ver in specifier_set:
                    valid_tags.append((tag_name, ver))
            except packaging.version.InvalidVersion:
                continue

        if not valid_tags:
            return None

        # Sort by version and return latest matching
        valid_tags.sort(key=lambda x: x[1])
        return valid_tags[-1][0]

    except Exception:
        return None


def is_commit_sha(value: str) -> bool:
    """Check if a value is a git commit SHA."""
    return bool(re.match(r"^[0-9a-f]{6,40}$", value, re.IGNORECASE))