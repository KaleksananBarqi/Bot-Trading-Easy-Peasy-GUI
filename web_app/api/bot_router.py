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
SRC_DIR = os.path.join(ROOT_DIR, "src")
LOG_FILE = os.path.join(SRC_DIR, "bot_trading.log")

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

class BotStatus(BaseModel):
    status: str

def run_bot_in_thread():
    global bot_running, last_bot_error
    try:
        last_bot_error = None
        # Pastikan sys.path memiliki root dan src
        if ROOT_DIR not in sys.path:
            sys.path.insert(0, ROOT_DIR)
        if SRC_DIR not in sys.path:
            sys.path.insert(0, SRC_DIR)

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
    """Generator untuk SSE log streaming dengan proteksi disconnect, cancelation, dan initial history."""
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write("Log file created.\n")

        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            # Baca chunk terakhir agar dashboard langsung menampilkan riwayat log awal
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            read_size = min(file_size, 32768)  # Baca hingga 32 KB terakhir
            if read_size > 0:
                f.seek(max(0, file_size - read_size), os.SEEK_SET)
                initial_chunk = f.read()
                initial_lines = initial_chunk.splitlines()
                # Jika potongan tidak dari awal file, buang baris pertama (mungkin terpotong)
                if file_size > read_size and initial_lines:
                    initial_lines.pop(0)
                
                # Kirim maksimal 80 baris terakhir
                for line in initial_lines[-80:]:
                    clean_line = line.rstrip("\r\n")
                    if clean_line:
                        yield f"data: {clean_line}\n\n"

            # Posisikan ke akhir file untuk tailing realtime
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
                if clean_line:
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
