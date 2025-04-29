#!/usr/bin/env python
# This is a direct script to run migrations with a hardcoded Neon database URL
import os
import sys
from alembic.config import Config
from alembic import command

# Define the database URL directly - replace with your actual connection string
DATABASE_URL = "postgresql://neondb_owner:YOURPASSWORD@ep-lingering-cloud-acvjfrnh-pooler.sa-east-1.aws.neon.tech/summary_tube_db?sslmode=require"

def run_direct_migration():
    """Run migration directly with hardcoded database URL"""
    
    print("Running migrations directly with Neon PostgreSQL...")
    
    try:
        # Get Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Override the database URL
        alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
        
        # Run the migration
        print(f"Running migration with database URL: {DATABASE_URL}")
        command.upgrade(alembic_cfg, "head")
        
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Ask for confirmation before proceeding
    password = input("Enter your Neon database password: ")
    
    # Update the connection string with the provided password
    actual_url = DATABASE_URL.replace("YOURPASSWORD", password)
    
    # Set the environment variable for potential dependencies
    os.environ["DATABASE_URL"] = actual_url
    
    # Run the migration
    run_direct_migration()
