
import logging
import sys
import os
import requests
import asyncio
from datetime import datetime, timedelta, timezone
from src import config

# ==========================================
# CUSTOM LOGGER & TIME UTILS (WIB TIME)
# ==========================================
WIB_OFFSET = timezone(timedelta(hours=7))

def get_wib_now():
    """Mengembalikan datetime sekarang dalam WIB (UTC+7)."""
    return datetime.now(timezone.utc).astimezone(WIB_OFFSET)

def convert_dt_to_wib(dt):
    """Mengubah datetime (UTC/Naive) ke WIB."""
    if dt is None: return None
    if dt.tzinfo is None:
        # Assume UTC if naive, or system local? 
        # Better safe: assume UTC if coming from timestamp, or local if coming from now()
        # Let's standardize on UTC input for safety everywhere in this bot
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(WIB_OFFSET)

def convert_timestamp_to_wib_str(ts, fmt='%a %b %d %H:%M:%S %Y'):
    """Mengubah unix timestamp ke string WIB."""
    if not ts: return "-"
    dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(WIB_OFFSET)
    return dt.strftime(fmt)

def wib_time(*args):
    """Converter untuk logging agar menggunakan WIB."""
    return get_wib_now().timetuple()

def setup_logger():
    # [FIX] Force UTF-8 untuk Windows Console agar emoji tidak crash
    if sys.platform.startswith('win'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Reset handlers if exist (to prevent duplicates during reload)
    if logger.handlers:
        logger.handlers = []

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s')
    formatter.converter = wib_time 

    # File Handler
    file_handler = logging.FileHandler(config.LOG_FILENAME, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

# ==========================================
# TELEGRAM NOTIFIER
# ==========================================
async def kirim_tele(pesan: str, alert: bool = False, channel: str = 'default') -> None:
    """
    Log pesan lokal (Telegram sudah dihapus karena menggunakan Local Web Dashboard).
    """
    prefix = "⚠️ [SYSTEM ALERT] " if alert else "[INFO] "
    # Format agar lebih mudah dibaca di local web log tanpa tag HTML
    pesan_bersih = pesan.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
    logger.info(f"{prefix}{channel.upper()}: {pesan_bersih}")

def kirim_tele_sync(pesan):
    """
    Log pesan secara sinkronous (Telegram sudah dihapus).
    """
    pesan_bersih = pesan.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
    print(f"✅ [SYNC LOG]: {pesan_bersih}")

# ==========================================
# FORMATTING TOOLS
# ==========================================
import time

# ... (rest of imports)

def get_next_rounded_time(interval_str: str) -> float:
    """
    Calculate the next fixed-time alignment timestamp (Unix Epoch based).
    Example: interval '1h' -> Returns next X:00:00 timestamp.
    """
    interval_seconds = parse_timeframe_to_seconds(interval_str)
    if interval_seconds <= 0: interval_seconds = 60
    
    now = time.time()
    # Calculate next aligned timestamp
    next_time = ((int(now) // interval_seconds) + 1) * interval_seconds
    return next_time

def format_currency(num: float | None) -> str:
    if num is None: return "0.00"
    return f"{num:,.2f}"

def parse_timeframe_to_seconds(tf_str: str) -> int:
    """
    Convert timeframe string (e.g. '1m', '1h') to seconds.
    Default to 60s if invalid.
    """
    if not tf_str: return 60
    
    unit = tf_str[-1].lower()
    try:
        val = int(tf_str[:-1])
    except ValueError:
        return 60
        
    if unit == 's': return val
    elif unit == 'm': return val * 60
    elif unit == 'h': return val * 3600
    elif unit == 'd': return val * 86400
    else: return 60


# ==========================================
# CONFIG HELPERS
# ==========================================

# Initialize Coin Config Map for O(1) access
# This maps symbol -> coin config ensuring O(1) lookup speed.
# We iterate to preserve the first occurrence behavior if duplicates exist.
_COIN_CONFIG_MAP = {}
for coin in config.DAFTAR_KOIN:
    if coin['symbol'] not in _COIN_CONFIG_MAP:
        _COIN_CONFIG_MAP[coin['symbol']] = coin

def get_coin_config(symbol: str) -> dict | None:
    """
    Cari konfigurasi koin dari config.DAFTAR_KOIN.
    Return None jika tidak ditemukan.
    """
    return _COIN_CONFIG_MAP.get(symbol)


def get_coin_leverage(symbol: str) -> int:
    """
    Ambil leverage untuk symbol tertentu.
    Return config.DEFAULT_LEVERAGE jika tidak ditemukan.
    """
    coin_cfg = get_coin_config(symbol)
    if coin_cfg:
        return coin_cfg.get('leverage', config.DEFAULT_LEVERAGE)
    return config.DEFAULT_LEVERAGE
