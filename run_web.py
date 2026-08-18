#!/usr/bin/env python3
"""
Entry point untuk menyalakan server Local Web Dashboard.
"""

import sys
import os
import uvicorn

# Pastikan root project ada di sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def main():
    print("==================================================")
    print(">>> EASY PEASY TRADING BOT - LOCAL WEB DASHBOARD")
    print("==================================================")
    print("Memulai server lokal...")
    print("Silakan buka browser dan akses:")
    print(">>> http://localhost:8000")
    print("==================================================")
    
    # Menjalankan aplikasi FastAPI menggunakan uvicorn (reload hanya memantau folder web_app)
    web_app_dir = os.path.join(ROOT_DIR, "web_app")
    uvicorn.run(
        "web_app.main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        reload_dirs=[web_app_dir],
        reload_excludes=["*.log", "*.json", ".env", "*.pyc", "__pycache__/*", "data_cache/*"]
    )

if __name__ == "__main__":
    main()
