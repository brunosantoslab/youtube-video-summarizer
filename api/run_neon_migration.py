# Script to run Alembic migrations with Neon PostgreSQL
import os
import sys
import subprocess
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine

# Add the current directory to the path so we can import config
sys.path.append(os.getcwd())

# Import the config module with our Neon settings
from config import get_neon_settings

def run_migration():
    """Run Alembic migration with Neon PostgreSQL database settings"""
    
    print("Running database migrations with Neon PostgreSQL configuration...")
    
    try:
        # Get settings with the Neon database URL
        settings = get_neon_settings()
        
        # Print the database URL for debugging
        print(f"Using database URL: {settings.database_url}")
        
        # Test database connection
        print("Testing database connection...")
        engine = create_engine(settings.database_url)
        connection = engine.connect()
        connection.close()
        print("Database connection successful!")
        
        # Get Alembic configuration
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
        
        # Run the migration
        print("Running migration with Alembic...")
        command.upgrade(alembic_cfg, "head")
        
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_migration()
