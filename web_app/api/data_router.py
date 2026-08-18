from fastapi import APIRouter
import json
import os
import time
import sys
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_DIR = os.path.join(ROOT_DIR, "data_cache")
SENTIMENT_CACHE_FILE = os.path.join(CACHE_DIR, "sentiment_history.json")

SERVER_START_TIME = time.time()
_last_cpu_time = time.process_time()
_last_wall_time = time.time()

def get_process_memory_mb() -> float:
    """Mendapatkan penggunaan memori RAM proses (Working Set) dalam MB di Windows."""
    try:
        import ctypes
        from ctypes import wintypes
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ('cb', wintypes.DWORD),
                ('PageFaultCount', wintypes.DWORD),
                ('PeakWorkingSetSize', ctypes.c_size_t),
                ('WorkingSetSize', ctypes.c_size_t),
                ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t),
            ]
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return round(counters.WorkingSetSize / (1024 * 1024), 1)
    except Exception:
        pass
    return 50.0

def get_process_cpu_percent() -> float:
    """Mendapatkan estimasi CPU utilization proses."""
    global _last_cpu_time, _last_wall_time
    now_wall = time.time()
    now_cpu = time.process_time()
    wall_diff = now_wall - _last_wall_time
    cpu_diff = now_cpu - _last_cpu_time
    
    _last_wall_time = now_wall
    _last_cpu_time = now_cpu
    
    if wall_diff <= 0:
        return 0.0
    
    num_cpus = os.cpu_count() or 1
    cpu_percent = (cpu_diff / (wall_diff * num_cpus)) * 100.0
    return round(min(100.0, max(0.0, cpu_percent)), 1)

@router.get("/sentiment")
def get_sentiment():
    """Mengambil history sentimen terakhir dari cache."""
    try:
        if os.path.exists(SENTIMENT_CACHE_FILE):
            with open(SENTIMENT_CACHE_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                
            if not history:
                return {"status": "success", "data": None, "history": []}
                
            latest = history[-1]
            return {"status": "success", "data": latest, "history": history}
        else:
            return {"status": "success", "data": None, "history": []}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/positions")
def get_positions():
    """
    Mengambil posisi aktif dari executor.
    """
    try:
        from src.main import executor
        if executor and hasattr(executor, 'position_cache'):
            positions = executor.position_cache
            return {"status": "success", "data": positions}
        return {"status": "success", "data": {}}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/system_stats")
def get_system_stats():
    """Mengembalikan statistik CPU, RAM, dan Uptime dashboard."""
    try:
        uptime_seconds = int(time.time() - SERVER_START_TIME)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        uptime_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return {
            "status": "success",
            "cpu_usage": get_process_cpu_percent(),
            "mem_usage_mb": get_process_memory_mb(),
            "uptime": uptime_formatted,
            "uptime_seconds": uptime_seconds
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
