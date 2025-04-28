@echo off
echo Running Unit Tests with Test Environment...

REM Backup existing .env if it exists
if exist .env (
    if exist .env.bak del .env.bak
    ren .env .env.bak
    echo Backed up existing .env to .env.bak
)

REM Copy test environment
copy .env.test .env
echo Using test environment from .env.test

REM Run pytest
python -m pytest tests/unit -v

REM Restore original .env if it existed
if exist .env.bak (
    del .env
    ren .env.bak .env
    echo Restored original .env
)

echo Test execution completed.
