import os
import json
import tempfile
import shutil
import pytest
from miniature.load import load_pkg


def make_gitdbs_config(tmpdir, repo_url, local_path):
    config_path = os.path.join(tmpdir, "gitdbs.json")
    with open(config_path, "w") as f:
        json.dump([{"db-repo": repo_url, "local_path": local_path}], f)
    return config_path


def test_load_pkg_success(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    repo_url = "https://github.com/test/repo"
    repo_path = os.path.join(tmpdir, "repo")
    os.makedirs(os.path.join(repo_path, "pkg"))
    config_path = make_gitdbs_config(tmpdir, repo_url, repo_path)

    def fake_shell(cmd):
        return ""
    monkeypatch.setattr("miniature.load.shell", fake_shell)

    result = load_pkg(
        repo=repo_url,
        path="pkg",
        version=None,
        target_dir=os.path.join(tmpdir, "out"),
        gitdbs_config=config_path
    )
    assert result["success"] is True
    assert result["repo"] == repo_url
    shutil.rmtree(tmpdir)


def test_load_pkg_missing_repo():
    with pytest.raises(ValueError):
        load_pkg(repo="", path="pkg")


def test_load_pkg_missing_path():
    with pytest.raises(ValueError):
        load_pkg(repo="repo", path="") 