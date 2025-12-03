#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/create_pr_with_workflow.sh [owner] [repo] [branch]
# Example:
#   ./scripts/create_pr_with_workflow.sh meltedtuna citysafesense-demo ci/add-snapshot-workflow

OWNER="${1:-meltedtuna}"
REPO="${2:-citysafesense-demo}"
BRANCH="${3:-ci/add-snapshot-workflow}"
WORKFLOW_PATH=".github/workflows/snapshot-and-artifact.yml"
README_PATH="README.md"

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not found. Install and authenticate it first: https://cli.github.com/"
  exit 1
fi

echo "Creating branch: ${BRANCH}"
git fetch origin || true
git checkout -B "${BRANCH}"

echo "Writing workflow file to ${WORKFLOW_PATH} (overwrites if exists)..."
mkdir -p "$(dirname "${WORKFLOW_PATH}")"
cat > "${WORKFLOW_PATH}" <<'YAML'
name: Build + Snapshot + Upload + Optional Deploy

on:
  workflow_dispatch:
  push:
    branches: [ main ]

concurrency:
  group: snapshot-preview-${{ github.ref_name || github.sha }}
  cancel-in-progress: true

permissions:
  contents: read
  actions: write

jobs:
  build:
    name: Build app
    runs-on: ubuntu-latest
    outputs:
      dist-path: ./dist
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Use Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18

      - name: Cache node modules
        uses: actions/cache@v4
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-node-

      - name: Install deps
        run: npm ci

      - name: Build
        run: npm run build

  serve-and-snapshot:
    name: Serve dist and capture snapshots
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Use Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18

      - name: Install deps (for puppeteer)
        run: |
          npm ci
          npm install --no-save http-server

      - name: Serve dist in background
        run: |
          mkdir -p artifacts
          npx http-server ./dist -p 5000 &>/dev/null & echo $! > /tmp/server.pid

      - name: Wait for server
        run: |
          echo "Waiting for http://localhost:5000..."
          for i in {1..20}; do
            if curl -sSf http://localhost:5000 >/dev/null; then
              echo "server up"; break
            fi
            sleep 1
          done

      - name: Run Puppeteer snapshots
        env:
          URL: http://localhost:5000
        run: |
          mkdir -p artifacts
          node scripts/export_snapshot.js --url=$URL --out=artifacts/snapshot_map.png
          node scripts/export_snapshot.js --url=$URL --out=artifacts/snapshot_ml.png
          node scripts/export_snapshot.js --url=$URL --out=artifacts/snapshot_devices.png
          ls -la artifacts

      - name: Upload snapshots
        uses: actions/upload-artifact@v4
        with:
          name: dashboard-snapshots
          path: artifacts/*.png

      - name: Shutdown server
        if: always()
        run: |
          if [ -f /tmp/server.pid ]; then kill $(cat /tmp/server.pid) || true; fi

  deploy-netlify:
    name: Deploy to Netlify (optional)
    runs-on: ubuntu-latest
    needs: serve-and-snapshot
    if: ${{ secrets.NETLIFY_AUTH_TOKEN != '' && secrets.NETLIFY_SITE_ID != '' }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Use Node
        uses: actions/setup-node@v4
        with:
          node-version: 18
      - name: Install Netlify CLI
        run: npm install --no-save netlify-cli
      - name: Deploy to Netlify
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
        run: |
          npx netlify deploy --dir=./dist --site=$NETLIFY_SITE_ID --prod --message "Preview from ${{ github.sha }}" || npx netlify deploy --dir=./dist --site=$NETLIFY_SITE_ID --message "Preview from ${{ github.sha }}"

  deploy-vercel:
    name: Deploy to Vercel (optional)
    runs-on: ubuntu-latest
    needs: serve-and-snapshot
    if: ${{ secrets.VERCEL_TOKEN != '' && secrets.VERCEL_PROJECT_ID != '' && secrets.VERCEL_ORG_ID != '' }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Use Node
        uses: actions/setup-node@v4
        with:
          node-version: 18
      - name: Install Vercel CLI
        run: npm install --no-save vercel
      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          npx vercel --prod --token $VERCEL_TOKEN --confirm --org $VERCEL_ORG_ID --project $VERCEL_PROJECT_ID
YAML

echo "Updating README with badges..."
BADGE_LINE="![CI Snapshot](https://github.com/${OWNER}/${REPO}/actions/workflows/$(basename ${WORKFLOW_PATH})/badge.svg) ![GHCR](https://img.shields.io/badge/ghcr-available-blue.svg)"
if [ -f "${README_PATH}" ]; then
  if ! grep -q "CI Snapshot" "${README_PATH}"; then
    echo -e "# CitySafeSense Demo (Vite + Tailwind)\n\n${BADGE_LINE}\n\n$(cat ${README_PATH})" > "${README_PATH}"
  else
    echo "README already contains badge block; leaving as-is."
  fi
else
  echo -e "# CitySafeSense Demo (Vite + Tailwind)\n\n${BADGE_LINE}\n\n" > "${README_PATH}"
fi

echo "Staging changes..."
git add "${WORKFLOW_PATH}" "${README_PATH}"
git commit -m "ci: add hardened snapshot workflow + README badges" || echo "No changes to commit"

echo "Pushing branch to origin..."
git push -u origin "${BRANCH}"

echo "Creating a draft PR..."
gh pr create \
  --title "ci: add snapshot workflow + badges" \
  --body "Adds build+snapshot workflow with optional Netlify/Vercel deploy jobs and README badges." \
  --base main \
  --head "${BRANCH}" \
  --draft \
  --label "ci"

echo "Done. Draft PR created (open your browser to review)."
