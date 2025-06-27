import os
import re
import json
import shutil
from typing import Optional, Dict, Any, List
from pyshell import shell, ShellError


def get_local_repo_path(repo_url: str, gitdbs_config: str = ".miniature/gitdbs.json") -> Optional[str]:
    """Get local path for a repository from gitdbs config.
    
    Args:
        repo_url: Repository URL (e.g., "https://github.com/user/repo")
        gitdbs_config: Path to gitdbs config file
        
    Returns:
        Local repository path or None if not found
    """
    if not os.path.exists(gitdbs_config):
        return None
    
    with open(gitdbs_config, 'r') as f:
        configs = json.load(f)
    
    for config in configs:
        if config.get('db-repo') == repo_url:
            local_path = config.get('local_path', '')
            if local_path.startswith('~'):
                local_path = os.path.expanduser(local_path)
            return local_path
    
    return None


def load_pkg(
    repo: str,
    path: str,
    version: Optional[str] = None,
    target_dir: Optional[str] = None,
    branch: str = "main",
    clean: bool = False,
    gitdbs_config: str = ".miniature/gitdbs.json"
) -> Dict[str, Any]:
    """Load a package from a local git repository.
    
    Args:
        repo: Repository URL (e.g., "https://github.com/user/repo")
        path: Path within the repository (e.g., "example_pkg")
        version: Version/tag to load (e.g., "v1.0.0", ">=0.3.2", "latest")
        target_dir: Directory to copy to (default: {path})
        branch: Branch to use if no version specified (default: "main")
        clean: Whether to clean existing target directory (default: False)
        gitdbs_config: Path to gitdbs config file
        
    Returns:
        Dict containing operation result with keys:
        - success: bool
        - target_dir: str
        - repo: str
        - path: str
        - version: str
        - message: str
        
    Raises:
        FileNotFoundError: If local repository not found
        ValueError: If invalid parameters
    """
    # Validate inputs
    if not repo:
        raise ValueError("Repository URL is required")
    
    if not path:
        raise ValueError("Path within repository is required")
    
    # Get local repository path
    local_repo_path = get_local_repo_path(repo, gitdbs_config)
    if not local_repo_path:
        raise FileNotFoundError(f"Local repository not found for {repo}. Check {gitdbs_config}")
    
    if not os.path.exists(local_repo_path):
        raise FileNotFoundError(f"Local repository path does not exist: {local_repo_path}")
    
    # Set default target directory
    if target_dir is None:
        target_dir = path
    
    # Clean target directory if it exists and clean=True
    if clean and os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    # Create target directory if it doesn't exist
    os.makedirs(os.path.dirname(target_dir) if os.path.dirname(target_dir) else ".", exist_ok=True)
    
    try:
        # Checkout appropriate version/branch
        if version:
            if version == "latest":
                # Get latest tag
                latest_tag = _find_latest_tag(local_repo_path)
                if not latest_tag:
                    raise ValueError(f"No tags found in repository")
                shell(f"cd {local_repo_path} && git checkout {latest_tag}")
                actual_version = latest_tag
            else:
                # Check if it's a direct tag name or version spec
                if '/' in version:
                    # Direct tag name - use as is
                    shell(f"cd {local_repo_path} && git checkout {version}")
                    actual_version = version
                else:
                    # Version specification - find matching tag
                    matching_tag = _find_matching_tag(local_repo_path, version)
                    if not matching_tag:
                        raise ValueError(f"No tag found matching version {version}")
                    shell(f"cd {local_repo_path} && git checkout {matching_tag}")
                    actual_version = matching_tag
        else:
            # Use branch
            shell(f"cd {local_repo_path} && git checkout {branch}")
            actual_version = branch
        
        # Copy files from local repository
        source_path = os.path.join(local_repo_path, path)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Path '{path}' not found in repository")
        
        if os.path.isdir(source_path):
            shutil.copytree(source_path, target_dir, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, target_dir)
        
        return {
            "success": True,
            "target_dir": target_dir,
            "repo": repo,
            "path": path,
            "version": actual_version,
            "message": f"Successfully loaded package from local {repo}/{path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "target_dir": target_dir,
            "repo": repo,
            "path": path,
            "version": version or branch,
            "message": f"Failed to load package: {e}",
            "error": e
        }


def load_pkg_from_config(
    config: Dict[str, Any],
    target_dir: Optional[str] = None,
    clean: bool = False,
    gitdbs_config: str = ".miniature/gitdbs.json"
) -> Dict[str, Any]:
    """Load a package using configuration dictionary.
    
    Args:
        config: Dictionary with keys: repo, path, version, branch
        target_dir: Directory to copy to
        clean: Whether to clean existing target directory
        gitdbs_config: Path to gitdbs config file
        
    Returns:
        Dict containing operation result
    """
    return load_pkg(
        repo=config.get('repo'),
        path=config.get('path'),
        version=config.get('version'),
        target_dir=target_dir,
        branch=config.get('branch', 'main'),
        clean=clean,
        gitdbs_config=gitdbs_config
    )


def load_pkgs_from_file(
    config_file: str,
    package_names: Optional[List[str]] = None,
    clean: bool = False,
    gitdbs_config: str = ".miniature/gitdbs.json"
) -> Dict[str, Any]:
    """Load packages from a config file.
    
    Args:
        config_file: Path to config file (JSON)
        package_names: List of package names to load (None = load all)
        clean: Whether to clean existing target directories
        gitdbs_config: Path to gitdbs config file
        
    Returns:
        Dict containing operation results with keys:
        - success: bool
        - results: Dict mapping package names to their results
        - message: str
    """
    # Load config file
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    
    # Validate config structure
    if not isinstance(config_data, dict) or 'packages' not in config_data:
        raise ValueError("Config file must contain 'packages' object")
    
    packages = config_data['packages']
    
    # Determine which packages to load
    if package_names is None:
        package_names = list(packages.keys())
    
    # Load packages
    results = {}
    for name in package_names:
        if name not in packages:
            results[name] = {
                "success": False,
                "message": f"Package '{name}' not found in config"
            }
            continue
        
        pkg_config = packages[name]
        
        # Extract config values
        repo = pkg_config.get('db-repo')
        root_dir = pkg_config.get('root-dir', '')
        version = pkg_config.get('version')
        branch = pkg_config.get('branch', 'main')
        target_dir = pkg_config.get('target-dir')
        
        if not repo:
            results[name] = {
                "success": False,
                "message": f"No 'db-repo' found for package '{name}'"
            }
            continue
        
        # Load the package
        result = load_pkg(
            repo=repo,
            path=root_dir,
            version=version,
            target_dir=target_dir,
            branch=branch,
            clean=clean,
            gitdbs_config=gitdbs_config
        )
        results[name] = result
    
    # Create summary
    success_count = sum(1 for r in results.values() if r["success"])
    total_count = len(results)
    all_success = success_count == total_count
    
    message = f"Loaded {success_count}/{total_count} packages"
    if not all_success:
        message += " (some failed)"
    
    return {
        "success": all_success,
        "results": results,
        "message": message
    }


def _find_latest_tag(repo_path: str) -> Optional[str]:
    """Find the latest tag in a local repository.
    
    Args:
        repo_path: Path to local git repository
        
    Returns:
        Latest tag name or None if no tags found
    """
    try:
        tags_output = shell(f"cd {repo_path} && git tag -l")
        tags = [tag.strip() for tag in tags_output.strip().split('\n') if tag.strip()]
        
        if not tags:
            return None
        
        # Sort tags by version
        import packaging.version
        version_tags = []
        
        for tag in tags:
            try:
                # Extract version part from tag (e.g., "example_pkg/0.1.1" -> "0.1.1")
                version_part = tag.split('/')[-1] if '/' in tag else tag
                tag_ver = packaging.version.parse(version_part.lstrip('v'))
                version_tags.append((tag, tag_ver))
            except packaging.version.InvalidVersion:
                continue
        
        if not version_tags:
            return tags[-1]  # Return last tag if no valid versions
        
        # Sort by version and return latest
        version_tags.sort(key=lambda x: x[1])
        return version_tags[-1][0]
            
    except Exception:
        return None


def _find_matching_tag(repo_path: str, version_spec: str) -> Optional[str]:
    """Find a tag matching version specification in a local repository.
    
    Args:
        repo_path: Path to local git repository
        version_spec: Version specification (e.g., "0.3.2", ">=0.3.2")
        
    Returns:
        Matching tag name or None if no match found
    """
    try:
        tags_output = shell(f"cd {repo_path} && git tag -l")
        tags = [tag.strip() for tag in tags_output.strip().split('\n') if tag.strip()]
        
        if not tags:
            return None
        
        # Parse version specification
        import packaging.version
        import packaging.specifiers
        
        # Create specifier set for version requirements
        specifier_set = packaging.specifiers.SpecifierSet(version_spec)
        
        valid_tags = []
        for tag in tags:
            try:
                # Extract version part from tag (e.g., "example_pkg/0.1.1" -> "0.1.1")
                version_part = tag.split('/')[-1] if '/' in tag else tag
                tag_ver = packaging.version.parse(version_part.lstrip('v'))
                
                # Check if version matches specifier
                if tag_ver in specifier_set:
                    valid_tags.append((tag, tag_ver))
            except packaging.version.InvalidVersion:
                continue
        
        if not valid_tags:
            return None
        
        # Sort by version and return latest
        valid_tags.sort(key=lambda x: x[1])
        return valid_tags[-1][0]
            
    except Exception:
        return None


def setup_local_repository(
    repo_url: str,
    local_path: str,
    gitdbs_config: str = ".miniature/gitdbs.json"
) -> Dict[str, Any]:
    """Setup a local repository by cloning it if it doesn't exist.
    
    Args:
        repo_url: Repository URL to clone
        local_path: Local path where to clone the repository
        gitdbs_config: Path to gitdbs config file to update
        
    Returns:
        Dict containing operation result with keys:
        - success: bool
        - local_path: str
        - message: str
    """
    # Expand user path
    if local_path.startswith('~'):
        local_path = os.path.expanduser(local_path)
    
    # Check if repository already exists
    if os.path.exists(local_path):
        return {
            "success": True,
            "local_path": local_path,
            "message": f"Repository already exists at {local_path}"
        }
    
    try:
        # Create parent directory
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Clone repository
        shell(f"git clone {repo_url} {local_path}")
        
        # Update gitdbs config
        _update_gitdbs_config(repo_url, local_path, gitdbs_config)
        
        return {
            "success": True,
            "local_path": local_path,
            "message": f"Repository cloned to {local_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "local_path": local_path,
            "message": f"Failed to clone repository: {e}",
            "error": e
        }


def _update_gitdbs_config(repo_url: str, local_path: str, gitdbs_config: str):
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
            break
    else:
        # Add new entry
        configs.append({
            "name": repo_url.split('/')[-1].replace('.git', ''),
            "description": f"Local copy of {repo_url}",
            "db-repo": repo_url,
            "local_path": local_path
        })
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(gitdbs_config), exist_ok=True)
    
    # Write updated config
    with open(gitdbs_config, 'w') as f:
        json.dump(configs, f, indent=4)

