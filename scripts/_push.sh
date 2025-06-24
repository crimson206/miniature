#!/bin/bash

# @description: Helper script to push package content to db-repo by cloning, overwriting folder, and pushing changes
# @arg pkg_root: Required. The root path of a pkg folder

# Validate pkg_root argument
if [ -z "$PKG_ROOT" ]; then
    echo "Error: pkg_root argument is required"
    echo "Usage: runsh _push <pkg_root>"
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
ROOT_DIR=$(node -p "require('$PKG_ROOT/runsh.pkg.json').root-dir" 2>/dev/null)

if [ -z "$PKG_NAME" ] || [ -z "$DB_REPO" ]; then
    echo "Error: Invalid runsh.pkg.json - missing name or db-repo"
    exit 1
fi

echo "Pushing package: $PKG_NAME"
echo "DB Repository: $DB_REPO"
echo "Branch: $BRANCH"
echo "Root directory: $ROOT_DIR"

# Create temporary directory for cloning
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

# Clone the db-repo
cd "$TEMP_DIR" || exit 1
if ! git clone "$DB_REPO" .; then
    echo "Error: Failed to clone repository"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Checkout the target branch
if ! git checkout "$BRANCH" 2>/dev/null; then
    echo "Creating new branch: $BRANCH"
    git checkout -b "$BRANCH"
fi

# Create root directory if it doesn't exist
if [ -n "$ROOT_DIR" ]; then
    mkdir -p "$ROOT_DIR"
    TARGET_DIR="$ROOT_DIR"
else
    TARGET_DIR="."
fi

# Remove existing content and copy new content
if [ -d "$TARGET_DIR" ]; then
    rm -rf "$TARGET_DIR"/*
fi

# Copy package content to target directory
cp -r "$PKG_ROOT"/* "$TARGET_DIR/"

# Add all changes
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "No changes to commit"
    rm -rf "$TEMP_DIR"
    exit 0
fi

# Commit changes
COMMIT_MSG="Update $PKG_NAME package"
if ! git commit -m "$COMMIT_MSG"; then
    echo "Error: Failed to commit changes"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Push changes
if ! git push origin "$BRANCH"; then
    echo "Error: Failed to push changes to remote"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "Successfully pushed changes to $DB_REPO:$BRANCH"

# Clean up
rm -rf "$TEMP_DIR"
