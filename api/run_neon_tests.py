#!/usr/bin/env python
"""
Script para executar testes de integração usando Neon PostgreSQL em vez de Docker
Autor: Bruno Santos
"""
import os
import sys
import pytest
from unittest import mock

# Classe de contêiner falso para substituir TestContainers
class MockContainer:
    def get_container_host_ip(self):
        return "localhost"
    
    def get_exposed_port(self, port):
        return port
    
    def start(self):
        pass


def run_tests_with_neon():
    """Executar testes de integração com Neon PostgreSQL"""
    # Configurar variáveis de ambiente
    os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_PS0NT6DzdvRn@ep-lingering-cloud-acvjfrnh-pooler.sa-east-1.aws.neon.tech/summary_tube_db?sslmode=require"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["TEST_MODE"] = "neon"
    
    # Criar patches para os contêineres
    postgres_mock = MockContainer()
    redis_mock = MockContainer()
    
    # Criar patches para as fixtures do TestContainers
    patches = [
        mock.patch("tests.conftest.PostgresContainer", return_value=postgres_mock),
        mock.patch("tests.conftest.RedisContainer", return_value=redis_mock),
    ]
    
    # Aplicar os patches
    for patch in patches:
        patch.start()
    
    try:
        # Executar os testes
        return pytest.main(["-xvs", "tests/integration/repositories"])
    finally:
        # Limpar os patches
        for patch in patches:
            patch.stop()
        
        # Limpar variáveis de ambiente
        for var in ["DATABASE_URL", "REDIS_URL", "TEST_MODE"]:
            if var in os.environ:
                del os.environ[var]


if __name__ == "__main__":
    sys.exit(run_tests_with_neon())
