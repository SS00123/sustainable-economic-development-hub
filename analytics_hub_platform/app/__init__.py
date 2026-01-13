"""Application layer: reusable UI components and styles.

This package also exposes a small CLI entrypoint (`analytics_hub_platform.app:main`)
used by the `analytics-hub` console script.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path


def main(argv: Sequence[str] | None = None) -> int:
    """Launch the Streamlit app.

    This targets the repo-local `streamlit_app.py` when present.
    """

    args = list(sys.argv[1:] if argv is None else argv)
    repo_root = Path(__file__).resolve().parents[2]
    app_file = repo_root / "streamlit_app.py"

    if not app_file.exists():
        print(
            "streamlit_app.py not found. Run from the repository root or use `streamlit run streamlit_app.py`.",
            file=sys.stderr,
        )
        return 2

    cmd = [sys.executable, "-m", "streamlit", "run", str(app_file), *args]
    return subprocess.call(cmd)
