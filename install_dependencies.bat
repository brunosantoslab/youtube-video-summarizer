@echo off
echo Installing YouTube Video Summarizer dependencies...

REM Upgrade pip
python -m pip install --upgrade pip

REM Install base requirements
python -m pip install -r api\requirements.txt

REM Install TestContainers with PostgreSQL and Redis extras
python -m pip install "testcontainers[postgres,redis]"

echo Installation complete!
echo To run unit tests: cd api && python -m pytest tests/unit
echo To run integration tests (requires Docker): cd api && python -m pytest tests/integration
