# GHCR Visibility & Package Metadata

This document explains how to make your GHCR package public, and how to add basic metadata.

## Make a GHCR package public (UI)
1. Go to your repository on GitHub: `https://github.com/<OWNER>/<REPO>`
2. Click **Packages** in the right-hand sidebar (or top 'Packages' tab).
3. Click the package `citysafesense`.
4. On the package page, click **Package settings**.
5. Under **Visibility**, choose **Public** and save.

## Make a GHCR package public (gh CLI)
You can use the GitHub CLI to open the package page or list packages, but changing visibility via CLI requires API calls.
A safe way is to open the package page and manually change visibility:

```bash
gh repo view <OWNER>/<REPO> --web
# then navigate to Packages and change visibility to Public
```

## Add package metadata / README
- GHCR displays metadata from the repository/package settings and from the Docker image labels.
- Add labels in your Dockerfile build step if you want additional metadata, e.g.:
  ```
  LABEL org.opencontainers.image.title="CitySafeSense"
  LABEL org.opencontainers.image.description="Edge AI for Urban Safety & Mobility"
  LABEL org.opencontainers.image.url="https://github.com/<OWNER>/<REPO>"
  ```
  These labels will be visible in the package details.

## Note about permissions
- Publishing to GHCR in CI uses `GITHUB_TOKEN` and requires repository permissions: `packages: write`.
- Making packages public is a repository-level operation that requires admin privileges.

## Troubleshooting
- If you don't see the Packages tab, ensure that:
  - The repository has at least one package published.
  - You have the required permissions to view/modify packages.

