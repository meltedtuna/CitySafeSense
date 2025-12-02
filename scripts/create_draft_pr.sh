#!/usr/bin/env bash
# Create a branch, commit changes, push, and open a draft PR using gh CLI.
# Usage: ./scripts/create_draft_pr.sh my-branch "My PR title" "PR body here"
set -euo pipefail
BRANCH="${1:-ci/add-tag-resolver-tests}"
TITLE="${2:-'Add tag resolver tests and CI'}"
BODY="${3:-'This PR adds expanded unit tests for tag_resolver and a CI workflow to run them.'}"

git fetch origin || true
git checkout -b "${BRANCH}"

git add src/ci/tag_resolver.py tests/test_tag_resolver.py .github/workflows/tag-resolver-tests.yml
git commit -m "${TITLE}" || echo "No changes to commit"
git push -u origin "${BRANCH}"

if command -v gh >/dev/null 2>&1; then
  gh pr create --title "${TITLE}" --body "${BODY}" --label "ci" --draft
  echo "Draft PR created via gh CLI."
else
  echo "gh CLI not found. Branch pushed: ${BRANCH}"
  echo "Create a draft PR from the GitHub UI."
fi
