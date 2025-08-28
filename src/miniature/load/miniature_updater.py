"""Miniature.json update functionality."""

import json
import os
from typing import List, Dict, Any
from pathlib import Path


def update_miniature_json(loaded_packages: List[Dict[str, Any]], miniature_file: str = "miniature.json") -> None:
    """Update miniature.json with loaded packages.

    Args:
        loaded_packages: List of loaded package information
        miniature_file: Path to miniature.json file (default: "miniature.json")
    """
    miniature_path = Path(miniature_file)
    
    # Load existing miniature.json or create new structure
    if miniature_path.exists():
        with open(miniature_path, "r") as f:
            miniature_data = json.load(f)
    else:
        miniature_data = {"miniatures": []}
    
    # Ensure miniatures array exists
    if "miniatures" not in miniature_data:
        miniature_data["miniatures"] = []
    
    # Convert existing miniatures to dict for easier lookup
    existing_miniatures = {
        mini.get("pkgName", mini.get("pkg_name", "")): mini 
        for mini in miniature_data["miniatures"]
    }
    
    # Update or add each loaded package
    for pkg_info in loaded_packages:
        pkg_name = pkg_info["pkg_name"]
        package_def = pkg_info["package_def"]
        
        # Create miniature entry
        miniature_entry = {
            "pkgName": pkg_name,
            "domain": package_def.domain,
            "repoName": package_def.repo_name,
            "branch": pkg_info["branch"],
            "localDir": pkg_info["target_dir"],
            "loaded": True,
        }
        
        # Add version if available
        if pkg_info.get("version") and pkg_info["version"] != pkg_info["branch"]:
            miniature_entry["version"] = pkg_info["version"]
        
        # Update existing entry or add new one
        existing_miniatures[pkg_name] = miniature_entry
    
    # Update miniatures array
    miniature_data["miniatures"] = list(existing_miniatures.values())
    
    # Write updated miniature.json
    with open(miniature_path, "w") as f:
        json.dump(miniature_data, f, indent=2)
    
    print(f"Updated {miniature_file} with {len(loaded_packages)} packages")


def mark_package_loaded(pkg_name: str, miniature_file: str = "miniature.json") -> None:
    """Mark a specific package as loaded in miniature.json.

    Args:
        pkg_name: Name of the package to mark as loaded
        miniature_file: Path to miniature.json file (default: "miniature.json")
    """
    miniature_path = Path(miniature_file)
    
    if not miniature_path.exists():
        print(f"Warning: {miniature_file} not found")
        return
    
    with open(miniature_path, "r") as f:
        miniature_data = json.load(f)
    
    if "miniatures" not in miniature_data:
        print(f"Warning: No miniatures found in {miniature_file}")
        return
    
    # Find and update the package
    updated = False
    for miniature in miniature_data["miniatures"]:
        if miniature.get("pkgName") == pkg_name or miniature.get("pkg_name") == pkg_name:
            miniature["loaded"] = True
            updated = True
            break
    
    if updated:
        with open(miniature_path, "w") as f:
            json.dump(miniature_data, f, indent=2)
        print(f"Marked {pkg_name} as loaded in {miniature_file}")
    else:
        print(f"Warning: Package {pkg_name} not found in {miniature_file}")


def mark_package_unloaded(pkg_name: str, miniature_file: str = "miniature.json") -> None:
    """Mark a specific package as unloaded in miniature.json.

    Args:
        pkg_name: Name of the package to mark as unloaded
        miniature_file: Path to miniature.json file (default: "miniature.json")
    """
    miniature_path = Path(miniature_file)
    
    if not miniature_path.exists():
        print(f"Warning: {miniature_file} not found")
        return
    
    with open(miniature_path, "r") as f:
        miniature_data = json.load(f)
    
    if "miniatures" not in miniature_data:
        print(f"Warning: No miniatures found in {miniature_file}")
        return
    
    # Find and update the package
    updated = False
    for miniature in miniature_data["miniatures"]:
        if miniature.get("pkgName") == pkg_name or miniature.get("pkg_name") == pkg_name:
            miniature["loaded"] = False
            updated = True
            break
    
    if updated:
        with open(miniature_path, "w") as f:
            json.dump(miniature_data, f, indent=2)
        print(f"Marked {pkg_name} as unloaded in {miniature_file}")
    else:
        print(f"Warning: Package {pkg_name} not found in {miniature_file}")