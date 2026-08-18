"""
config_manager.py — Mengelola semua baca/tulis konfigurasi bot.
Menangani: .env, gui_config.json, pnl_config.json
"""

import os
import json
import threading
from pathlib import Path
from typing import Any

# ─── Root paths ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
ENV_PATH = SRC_DIR / ".env"
GUI_CONFIG_PATH = ROOT_DIR / "gui_config.json"
PNL_CONFIG_PATH = SRC_DIR / "utils" / "pnl_config.json"

_lock = threading.Lock()

# =============================================================================
# DEFAULTS — semua nilai default dari config.py
# =============================================================================
DEFAULT_BOT_CONFIG = {
    # AI Brain
    "AI_MODEL_NAME": "arcee-ai/trinity-large-preview:free",
    "AI_TEMPERATURE": 0.0,
    "AI_CONFIDENCE_THRESHOLD": 65,
    "AI_APP_URL": "https://github.com/KaleksananBarqi/Bot-Trading-Easy-Peasy",
    "AI_APP_TITLE": "Bot Trading Easy Peasy",
    # Reasoning
    "AI_REASONING_ENABLED": False,
    "AI_REASONING_EFFORT": "medium",
    "AI_REASONING_EXCLUDE": False,
    "AI_LOG_REASONING": True,
    # Sentiment
    "ENABLE_SENTIMENT_ANALYSIS": True,
    "AI_SENTIMENT_MODEL": "arcee-ai/trinity-large-preview:free",
    "SENTIMENT_ANALYSIS_INTERVAL": "1h",
    "SENTIMENT_UPDATE_INTERVAL": "1h",
    # Vision
    "USE_PATTERN_RECOGNITION": True,
    "AI_VISION_MODEL": "meta-llama/llama-4-maverick",
    "AI_VISION_TEMPERATURE": 0.0,
    "AI_VISION_MAX_TOKENS": 300,
    "PATTERN_MAX_RETRIES": 2,
    "PATTERN_MIN_ANALYSIS_LENGTH": 50,
    # Risk
    "USE_DYNAMIC_SIZE": False,
    "RISK_PERCENT_PER_TRADE": 3,
    "DEFAULT_AMOUNT_USDT": 10,
    "MIN_ORDER_USDT": 5,
    "DEFAULT_LEVERAGE": 10,
    "DEFAULT_MARGIN_TYPE": "isolated",
    "MAX_POSITIONS_PER_CATEGORY": 5,
    # SL/TP
    "DEFAULT_SL_PERCENT": 0.015,
    "DEFAULT_TP_PERCENT": 0.025,
    "ATR_PERIOD": 14,
    "ATR_MULTIPLIER_SL": 1.0,
    "ATR_MULTIPLIER_TP1": 3.0,
    "TRAP_SAFETY_SL": 2.0,
    # Trailing Stop
    "ENABLE_TRAILING_STOP": True,
    "USE_NATIVE_TRAILING": True,
    "TRAILING_ACTIVATION_DELAY": 60,
    "TRAILING_ACTIVATION_THRESHOLD": 0.80,
    "TRAILING_CALLBACK_RATE": 0.001,
    "TRAILING_MIN_PROFIT_LOCK": 0.005,
    "TRAILING_SL_UPDATE_COOLDOWN": 3,
    "NATIVE_TRAILING_MIN_RATE": 0.1,
    "NATIVE_TRAILING_MAX_RATE": 5.0,
    # Order execution
    "ENABLE_MARKET_ORDERS": False,
    "LIMIT_ORDER_EXPIRY_SECONDS": 7200,
    "ORDER_SLTP_RETRIES": 3,
    "ORDER_SLTP_RETRY_DELAY": 2,
    # Anti-FOMO
    "COOLDOWN_IF_PROFIT": 3600,
    "COOLDOWN_IF_LOSS": 7200,
    # Timeframes
    "TIMEFRAME_TREND": "4h",
    "LIMIT_TREND": 500,
    "TIMEFRAME_SETUP": "1h",
    "LIMIT_SETUP": 100,
    "TIMEFRAME_EXEC": "15m",
    "LIMIT_EXEC": 300,
    # EMA
    "EMA_TREND_MAJOR": 50,
    "EMA_FAST": 7,
    "EMA_SLOW": 21,
    # RSI
    "RSI_PERIOD": 14,
    "RSI_OVERSOLD": 35,
    "RSI_OVERBOUGHT": 65,
    "RSI_DEEP_OVERSOLD": 25,
    "RSI_DEEP_OVERBOUGHT": 75,
    # StochRSI
    "STOCHRSI_LEN": 14,
    "STOCHRSI_K": 3,
    "STOCHRSI_D": 3,
    # MACD
    "MACD_FAST": 12,
    "MACD_SLOW": 26,
    "MACD_SIGNAL": 9,
    # Bollinger Bands
    "BB_LENGTH": 20,
    "BB_STD": 2.0,
    # Volume
    "VOL_MA_PERIOD": 20,
    "VOLUME_SPIKE_MULTIPLIER": 1.5,
    "ORDERBOOK_RANGE_PERCENT": 0.02,
    # Wick Rejection
    "WICK_REJECTION_MIN_BODY_RATIO": 0.01,
    "WICK_REJECTION_MIN_BODY_REF": 0.00000001,
    "WICK_REJECTION_MULTIPLIER": 2.0,
    # Market Structure
    "MIN_BARS_MARKET_STRUCTURE": 50,
    # ADX
    "ADX_PERIOD": 14,
    # BTC Correlation
    "USE_BTC_CORRELATION": True,
    "BTC_EMA_PERIOD": 50,
    "CORRELATION_THRESHOLD_BTC": 0.8,
    "CORRELATION_PERIOD": 30,
    # Whale Detection
    "WHALE_THRESHOLD_USDT": 1000000,
    "WHALE_HISTORY_LIMIT": 10,
    "STABLECOIN_INFLOW_THRESHOLD_PERCENT": 0.05,
    "WHALE_DEDUP_WINDOW_SECONDS": 5,
    # System
    "PAKAI_DEMO": True,
    "MONGO_DB_NAME": "bot_trading_easy_peasy",
    "MONGO_COLLECTION_NAME": "trades_02_2026",
    "CONCURRENCY_LIMIT": 20,
    "LOOP_SLEEP_DELAY": 1,
    "ERROR_SLEEP_DELAY": 5,
    "SAFETY_MONITOR_INTERVAL": 60,
    "API_REQUEST_TIMEOUT": 10,
    "API_RECV_WINDOW": 10000,
    "LOOP_SKIP_DELAY": 2,
    "WS_KEEP_ALIVE_INTERVAL": 1800,
    # News
    "NEWS_MAX_PER_SOURCE": 15,
    "NEWS_MAX_TOTAL": 200,
    "NEWS_RETENTION_LIMIT": 15,
    "NEWS_MAX_AGE_HOURS": 24,
    "NEWS_COIN_SPECIFIC_MIN": 6,
    "NEWS_BTC_MAX": 5,
    "NEWS_MACRO_MAX": 4,
    # Coins
    "DAFTAR_KOIN": [
        {
            "symbol": "BTC/USDT",
            "category": "KING",
            "leverage": 20,
            "margin_type": "isolated",
            "amount": 20,
            "btc_corr": False,
            "keywords": ["bitcoin", "btc"]
        }
    ],
    # RSS Feeds
    "RSS_FEED_URLS": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://cryptonews.com/news/feed/",
        "https://ambcrypto.com/feed",
        "https://decrypt.co/feed",
        "https://www.theblock.co/rss.xml",
        "https://cryptoslate.com/feed/",
        "https://blockworks.co/feed/",
        "https://news.bitcoin.com/feed/",
        "https://u.today/rss",
        "https://www.newsbtc.com/feed/",
        "https://dailyhodl.com/feed/",
        "https://beincrypto.com/feed/",
        "https://www.portalkripto.com/feed/",
        "https://jelajahcoin.com/feed/",
        "https://blockchainmedia.id/feed/",
        "https://cryptopotato.com/tag/solana/feed/",
    ],
    "MACRO_KEYWORDS": [
        "federal reserve", "fed", "fomc", "inflation", "cpi",
        "recession", "interest rate", "powell", "sec", "crypto regulation"
    ],
}

DEFAULT_PNL_CONFIG = {
    "user": {
        "username": "username",
        "profile_picture_path": "",
        "show_qr": True,
        "qr_data": "https://www.binance.com/en/futures",
        "referral_code": "",
        "referral_title": "Referral Code",
        "base_currency": "USDT"
    },
    "images": {
        "exchange_logo_path": "assets/icons/download.png",
        "exchange_logo_max_width": 250,
        "exchange_logo_max_height": 100,
        "watermark_path": "",
        "show_watermark": False,
        "right_panel_image_path": "assets/bg.jpg",
        "right_panel_image_opacity": 0.8
    },
    "style": {
        "theme": "dark",
        "layout_mode": "landscape",
        "bg_gradient_colors": ["#030201", "#030201", "#809ab5"],
        "card_bg_color": "#1E2329",
        "right_panel_bg_color": "#1E232966",
        "text_primary": "#EAECEF",
        "text_secondary": "#848E9C",
        "text_tertiary": "#5E6673",
        "accent_color": "#F0B90B",
        "up_color": "#2EBD85",
        "down_color": "#F6465D",
        "leverage_bg_color": "#2B3139",
        "font_family": "Inter"
    },
    "fonts": {
        "regular": "assets/fonts/Inter_24pt-Regular.ttf",
        "bold": "assets/fonts/Inter_24pt-Bold.ttf",
        "data_regular": "assets/fonts/Electrolize-Regular.ttf",
        "data_bold": "assets/fonts/Electrolize-Regular.ttf"
    },
    "card_settings": {
        "width": 1920,
        "height": 1080,
        "margin": 60,
        "border_radius": 40
    }
}

# =============================================================================
# .ENV MANAGER
# =============================================================================

class EnvManager:
    """Baca dan tulis file .env."""

    @staticmethod
    def load() -> dict:
        data = {
            "BINANCE_API_KEY": "",
            "BINANCE_SECRET_KEY": "",
            "BINANCE_TESTNET_KEY": "",
            "BINANCE_TESTNET_SECRET": "",
            "TELEGRAM_TOKEN": "",
            "TELEGRAM_CHAT_ID": "",
            "TELEGRAM_MESSAGE_THREAD_ID": "",
            "TELEGRAM_TOKEN_SENTIMENT": "",
            "TELEGRAM_CHAT_ID_SENTIMENT": "",
            "TELEGRAM_MESSAGE_THREAD_ID_SENTIMENT": "",
            "AI_API_KEY": "",
            "CMC_API_KEY": "",
            "MONGO_URI": "mongodb://localhost:27017/",
        }
        if not ENV_PATH.exists():
            return data
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip()
                    if key in data:
                        data[key] = val
        except Exception:
            pass
        return data

    @staticmethod
    def save(data: dict) -> bool:
        try:
            with _lock:
                # Baca file lama untuk preserve komentar
                lines = []
                if ENV_PATH.exists():
                    with open(ENV_PATH, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                # Update nilai yang ada
                updated_keys = set()
                new_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("#") or "=" not in stripped:
                        new_lines.append(line)
                        continue
                    key = stripped.split("=")[0].strip()
                    if key in data:
                        new_lines.append(f"{key}={data[key]}\n")
                        updated_keys.add(key)
                    else:
                        new_lines.append(line)

                # Tambahkan key baru yang belum ada
                for key, val in data.items():
                    if key not in updated_keys:
                        new_lines.append(f"{key}={val}\n")

                with open(ENV_PATH, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
            return True
        except Exception as e:
            print(f"[ConfigManager] Error saving .env: {e}")
            return False


# =============================================================================
# BOT CONFIG MANAGER (gui_config.json)
# =============================================================================

class BotConfigManager:
    """Baca dan tulis gui_config.json (override untuk config.py)."""

    @staticmethod
    def load() -> dict:
        config = dict(DEFAULT_BOT_CONFIG)
        if not GUI_CONFIG_PATH.exists():
            return config
        try:
            with open(GUI_CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            config.update(saved)
        except Exception:
            pass
        return config

    @staticmethod
    def save(data: dict) -> bool:
        try:
            with _lock:
                # Merge dengan existing agar tidak hilang key yang tidak di-update
                existing = BotConfigManager.load()
                existing.update(data)
                with open(GUI_CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(existing, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ConfigManager] Error saving gui_config.json: {e}")
            return False

    @staticmethod
    def get(key: str, fallback: Any = None) -> Any:
        cfg = BotConfigManager.load()
        return cfg.get(key, fallback if fallback is not None else DEFAULT_BOT_CONFIG.get(key))


# =============================================================================
# PNL CONFIG MANAGER (pnl_config.json)
# =============================================================================

class PnlConfigManager:
    """Baca dan tulis pnl_config.json."""

    @staticmethod
    def load() -> dict:
        import copy
        config = copy.deepcopy(DEFAULT_PNL_CONFIG)
        if not PNL_CONFIG_PATH.exists():
            return config
        try:
            with open(PNL_CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Deep merge
            for section, vals in saved.items():
                if section in config and isinstance(vals, dict):
                    config[section].update(vals)
                else:
                    config[section] = vals
        except Exception:
            pass
        return config

    @staticmethod
    def save(data: dict) -> bool:
        try:
            with _lock:
                with open(PNL_CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ConfigManager] Error saving pnl_config.json: {e}")
            return False


# =============================================================================
# CONNECTION TESTERS
# =============================================================================

def test_binance_connection(api_key: str, secret_key: str, is_demo: bool) -> tuple[bool, str]:
    """Test koneksi ke Binance. Return (success, message)."""
    try:
        import ccxt
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
        })
        if is_demo:
            exchange.enable_demo_trading(True)
        balance = exchange.fetch_balance()
        usdt = balance.get('USDT', {}).get('free', 0)
        return True, f"✅ Terhubung! Saldo USDT: ${usdt:.2f}"
    except Exception as e:
        return False, f"❌ Gagal: {str(e)[:120]}"


def test_telegram_connection(token: str, chat_id: str) -> tuple[bool, str]:
    """Test kirim pesan ke Telegram. Return (success, message)."""
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        r = requests.post(url, data={
            'chat_id': chat_id,
            'text': '🤖 <b>Test koneksi Bot Trading Easy Peasy</b>\nKoneksi Telegram berhasil! ✅',
            'parse_mode': 'HTML'
        }, timeout=10)
        if r.status_code == 200:
            return True, "✅ Pesan test berhasil dikirim!"
        else:
            return False, f"❌ HTTP {r.status_code}: {r.json().get('description', 'Unknown error')}"
    except Exception as e:
        return False, f"❌ Gagal: {str(e)[:120]}"


def test_mongodb_connection(uri: str) -> tuple[bool, str]:
    """Test koneksi ke MongoDB. Return (success, message)."""
    try:
        from pymongo import MongoClient
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        dbs = client.list_database_names()
        return True, f"✅ Terhubung! Databases: {', '.join(dbs[:3])}"
    except Exception as e:
        return False, f"❌ Gagal: {str(e)[:120]}"


def test_ai_api_connection(api_key: str, base_url: str, model: str) -> tuple[bool, str]:
    """Test koneksi ke OpenRouter/AI API. Return (success, message)."""
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        r = requests.get(f"{base_url.rstrip('/')}/models", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            count = len(data.get("data", []))
            return True, f"✅ Terhubung! {count} model tersedia."
        else:
            return False, f"❌ HTTP {r.status_code}: {r.text[:80]}"
    except Exception as e:
        return False, f"❌ Gagal: {str(e)[:120]}"
