"""Core package loading functionality."""

import os
import shutil
from typing import Optional, Dict, Any
from pathlib import Path
from git import Repo

from ..cache import get_cache
from ..models import PackageDefinition
from .version_utils import find_latest_tag, find_matching_tag, is_commit_sha


def load_pkg(
    repo: Optional[str] = None,
    version: Optional[str] = None,
    target_dir: Optional[str] = None,
    branch: str = "main",
    clean: bool = False,
    gitdbs_config: Optional[str] = None,  # Deprecated
    cache_dir: Optional[str] = None,
    # New parameters for repotree
    package_def: Optional[PackageDefinition] = None,
    use_symlink: bool = False,
    update_miniature: bool = True,
) -> Dict[str, Any]:
    """Load a package from a git repository using cache.

    Args:
        repo: Repository URL (can be constructed from package_def)
        version: Version/tag to load (e.g., "v1.0.0", ">=0.3.2", "latest")
        target_dir: Directory to copy/link to
        branch: Branch to use if no version specified
        clean: Whether to clean existing target directory
        gitdbs_config: DEPRECATED - Path to gitdbs config file
        cache_dir: Cache directory path
        package_def: PackageDefinition object with full repotree config
        use_symlink: Whether to create symlink instead of copying
        update_miniature: Whether to update miniature.json after successful load

    Returns:
        Dict containing operation result
    """
    # Handle package_def for repotree compatibility
    if package_def:
        repo = repo or package_def.get_repo_url()
        branch = branch if branch != "main" else package_def.get_branch_or_tag()
        target_dir = target_dir or package_def.local_dir

        # Handle as_pkg for version constraints
        if package_def.as_pkg:
            version = version or package_def.as_pkg.version

    # Validate inputs
    if not repo:
        return {"success": False, "message": "Repository URL is required"}

    # Set default target directory
    if target_dir is None:
        # Extract repository name from URL
        repo_name = repo.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        # Add branch suffix if not main/master
        if branch not in ['main', 'master']:
            target_dir = f"{repo_name}-{branch}"
        else:
            target_dir = repo_name

    target_path = Path(target_dir)

    # Clean target directory if requested
    if clean and target_path.exists():
        if target_path.is_symlink():
            target_path.unlink()
        else:
            shutil.rmtree(target_path)

    try:
        # Get cache instance
        cache = get_cache(Path(cache_dir) if cache_dir else None)

        # Clone or update repository in cache
        repo_path = cache.clone_or_update(repo, branch)

        # Get the git repository
        git_repo = Repo(repo_path)

        # Determine version to checkout
        actual_version = None

        if version:
            if version == "latest":
                # Get latest tag for the repository
                latest_tag = find_latest_tag(git_repo)
                if latest_tag:
                    git_repo.git.checkout(latest_tag)
                    actual_version = latest_tag
                else:
                    # No tags, use current branch
                    actual_version = git_repo.active_branch.name
            else:
                # Check if it's a direct tag/commit or version spec
                if "/" in version or is_commit_sha(version):
                    # Direct reference
                    git_repo.git.checkout(version)
                    actual_version = version
                else:
                    # Version specification - find matching tag
                    matching_tag = find_matching_tag(git_repo, version)
                    if matching_tag:
                        git_repo.git.checkout(matching_tag)
                        actual_version = matching_tag
                    else:
                        return {
                            "success": False,
                            "message": f"No tag found matching version {version}",
                        }
        else:
            # Checkout branch
            if branch in git_repo.heads:
                git_repo.heads[branch].checkout()
            elif f"origin/{branch}" in git_repo.refs:
                git_repo.create_head(branch, f"origin/{branch}").checkout()
            actual_version = branch

        # Create target directory parent if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy or symlink entire repository
        if use_symlink:
            cache.create_symlink(repo, target_path, ".", branch)
        else:
            # Copy entire repository
            shutil.copytree(repo_path, target_path, dirs_exist_ok=True)
            
            # If target is on Windows filesystem (WSL), disable filemode tracking
            from ..utils import should_disable_filemode, fix_git_filemode
            if should_disable_filemode(str(target_path)):
                try:
                    fix_git_filemode(str(target_path))
                    print(f"Note: Disabled git filemode tracking for Windows filesystem")
                except Exception:
                    pass  # Silently ignore if fix fails

        # Handle custom config if present
        if package_def and package_def.custom_config.install:
            print(
                f"Note: Run '{package_def.custom_config.install}' to install the package"
            )

        result = {
            "success": True,
            "target_dir": str(target_path),
            "repo": repo,
            "branch": branch,
            "version": actual_version,
            "message": f"Successfully loaded repository from {repo} (branch: {branch})",
        }

        # Update miniature.json if requested
        if update_miniature:
            try:
                from .miniature_updater import update_miniature_json
                
                # Create package info for miniature.json update
                pkg_name = package_def.pkg_name if package_def else target_dir
                
                # If no package_def, create a minimal one for the update
                if not package_def:
                    # Parse repo URL to extract components
                    repo_parts = repo.rstrip('/').split('/')
                    if len(repo_parts) >= 2:
                        # Extract domain (everything except last 2 parts)
                        if repo.startswith(('http://', 'https://')):
                            protocol_and_host = '/'.join(repo_parts[:3])  # e.g., https://github.com
                            domain = protocol_and_host + '/'
                            repo_name = '/'.join(repo_parts[3:])  # e.g., crimson206/runpy
                        else:
                            domain = repo_parts[0] + '/'
                            repo_name = '/'.join(repo_parts[1:])
                        
                        if repo_name.endswith('.git'):
                            repo_name = repo_name[:-4]
                    else:
                        domain = repo
                        repo_name = repo
                    
                    package_def = PackageDefinition(
                        pkg_name=pkg_name,
                        domain=domain,
                        repo_name=repo_name,
                        branch=branch,
                        local_dir=target_dir,
                        loaded=True,
                    )
                
                loaded_packages = [{
                    "pkg_name": pkg_name,
                    "repo": repo,
                    "target_dir": str(target_path),
                    "branch": branch,
                    "version": actual_version,
                    "package_def": package_def,
                }]
                
                update_miniature_json(loaded_packages)
                
            except Exception as e:
                print(f"Warning: Failed to update miniature.json: {e}")

        return result

    except Exception as e:
        return {
            "success": False,
            "target_dir": str(target_path),
            "repo": repo,
            "branch": branch,
            "version": version or branch,
            "message": f"Failed to load repository: {e}",
            "error": e,
        }