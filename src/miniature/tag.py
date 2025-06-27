import os
from typing import Optional, Dict, Any
from pyshell import shell, ShellError
from .load import get_local_repo_path


def create_tag(
    repo_url: str,
    tag_name: str,
    tag_message: Optional[str] = None,
    force: bool = False,
    push: bool = True,
    gitdbs_config: str = ".miniature/gitdbs.json"
) -> Dict[str, Any]:
    """Create a git tag in a local repository and optionally push it to remote.
    
    Args:
        repo_url: Repository URL (e.g., "https://github.com/user/repo")
        tag_name: Name of the tag to create
        tag_message: Custom tag message (default: tag_name)
        force: Whether to force overwrite existing tag (default: False)
        push: Whether to push tag to remote (default: True)
        gitdbs_config: Path to gitdbs config file
        
    Returns:
        Dict containing operation result with keys:
        - action: str (created, overwritten, pushed)
        - tag_name: str
        - message: str
        
    Raises:
        FileNotFoundError: If local repository not found
        ShellError: If git operations fail
        ValueError: If tag exists and force=False
    """
    # Get local repository path
    local_repo_path = get_local_repo_path(repo_url, gitdbs_config)
    if not local_repo_path:
        raise FileNotFoundError(f"Local repository not found for {repo_url}. Check {gitdbs_config}")
    
    if not os.path.exists(local_repo_path):
        raise FileNotFoundError(f"Local repository path does not exist: {local_repo_path}")
    
    # Set default tag message
    if tag_message is None:
        tag_message = tag_name
    
    # Check if tag already exists
    try:
        shell(f"cd {local_repo_path} && git show-ref --tags --verify --quiet refs/tags/{tag_name}")
        tag_exists = True
    except ShellError:
        tag_exists = False
    
    # Handle existing tag
    if tag_exists:
        if force:
            # Delete local tag
            shell(f"cd {local_repo_path} && git tag -d {tag_name}")
            action = "overwritten"
        else:
            raise ValueError(f"Tag '{tag_name}' already exists. Use force=True to overwrite.")
    else:
        action = "created"
    
    # Create new tag
    shell(f"cd {local_repo_path} && git tag -a {tag_name} -m \"{tag_message}\"")
    
    # Push tag if requested
    if push:
        if force:
            # Use --force to overwrite remote tag
            shell(f"cd {local_repo_path} && git push --force origin {tag_name}")
        else:
            # Normal push
            shell(f"cd {local_repo_path} && git push origin {tag_name}")
        action = "pushed"
    
    return {
        "action": action,
        "tag_name": tag_name,
        "message": f"Tag '{tag_name}' {action}"
    }


def clean_tag(
    repo_url: str,
    tag_name: str,
    remote: Optional[str] = None,
    gitdbs_config: str = ".miniature/gitdbs.json"
) -> Dict[str, Any]:
    """Delete a tag locally and optionally from the remote.
    
    Args:
        repo_url: Repository URL
        tag_name: Name of the tag to delete
        remote: Remote name (if given, also delete from remote)
        gitdbs_config: Path to gitdbs config file
        
    Returns:
        Dict with result info
    Raises:
        FileNotFoundError: If local repository not found
        ShellError: If git operations fail
    """
    # Get local repository path
    local_repo_path = get_local_repo_path(repo_url, gitdbs_config)
    if not local_repo_path:
        raise FileNotFoundError(f"Local repository not found for {repo_url}. Check {gitdbs_config}")
    
    if not os.path.exists(local_repo_path):
        raise FileNotFoundError(f"Local repository path does not exist: {local_repo_path}")
    
    # Delete local tag (ignore error if not exist)
    try:
        shell(f"cd {local_repo_path} && git tag -d {tag_name}")
        local_msg = f"Deleted local tag '{tag_name}'"
    except ShellError:
        local_msg = f"Local tag '{tag_name}' did not exist"
    
    remote_msg = None
    if remote:
        try:
            shell(f"cd {local_repo_path} && git push {remote} :refs/tags/{tag_name}")
            remote_msg = f"Deleted remote tag '{tag_name}'"
        except ShellError:
            remote_msg = f"Remote tag '{tag_name}' did not exist or could not be deleted"
    
    return {
        "local": local_msg,
        "remote": remote_msg
    }
