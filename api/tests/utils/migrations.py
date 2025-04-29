"""
Utilities for managing database migrations in tests
Author: Bruno Santos
"""
import os
import logging
from alembic.config import Config
from alembic import command

logger = logging.getLogger(__name__)


def apply_migrations(database_url: str) -> None:
    """
    Apply all migrations to a test database
    
    Args:
        database_url: Connection string for the database
    """
    try:
        # Get the base API directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Create Alembic configuration
        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
        
        # Override the sqlalchemy.url setting with our test database URL
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run the migrations
        logger.info(f"Applying migrations to {database_url}")
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Migrations applied successfully")
    except Exception as e:
        logger.error(f"Error applying migrations: {str(e)}")
        raise
