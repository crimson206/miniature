#!/bin/bash

# @description: Load a package from GitHub repository using npx degit (similar to clone but loads folder only)
# @option repo_url: GitHub repository URL or owner/repo format
# @option target_dir [optional]: Target directory to load the package into
# @option version: Specific version/tag to load (default: latest)
# @option force,f [flag]: Force overwrite if target directory exists

# USER SETTING
# Your custom configuration goes here

# Validate repo_url argument
if [ -z "$REPO_URL" ]; then
    echo "Error: repo_url argument is required"
    echo "Usage: runsh load <repo_url> [target_dir] [options]"
    echo "Examples:"
    echo "  runsh load owner/repo"
    echo "  runsh load https://github.com/owner/repo"
    echo "  runsh load owner/repo my-package --version v1.0.0"
    exit 1
fi

# Parse repository URL
if [[ "$REPO_URL" == https://github.com/* ]]; then
    # Extract owner/repo from full URL
    REPO_PATH=$(echo "$REPO_URL" | sed 's|https://github.com/||')
else
    REPO_PATH="$REPO_URL"
fi

# Set target directory
if [ -n "$TARGET_DIR" ]; then
    OUTPUT_DIR="$TARGET_DIR"
else
    # Extract repo name from path
    REPO_NAME=$(basename "$REPO_PATH")
    OUTPUT_DIR="$REPO_NAME"
fi

# Check if target directory exists
if [ -d "$OUTPUT_DIR" ]; then
    if [ "$FORCE" = "1" ]; then
        if [ "$QUIET" != "1" ]; then
            echo "Warning: Directory '$OUTPUT_DIR' already exists. Force flag is set, will overwrite."
        fi
        rm -rf "$OUTPUT_DIR"
    else
        echo "Error: Directory '$OUTPUT_DIR' already exists. Use --force to overwrite."
        exit 1
    fi
fi

# Build degit command
DEGIT_CMD="npx degit"

# Add version if specified
if [ -n "$VERSION" ]; then
    DEGIT_CMD="$DEGIT_CMD $REPO_PATH#$VERSION"
else
    DEGIT_CMD="$DEGIT_CMD $REPO_PATH"
fi

# Add output directory
DEGIT_CMD="$DEGIT_CMD $OUTPUT_DIR"

if [ "$QUIET" != "1" ]; then
    echo "Loading package from: $REPO_PATH"
    if [ -n "$VERSION" ]; then
        echo "Version: $VERSION"
    fi
    echo "Target directory: $OUTPUT_DIR"
    echo "Command: $DEGIT_CMD"
fi

# Execute degit command
if eval "$DEGIT_CMD"; then
    if [ "$QUIET" != "1" ]; then
        echo "Successfully loaded package to: $OUTPUT_DIR"
    fi
else
    echo "Error: Failed to load package"
    exit 1
fi 