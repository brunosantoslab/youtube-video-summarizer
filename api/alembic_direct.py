#!/usr/bin/env python
"""
Direct Alembic migration script with Neon PostgreSQL
This bypasses all environment variables and directly uses the connection string
"""
import sys
from alembic.config import Config
from alembic import command

# The direct connection string to Neon PostgreSQL
CONNECTION_STRING = "postgresql://neondb_owner:npg_PS0NT6DzdvRn@ep-lingering-cloud-acvjfrnh-pooler.sa-east-1.aws.neon.tech/summary_tube_db?sslmode=require"

def run_migrations():
    """Run Alembic migrations with direct connection string"""
    print("Running migrations with direct Neon PostgreSQL connection...")
    
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Set the database URL directly
    alembic_cfg.set_main_option("sqlalchemy.url", CONNECTION_STRING)
    
    try:
        # Run upgrade to latest version
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
        return 0
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(run_migrations())
