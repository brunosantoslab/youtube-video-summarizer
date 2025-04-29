# api/scripts/alembic_utils.py
from alembic.config import Config
from alembic import command
import os
import sys

# Adicionar o diretório atual ao path para importação de módulos
sys.path.insert(0, os.path.abspath("."))


def get_alembic_config() -> Config:
    """Obter a configuração do Alembic"""
    config = Config("alembic.ini")
    config.set_main_option("script_location", "infrastructure/persistence/migrations")
    return config


def init_migrations():
    """Inicializar as migrações do Alembic"""
    config = get_alembic_config()
    command.init(config, "infrastructure/persistence/migrations")


def generate_migration(message="Migration"):
    """Gerar uma nova migração"""
    config = get_alembic_config()
    command.revision(config, message=message, autogenerate=True)


def apply_migrations():
    """Aplicar todas as migrações pendentes"""
    config = get_alembic_config()
    command.upgrade(config, "head")