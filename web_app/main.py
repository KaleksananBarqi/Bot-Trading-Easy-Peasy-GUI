from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from web_app.api import config_router, bot_router, data_router
import os

app = FastAPI(title="Easy Peasy Bot Web Dashboard")

# Daftarkan Router API
app.include_router(config_router.router, prefix="/api/config", tags=["config"])
app.include_router(bot_router.router, prefix="/api/bot", tags=["bot"])
app.include_router(data_router.router, prefix="/api/data", tags=["data"])

# Path ke frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

# Menyajikan file statis (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def index():
    """Route utama yang menyajikan dashboard UI."""
    return FileResponse(os.path.join(frontend_dir, "index.html"))
