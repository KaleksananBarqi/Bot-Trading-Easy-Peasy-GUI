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

@router.get("/prompts/defaults")
def get_default_prompts():
    """Mengambil template prompt bawaan (default) dari config."""
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
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
