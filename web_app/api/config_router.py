from fastapi import APIRouter, HTTPException
import json
import os
from pydantic import BaseModel
from typing import Dict, Any, Optional
from dotenv import load_dotenv

router = APIRouter()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_FILE = os.path.join(ROOT_DIR, "gui_config.json")
ENV_FILE = os.path.join(ROOT_DIR, ".env")
ENV_EXAMPLE_FILE = os.path.join(ROOT_DIR, "src", ".env.example")

DEFAULT_ENV_KEYS = [
    "BINANCE_API_KEY",
    "BINANCE_SECRET_KEY",
    "BINANCE_TESTNET_KEY",
    "BINANCE_TESTNET_SECRET",
    "AI_API_KEY",
    "AI_BASE_URL",
    "CMC_API_KEY",
    "MONGO_URI"
]

class ConfigUpdate(BaseModel):
    config: Dict[str, Any]

class EnvUpdate(BaseModel):
    env: Dict[str, str]

def read_env_file() -> Dict[str, str]:
    """Membaca seluruh variabel dari .env dengan fallback template default."""
    env_vars = {key: "" for key in DEFAULT_ENV_KEYS}
    
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str and not line_str.startswith("#"):
                    parts = line_str.split("=", 1)
                    if len(parts) == 2:
                        k = parts[0].strip()
                        v = parts[1].strip()
                        # Hapus tanda kutip jika ada
                        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                            v = v[1:-1]
                        env_vars[k] = v
    else:
        # Jika .env belum ada, ambil dari os.environ atau default
        for k in DEFAULT_ENV_KEYS:
            env_vars[k] = os.getenv(k, "")
            
    return env_vars

@router.get("/")
def get_config():
    """Mengambil gui_config.json dan isi .env secara lengkap."""
    try:
        config_data = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                
        env_vars = read_env_file()
        return {"json": config_data, "env": env_vars}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/env/status")
def get_env_status():
    """Memeriksa kelengkapan variabel penting di .env."""
    try:
        env_vars = read_env_file()
        status = {
            "has_binance_live": bool(env_vars.get("BINANCE_API_KEY") and env_vars.get("BINANCE_SECRET_KEY")),
            "has_binance_testnet": bool(env_vars.get("BINANCE_TESTNET_KEY") and env_vars.get("BINANCE_TESTNET_SECRET")),
            "has_ai": bool(env_vars.get("AI_API_KEY")),
            "has_cmc": bool(env_vars.get("CMC_API_KEY")),
            "has_mongo": bool(env_vars.get("MONGO_URI")),
        }
        return {"status": "success", "data": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/json")
def update_json_config(data: ConfigUpdate):
    """Menyimpan pembaruan ke gui_config.json"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data.config, f, indent=2)
            
        # Hot-reload MongoManager agar sinkron jika MONGO_COLLECTION_NAME diubah
        try:
            from src.modules.mongo_manager import MongoManager
            if MongoManager._instance is not None:
                MongoManager().reload_config()
        except Exception:
            pass
            
        return {"status": "success", "message": "Konfigurasi JSON berhasil disimpan!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/env")
def update_env_config(data: EnvUpdate):
    """Menyimpan pembaruan ke file .env dan memperbarui os.environ."""
    try:
        lines = []
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
        elif os.path.exists(ENV_EXAMPLE_FILE):
            with open(ENV_EXAMPLE_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
        new_lines = []
        updated_keys = set()
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                key = stripped.split("=", 1)[0].strip()
                if key in data.env:
                    val = data.env[key]
                    new_lines.append(f"{key}={val}\n")
                    updated_keys.add(key)
                    os.environ[key] = str(val)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
                
        # Tambahkan kunci baru yang belum ada di file
        for key, value in data.env.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}\n")
                os.environ[key] = str(value)
                
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        # Sinkronkan juga ke src/.env jika ada agar konsisten di IDE & runtime
        src_env_path = os.path.join(ROOT_DIR, "src", ".env")
        if os.path.exists(os.path.dirname(src_env_path)):
            try:
                with open(src_env_path, "w", encoding="utf-8") as f_src:
                    f_src.writelines(new_lines)
            except Exception:
                pass
            
        load_dotenv(ENV_FILE, override=True)
        return {"status": "success", "message": "Pengaturan .env berhasil disimpan!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PromptTestRequest(BaseModel):
    symbol: str = "BTC/USDT"
    call_ai: bool = False
    prompt_overrides: Optional[Dict[str, str]] = None

@router.get("/prompts/defaults")
def get_default_prompts():
    """Mengambil template prompt bawaan (default) dari folder prompts/ atau config."""
    try:
        import sys
        sys.path.insert(0, os.path.join(ROOT_DIR, 'src'))
        import config as bot_config
        
        return {
            "status": "success",
            "data": {
                "AI_SYSTEM_ROLE": getattr(bot_config, 'DEFAULT_AI_SYSTEM_ROLE', ''),
                "PROMPT_STRATEGY_SELECTION": getattr(bot_config, 'DEFAULT_PROMPT_STRATEGY_SELECTION', ''),
                "PROMPT_SENTIMENT_ANALYSIS": getattr(bot_config, 'DEFAULT_PROMPT_SENTIMENT_ANALYSIS', ''),
                "PROMPT_PATTERN_RECOGNITION": getattr(bot_config, 'DEFAULT_PROMPT_PATTERN_RECOGNITION', ''),
                "PROMPT_BTC_WITH_CONTEXT": getattr(bot_config, 'DEFAULT_PROMPT_BTC_WITH_CONTEXT', ''),
                "PROMPT_BTC_NO_CONTEXT": getattr(bot_config, 'DEFAULT_PROMPT_BTC_NO_CONTEXT', ''),
                "PROMPT_MARKET_ANALYSIS_OUTPUT_FORMAT": getattr(bot_config, 'DEFAULT_PROMPT_MARKET_ANALYSIS_OUTPUT_FORMAT', ''),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompts/variables")
def get_prompt_variables():
    """Mengembalikan katalog tag/variabel dinamis yang dapat disisipkan ke masing-masing prompt."""
    return {
        "status": "success",
        "data": {
            "AI_SYSTEM_ROLE": [
                {"tag": "{timeframe_trend}", "desc": "Timeframe analisa tren global (misal: 1d / 4h)"},
                {"tag": "{limit_trend}", "desc": "Jumlah candle data tren"},
                {"tag": "{ema_trend_major}", "desc": "Periode EMA filter tren (misal: 50)"},
                {"tag": "{rsi_deep_oversold}", "desc": "Batas bawah oversold ekstrim (misal: 25)"},
                {"tag": "{rsi_deep_overbought}", "desc": "Batas atas overbought ekstrim (misal: 75)"},
                {"tag": "{volume_spike_multiplier}", "desc": "Pengali lonjakan volume (misal: 1.5x)"},
                {"tag": "{timeframe_exec}", "desc": "Timeframe eksekusi order (misal: 15m)"},
                {"tag": "{adx_period}", "desc": "Periode indikator kekuatan tren ADX (misal: 14)"}
            ],
            "PROMPT_STRATEGY_SELECTION": [
                {"tag": "{volume_spike}", "desc": "Ambang batas konfirmasi volume spike"},
                {"tag": "{adx_period}", "desc": "Ambang batas kekuatan tren ADX"},
                {"tag": "{ema_fast}", "desc": "Periode EMA Cepat (misal: 7)"},
                {"tag": "{ema_slow}", "desc": "Periode EMA Lambat (misal: 21)"},
                {"tag": "{execution_mode_text}", "desc": "Status izin Market Order vs Limit Order"}
            ],
            "PROMPT_SENTIMENT_ANALYSIS": [
                {"tag": "{fng_value}", "desc": "Skor Fear & Greed Index (0-100)"},
                {"tag": "{fng_text}", "desc": "Kategori F&G (misal: Extreme Fear, Neutral, Greed)"},
                {"tag": "{inflow_status}", "desc": "Arah aliran dana Stablecoin (Inflow/Outflow)"},
                {"tag": "{whale_str}", "desc": "Daftar aktivitas transaksi Whale terbaru"},
                {"tag": "{news_str}", "desc": "Daftar headline berita terkini dari RSS feed"}
            ],
            "PROMPT_PATTERN_RECOGNITION": [
                {"tag": "{timeframe}", "desc": "Timeframe chart yang dianalisis (misal: 1h)"},
                {"tag": "{symbol}", "desc": "Simbol koin (misal: BTC/USDT)"},
                {"tag": "{raw_info}", "desc": "Data teknikal angka candle & MACD pelengkap"}
            ],
            "PROMPT_BTC_WITH_CONTEXT": [
                {"tag": "{market_struct}", "desc": "Struktur market koin saat ini (BULLISH/BEARISH/SIDEWAYS)"},
                {"tag": "{btc_trend}", "desc": "Arah tren Bitcoin (BULLISH/BEARISH)"},
                {"tag": "{btc_instruction}", "desc": "Instruksi spesifik korelasi BTC"},
                {"tag": "{rsi_oversold}", "desc": "Level oversold"},
                {"tag": "{rsi_overbought}", "desc": "Level overbought"}
            ],
            "PROMPT_BTC_NO_CONTEXT": [
                {"tag": "{timeframe_trend}", "desc": "Timeframe tren utama"},
                {"tag": "{market_struct}", "desc": "Struktur market"},
                {"tag": "{rsi_oversold}", "desc": "Level oversold"},
                {"tag": "{volume_spike}", "desc": "Multiplier volume spike"},
                {"tag": "{rsi_overbought}", "desc": "Level overbought"}
            ],
            "PROMPT_MARKET_ANALYSIS_OUTPUT_FORMAT": [
                {"tag": "{execution_mode_json}", "desc": "Opsi enum format JSON untuk mode eksekusi"}
            ]
        }
    }

@router.post("/prompts/test")
async def test_prompt_sandbox(data: PromptTestRequest):
    """Uji prompt di sandbox pada data pasar riil secara instan tanpa membuat order."""
    try:
        import sys
        sys.path.insert(0, os.path.join(ROOT_DIR, 'src'))
        import config as bot_config
        import ccxt.async_support as ccxt_async
        from src.modules.market_data import _calculate_tech_data_threaded
        from src.utils.calc import calculate_dual_scenarios
        from src.utils.prompt_builder import build_market_prompt
        from src.modules.ai_brain import AIBrain

        symbol = data.symbol.strip().upper()
        if not symbol.endswith("/USDT"):
            symbol = f"{symbol}/USDT"

        # 1. Fetch live market candles via public CCXT (dengan fallback jika koneksi terhambat)
        bars_exec = []
        bars_trend = []
        try:
            import asyncio
            exchange = ccxt_async.binance({'options': {'defaultType': 'future'}})
            try:
                tf_exec = bot_config.TIMEFRAME_EXEC
                tf_trend = bot_config.TIMEFRAME_TREND
                
                bars_exec = await asyncio.wait_for(exchange.fetch_ohlcv(symbol, tf_exec, limit=100), timeout=3.0)
                bars_trend = await asyncio.wait_for(exchange.fetch_ohlcv(symbol, tf_trend, limit=100), timeout=3.0)
            finally:
                await exchange.close()
        except Exception:
            pass

        # Fallback simulation if exchange connection unreachable
        if not bars_exec or len(bars_exec) < 30:
            import time
            import math
            now_ts = int(time.time() * 1000)
            base_p = 65000.0 if "BTC" in symbol else 2600.0 if "ETH" in symbol else 140.0 if "SOL" in symbol else 10.0
            
            bars_exec = []
            bars_trend = []
            for i in range(100, 0, -1):
                t_exec = now_ts - (i * 15 * 60 * 1000)
                t_trend = now_ts - (i * 4 * 3600 * 1000)
                
                wave_exec = math.sin(i / 5.0) * (base_p * 0.015)
                p_c_exec = base_p + wave_exec
                p_o_exec = p_c_exec - (base_p * 0.002)
                p_h_exec = max(p_o_exec, p_c_exec) + (base_p * 0.003)
                p_l_exec = min(p_o_exec, p_c_exec) - (base_p * 0.003)
                vol_exec = 100.0 + (math.cos(i) * 30.0)
                bars_exec.append([t_exec, p_o_exec, p_h_exec, p_l_exec, p_c_exec, vol_exec])
                
                wave_trend = math.sin(i / 10.0) * (base_p * 0.04)
                p_c_trend = base_p + wave_trend
                p_o_trend = p_c_trend - (base_p * 0.005)
                p_h_trend = max(p_o_trend, p_c_trend) + (base_p * 0.008)
                p_l_trend = min(p_o_trend, p_c_trend) - (base_p * 0.008)
                vol_trend = 500.0 + (math.cos(i) * 100.0)
                bars_trend.append([t_trend, p_o_trend, p_h_trend, p_l_trend, p_c_trend, vol_trend])

        # 2. Calculate Technicals
        tech_data = _calculate_tech_data_threaded(bars_exec, bars_trend, symbol)
        if not tech_data:
            raise HTTPException(status_code=500, detail="Gagal menghitung indikator teknikal untuk sandbox.")

        tech_data['btc_trend'] = "BULLISH" if tech_data.get('global_trend_1d') == "BULLISH" else "BEARISH"
        tech_data['btc_correlation'] = 0.85
        tech_data['order_book'] = {"imbalance_pct": 5.2, "bid_vol": 120.5, "ask_vol": 114.2}

        # 3. Dual Scenarios
        current_price = tech_data['price']
        dual_scenarios = calculate_dual_scenarios(
            price=current_price,
            atr=tech_data.get('atr', 0)
        )

        # 4. Dummy / Cached Sentiment & Pattern
        sentiment_data = {"fng_value": 55, "fng_text": "Greed", "news": ["Market steady with institutional inflows."]}
        onchain_data = {"stablecoin_inflow": "Neutral", "whale_activity": ["Large transfer to exchange detected."]}
        pattern_ctx = "BULLISH (Cup & Handle pattern visible on 1h timeframe, MACD histogram expanding positive)."
        sentiment_analysis = {
            "overall_sentiment": "BULLISH",
            "sentiment_score": 68,
            "market_phase": "MARKUP",
            "summary": "Smart money menunjukkan akumulasi stabil di zona support."
        }

        # 5. Apply temporary prompt overrides if provided
        original_prompts = {}
        if data.prompt_overrides:
            for k, v in data.prompt_overrides.items():
                if hasattr(bot_config, k):
                    original_prompts[k] = getattr(bot_config, k)
                    setattr(bot_config, k, v)

        try:
            rendered_prompt = build_market_prompt(
                symbol=symbol,
                tech_data=tech_data,
                sentiment_data=sentiment_data,
                onchain_data=onchain_data,
                pattern_analysis=pattern_ctx,
                dual_scenarios=dual_scenarios,
                show_btc_context=True,
                sentiment_analysis=sentiment_analysis
            )
        finally:
            for k, v in original_prompts.items():
                setattr(bot_config, k, v)

        # 6. Call AI if requested
        ai_decision = None
        if data.call_ai:
            if not bot_config.AI_API_KEY:
                ai_decision = {
                    "decision": "WAIT",
                    "confidence": 0,
                    "reason": "AI_API_KEY belum dikonfigurasi di .env"
                }
            else:
                brain = AIBrain()
                ai_decision = await brain.analyze_market(rendered_prompt)

        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "tech_summary": {
                    "price": tech_data.get("price"),
                    "rsi": round(tech_data.get("rsi", 0), 2),
                    "adx": round(tech_data.get("adx", 0), 2),
                    "ema_fast": tech_data.get("ema_fast"),
                    "ema_slow": tech_data.get("ema_slow"),
                    "trend_major": tech_data.get("trend_major"),
                    "market_structure": tech_data.get("market_structure"),
                    "global_trend_1d": tech_data.get("global_trend_1d")
                },
                "rendered_prompt": rendered_prompt,
                "ai_decision": ai_decision,
                "model": bot_config.AI_MODEL_NAME if data.call_ai else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sandbox Error: {str(e)}")

BUILTIN_PRESETS = {
    "conservative": {
        "name": "🛡️ Konservatif (Low Risk)",
        "description": "Fokus proteksi modal: Leverage rendah 5x, hanya strategi Reversal di zona Pivot kuat, batas rugi harian aktif.",
        "config": {
            "DEFAULT_LEVERAGE": 5,
            "USE_DYNAMIC_SIZE": False,
            "DEFAULT_AMOUNT_USDT": 10,
            "DEFAULT_SL_PERCENT": 0.01,
            "DEFAULT_TP_PERCENT": 0.02,
            "ENABLED_STRATEGIES": ["LIQUIDITY_REVERSAL_MASTER"],
            "MAX_POSITIONS_PER_CATEGORY": 2,
            "MAX_TOTAL_OPEN_POSITIONS": 2,
            "MAX_DAILY_LOSS_USDT": 15,
            "AI_CONFIDENCE_THRESHOLD": 75,
        }
    },
    "aggressive": {
        "name": "⚡ Agresif Scalper (High Frequency)",
        "description": "Memaksimalkan peluang: Leverage 20x, Dynamic Sizing 3%, seluruh strategi aktif dengan jeda cooldown lebih cepat.",
        "config": {
            "DEFAULT_LEVERAGE": 20,
            "USE_DYNAMIC_SIZE": True,
            "RISK_PERCENT_PER_TRADE": 3,
            "DEFAULT_SL_PERCENT": 0.015,
            "DEFAULT_TP_PERCENT": 0.03,
            "ENABLED_STRATEGIES": ["LIQUIDITY_REVERSAL_MASTER", "PULLBACK_CONTINUATION", "BREAKDOWN_FOLLOW"],
            "MAX_POSITIONS_PER_CATEGORY": 5,
            "MAX_TOTAL_OPEN_POSITIONS": 5,
            "MAX_DAILY_LOSS_USDT": 50,
            "COOLDOWN_IF_PROFIT": 1800,
            "COOLDOWN_IF_LOSS": 3600,
            "AI_CONFIDENCE_THRESHOLD": 60,
        }
    },
    "trend_follower": {
        "name": "🌊 Trend Follower (Pullback & Breakout)",
        "description": "Mengikuti arah tren besar: Leverage 10x, hanya Pullback dan Breakout, target TP lebih lebar.",
        "config": {
            "DEFAULT_LEVERAGE": 10,
            "USE_DYNAMIC_SIZE": False,
            "DEFAULT_AMOUNT_USDT": 15,
            "DEFAULT_SL_PERCENT": 0.02,
            "DEFAULT_TP_PERCENT": 0.05,
            "ENABLED_STRATEGIES": ["PULLBACK_CONTINUATION", "BREAKDOWN_FOLLOW"],
            "TIMEFRAME_TREND": "1d",
            "TIMEFRAME_SETUP": "4h",
            "TIMEFRAME_EXEC": "1h",
            "AI_CONFIDENCE_THRESHOLD": 65,
        }
    }
}

PRESETS_DIR = os.path.join(ROOT_DIR, "presets")

@router.get("/presets")
def get_presets():
    """Mengambil daftar seluruh preset bawaan dan custom pengguna."""
    try:
        presets = dict(BUILTIN_PRESETS)
        
        # Baca custom user presets jika ada
        if os.path.exists(PRESETS_DIR):
            for file in os.listdir(PRESETS_DIR):
                if file.endswith(".json"):
                    preset_id = file[:-5]
                    file_path = os.path.join(PRESETS_DIR, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            presets[preset_id] = data
                    except Exception:
                        pass
                        
        return {"status": "success", "data": presets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PresetApply(BaseModel):
    preset_id: str

@router.post("/presets/apply")
def apply_preset(data: PresetApply):
    """Menerapkan konfigurasi preset ke gui_config.json."""
    try:
        presets_resp = get_presets()
        all_presets = presets_resp.get("data", {})
        
        if data.preset_id not in all_presets:
            raise HTTPException(status_code=404, detail=f"Preset '{data.preset_id}' tidak ditemukan.")
            
        preset_patch = all_presets[data.preset_id].get("config", {})
        
        # Load existing config
        current_config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                current_config = json.load(f)
                
        # Merge preset patch into current config
        current_config.update(preset_patch)
        
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(current_config, f, indent=2)
            
        return {"status": "success", "message": f"Preset '{all_presets[data.preset_id].get('name', data.preset_id)}' berhasil diterapkan!", "config": current_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PresetSave(BaseModel):
    preset_id: str
    name: str
    description: str
    config: Dict[str, Any]

@router.post("/presets/save")
def save_custom_preset(data: PresetSave):
    """Menyimpan konfigurasi saat ini sebagai custom preset baru."""
    try:
        if not os.path.exists(PRESETS_DIR):
            os.makedirs(PRESETS_DIR, exist_ok=True)
            
        safe_id = "".join([c for c in data.preset_id if c.isalnum() or c in ('_', '-')]).lower()
        if not safe_id:
            safe_id = "custom_preset"
            
        file_path = os.path.join(PRESETS_DIR, f"{safe_id}.json")
        payload = {
            "name": data.name,
            "description": data.description,
            "is_custom": True,
            "config": data.config
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            
        return {"status": "success", "message": f"Preset '{data.name}' berhasil disimpan!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
