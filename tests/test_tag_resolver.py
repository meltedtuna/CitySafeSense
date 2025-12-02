import pytest
from src.ci.tag_resolver import resolve_tag

def test_input_tag_precedence():
    assert resolve_tag("v2.0.0", "v1.9.0", ["v1.8.0","v1.9.0"]) == "v2.0.0"

def test_release_tag_fallback():
    assert resolve_tag("", "v1.9.1", ["v1.8.0","v1.9.0"]) == "v1.9.1"

def test_git_tags_semver_sort():
    tags = ["v1.2.0","v1.10.0","v1.3.5"]
    assert resolve_tag("", "", tags) == "v1.10.0"

def test_no_tags_returns_latest():
    assert resolve_tag("", "", []) == "latest"
    assert resolve_tag(None, None, None) == "latest"

def test_non_semver_tags():
    tags = ["build-123","build-124","alpha"]
    # prefer tags with digits; expect one of the digit tags
    res = resolve_tag("", "", tags)
    assert res in ["build-123","build-124"]


def test_whitespace_input_and_release():
    assert resolve_tag("  v3.0.0  ", " v2.0.0 ", ["v1.0.0"]) == "v3.0.0"
    assert resolve_tag("", "   v2.1.0  ", ["v1.0.0"]) == "v2.1.0"

def test_numeric_tags_no_v():
    tags = ["1.0.0", "2.0.0", "1.10.0"]
    assert resolve_tag("", "", tags) == "2.0.0"

def test_malformed_tags_and_duplicates():
    tags = ["alpha", "beta", "alpha", ""]
    # should return one of the tags present (semver sort won't apply)
    res = resolve_tag("", "", tags)
    assert res in tags or res == "latest"

def test_pre_release_and_build_metadata():
    tags = ["v1.2.0-rc1", "v1.2.0", "v1.1.9"]
    # semver-like detection should pick v1.2.0 over rc
    assert resolve_tag("", "", tags) == "v1.2.0"

def test_large_number_versions():
    tags = ["v10.2.3", "v2.20.30", "v3.100.1"]
    assert resolve_tag("", "", tags) == "v10.2.3" or resolve_tag("", "", tags) == "v3.100.1"



def test_mixed_digit_and_alpha_tags():
    tags = ["alpha", "v1.0.0", "build-42", "rc"]
    # semver should pick v1.0.0; digit preference applies when semver absent
    assert resolve_tag("", "", tags) == "v1.0.0"
