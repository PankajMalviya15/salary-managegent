#!/usr/bin/env python
"""Run all tests and print results."""
import subprocess
import sys

result = subprocess.run(
    [
        sys.executable, "-m", "pytest",
        "tests/test_employees_api.py",
        "tests/test_analytics_api.py",
        "-v", "--tb=line",
    ],
    capture_output=True, text=True,
)
print(result.stdout)
if result.stderr:
    print(result.stderr)
sys.exit(result.returncode)
