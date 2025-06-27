#!/usr/bin/env python3
"""
Utility functions for miniature examples.
Common operations that can be shared across different example files.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from pyshell import shell, ShellError


def create_test_repository(
    repo_name: str,
    description: str = "Test repository for miniature examples",
    gitignore: str = "Python"
) -> Dict[str, Any]:
    """Create a new test repository on GitHub.
    
    Args:
        repo_name: Name of the repository to create
        description: Repository description
        gitignore: Gitignore template to use
        
    Returns:
        Dict with creation result
    """
    try:
        # Create repository
        shell(f'gh repo create {repo_name} --public --description "{description}" --gitignore {gitignore}')
        
        # Wait a moment for GitHub to process
        time.sleep(2)
        
        # Clone to local
        local_path = f"~/miniature/{repo_name}"
        expanded_path = os.path.expanduser(local_path)
        
        if not os.path.exists(expanded_path):
            shell(f"mkdir -p ~/miniature && cd ~/miniature && git clone https://github.com/crimson206/{repo_name}.git")
        
        # Update gitdbs config
        update_gitdbs_config(
            repo_url=f"https://github.com/crimson206/{repo_name}",
            local_path=local_path,
            name=repo_name,
            description=description
        )
        
        return {
            "success": True,
            "repo_name": repo_name,
            "repo_url": f"https://github.com/crimson206/{repo_name}",
            "local_path": expanded_path,
            "message": f"Repository {repo_name} created and cloned successfully"
        }
        
    except ShellError as e:
        return {
            "success": False,
            "repo_name": repo_name,
            "error": str(e),
            "message": f"Failed to create repository {repo_name}: {e}"
        }


def update_gitdbs_config(
    repo_url: str,
    local_path: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    gitdbs_config: str = ".miniature/gitdbs.json"
):
    """Update gitdbs config file with new repository entry."""
    configs = []
    
    # Load existing config
    if os.path.exists(gitdbs_config):
        with open(gitdbs_config, 'r') as f:
            configs = json.load(f)
    
    # Check if entry already exists
    for config in configs:
        if config.get('db-repo') == repo_url:
            config['local_path'] = local_path
            if name:
                config['name'] = name
            if description:
                config['description'] = description
            break
    else:
        # Add new entry
        configs.append({
            "name": name or repo_url.split('/')[-1].replace('.git', ''),
            "description": description or f"Local copy of {repo_url}",
            "db-repo": repo_url,
            "local_path": local_path
        })
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(gitdbs_config), exist_ok=True)
    
    # Write updated config
    with open(gitdbs_config, 'w') as f:
        json.dump(configs, f, indent=4)


def delete_all_tags(repo_path: str) -> Dict[str, Any]:
    """Delete all existing tags in the repository.
    
    Args:
        repo_path: Path to local repository
        
    Returns:
        Dict with deletion result
    """
    try:
        existing_tags = shell(f"cd {repo_path} && git tag -l").strip().split('\n')
        existing_tags = [tag for tag in existing_tags if tag]  # Remove empty strings
        
        if not existing_tags:
            return {
                "success": True,
                "deleted_count": 0,
                "message": "No existing tags found"
            }
        
        deleted_count = 0
        errors = []
        
        for tag in existing_tags:
            try:
                shell(f"cd {repo_path} && git tag -d {tag}")
                shell(f"cd {repo_path} && git push origin :refs/tags/{tag}")
                deleted_count += 1
            except ShellError as e:
                errors.append(f"Error deleting tag {tag}: {e}")
        
        return {
            "success": len(errors) == 0,
            "deleted_count": deleted_count,
            "total_tags": len(existing_tags),
            "errors": errors,
            "message": f"Deleted {deleted_count}/{len(existing_tags)} tags"
        }
        
    except ShellError as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error listing tags: {e}"
        }


def cleanup_test_repository(
    repo_name: str,
    delete_remote: bool = False
) -> Dict[str, Any]:
    """Clean up a test repository.
    
    Args:
        repo_name: Name of the repository to clean up
        delete_remote: Whether to delete the remote repository too
        
    Returns:
        Dict with cleanup result
    """
    try:
        local_path = os.path.expanduser(f"~/miniature/{repo_name}")
        
        # Delete local repository
        local_deleted = False
        if os.path.exists(local_path):
            shell(f"rm -rf {local_path}")
            local_deleted = True
        
        # Delete remote repository if requested
        remote_deleted = False
        remote_error = None
        if delete_remote:
            try:
                shell(f"gh repo delete {repo_name} --confirm")
                remote_deleted = True
            except ShellError as e:
                remote_error = str(e)
                # Continue with local cleanup even if remote deletion fails
        
        # Remove from gitdbs config
        remove_from_gitdbs_config(f"https://github.com/crimson206/{repo_name}")
        
        message = f"Repository {repo_name} cleaned up"
        if local_deleted:
            message += " (local deleted)"
        if remote_deleted:
            message += " (remote deleted)"
        elif delete_remote and remote_error:
            message += f" (local deleted, remote failed: {remote_error[:50]}...)"
        
        return {
            "success": True,
            "repo_name": repo_name,
            "local_deleted": local_deleted,
            "remote_deleted": remote_deleted,
            "remote_error": remote_error,
            "message": message
        }
        
    except ShellError as e:
        return {
            "success": False,
            "repo_name": repo_name,
            "error": str(e),
            "message": f"Error cleaning up repository {repo_name}: {e}"
        }


def remove_from_gitdbs_config(
    repo_url: str,
    gitdbs_config: str = ".miniature/gitdbs.json"
):
    """Remove a repository entry from gitdbs config."""
    if not os.path.exists(gitdbs_config):
        return
    
    with open(gitdbs_config, 'r') as f:
        configs = json.load(f)
    
    # Remove matching entry
    configs = [config for config in configs if config.get('db-repo') != repo_url]
    
    with open(gitdbs_config, 'w') as f:
        json.dump(configs, f, indent=4)


def create_test_package(
    pkg_name: str,
    version: str,
    repo_url: str,
    root_dir: str = "",
    target_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Create a test package with pkg.json and sample files.
    
    Args:
        pkg_name: Name of the package
        version: Version of the package
        repo_url: Repository URL for db-repo
        root_dir: Root directory in repository
        target_dir: Target directory to create package in
        
    Returns:
        Dict with creation result
    """
    if target_dir is None:
        target_dir = pkg_name
    
    try:
        os.makedirs(target_dir, exist_ok=True)
        
        # Create pkg.json
        pkg_config = {
            "name": pkg_name,
            "version": version,
            "description": f"Test package {pkg_name}",
            "db-repo": repo_url,
            "root-dir": root_dir,
            "branch": "main"
        }
        
        with open(os.path.join(target_dir, "pkg.json"), "w") as f:
            json.dump(pkg_config, f, indent=2)
        
        # Create sample files
        with open(os.path.join(target_dir, "main.py"), "w") as f:
            f.write(f'print("Hello from {pkg_name}!")\n')
        
        with open(os.path.join(target_dir, "README.md"), "w") as f:
            f.write(f"# {pkg_name}\n\nThis is a test package for miniature examples.\n")
        
        return {
            "success": True,
            "pkg_name": pkg_name,
            "target_dir": os.path.abspath(target_dir),
            "message": f"Test package {pkg_name} created successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "pkg_name": pkg_name,
            "error": str(e),
            "message": f"Failed to create test package {pkg_name}: {e}"
        }


def get_repository_info(repo_name: str) -> Dict[str, Any]:
    """Get information about a repository.
    
    Args:
        repo_name: Name of the repository
        
    Returns:
        Dict with repository information
    """
    local_path = os.path.expanduser(f"~/miniature/{repo_name}")
    
    if not os.path.exists(local_path):
        return {
            "exists": False,
            "message": f"Repository {repo_name} not found locally"
        }
    
    try:
        # Get git status
        status = shell(f"cd {local_path} && git status --porcelain")
        
        # Get recent commits
        commits = shell(f"cd {local_path} && git log --oneline -5")
        
        # Get tags
        tags = shell(f"cd {local_path} && git tag -l")
        
        return {
            "exists": True,
            "local_path": local_path,
            "repo_url": f"https://github.com/crimson206/{repo_name}",
            "status": status.strip() if status.strip() else "Clean working directory",
            "recent_commits": commits.strip().split('\n') if commits.strip() else [],
            "tags": tags.strip().split('\n') if tags.strip() else []
        }
        
    except ShellError as e:
        return {
            "exists": True,
            "local_path": local_path,
            "error": str(e),
            "message": f"Error getting repository info: {e}"
        }
