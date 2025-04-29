# Script to run Alembic migrations with Neon PostgreSQL
import os
import sys
import subprocess
import re
from dotenv import load_dotenv

def run_migration():
    """Run Alembic migration with Neon PostgreSQL database URL"""
    
    print("Running database migrations with Neon PostgreSQL configuration...")
    
    # Path to the .env.local file
    env_local_path = os.path.join(os.path.dirname(os.getcwd()), '.env.local')
    
    if not os.path.exists(env_local_path):
        print(f"Error: .env.local file not found at {env_local_path}")
        return False
    
    # Load the variables from .env.local
    load_dotenv(env_local_path)
    
    # Get the DATABASE_URL from .env.local
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL not found in .env.local")
        return False
    
    # Set the environment variable for Alembic
    os.environ['DATABASE_URL'] = database_url
    
    print(f"Using database URL: {database_url}")
    
    # Run Alembic using subprocess
    try:
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                                 capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"Migration failed with error: {result.stderr}")
            return False
        else:
            print("Migrations completed successfully.")
            return True
    except Exception as e:
        print(f"Exception occurred during migration: {str(e)}")
        return False

if __name__ == "__main__":
    run_migration()
