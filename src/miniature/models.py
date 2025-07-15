from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class PkgJson(BaseModel):
    """Package metadata file (pkg.json) model.
    
    Required fields:
        version: Package version (e.g., "0.1.0", "1.2.3")
    
    Optional fields:
        name: Package display name
        description: Package description
        branch: branch name, where the package will be pushed to
    """
    version: str
    name: Optional[str] = None
    description: Optional[str] = None
    branch: Optional[str] = "main"


class MiniatureEntry(BaseModel):
    """Single package entry in miniature.json.
    
    Fields:
        pathName: Package path identifier (e.g., "component/my-card")
                  Used for creating tags like "component/my-card/v0.1.0"
        repo: Repository URL
        link: Local directory path relative to miniature.json
        version: Version specification (optional, defaults to "latest")
                 Can be exact version, "latest", or semver constraint
    """
    pathName: str
    repo: HttpUrl
    link: str
    version: Optional[str] = Field(default="latest")


class MiniatureJson(BaseModel):
    """Central miniature configuration file model.
    
    Contains a list of package entries to be loaded.
    """
    miniatures: List[MiniatureEntry] = Field(default_factory=list)

