"""
run_demo.py — Entry point don gian de chay OpenCode Agent.

Su dung:
    python run_demo.py                          # Interactive mode
    python run_demo.py "Viet ham tinh giai thua"  # Chay truc tiep
    python run_demo.py --help                   # Xem tat ca options

Hoac qua module:
    python -m src.cli                           # Interactive
    python -m src.cli run "requirement"         # Run command
    python -m src.cli demo                      # Random demo
    python -m src.cli --help                    # Help
"""

import os
import sys

# Force UTF-8 output on Windows to support unicode characters
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from src.cli.app import main

if __name__ == "__main__":
    main()