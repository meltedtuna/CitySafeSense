"""
Utility to resolve image tag selection logic for the smoke workflow.

Logic:
- If input_tag provided (non-empty), return it.
- Else if release_tag provided (non-empty), return it.
- Else if git_tags list provided and non-empty, return the latest tag using semantic sort if possible,
  otherwise return the last element (assuming tags are ordered).
- Else return "latest".
This module is intended for unit testing the tag resolution logic outside of GitHub Actions.
"""
from typing import List, Optional
import re

def _semver_key(tag: str):
    # attempt to parse semantic version like v1.2.3 or 1.2.3
    m = re.search(r'(\d+)(?:\.(\d+))?(?:\.(\d+))?', tag)
    if not m:
        return (0,0,0)
    major = int(m.group(1)) if m.group(1) else 0
    minor = int(m.group(2)) if m.group(2) else 0
    patch = int(m.group(3)) if m.group(3) else 0
    return (major, minor, patch)

def resolve_tag(input_tag: Optional[str], release_tag: Optional[str], git_tags: Optional[List[str]]):
    """
    Resolve the image tag based on priorities.
    """
    if input_tag and input_tag.strip():
        return input_tag.strip()
    if release_tag and release_tag.strip():
        return release_tag.strip()
    if git_tags:
        # prefer tags that contain digits (build numbers or versions) when semver parsing isn't decisive
        digit_tags = [t for t in git_tags if any(ch.isdigit() for ch in t)]
        if digit_tags:
            try:
                tags = digit_tags
            except Exception:
                tags = git_tags
        else:
            tags = git_tags

        # attempt to sort by semver-like pattern
        try:
            # filter out empty
            tags = [t for t in git_tags if t]
            # sort by semver key descending
            tags_sorted = sorted(tags, key=_semver_key, reverse=True)
            return tags_sorted[0]
        except Exception:
            return git_tags[-1] if git_tags else "latest"
    return "latest"
