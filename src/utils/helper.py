
import logging
import sys
import os
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

def convert_timestamp_to_wib_str(ts, fmt='%d/%m/%Y %H:%M:%S WIB'):
    """Mengubah unix timestamp, string ISO, atau datetime ke string format WIB."""
    if not ts:
        return "-"
    try:
        if isinstance(ts, (int, float)):
            # Handle millisecond timestamp if > 1e11
            sec = ts / 1000.0 if ts > 1e11 else float(ts)
            dt = datetime.fromtimestamp(sec, tz=timezone.utc).astimezone(WIB_OFFSET)
        elif isinstance(ts, datetime):
            if ts.tzinfo is None:
                dt = ts.replace(tzinfo=timezone.utc).astimezone(WIB_OFFSET)
            else:
                dt = ts.astimezone(WIB_OFFSET)
        elif isinstance(ts, str):
            ts_clean = ts.strip().replace('Z', '+00:00')
            try:
                dt = datetime.fromisoformat(ts_clean)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                dt = dt.astimezone(WIB_OFFSET)
            except Exception:
                return str(ts)
        else:
            return str(ts)
        return dt.strftime(fmt)
    except Exception:
        return str(ts)

def wib_time(*args):
    """Converter untuk logging agar menggunakan WIB."""
    try:
        return get_wib_now().timetuple()
    except Exception:
        import time
        return time.localtime(*args)

def get_ai_client_headers() -> dict:
    """
    Menyiapkan HTTP header yang sesuai dengan AI Provider.
    Jika menggunakan AgentRouter, inject header resmi (codex_cli_rs) untuk melewati proteksi WAF.
    Jika menggunakan OpenRouter, gunakan HTTP-Referer dan X-Title.
    """
    base_url = str(getattr(config, 'AI_BASE_URL', '') or '').lower()
    if 'agentrouter' in base_url:
        return {
            "User-Agent": "codex_cli_rs/0.101.0",
            "originator": "codex_cli_rs"
        }
    headers = {}
    if getattr(config, 'AI_APP_URL', None):
        headers["HTTP-Referer"] = config.AI_APP_URL
    if getattr(config, 'AI_APP_TITLE', None):
        headers["X-Title"] = config.AI_APP_TITLE
    return headers

def get_aiohttp_connector():
    """
    Mengembalikan TCPConnector dengan ThreadedResolver agar stabil di Windows (mencegah ClientConnectorDNSError).
    """
    import aiohttp
    return aiohttp.TCPConnector(resolver=aiohttp.ThreadedResolver())

def create_aiohttp_session(timeout_seconds: float = 10.0, **kwargs):
    """
    Membuat ClientSession aiohttp yang sudah terhubung dengan ThreadedResolver.
    """
    import aiohttp
    connector = get_aiohttp_connector()
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    return aiohttp.ClientSession(connector=connector, timeout=timeout, **kwargs)


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
# SYSTEM NOTIFIER / LOCAL LOGGER
# ==========================================
async def kirim_tele(pesan: str, alert: bool = False, channel: str = 'default') -> None:
    """
    Kirim notifikasi ke log sistem lokal & Web Dashboard.
    """
    prefix = "⚠️ [SYSTEM ALERT] " if alert else "[INFO] "
    # Format agar lebih mudah dibaca di local web log tanpa tag HTML
    pesan_bersih = pesan.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
    logger.info(f"{prefix}{channel.upper()}: {pesan_bersih}")

def kirim_tele_sync(pesan: str) -> None:
    """
    Log pesan notifikasi secara sinkronous ke konsol/log.
    """
    pesan_bersih = pesan.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
    print(f"✅ [SYNC LOG]: {pesan_bersih}")

# Alias modern
kirim_notif = kirim_tele
kirim_notif_sync = kirim_tele_sync

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


def normalize_binance_symbol(raw_sym: str) -> str:
    """Konversi symbol Binance WS (BTCUSDT) ke format CCXT (BTC/USDT).
    
    Menggunakan pencocokan suffix yang aman, bukan string replace naif,
    untuk menghindari kerusakan pada pair non-USDT atau token dengan
    substring 'USDT' di namanya.
    """
    if not raw_sym or not isinstance(raw_sym, str):
        return str(raw_sym or '')
    for quote in ('USDT', 'USDC', 'BUSD', 'FDUSD'):
        if raw_sym.endswith(quote):
            return f"{raw_sym[:-len(quote)]}/{quote}"
    return raw_sym


# ==========================================
# CONFIG HELPERS
# ==========================================

# Initialize Coin Config Map for O(1) access
# This maps symbol -> coin config ensuring O(1) lookup speed.
# We iterate to preserve the first occurrence behavior if duplicates exist.
_COIN_CONFIG_MAP = {}
for coin in getattr(config, 'DAFTAR_KOIN', []):
    sym = coin.get('symbol') if isinstance(coin, dict) else getattr(coin, 'symbol', None)
    if sym and sym not in _COIN_CONFIG_MAP:
        _COIN_CONFIG_MAP[sym] = coin

def get_coin_config(symbol: str) -> dict | None:
    """
    Cari konfigurasi koin dari config.DAFTAR_KOIN.
    Return None jika tidak ditemukan.
    """
    # Check dynamic config if not found in precomputed map
    if symbol in _COIN_CONFIG_MAP:
        return _COIN_CONFIG_MAP[symbol]
    for coin in getattr(config, 'DAFTAR_KOIN', []):
        sym = coin.get('symbol') if isinstance(coin, dict) else getattr(coin, 'symbol', None)
        if sym == symbol:
            return coin
    return None


def get_coin_leverage(symbol: str) -> int:
    """
    Ambil leverage untuk symbol tertentu.
    Return config.DEFAULT_LEVERAGE jika tidak ditemukan.
    """
    coin_cfg = get_coin_config(symbol)
    if coin_cfg:
        return coin_cfg.get('leverage', getattr(config, 'DEFAULT_LEVERAGE', 10))
    return getattr(config, 'DEFAULT_LEVERAGE', 10)
