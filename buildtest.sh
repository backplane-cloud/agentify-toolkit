#!/usr/bin/env bash
set -e

# Check for Python and Twine
command -v python3 >/dev/null 2>&1 || { echo >&2 "python3 not found."; exit 1; }
command -v twine >/dev/null 2>&1 || { echo >&2 "twine not found."; exit 1; }

echo "Cleaning build artifacts..."
rm -rf dist/ build/ *.egg-info

echo "Building wheel + sdist..."
python3 -m build

echo "Uploading to TestPyPI..."
python3 -m twine upload -r testpypi dist/*

echo "Done!"
