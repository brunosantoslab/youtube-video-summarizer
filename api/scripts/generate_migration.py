# api/scripts/generate_migration.py
import os
import sys
from alembic.config import Config
from alembic import command

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath("."))

# Create an Alembic configuration and run the migration
config = Config("alembic.ini")
message = sys.argv[1] if len(sys.argv) > 1 else "Initial migration"
command.revision(config, message=message, autogenerate=True)

print(f"Migration created: {message}")