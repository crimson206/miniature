import os
import json
import tempfile
import shutil
from miniature.load import get_local_repo_path

def test_get_local_repo_path_found():
    tmpdir = tempfile.mkdtemp()
    repo_url = "https://github.com/test/repo"
    local_path = os.path.join(tmpdir, "repo")
    config_path = os.path.join(tmpdir, "gitdbs.json")
    with open(config_path, "w") as f:
        json.dump([{"db-repo": repo_url, "local_path": local_path}], f)
    assert get_local_repo_path(repo_url, config_path) == local_path
    shutil.rmtree(tmpdir)

def test_get_local_repo_path_not_found():
    tmpdir = tempfile.mkdtemp()
    repo_url = "https://github.com/test/repo"
    config_path = os.path.join(tmpdir, "gitdbs.json")
    with open(config_path, "w") as f:
        json.dump([], f)
    assert get_local_repo_path(repo_url, config_path) is None
    shutil.rmtree(tmpdir) 