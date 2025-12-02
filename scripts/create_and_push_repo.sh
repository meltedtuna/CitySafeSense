#!/usr/bin/env bash
# Create a GitHub repository and push the current repo to it.
# Requires: gh CLI (https://cli.github.com/) authenticated, or GITHUB_TOKEN env var and curl.
# Usage:
#   ./scripts/create_and_push_repo.sh my-org/my-repo
set -euo pipefail
REPO="$1"
# If gh CLI available, use it
if command -v gh >/dev/null 2>&1; then
  echo "Creating repository via gh CLI..."
  gh repo create "$REPO" --public --confirm
  git remote add origin "git@github.com:${REPO}.git" || true
  git branch -M main
  git push -u origin main
  echo "Pushed to git@github.com:${REPO}.git"
else
  echo "gh CLI not found. Please install it or create the repo manually and push."
  exit 1
fi
