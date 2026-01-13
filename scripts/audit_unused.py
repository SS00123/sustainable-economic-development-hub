"""Simple dead-code and unused-import audit helper.

This script is intentionally lightweight; it doesn't change code.

Usage:
  python scripts/audit_unused.py
"""

from __future__ import annotations

import subprocess
import sys


def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> int:
    code = 0
    code |= run([sys.executable, "-m", "ruff", "check", ".", "--select", "F401"])
    return code


if __name__ == "__main__":
    raise SystemExit(main())
