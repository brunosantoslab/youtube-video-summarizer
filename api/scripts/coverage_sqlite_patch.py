#!/usr/bin/env python3
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

# Continue with normal execution
if __name__ == "__main__" and len(sys.argv) > 1:
    # Remove este script dos argumentos
    args = sys.argv[1:]
    
    if args[0] == "-m":
        # python -m coverage_sqlite_patch -m pytest ...
        module_name = args[1]
        module = __import__(module_name)
        if hasattr(module, "main"):
            module.main()
        else:
            print(f"Module {module_name} does not have a main() function")
            sys.exit(1)
    else:
        # python coverage_sqlite_patch.py script.py arg1 arg2 ...
        script_path = args[0]
        
        # Execute o script com os argumentos restantes
        import runpy
        sys.argv = args
        runpy.run_path(script_path, run_name="__main__")
