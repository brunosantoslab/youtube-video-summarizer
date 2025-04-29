# api/scripts/db_migration.py
import os
import sys
import subprocess
import importlib.util

# Add current directory to path for module imports
sys.path.insert(0, os.path.abspath("."))

def check_alembic_installed():
    """Check if Alembic is installed"""
    alembic_spec = importlib.util.find_spec("alembic")
    if alembic_spec is None:
        print("Alembic is not installed. Please run: pip install alembic")
        sys.exit(1)

def init_migrations():
    """Initialize Alembic migrations"""
    check_alembic_installed()
    try:
        # Create migrations directory if it doesn't exist
        os.makedirs("api/infrastructure/persistence/migrations/versions", exist_ok=True)
        
        # Create alembic.ini file
        with open("alembic.ini", "w") as f:
            f.write("""[alembic]
script_location = api/infrastructure/persistence/migrations
prepend_sys_path = .
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""")
        
        # Set up the migrations directory structure
        os.makedirs("api/infrastructure/persistence/migrations", exist_ok=True)
        
        # Create env.py
        with open("api/infrastructure/persistence/migrations/env.py", "w") as f:
            f.write("""from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import our models to make them available to Alembic
from infrastructure.persistence.base import Base
import infrastructure.persistence.user_entity
import infrastructure.persistence.video_entity
import infrastructure.persistence.transcript_entity

# This is the Alembic Config object
config = context.config

# Import application settings
from config import get_settings
settings = get_settings()

# Override the database URL with our configuration
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add model's MetaData object for autogenerate support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    \"\"\"Run migrations in 'offline' mode.\"\"\"
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    \"\"\"Run migrations in 'online' mode.\"\"\"
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""")
        
        # Create script.py.mako
        os.makedirs("api/infrastructure/persistence/migrations/versions", exist_ok=True)
        with open("api/infrastructure/persistence/migrations/script.py.mako", "w") as f:
            f.write("""\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
""")
        
        print("Alembic migration directory initialized successfully.")
    except Exception as e:
        print(f"Error initializing Alembic: {str(e)}")
        sys.exit(1)

def generate_migration(message="Migration"):
    """Generate a new migration"""
    check_alembic_installed()
    try:
        # Run alembic revision command
        subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            check=True
        )
        print(f"Migration created: {message}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating migration: {str(e)}")
        sys.exit(1)

def apply_migrations():
    """Apply all pending migrations"""
    check_alembic_installed()
    try:
        # Run alembic upgrade command
        subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True
        )
        print("Migrations applied successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error applying migrations: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/db_migration.py [init|generate|apply] [message]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        init_migrations()
    elif command == "generate":
        message = sys.argv[2] if len(sys.argv) > 2 else "Migration"
        generate_migration(message)
    elif command == "apply":
        apply_migrations()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python scripts/db_migration.py [init|generate|apply] [message]")
        sys.exit(1)