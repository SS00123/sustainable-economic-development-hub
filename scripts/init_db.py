#!/usr/bin/env python
"""
Database Initialization Script
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Run this script to initialize the database with synthetic data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.infrastructure.settings import get_settings


def main():
    """Initialize the database."""
    settings = get_settings()
    
    print("=" * 60)
    print("Sustainable Economic Development Analytics Hub")
    print("Database Initialization")
    print("=" * 60)
    print()
    print(f"Environment: {settings.environment}")
    print(f"Database: {settings.db_path or 'Default (analytics_hub.db)'}")
    print()
    
    try:
        initialize_database()
        print()
        print("✅ Database initialized successfully!")
        print()
        print("You can now run the application:")
        print("  streamlit run app.py          # Dashboard")
        print("  uvicorn main_api:app --reload # API")
        print()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
