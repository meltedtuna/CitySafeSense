#!/usr/bin/env python3
import subprocess, sys
print("Running tag resolver unit tests (pytest)...")
rc = subprocess.call([sys.executable, "-m", "pytest", "tests/test_tag_resolver.py", "-q"])
sys.exit(rc)
