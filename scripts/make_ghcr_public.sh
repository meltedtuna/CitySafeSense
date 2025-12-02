#!/usr/bin/env bash
# Helper: open the repo page and echo next steps to make GHCR package public
# Usage: ./scripts/make_ghcr_public.sh <OWNER> <REPO>
OWNER="$1"
REPO="$2"
if [ -z "$OWNER" ] || [ -z "$REPO" ]; then
  echo "Usage: $0 <OWNER> <REPO>"
  exit 1
fi

echo "Opening repository page in browser. Please navigate to Packages -> citysafesense -> Package settings to change visibility."
if command -v gh >/dev/null 2>&1; then
  gh repo view "${OWNER}/${REPO}" --web
else
  echo "Install GitHub CLI (gh) to open the repo page from the command line, or open:"
  echo "https://github.com/${OWNER}/${REPO}"
fi

echo ""
echo "If you prefer to use the API with 'gh api' you can list packages with:"
echo "  gh api repos/${OWNER}/${REPO}/packages --jq '.[].name'"
echo ""
echo "Manual step: On the package page, change Visibility -> Public, and optionally add labels to your image build."
