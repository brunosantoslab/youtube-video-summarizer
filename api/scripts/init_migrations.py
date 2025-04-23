# api/scripts/init_migrations.py
import os
import sys
from alembic.config import Config
from alembic import command

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath("."))

# Create the migration directory
os.makedirs("infrastructure/persistence/migrations/versions", exist_ok=True)

# Initialize Alembic
config = Config("alembic.ini")
command.init(config, "infrastructure/persistence/migrations")

print("Alembic migration directory initialized successfully.")