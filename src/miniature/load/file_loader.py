"""File-based package loading with miniature.json update functionality."""

import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

from ..models import PackageDefinition, RepotreeConfig, PkgJson
from .core import load_pkg
from .miniature_updater import update_miniature_json


def load_pkgs_from_file(
    config_file: str,
    package_names: Optional[List[str]] = None,
    clean: bool = False,
    gitdbs_config: Optional[str] = None,  # Deprecated
    cache_dir: Optional[str] = None,
    update_miniature: bool = True,
) -> List[Dict[str, Any]]:
    """Load packages from a configuration file.

    Supports pkg.json (with dependencies), miniature.json, and repotree.json formats.
    Automatically updates miniature.json with loaded packages.

    Args:
        config_file: Path to config file (pkg.json, miniature.json, or repotree.json)
        package_names: List of package names to load (None = load all)
        clean: Whether to clean existing target directories
        gitdbs_config: DEPRECATED
        cache_dir: Cache directory path
        update_miniature: Whether to update miniature.json after loading

    Returns:
        List of results for each package
    """
    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_path, "r") as f:
        data = json.load(f)

    results = []
    loaded_packages = []  # Track packages for miniature.json update

    # Check if it's pkg.json format (has "dependencies" array and optionally "name")
    if "dependencies" in data and isinstance(data["dependencies"], list):
        # Load as pkg.json with dependencies
        pkg_config = PkgJson.from_file(config_path)

        for entry in pkg_config.dependencies:
            if package_names and entry.pkg_name not in package_names:
                continue

            # Set loaded=True for dependencies we want to load
            entry.loaded = True

            result = load_pkg(
                package_def=entry,
                clean=clean,
                cache_dir=cache_dir,
                use_symlink=False,  # TODO: Make configurable
            )
            results.append(result)
            
            # Track successful loads for miniature.json update
            if result["success"]:
                loaded_packages.append({
                    "pkg_name": entry.pkg_name,
                    "repo": result["repo"],
                    "target_dir": result["target_dir"],
                    "branch": result["branch"],
                    "version": result["version"],
                    "package_def": entry,
                })

    # Check if it's repotree format (has "miniatures" or "repos")
    elif "miniatures" in data or "repos" in data:
        # Load as repotree config
        config = RepotreeConfig.from_file(config_path)

        for entry in config.get_loaded_entries():
            if package_names and entry.pkg_name not in package_names:
                continue

            result = load_pkg(
                package_def=entry,
                clean=clean,
                cache_dir=cache_dir,
                use_symlink=False,  # TODO: Make configurable
            )
            results.append(result)
            
            # Track successful loads for miniature.json update
            if result["success"]:
                loaded_packages.append({
                    "pkg_name": entry.pkg_name,
                    "repo": result["repo"],
                    "target_dir": result["target_dir"],
                    "branch": result["branch"],
                    "version": result["version"],
                    "package_def": entry,
                })

    # Legacy miniature format with "packages"
    elif "packages" in data:
        packages = data["packages"]

        if package_names is None:
            package_names = list(packages.keys())

        for name in package_names:
            if name not in packages:
                results.append(
                    {
                        "success": False,
                        "message": f"Package '{name}' not found in config",
                    }
                )
                continue

            pkg_config = packages[name]

            # Convert to PackageDefinition
            package_def = PackageDefinition(
                pkg_name=name,
                domain=pkg_config.get("db-repo", ""),
                path_name=pkg_config.get("root-dir", "."),
                branch=pkg_config.get("branch", "main"),
                local_dir=pkg_config.get("target-dir", name),
                version=pkg_config.get("version"),
                loaded=True,
            )

            result = load_pkg(package_def=package_def, clean=clean, cache_dir=cache_dir)
            results.append(result)
            
            # Track successful loads for miniature.json update
            if result["success"]:
                loaded_packages.append({
                    "pkg_name": name,
                    "repo": result["repo"],
                    "target_dir": result["target_dir"],
                    "branch": result["branch"],
                    "version": result["version"],
                    "package_def": package_def,
                })

    else:
        raise ValueError(
            "Invalid config file format - expected 'dependencies', 'miniatures', or 'packages' field"
        )

    # Update miniature.json if requested and there are successful loads
    if update_miniature and loaded_packages:
        try:
            update_miniature_json(loaded_packages)
        except Exception as e:
            print(f"Warning: Failed to update miniature.json: {e}")

    return results