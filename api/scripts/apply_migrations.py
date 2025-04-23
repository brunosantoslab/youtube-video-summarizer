# api/scripts/apply_migrations.py
import os
import sys
from alembic.config import Config
from alembic import command

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath("."))

# Create an Alembic configuration and run the migration
config = Config("alembic.ini")
command.upgrade(config, "head")

print("Migrations applied successfully.")