#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import importlib

# Ensure project root is on sys.path so package imports work reliably
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

from cps.setup_manager import is_first_run, run_interactive_setup
from cps.main import main as cps_main


def hide_console_windows():
    try:
        import ctypes

        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')

        SW_HIDE = 0

        hWnd = kernel32.GetConsoleWindow()
        if hWnd:
            user32.ShowWindow(hWnd, SW_HIDE)
    except Exception:
        # Non-Windows platforms or ctypes failures are safe to ignore
        pass


def create_app():
    cps_pkg = importlib.import_module('cps.__init__')
    return cps_pkg.create_app()


if __name__ == '__main__':
    # Check if first-run setup is needed
    if is_first_run():
        print("\n🚀 First-run setup detected. Starting configuration wizard...\n")
        if not run_interactive_setup():
            print("\n❌ Setup cancelled or failed. Exiting.")
            sys.exit(1)

    if os.name == "nt":
        hide_console_windows()

    cps_main()
