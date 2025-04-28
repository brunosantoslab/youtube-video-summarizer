#!/usr/bin/env python
"""
This script applies Alembic migrations directly to a Neon PostgreSQL database.
It requires the database password to be entered at runtime.
"""
import os
import sys
import subprocess
import argparse
from getpass import getpass

# Connection template for Neon
CONNECTION_TEMPLATE = "postgresql://neondb_owner:{password}@ep-lingering-cloud-acvjfrnh-pooler.sa-east-1.aws.neon.tech/summary_tube_db?sslmode=require"

def run_migration(password):
    """Apply migration with Alembic to Neon database"""
    # Form the connection string
    connection_string = CONNECTION_TEMPLATE.format(password=password)
    
    print("Applying migration to Neon PostgreSQL database...")
    
    # Change to the api directory
    os.chdir("api")
    
    # Call alembic directly with the connection string as an environment variable
    env = os.environ.copy()
    env["DATABASE_URL"] = connection_string
    
    # Run alembic with the environment variable
    try:
        process = subprocess.Popen(
            ["alembic", "upgrade", "head"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        # Print the output and error
        if stdout:
            print("\nOutput:")
            print(stdout)
        
        if stderr:
            print("\nErrors:")
            print(stderr)
        
        if process.returncode == 0:
            print("Migration applied successfully!")
            return True
        else:
            print(f"Migration failed with return code: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"Error running migration: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Apply Alembic migrations to Neon PostgreSQL database")
    parser.add_argument('--password', help="Database password (will prompt if not provided)")
    
    args = parser.parse_args()
    
    # Get password from argument or prompt
    password = args.password
    if not password:
        password = getpass("Enter Neon database password: ")
    
    # Run the migration
    run_migration(password)

if __name__ == "__main__":
    main()
