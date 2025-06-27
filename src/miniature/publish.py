import json
import os
from typing import Optional, Dict, Any
from .push import push_pkg
from .tag import create_tag


def publish_pkg(
    pkg_dir: str = ".",
    meta_file: str = "pkg.json",
    commit_message: Optional[str] = None,
    push: bool = True,
    tag: bool = True,
    force_tag: bool = False,
    gitdbs_config: str = ".miniature/gitdbs.json"
) -> Dict[str, Any]:
    """Publish a package with push and optional tagging using local repository.
    
    Args:
        pkg_dir: Directory containing the package to publish
        meta_file: Name of the meta file (default: "pkg.json")
        commit_message: Custom commit message (default: "Update from {dirname}")
        push: Whether to push changes to remote (default: True)
        tag: Whether to create a tag (default: True)
        force_tag: Whether to force overwrite existing tag (default: False)
        gitdbs_config: Path to gitdbs config file
        
    Returns:
        Dict containing operation result with keys:
        - success: bool
        - repo_path: str (path to local repository)
        - commit_message: str
        - pushed: bool
        - tag_result: Dict from create_tag (if tag=True)
        - message: str
        
    Raises:
        FileNotFoundError: If meta file doesn't exist
        ShellError: If git operations fail
        ValueError: If tag exists and force_tag=False
    """
    # Load package configuration to get version and root-dir
    meta_file_path = os.path.join(pkg_dir, meta_file)
    
    if not os.path.exists(meta_file_path):
        raise FileNotFoundError(f"Meta file not found: {meta_file_path}")
    
    with open(meta_file_path, 'r') as f:
        pkg_config = json.load(f)
    
    version = pkg_config.get('version')
    root_dir = pkg_config.get('root-dir', '')
    repo_url = pkg_config.get('db-repo')
    
    if not version:
        raise ValueError(f"No 'version' found in {meta_file}")
    
    if not repo_url:
        raise ValueError(f"No 'db-repo' found in {meta_file}")
    
    # Push the package
    push_result = push_pkg(
        pkg_dir=pkg_dir,
        meta_file=meta_file,
        commit_message=commit_message,
        push=push,
        gitdbs_config=gitdbs_config
    )
    
    if not push_result["success"]:
        return push_result
    
    # Create tag if requested
    tag_result = None
    if tag:
        # Generate tag name: {root-dir}/{version}
        tag_name = f"{root_dir}/{version}" if root_dir else version
        
        try:
            tag_result = create_tag(
                repo_url=repo_url,
                tag_name=tag_name,
                tag_message=f"Release {tag_name}",
                force=force_tag,
                push=push,  # Same push setting as main operation
                gitdbs_config=gitdbs_config
            )
        except Exception as e:
            # If tagging fails, return push result with error info
            return {
                "success": False,
                "repo_path": push_result["repo_path"],
                "commit_message": push_result["commit_message"],
                "pushed": push_result["pushed"],
                "tag_result": None,
                "message": f"Push successful but tagging failed: {e}"
            }
    
    # Combine results
    if tag and tag_result:
        message = f"{push_result['message']}, {tag_result['message']}"
    else:
        message = push_result['message']
    
    result = {
        "success": True,
        "repo_path": push_result["repo_path"],
        "commit_message": push_result["commit_message"],
        "pushed": push_result["pushed"],
        "tag_result": tag_result,
        "message": message
    }
    
    return result


def publish_pkg_from_json(
    pkg_json_path: str,
    commit_message: Optional[str] = None,
    push: bool = True,
    tag: bool = True,
    force_tag: bool = False,
    gitdbs_config: str = ".miniature/gitdbs.json"
) -> Dict[str, Any]:
    """Publish a package using full path to pkg.json file.
    
    This is a convenience function that extracts the directory and file name
    from the full pkg.json path.
    
    Args:
        pkg_json_path: Full path to pkg.json file
        commit_message: Custom commit message
        push: Whether to push changes to remote (default: True)
        tag: Whether to create a tag (default: True)
        force_tag: Whether to force overwrite existing tag (default: False)
        gitdbs_config: Path to gitdbs config file
        
    Returns:
        Dict containing operation result
        
    Raises:
        FileNotFoundError: If pkg.json doesn't exist
        ShellError: If git operations fail
        ValueError: If tag exists and force_tag=False
    """
    pkg_dir = os.path.dirname(os.path.abspath(pkg_json_path))
    meta_file = os.path.basename(pkg_json_path)
    
    return publish_pkg(
        pkg_dir=pkg_dir,
        meta_file=meta_file,
        commit_message=commit_message,
        push=push,
        tag=tag,
        force_tag=force_tag,
        gitdbs_config=gitdbs_config
    )
