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


from typing import List, Dict, Any, Optional

# ==============================================================================
# TRADE HISTORY & QUANT ANALYTICS ENDPOINTS
# ==============================================================================

@router.get("/trades/collections")
def get_trade_collections():
    """
    Mengambil daftar seluruh collection di database MongoDB saat ini dan active collection.
    """
    try:
        from src.modules.mongo_manager import MongoManager
        mongo = MongoManager()
        cols = mongo.get_available_trade_collections()
        return {
            "status": "success",
            "active_collection": mongo.collection_name,
            "collections": cols
        }
    except Exception as e:
        return {
            "status": "error",
            "active_collection": "trades_08_2026",
            "collections": ["trades_08_2026"],
            "message": str(e)
        }


@router.get("/trades/analytics")
def get_trades_analytics(
    days: int = 0,
    symbol: str = "ALL",
    strategy: str = "ALL",
    side: str = "ALL",
    collection: Optional[str] = None
):
    """
    Mengambil kalkulasi metrik kuantitatif lengkap (EV, Calmar, Sharpe, Sortino, SQN, Max Drawdown)
    serta data time series untuk visualisasi grafik.
    """
    try:
        from src.modules.quant_analytics import QuantAnalyticsEngine
        engine = QuantAnalyticsEngine()
        raw_trades = engine.fetch_raw_trades(
            days=days,
            symbol=symbol if symbol != "ALL" else None,
            strategy=strategy if strategy != "ALL" else None,
            side=side if side != "ALL" else None,
            collection_name=collection
        )
        metrics = engine.calculate_metrics(raw_trades)
        return metrics
    except Exception as e:
        return {"status": "error", "message": f"Gagal menghitung analitik: {str(e)}"}


@router.get("/trades/history")
def get_trades_history(
    page: int = 1,
    limit: int = 20,
    symbol: str = "ALL",
    side: str = "ALL",
    result: str = "ALL",
    days: int = 0,
    sort_by: str = "timestamp",
    ascending: bool = False,
    collection: Optional[str] = None
):
    """
    Mengambil data riwayat trade dari MongoDB dengan pagination dan filter.
    """
    try:
        from src.modules.mongo_manager import MongoManager
        from datetime import datetime, timedelta
        mongo = MongoManager()
        if collection:
            mongo.switch_collection(collection)
        
        filter_query = {}
        if days > 0:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            filter_query['timestamp'] = {'$gte': cutoff_date}
        if symbol and symbol != "ALL":
            filter_query['symbol'] = symbol.upper()
        if side and side != "ALL":
            filter_query['side'] = side.upper()
        if result and result != "ALL":
            filter_query['result'] = result.upper()
            
        # Hitung total dokumen yang cocok
        total_items = mongo.get_trade_count(filter_query)
        
        # Hitung total pages
        page = max(1, page)
        limit = max(1, min(100, limit))
        total_pages = max(1, (total_items + limit - 1) // limit)
        
        # Ambil trades dengan filter dan sorting
        all_matched = mongo.get_trades(
            filter_query=filter_query,
            sort_by=sort_by,
            ascending=ascending,
            limit=5000
        )
        
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_trades = all_matched[start_idx:end_idx]
        
        # Sanitasi _id menjadi string
        cleaned_trades = []
        for t in paginated_trades:
            doc = dict(t)
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            cleaned_trades.append(doc)
            
        return {
            "status": "success",
            "data": cleaned_trades,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total_items,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gagal memuat histori transaksi: {str(e)}",
            "data": [],
            "pagination": {"page": 1, "limit": limit, "total_items": 0, "total_pages": 1}
        }


@router.get("/trades/filters")
def get_trade_filter_options(collection: Optional[str] = None):
    """
    Mengambil daftar koin dan strategi unik yang tercatat di database untuk opsi dropdown filter.
    """
    try:
        from src.modules.mongo_manager import MongoManager
        mongo = MongoManager()
        if collection:
            mongo.switch_collection(collection)
        trades = mongo.get_trades(limit=2000)
        
        symbols = sorted(list(set(t.get('symbol') for t in trades if t.get('symbol'))))
        strategies = sorted(list(set(t.get('strategy_tag') for t in trades if t.get('strategy_tag'))))
        
        return {
            "status": "success",
            "symbols": symbols,
            "strategies": strategies
        }
    except Exception as e:
        return {"status": "error", "symbols": [], "strategies": [], "message": str(e)}

