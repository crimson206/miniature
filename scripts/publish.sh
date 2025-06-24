#!/bin/bash

# @description: Publish a package by generating a tag with '{root-dir}/v{version}' format
# @arg pkg_root: Required. The root path of a pkg folder
# @option force,f [flag]: If the tag already exists, publish causes an error. If it is on, the version is override

# USER SETTING
# Your custom configuration goes here

# Validate pkg_root argument
if [ -z "$PKG_ROOT" ]; then
    echo "Error: pkg_root argument is required"
    echo "Usage: runsh publish <pkg_root> [options]"
    exit 1
fi

# Check if pkg_root directory exists
if [ ! -d "$PKG_ROOT" ]; then
    echo "Error: Directory '$PKG_ROOT' does not exist"
    exit 1
fi

# Check if runsh.pkg.json exists
if [ ! -f "$PKG_ROOT/runsh.pkg.json" ]; then
    echo "Error: runsh.pkg.json not found in '$PKG_ROOT'"
    exit 1
fi

# Get package info from runsh.pkg.json
PKG_NAME=$(node -p "require('$PKG_ROOT/runsh.pkg.json').name" 2>/dev/null)
DB_REPO=$(node -p "require('$PKG_ROOT/runsh.pkg.json').db-repo" 2>/dev/null)
BRANCH=$(node -p "require('$PKG_ROOT/runsh.pkg.json').branch" 2>/dev/null || echo "main")
TAG_VERSION=$(node -p "require('$PKG_ROOT/runsh.pkg.json').version" 2>/dev/null)

if [ -z "$PKG_NAME" ] || [ -z "$DB_REPO" ] || [ -z "$TAG_VERSION" ]; then
    echo "Error: Invalid runsh.pkg.json - missing name, db-repo, or version"
    exit 1
fi

# Create tag name
TAG_NAME="${PKG_NAME}/v${TAG_VERSION}"

echo "Publishing package: $PKG_NAME"
echo "Tag: $TAG_NAME"
echo "DB Repository: $DB_REPO"
echo "Branch: $BRANCH"

# First, push content to db-repo
echo "Pushing content to db-repo..."
if ! runsh _push "$PKG_ROOT"; then
    echo "Error: Failed to push content to db-repo"
    exit 1
fi

# Create temporary directory for tag operations
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory for tag operations: $TEMP_DIR"

# Clone the db-repo for tag operations
cd "$TEMP_DIR" || exit 1
if ! git clone "$DB_REPO" .; then
    echo "Error: Failed to clone repository for tag operations"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Check if tag already exists
if git tag -l "$TAG_NAME" | grep -q "$TAG_NAME"; then
    if [ "$FORCE" = "1" ]; then
        echo "Warning: Tag '$TAG_NAME' already exists. Force flag is set, will override."
        git tag -d "$TAG_NAME" 2>/dev/null
        git push origin ":refs/tags/$TAG_NAME" 2>/dev/null
    else
        echo "Error: Tag '$TAG_NAME' already exists. Use --force to override."
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

# Create tag
git tag "$TAG_NAME"

# Push tag to remote
if git push origin "$TAG_NAME"; then
    echo "Successfully published $TAG_NAME to $DB_REPO"
else
    echo "Error: Failed to push tag to remote"
    git tag -d "$TAG_NAME" 2>/dev/null
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Clean up
rm -rf "$TEMP_DIR" 