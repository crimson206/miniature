import json
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
import pytest
from miniature.publish import publish_pkg, publish_pkg_from_json


class TestPublishPkg:
    """Test cases for publish_pkg function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.pkg_dir = os.path.join(self.temp_dir, "test_pkg")
        os.makedirs(self.pkg_dir)
        
        # Create test pkg.json
        self.pkg_config = {
            "version": "1.0.0",
            "root-dir": "test_pkg",
            "db-repo": "https://github.com/test/repo"
        }
        
        self.pkg_json_path = os.path.join(self.pkg_dir, "pkg.json")
        with open(self.pkg_json_path, 'w') as f:
            json.dump(self.pkg_config, f)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('miniature.publish.push_pkg')
    @patch('miniature.publish.create_tag')
    def test_publish_pkg_success_with_tag(self, mock_create_tag, mock_push_pkg):
        """Test successful package publishing with tagging."""
        # Mock push result
        mock_push_pkg.return_value = {
            "success": True,
            "repo_path": "/tmp/repo",
            "commit_message": "Update test_pkg",
            "pushed": True,
            "message": "Package pushed successfully"
        }
        
        # Mock tag result
        mock_create_tag.return_value = {
            "success": True,
            "tag_name": "test_pkg/1.0.0",
            "message": "Tag created successfully"
        }
        
        result = publish_pkg(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            commit_message="Test commit",
            push=True,
            tag=True
        )
        
        # Verify push was called
        mock_push_pkg.assert_called_once_with(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            commit_message="Test commit",
            push=True,
            gitdbs_config=".miniature/gitdbs.json"
        )
        
        # Verify tag was created
        mock_create_tag.assert_called_once_with(
            repo_url="https://github.com/test/repo",
            tag_name="test_pkg/1.0.0",
            tag_message="Release test_pkg/1.0.0",
            force=False,
            push=True,
            gitdbs_config=".miniature/gitdbs.json"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["repo_path"] == "/tmp/repo"
        assert result["commit_message"] == "Update test_pkg"
        assert result["pushed"] is True
        assert result["tag_result"]["success"] is True
        assert "Package pushed successfully" in result["message"]
        assert "Tag created successfully" in result["message"]
    
    @patch('miniature.publish.push_pkg')
    def test_publish_pkg_success_without_tag(self, mock_push_pkg):
        """Test successful package publishing without tagging."""
        mock_push_pkg.return_value = {
            "success": True,
            "repo_path": "/tmp/repo",
            "commit_message": "Update test_pkg",
            "pushed": True,
            "message": "Package pushed successfully"
        }
        
        result = publish_pkg(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            tag=False
        )
        
        # Verify push was called
        mock_push_pkg.assert_called_once()
        
        # Verify tag was not created
        assert result["tag_result"] is None
        assert result["success"] is True
        assert "Package pushed successfully" in result["message"]
    
    @patch('miniature.publish.push_pkg')
    def test_publish_pkg_push_failure(self, mock_push_pkg):
        """Test package publishing when push fails."""
        mock_push_pkg.return_value = {
            "success": False,
            "message": "Push failed"
        }
        
        result = publish_pkg(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json"
        )
        
        assert result["success"] is False
        assert "Push failed" in result["message"]
    
    @patch('miniature.publish.push_pkg')
    @patch('miniature.publish.create_tag')
    def test_publish_pkg_tag_failure(self, mock_create_tag, mock_push_pkg):
        """Test package publishing when tagging fails."""
        mock_push_pkg.return_value = {
            "success": True,
            "repo_path": "/tmp/repo",
            "commit_message": "Update test_pkg",
            "pushed": True,
            "message": "Package pushed successfully"
        }
        
        mock_create_tag.side_effect = Exception("Tag creation failed")
        
        result = publish_pkg(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            tag=True
        )
        
        assert result["success"] is False
        assert result["pushed"] is True
        assert "Push successful but tagging failed" in result["message"]
    
    def test_publish_pkg_meta_file_not_found(self):
        """Test publishing with non-existent meta file."""
        with pytest.raises(FileNotFoundError, match="Meta file not found"):
            publish_pkg(
                pkg_dir=self.pkg_dir,
                meta_file="nonexistent.json"
            )
    
    def test_publish_pkg_missing_version(self):
        """Test publishing with missing version in pkg.json."""
        # Create pkg.json without version
        invalid_config = {
            "root-dir": "test_pkg",
            "db-repo": "https://github.com/test/repo"
        }
        
        with open(self.pkg_json_path, 'w') as f:
            json.dump(invalid_config, f)
        
        with pytest.raises(ValueError, match="No 'version' found"):
            publish_pkg(pkg_dir=self.pkg_dir, meta_file="pkg.json")
    
    def test_publish_pkg_missing_db_repo(self):
        """Test publishing with missing db-repo in pkg.json."""
        # Create pkg.json without db-repo
        invalid_config = {
            "version": "1.0.0",
            "root-dir": "test_pkg"
        }
        
        with open(self.pkg_json_path, 'w') as f:
            json.dump(invalid_config, f)
        
        with pytest.raises(ValueError, match="No 'db-repo' found"):
            publish_pkg(pkg_dir=self.pkg_dir, meta_file="pkg.json")
    
    @patch('miniature.publish.push_pkg')
    @patch('miniature.publish.create_tag')
    def test_publish_pkg_with_root_dir(self, mock_create_tag, mock_push_pkg):
        """Test publishing with root-dir specified."""
        mock_push_pkg.return_value = {
            "success": True,
            "repo_path": "/tmp/repo",
            "commit_message": "Update test_pkg",
            "pushed": True,
            "message": "Package pushed successfully"
        }
        
        mock_create_tag.return_value = {
            "success": True,
            "tag_name": "test_pkg/1.0.0",
            "message": "Tag created successfully"
        }
        
        result = publish_pkg(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            tag=True
        )
        
        # Verify tag name includes root-dir
        mock_create_tag.assert_called_once_with(
            repo_url="https://github.com/test/repo",
            tag_name="test_pkg/1.0.0",  # root-dir/version
            tag_message="Release test_pkg/1.0.0",
            force=False,
            push=True,
            gitdbs_config=".miniature/gitdbs.json"
        )
    
    @patch('miniature.publish.push_pkg')
    @patch('miniature.publish.create_tag')
    def test_publish_pkg_without_root_dir(self, mock_create_tag, mock_push_pkg):
        """Test publishing without root-dir specified."""
        # Update pkg.json to remove root-dir
        self.pkg_config.pop("root-dir")
        with open(self.pkg_json_path, 'w') as f:
            json.dump(self.pkg_config, f)
        
        mock_push_pkg.return_value = {
            "success": True,
            "repo_path": "/tmp/repo",
            "commit_message": "Update test_pkg",
            "pushed": True,
            "message": "Package pushed successfully"
        }
        
        mock_create_tag.return_value = {
            "success": True,
            "tag_name": "1.0.0",
            "message": "Tag created successfully"
        }
        
        result = publish_pkg(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            tag=True
        )
        
        # Verify tag name is just version
        mock_create_tag.assert_called_once_with(
            repo_url="https://github.com/test/repo",
            tag_name="1.0.0",  # just version
            tag_message="Release 1.0.0",
            force=False,
            push=True,
            gitdbs_config=".miniature/gitdbs.json"
        )
    
    @patch('miniature.publish.push_pkg')
    @patch('miniature.publish.create_tag')
    def test_publish_pkg_force_tag(self, mock_create_tag, mock_push_pkg):
        """Test publishing with force tag option."""
        mock_push_pkg.return_value = {
            "success": True,
            "repo_path": "/tmp/repo",
            "commit_message": "Update test_pkg",
            "pushed": True,
            "message": "Package pushed successfully"
        }
        
        mock_create_tag.return_value = {
            "success": True,
            "tag_name": "test_pkg/1.0.0",
            "message": "Tag created successfully"
        }
        
        result = publish_pkg(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            tag=True,
            force_tag=True
        )
        
        # Verify force=True was passed to create_tag
        mock_create_tag.assert_called_once_with(
            repo_url="https://github.com/test/repo",
            tag_name="test_pkg/1.0.0",
            tag_message="Release test_pkg/1.0.0",
            force=True,  # force tag
            push=True,
            gitdbs_config=".miniature/gitdbs.json"
        )
    
    @patch('miniature.publish.push_pkg')
    @patch('miniature.publish.create_tag')
    def test_publish_pkg_no_push(self, mock_create_tag, mock_push_pkg):
        """Test publishing without pushing."""
        mock_push_pkg.return_value = {
            "success": True,
            "repo_path": "/tmp/repo",
            "commit_message": "Update test_pkg",
            "pushed": False,
            "message": "Package committed locally"
        }
        
        mock_create_tag.return_value = {
            "success": True,
            "tag_name": "test_pkg/1.0.0",
            "message": "Tag created locally"
        }
        
        result = publish_pkg(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            push=False,
            tag=True
        )
        
        # Verify push=False was passed to both functions
        mock_push_pkg.assert_called_once_with(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            commit_message=None,
            push=False,
            gitdbs_config=".miniature/gitdbs.json"
        )
        
        mock_create_tag.assert_called_once_with(
            repo_url="https://github.com/test/repo",
            tag_name="test_pkg/1.0.0",
            tag_message="Release test_pkg/1.0.0",
            force=False,
            push=False,  # same as main push setting
            gitdbs_config=".miniature/gitdbs.json"
        )


class TestPublishPkgFromJson:
    """Test cases for publish_pkg_from_json function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.pkg_dir = os.path.join(self.temp_dir, "test_pkg")
        os.makedirs(self.pkg_dir)
        
        # Create test pkg.json
        self.pkg_config = {
            "version": "1.0.0",
            "root-dir": "test_pkg",
            "db-repo": "https://github.com/test/repo"
        }
        
        self.pkg_json_path = os.path.join(self.pkg_dir, "pkg.json")
        with open(self.pkg_json_path, 'w') as f:
            json.dump(self.pkg_config, f)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('miniature.publish.publish_pkg')
    def test_publish_pkg_from_json_success(self, mock_publish_pkg):
        """Test successful publishing from JSON file path."""
        expected_result = {
            "success": True,
            "repo_path": "/tmp/repo",
            "commit_message": "Update test_pkg",
            "pushed": True,
            "message": "Package published successfully"
        }
        
        mock_publish_pkg.return_value = expected_result
        
        result = publish_pkg_from_json(
            pkg_json_path=self.pkg_json_path,
            commit_message="Test commit",
            push=True,
            tag=True,
            force_tag=False
        )
        
        # Verify publish_pkg was called with correct parameters
        mock_publish_pkg.assert_called_once_with(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            commit_message="Test commit",
            push=True,
            tag=True,
            force_tag=False,
            gitdbs_config=".miniature/gitdbs.json"
        )
        
        assert result == expected_result
    
    def test_publish_pkg_from_json_file_not_found(self):
        """Test publishing from non-existent JSON file."""
        non_existent_path = os.path.join(self.temp_dir, "nonexistent.json")
        
        with pytest.raises(FileNotFoundError):
            publish_pkg_from_json(pkg_json_path=non_existent_path)
    
    @patch('miniature.publish.publish_pkg')
    def test_publish_pkg_from_json_custom_gitdbs_config(self, mock_publish_pkg):
        """Test publishing with custom gitdbs config path."""
        mock_publish_pkg.return_value = {"success": True}
        
        publish_pkg_from_json(
            pkg_json_path=self.pkg_json_path,
            gitdbs_config="/custom/path/gitdbs.json"
        )
        
        # Verify custom gitdbs config was passed
        mock_publish_pkg.assert_called_once_with(
            pkg_dir=self.pkg_dir,
            meta_file="pkg.json",
            commit_message=None,
            push=True,
            tag=True,
            force_tag=False,
            gitdbs_config="/custom/path/gitdbs.json"
        )
    
    @patch('miniature.publish.publish_pkg')
    def test_publish_pkg_from_json_absolute_path(self, mock_publish_pkg):
        """Test publishing with absolute path to pkg.json."""
        mock_publish_pkg.return_value = {"success": True}
        
        # Use absolute path
        abs_pkg_json_path = os.path.abspath(self.pkg_json_path)
        
        publish_pkg_from_json(pkg_json_path=abs_pkg_json_path)
        
        # Verify correct directory was extracted
        expected_dir = os.path.dirname(abs_pkg_json_path)
        mock_publish_pkg.assert_called_once_with(
            pkg_dir=expected_dir,
            meta_file="pkg.json",
            commit_message=None,
            push=True,
            tag=True,
            force_tag=False,
            gitdbs_config=".miniature/gitdbs.json"
        )
