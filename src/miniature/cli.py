"""CLI interface for miniature package management system."""

from runpycli import Runpy

# Import all the functions we want to expose as CLI commands
from .load import load_pkg, load_pkgs_from_file
from .publish import publish_pkg
from .tag import tag_pkg
from .push import push_pkg
from .cache import get_cache
from .utils import fix_git_filemode, fix_cache_filemode, is_windows_filesystem

cli = Runpy()

# Register functions directly without wrappers
cli.register(load_pkg, name="load")
cli.register(load_pkgs_from_file, name="load-from-file")
cli.register(publish_pkg, name="publish")
cli.register(tag_pkg, name="tag-package")
cli.register(push_pkg, name="push")

# Cache management functions
@cli.register
def cache_list(cache_dir=None):
    """List all cached repositories."""
    cache = get_cache(cache_dir)
    return cache.list_cached_repos()

@cli.register
def cache_clear(cache_dir=None, confirm=False):
    """Clear the repository cache."""
    if not confirm:
        response = input("Are you sure you want to clear the cache? (y/N): ")
        if response.lower() != 'y':
            return {"status": "cancelled", "message": "Cache clear cancelled"}
    
    cache = get_cache(cache_dir)
    cache.clear_cache()
    return {"status": "success", "message": "Cache cleared successfully"}

@cli.register
def cache_remove(repo_url, cache_dir=None):
    """Remove a specific repository from cache."""
    cache = get_cache(cache_dir)
    cache.remove_repo(repo_url)
    return {"status": "success", "message": f"Removed {repo_url} from cache"}

# Utility functions
cli.register(fix_git_filemode, name="fix-filemode")
cli.register(fix_cache_filemode, name="fix-cache-modes")
cli.register(is_windows_filesystem, name="check-windows-fs")

if __name__ == "__main__":
    cli.app()