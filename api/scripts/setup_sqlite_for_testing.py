#!/usr/bin/env python3
"""
Script to configure the test environment in environments without native SQLite support.
This script should be executed before tests when Python doesn't have the _sqlite3 module.

Author: Bruno Santos
"""
import sys
import os
import importlib.util
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_sqlite3():
    """Checks if the sqlite3 module is available and working."""
    try:
        import sqlite3
        logger.info(f"SQLite3 module found: {sqlite3.__file__}")
        logger.info(f"SQLite version: {sqlite3.sqlite_version}")
        return True
    except ImportError:
        logger.warning("SQLite3 module not found!")
        return False
    except Exception as e:
        logger.warning(f"Error checking SQLite3: {str(e)}")
        return False

def check_pysqlite3():
    """Checks if the pysqlite3 module is available."""
    if importlib.util.find_spec("pysqlite3"):
        logger.info("pysqlite3 module found")
        return True
    else:
        logger.warning("pysqlite3 module not found")
        return False

def install_pysqlite3():
    """Installs the pysqlite3 package."""
    try:
        logger.info("Installing pysqlite3...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pysqlite3"])
        logger.info("pysqlite3 installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install pysqlite3: {str(e)}")
        return False

def create_patched_coverage_file():
    """Creates an initialization file to replace sqlite3 in coverage tests."""
    patch_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coverage_sqlite_patch.py")
    
    content = """#!/usr/bin/env python3
# Patch SQLite before running coverage tests
import sys

try:
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("SQLite3 successfully patched with pysqlite3")
except ImportError:
    print("WARNING: pysqlite3 not found. Coverage tests may fail.")
except Exception as e:
    print(f"Error patching SQLite3: {str(e)}")
"""
    
    with open(patch_file, "w") as f:
        f.write(content)
    
    logger.info(f"Created SQLite patch file at {patch_file}")
    logger.info("To use it, run: python -m scripts.coverage_sqlite_patch -m pytest ...")
    
    # Make the file executable on Unix systems
    try:
        os.chmod(patch_file, 0o755)
    except:
        pass
    
    return patch_file

def main():
    """Main function."""
    logger.info("Checking SQLite setup for testing...")
    
    if check_sqlite3():
        logger.info("SQLite3 is available and working correctly.")
        return 0
    
    logger.warning("Native SQLite support is missing.")
    
    if not check_pysqlite3():
        logger.info("pysqlite3 not found. Attempting to install...")
        if not install_pysqlite3():
            logger.error("Failed to install pysqlite3. Tests that require SQLite will likely fail.")
            logger.error("Try installing manually: pip install pysqlite3")
            return 1
    
    patch_file = create_patched_coverage_file()
    
    logger.info("\n===== SETUP COMPLETE =====")
    logger.info("To run tests with correct SQLite support, use one of these methods:")
    logger.info("1. Import the patch at the start of your tests:")
    logger.info("   ```")
    logger.info("   import pysqlite3")
    logger.info("   import sys")
    logger.info("   sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')")
    logger.info("   ```")
    logger.info("")
    logger.info("2. Use the generated patch file:")
    logger.info(f"   python -m scripts.coverage_sqlite_patch -m pytest ...")
    logger.info("")
    logger.info("3. For a permanent solution, install SQLite development libraries:")
    logger.info("   sudo apt-get install -y libsqlite3-dev")
    logger.info("   Then reinstall Python or use Docker for development")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
