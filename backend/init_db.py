#!/usr/bin/env python3
"""
Script to initialize the database with all tables and default admin user
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from database import init_database

if __name__ == '__main__':
    print("Initializing database...")
    init_database()
    print("\nDatabase initialized successfully!")
    print("\nDefault admin user created:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n⚠️  IMPORTANT: Change the admin password after first login!")
