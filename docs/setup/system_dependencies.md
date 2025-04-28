# Dependências do Sistema

Este documento descreve as dependências do sistema necessárias para executar o YouTube Video Summarizer.

## Dependências Gerais

### Docker e Docker Compose
Recomendamos o uso de Docker para garantir a consistência do ambiente de desenvolvimento:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Windows
# Baixe e instale o Docker Desktop para Windows
```

## Dependências do Python (Desenvolvimento sem Docker)

Se você preferir desenvolver sem Docker, certifique-se de instalar as seguintes dependências do sistema:

### Ubuntu/Debian
```bash
# Dependências essenciais
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    pkg-config

# Dependências do SQLite (necessárias para testes com coverage)
sudo apt-get install -y libsqlite3-dev

# Dependências do PostgreSQL
sudo apt-get install -y libpq-dev

# Dependências de criptografia
sudo apt-get install -y libssl-dev

# Para WSL (Windows Subsystem for Linux)
# As mesmas dependências acima são necessárias no WSL
```

### Windows
```powershell
# Instale o Python 3.10+ a partir do site oficial do Python
# Certifique-se de marcar a opção "Add Python to PATH"

# Ferramentas de build para Windows
pip install wheel setuptools
```

### macOS
```bash
# Instale o Homebrew se ainda não estiver instalado
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instale as dependências
brew update
brew install python@3.10
brew install sqlite
brew install openssl
brew install postgresql
```

## Ambiente Virtual Python

Recomendamos o uso de ambientes virtuais Python:

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows
venv\Scripts\activate

# No Linux/macOS
source venv/bin/activate

# Instalar dependências
pip install -r api/requirements.txt
```

## Resolução de Problemas

### Erro do SQLite (_sqlite3)

Se você encontrar o erro "ModuleNotFoundError: No module named '_sqlite3'" ao executar testes:

```bash
# No Ubuntu/Debian/WSL
sudo apt-get install -y libsqlite3-dev
# Reconstrua o Python ou instale o módulo pysqlite3
pip install pysqlite3

# Após instalar o pysqlite3, você pode precisar modificar seu código para usá-lo:
# No início do seu código de teste ou scripts que usam o SQLite:
import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
```

Nota: A abordagem com o módulo pysqlite3 é uma solução temporária. Para um ambiente de produção, recomendamos fortemente usar o Docker ou reconstruir o Python com suporte a SQLite.

### Erro de versão do FastAPI

Se você encontrar problemas com a versão do FastAPI:

```bash
# Instale uma versão específica compatível
pip install "fastapi<0.95.0"
```

## Verificação da Instalação

Para verificar se todas as dependências estão instaladas corretamente:

```bash
# Verifique a versão do Python
python --version  # Deve ser 3.10+

# Verifique o SQLite
python -c "import sqlite3; print(sqlite3.sqlite_version)"

# Verifique o ambiente de teste
python -m pytest --version
```

## Execução dos Testes

```bash
# Testes unitários (não requerem Docker)
cd api
python -m pytest tests/unit

# Testes de integração (requerem Docker)
python -m pytest tests/integration
```

## Suporte

Se você encontrar problemas com as dependências do sistema, verifique:

1. A versão do Python está correta? (Python 3.10+)
2. Todas as bibliotecas do sistema estão instaladas?
3. O Docker está configurado corretamente?

Para problemas específicos, consulte a seção de issues no GitHub.