from pathlib import Path

def test_ascii_filenames():
    """Ensure all page filenames are ASCII."""
    pages_dir = Path("pages")
    if pages_dir.exists():
        for p in pages_dir.glob("*.py"):
            assert p.name.isascii(), f"Non-ASCII filename found: {p.name}"

def test_no_datetime_utc():
    """Ensure datetime . UTC (Python 3.11+) is not used."""
    # Scan all python files
    root_dir = Path(".")
    for path in root_dir.rglob("*.py"):
        if "venv" in str(path) or "__pycache__" in str(path):
            continue

        # Skip this test file itself and the verification script
        if path.name in ["test_repo_sanity.py", "verify_repo.py"]:
            continue

        try:
            content = path.read_text(encoding="utf-8")
            assert "datetime" + ".UTC" not in content, f"Found 'datetime' + '.UTC' in {path}. Use 'datetime.now(timezone.utc)' instead."
        except UnicodeDecodeError:
            pass # Skip binary files if any

def test_key_files_exist():
    """Ensure critical files exist."""
    required_files = [
        "streamlit_app.py",
        "requirements.txt",
        "README.md",
        "analytics_hub_platform/ui/html.py"
    ]
    for f in required_files:
        assert Path(f).exists(), f"Missing required file: {f}"
