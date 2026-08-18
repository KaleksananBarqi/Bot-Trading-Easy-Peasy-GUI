import asyncio
import os
import sys
import threading
import importlib
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

router = APIRouter()

bot_thread = None
bot_running = False
last_bot_error = None

# Path ke root directory & file log
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(ROOT_DIR, "bot_trading.log")

class BotStatus(BaseModel):
    status: str

def run_bot_in_thread():
    global bot_running, last_bot_error
    try:
        last_bot_error = None
        # Reload environment variables dari .env
        env_path = os.path.join(ROOT_DIR, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            
        # Hot-reload konfigurasi bot agar membaca perubahan terbaru dari gui_config.json & .env
        if "src.config" in sys.modules:
            import src.config
            importlib.reload(src.config)
        if "config" in sys.modules:
            import config
            importlib.reload(config)
            
        from src import main as bot_main
        from src.utils.helper import logger
        
        logger.info("Mulai bot di background thread...")
        
        # Buat event loop baru untuk thread bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Eksekusi main bot
        loop.run_until_complete(bot_main.main())
    except Exception as e:
        last_bot_error = str(e)
        print(f"Bot thread error: {e}")
    finally:
        bot_running = False
        print("Bot thread berhenti.")

@router.get("/status")
def get_bot_status():
    return {
        "running": bot_running,
        "last_error": last_bot_error
    }

@router.post("/start")
def start_bot():
    global bot_thread, bot_running, last_bot_error
    if bot_running:
        return {"status": "error", "message": "Bot sudah berjalan!"}
    
    last_bot_error = None
    bot_running = True
    
    bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
    bot_thread.start()
    
    return {"status": "success", "message": "Bot dimulai"}

@router.post("/stop")
def stop_bot():
    global bot_running
    if not bot_running:
        return {"status": "error", "message": "Bot tidak sedang berjalan!"}
    
    bot_running = False
    
    from web_app.api import bot_control_flag
    bot_control_flag.SHOULD_STOP = True
    
    return {"status": "success", "message": "Sinyal stop dikirim ke bot."}

async def log_generator(request: Request):
    """Generator untuk SSE log streaming dengan proteksi disconnect dan cancelation."""
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write("Log file created.\n")

        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            # Pindah ke akhir file (tail mode)
            f.seek(0, os.SEEK_END)
            while True:
                # Cek jika client menutup koneksi
                if await request.is_disconnected():
                    break
                
                line = f.readline()
                if not line:
                    await asyncio.sleep(0.5)
                    continue
                
                # Format SSE: data: <message>\n\n
                clean_line = line.rstrip("\r\n")
                yield f"data: {clean_line}\n\n"
    except asyncio.CancelledError:
        # Client disconnect normal
        pass
    except Exception as e:
        yield f"data: [SSE Error] {str(e)}\n\n"

@router.get("/logs/stream")
async def stream_logs(request: Request):
    return StreamingResponse(
        log_generator(request), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
