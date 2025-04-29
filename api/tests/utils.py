"""
Utilities for testing
Author: Bruno Santos
"""

import subprocess
import os
from alembic.config import Config
from alembic import command


def apply_migrations(database_url):
    """
    Apply database migrations using Alembic
    
    Args:
        database_url: Database URL to apply migrations to
    """
    try:
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Override the database URL in the config
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run the migration
        command.upgrade(alembic_cfg, "head")
        
        print("Test database migrations applied successfully")
    except Exception as e:
        print(f"Error applying migrations: {str(e)}")
        raise