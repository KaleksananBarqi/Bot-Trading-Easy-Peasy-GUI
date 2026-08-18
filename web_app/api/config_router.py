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
            
        load_dotenv(ENV_FILE, override=True)
        return {"status": "success", "message": "Pengaturan .env berhasil disimpan!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
