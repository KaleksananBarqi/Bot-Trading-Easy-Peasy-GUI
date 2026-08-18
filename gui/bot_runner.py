"""
bot_runner.py — Menjalankan dan menghentikan bot sebagai subprocess.
Handles: start, stop, log streaming, status, dan Streamlit dashboard.
"""

import subprocess
import threading
import time
import os
import sys
import signal
from pathlib import Path
from typing import Callable, Optional

ROOT_DIR = Path(__file__).parent.parent
SRC_MAIN = ROOT_DIR / "src" / "main.py"
STREAMLIT_DASHBOARD = ROOT_DIR / "streamlit" / "dashboard.py"


class BotRunner:
    """Manager untuk menjalankan bot dan dashboard sebagai subprocess."""

    def __init__(self):
        self._bot_proc: Optional[subprocess.Popen] = None
        self._dash_proc: Optional[subprocess.Popen] = None
        self._log_thread: Optional[threading.Thread] = None
        self._log_callback: Optional[Callable[[str], None]] = None
        self._start_time: Optional[float] = None
        self._stop_event = threading.Event()

        # Statistik sesi
        self.session_stats = {
            "buy_signals": 0,
            "sell_signals": 0,
            "executions": 0,
            "errors": 0,
        }

    # ─── BOT CONTROL ─────────────────────────────────────────────────────────

    def start_bot(self, log_callback: Callable[[str], None]) -> tuple[bool, str]:
        """
        Jalankan bot sebagai subprocess.
        log_callback dipanggil setiap ada baris log baru.
        """
        if self.is_running():
            return False, "Bot sudah berjalan."

        # Pastikan gui_config.json ada
        from gui.config_manager import GUI_CONFIG_PATH, BotConfigManager
        if not GUI_CONFIG_PATH.exists():
            BotConfigManager.save({})  # Buat default

        self._log_callback = log_callback
        self._stop_event.clear()
        self.session_stats = {k: 0 for k in self.session_stats}

        try:
            python_exe = sys.executable
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONPATH"] = str(ROOT_DIR)

            self._bot_proc = subprocess.Popen(
                [python_exe, str(SRC_MAIN)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
                cwd=str(ROOT_DIR),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            self._start_time = time.time()

            # Thread untuk baca log
            self._log_thread = threading.Thread(
                target=self._stream_logs,
                daemon=True,
            )
            self._log_thread.start()

            return True, "Bot berhasil dimulai!"

        except Exception as e:
            return False, f"Gagal menjalankan bot: {e}"

    def stop_bot(self) -> tuple[bool, str]:
        """Stop bot dengan graceful shutdown."""
        if not self.is_running():
            return False, "Bot tidak sedang berjalan."

        try:
            self._stop_event.set()

            # Graceful terminate
            if sys.platform == "win32":
                self._bot_proc.terminate()
            else:
                self._bot_proc.send_signal(signal.SIGTERM)

            # Tunggu 5 detik
            try:
                self._bot_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill
                self._bot_proc.kill()
                self._bot_proc.wait()

            self._bot_proc = None
            self._start_time = None
            return True, "Bot berhasil dihentikan."

        except Exception as e:
            return False, f"Error saat stop: {e}"

    def is_running(self) -> bool:
        """Cek apakah bot sedang berjalan."""
        if self._bot_proc is None:
            return False
        return self._bot_proc.poll() is None

    def get_uptime(self) -> str:
        """Kembalikan string uptime bot."""
        if not self.is_running() or self._start_time is None:
            return "--:--:--"
        elapsed = int(time.time() - self._start_time)
        h = elapsed // 3600
        m = (elapsed % 3600) // 60
        s = elapsed % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def get_exit_code(self) -> Optional[int]:
        """Cek exit code bot setelah berhenti."""
        if self._bot_proc:
            return self._bot_proc.poll()
        return None

    # ─── LOG STREAMING ───────────────────────────────────────────────────────

    def _stream_logs(self):
        """Thread: baca stdout bot dan panggil callback."""
        try:
            for line in iter(self._bot_proc.stdout.readline, ""):
                if self._stop_event.is_set():
                    break
                line = line.rstrip("\n")
                if line:
                    # Update session stats dari log
                    self._parse_log_stats(line)
                    if self._log_callback:
                        self._log_callback(line)
            # Bot selesai
            if self._log_callback:
                self._log_callback(
                    f"[GUI] --- Bot process ended (exit code: {self.get_exit_code()}) ---"
                )
        except Exception as e:
            if self._log_callback:
                self._log_callback(f"[GUI] Log stream error: {e}")

    def _parse_log_stats(self, line: str):
        """Parse log line untuk update statistik sesi."""
        lower = line.lower()
        if "buy" in lower or "long" in lower and "signal" in lower:
            self.session_stats["buy_signals"] += 1
        elif "sell" in lower or "short" in lower and "signal" in lower:
            self.session_stats["sell_signals"] += 1
        if "execute_entry" in lower or "order placed" in lower:
            self.session_stats["executions"] += 1
        if "error" in lower or "❌" in line:
            self.session_stats["errors"] += 1

    # ─── STREAMLIT DASHBOARD ─────────────────────────────────────────────────

    def start_dashboard(self) -> tuple[bool, str]:
        """Buka Streamlit dashboard di browser."""
        try:
            python_exe = sys.executable
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT_DIR)

            self._dash_proc = subprocess.Popen(
                [
                    python_exe, "-m", "streamlit", "run",
                    str(STREAMLIT_DASHBOARD),
                    "--server.headless", "false",
                    "--browser.gatherUsageStats", "false",
                ],
                env=env,
                cwd=str(ROOT_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            return True, "Dashboard dibuka di browser!"
        except Exception as e:
            return False, f"Gagal buka dashboard: {e}"

    def stop_dashboard(self):
        """Stop Streamlit dashboard."""
        if self._dash_proc and self._dash_proc.poll() is None:
            self._dash_proc.terminate()
            self._dash_proc = None

    def is_dashboard_running(self) -> bool:
        if self._dash_proc is None:
            return False
        return self._dash_proc.poll() is None

    def open_log_file(self):
        """Buka file log di text editor default."""
        log_path = ROOT_DIR / "src" / "bot_trading.log"
        if log_path.exists():
            if sys.platform == "win32":
                os.startfile(str(log_path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(log_path)])
            else:
                subprocess.Popen(["xdg-open", str(log_path)])


# Singleton instance
_bot_runner_instance: Optional[BotRunner] = None

def get_bot_runner() -> BotRunner:
    global _bot_runner_instance
    if _bot_runner_instance is None:
        _bot_runner_instance = BotRunner()
    return _bot_runner_instance
