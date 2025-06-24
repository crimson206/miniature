#!/bin/bash

# @description: Publish a package by generating a tag with '{root-dir}/v{version}' format
# @arg pkg_root: Required. The root path of a pkg folder
# @option force,f [flag]: If the tag already exists, publish causes an error. If it is on, the version is override

# USER SETTING
# Your custom configuration goes here

PKG_ROOT='example_pkg'

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


echo $PKG_NAME


node -p "require('example_pkg/runsh.pkg.json').name" 2>/dev/null