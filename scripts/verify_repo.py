import argparse
import sys
import os
from pathlib import Path

def check_phase_0():
    print("Running Phase 0 Checks...")
    errors = []

    # 1. Check for non-ASCII filenames in pages/
    pages_dir = Path("pages")
    if pages_dir.exists():
        for p in pages_dir.glob("*.py"):
            if not p.name.isascii():
                errors.append(f"Non-ASCII filename found: {p.name}")

    # 2. Check for datetime.UTC usage (Python 3.11+ only)
    # We'll scan all .py files
    for root, dirs, files in os.walk("."):
        if "venv" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                try:
                    content = path.read_text(encoding="utf-8")
                    if "datetime.UTC" in content:
                        # Exclude this script itself if it mentions it in a string
                        if path.name != "verify_repo.py":
                             errors.append(f"Found 'datetime.UTC' in {path}")
                except Exception as e:
                    print(f"Could not read {path}: {e}")

    # 3. Check for unsafe_allow_html usage (just counting for now, not failing unless excessive/uncontrolled)
    unsafe_count = 0
    for root, dirs, files in os.walk("."):
        if "venv" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                try:
                    content = path.read_text(encoding="utf-8")
                    unsafe_count += content.count("unsafe_allow_html=True")
                except:
                    pass
    print(f"Found {unsafe_count} occurrences of unsafe_allow_html=True")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return False

    print("Phase 0 Checks Passed!")
    return True

def check_phase_1():
    print("Running Phase 1 Checks...")

    # 1. Check for datetime.UTC again (strict check)
    errors = []
    for root, dirs, files in os.walk("."):
        if "venv" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                if path.name == "verify_repo.py": continue
                try:
                    content = path.read_text(encoding="utf-8")
                    if "datetime.UTC" in content:
                        errors.append(f"Found 'datetime.UTC' in {path}")
                except: pass

    if errors:
        for e in errors: print(f"ERROR: {e}")
        return False

    # 2. Check for unsafe_allow_html in pages (should be replaced by render_html)
    # We allow it in ui/html.py and tests, but not in pages/
    pages_dir = Path("pages")
    if pages_dir.exists():
        for p in pages_dir.glob("*.py"):
            content = p.read_text(encoding="utf-8")
            if "unsafe_allow_html=True" in content:
                print(f"ERROR: Found unsafe_allow_html=True in {p}. Use render_html() instead.")
                return False

    # 3. Check if requirements are split
    if not Path("requirements.txt").exists() or not Path("requirements-dev.txt").exists():
        print("ERROR: requirements.txt or requirements-dev.txt missing")
        return False

    print("Phase 1 Checks Passed!")
    return True

def check_phase_2():
    print("Running Phase 2 Checks (UI Modernization)...")
    errors = []

    # 1. Theme Consolidation Verification
    # dark_theme.py should NOT exist
    if (Path("analytics_hub_platform/ui/dark_theme.py").exists()):
        errors.append("analytics_hub_platform/ui/dark_theme.py still exists! It should be consolidated into theme.py")

    # theme.py SHOULD exist
    if not (Path("analytics_hub_platform/ui/theme.py").exists()):
        errors.append("analytics_hub_platform/ui/theme.py is missing!")

    # 2. RTL Support Verification
    html_utils = Path("analytics_hub_platform/ui/html.py")
    if not html_utils.exists():
        errors.append("analytics_hub_platform/ui/html.py is missing!")
    else:
        content = html_utils.read_text(encoding="utf-8")
        if "is_rtl_language" not in content:
            errors.append("is_rtl_language function missing from ui/html.py")

    # 3. Modular Sections Verification
    sections_dir = Path("analytics_hub_platform/ui/sections")
    if not sections_dir.exists() or not sections_dir.is_dir():
        errors.append("analytics_hub_platform/ui/sections directory is missing!")
    else:
        # Check for at least one section file
        if not list(sections_dir.glob("*.py")):
            errors.append("No section components found in analytics_hub_platform/ui/sections")

    if errors:
        for e in errors: print(f"ERROR: {e}")
        return False

    print("Phase 2 Checks Passed!")
    return True

def check_phase_3():
    print("Running Phase 3 Checks (Production Readiness)...")
    errors = []

    # 1. Production Packaging
    if not Path("Dockerfile").exists():
        errors.append("Dockerfile is missing!")

    config_toml = Path(".streamlit/config.toml")
    if not config_toml.exists():
        errors.append(".streamlit/config.toml is missing!")
    else:
        content = config_toml.read_text(encoding="utf-8")
        if "enableXsrfProtection = true" not in content:
            errors.append("XSRF protection not enabled in config.toml")
        if "showErrorDetails = false" not in content:
            errors.append("Error details not hidden in config.toml")

    # 2. Logging
    if not Path("analytics_hub_platform/infrastructure/prod_logging.py").exists():
        errors.append("Production logging configuration missing!")

    # 3. CI/CD
    if not Path(".github/workflows/ci.yml").exists():
        errors.append("CI/CD workflow missing!")

    # 4. Dependencies
    if not Path("requirements.txt").exists():
        errors.append("requirements.txt missing!")

    if errors:
        for e in errors: print(f"ERROR: {e}")
        return False

    print("Phase 3 Checks Passed!")
    return True

def main():
    parser = argparse.ArgumentParser(description="Verify repository state per phase.")
    parser.add_argument("--phase", type=int, choices=[0, 1, 2, 3], required=True, help="Phase to verify")
    args = parser.parse_args()

    success = False
    if args.phase == 0:
        success = check_phase_0()
    elif args.phase == 1:
        success = check_phase_1()
    elif args.phase == 2:
        success = check_phase_2()
    elif args.phase == 3:
        success = check_phase_3()

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
