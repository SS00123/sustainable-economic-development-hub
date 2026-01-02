#!/usr/bin/env python3
"""
Deployment Readiness Check
Verifies all requirements for Streamlit Community Cloud deployment
"""

import sys
from pathlib import Path


def check_file_exists(filepath: str, required: bool = True) -> bool:
    """Check if a file exists."""
    path = Path(filepath)
    exists = path.exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    requirement = "REQUIRED" if required else "OPTIONAL"
    print(f"{status} {filepath} ({requirement}): {'Found' if exists else 'Missing'}")
    return exists


def check_requirements_txt():
    """Validate requirements.txt."""
    print("\n📦 Checking requirements.txt...")
    path = Path("requirements.txt")

    if not path.exists():
        print("❌ requirements.txt not found!")
        return False

    with open(path) as f:
        content = f.read()

    required_packages = [
        "streamlit",
        "pandas",
        "numpy",
        "plotly",
        "sqlalchemy",
        "pydantic",
        "pydantic-settings",
    ]

    missing = []
    for package in required_packages:
        if package.lower() not in content.lower():
            missing.append(package)

    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        return False

    print("✅ All required packages found")
    return True


def check_streamlit_config():
    """Check .streamlit/config.toml."""
    print("\n🎨 Checking Streamlit configuration...")
    path = Path(".streamlit/config.toml")

    if not path.exists():
        print("❌ .streamlit/config.toml not found!")
        return False

    with open(path) as f:
        content = f.read()

    required_sections = ["[theme]", "[server]", "[browser]"]
    missing = [s for s in required_sections if s not in content]

    if missing:
        print(f"⚠️  Missing sections: {', '.join(missing)}")
        return False

    print("✅ Streamlit config valid")
    return True


def check_main_file():
    """Check main entry point."""
    print("\n🚀 Checking main entry point...")
    path = Path("app.py")

    if not path.exists():
        print("❌ app.py not found!")
        return False

    with open(path) as f:
        content = f.read()

    if "st.set_page_config" not in content:
        print("⚠️  st.set_page_config not found in app.py")
        return False

    if "import streamlit" not in content:
        print("❌ Streamlit not imported in app.py")
        return False

    print("✅ app.py is valid")
    return True


def check_gitignore():
    """Check .gitignore for secrets."""
    print("\n🔒 Checking .gitignore...")
    path = Path(".gitignore")

    if not path.exists():
        print("⚠️  .gitignore not found")
        return False

    with open(path) as f:
        content = f.read()

    critical_entries = [".env", "secrets.toml", "*.key", "*.pem"]
    missing = [e for e in critical_entries if e not in content]

    if missing:
        print(f"⚠️  Missing critical entries: {', '.join(missing)}")
        print("   Make sure secrets are not committed!")
    else:
        print("✅ .gitignore properly configured")

    return True


def main():
    """Run all deployment checks."""
    print("=" * 60)
    print("🚀 STREAMLIT COMMUNITY CLOUD DEPLOYMENT CHECK")
    print("=" * 60)

    checks = [
        ("app.py", True),
        ("requirements.txt", True),
        ("packages.txt", False),
        (".streamlit/config.toml", True),
        (".streamlit/secrets.toml.example", False),
        (".gitignore", True),
        ("README.md", False),
        ("DEPLOYMENT.md", False),
    ]

    print("\n📁 Checking required files...")
    file_checks = [check_file_exists(f, req) for f, req in checks]

    validation_checks = [
        check_requirements_txt(),
        check_streamlit_config(),
        check_main_file(),
        check_gitignore(),
    ]

    all_passed = all(file_checks) and all(validation_checks)

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("1. Push your code to GitHub")
        print("2. Go to share.streamlit.io")
        print("3. Connect your repository")
        print("4. Deploy!")
        print("\n📖 See DEPLOYMENT.md for detailed instructions")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - REVIEW ABOVE")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
