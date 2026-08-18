#!/usr/bin/env python3
"""
run_gui.py — Entry point GUI Easy Peasy Trading Bot.
Double-click file ini untuk membuka Control Panel GUI.

Cara pakai:
  python run_gui.py
  Atau double-click run_gui.py di File Explorer
"""

import sys
import os

# Pastikan root project ada di sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def check_dependencies():
    """Cek apakah semua dependency GUI sudah terinstall."""
    missing = []
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")

    if missing:
        print("=" * 60)
        print("⚠️  DEPENDENCY KURANG!")
        print("Jalankan perintah berikut untuk install:")
        print()
        for pkg in missing:
            print(f"  pip install {pkg}")
        print("=" * 60)
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)


def main():
    check_dependencies()

    print("Easy Peasy Trading Bot - GUI Control Panel")
    print("=" * 50)
    print("Memuat interface...")

    try:
        from gui.app import App
        app = App()
        app.run()
    except Exception as e:
        import traceback
        print(f"\nError saat membuka GUI:")
        traceback.print_exc()
        print("\nJika masalah berlanjut, coba:")
        print("  pip install customtkinter --upgrade")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)


if __name__ == "__main__":
    main()
