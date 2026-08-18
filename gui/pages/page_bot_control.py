"""
page_bot_control.py — Halaman 7: Bot Control (UTAMA).
Start/Stop bot, live log viewer, dan monitoring koin.
"""

import customtkinter as ctk
import threading
import time
from gui.theme import COLORS, FONTS, button_success, button_danger, button_secondary, frame_section


class PageBotControl(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self._log_lines = []
        self._log_lock = threading.Lock()
        self._build()
        self._start_status_update()

    def _build(self):
        # Title
        ctk.CTkLabel(self, text="🚀  Bot Control Center",
                     font=FONTS["title_xl"], text_color=COLORS["text_primary"], anchor="w"
                     ).pack(fill="x", padx=20, pady=(20, 4))
        ctk.CTkLabel(self, text="Start, stop, dan pantau bot trading secara real-time.",
                     font=FONTS["body_md"], text_color=COLORS["text_secondary"], anchor="w"
                     ).pack(fill="x", padx=20, pady=(0, 16))

        # ── TOP PANEL: Status + Buttons ───────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(0, 16))
        top.columnconfigure(0, weight=0)
        top.columnconfigure(1, weight=1)
        top.columnconfigure(2, weight=0)

        # Status Card
        self._status_card = ctk.CTkFrame(top, fg_color=COLORS["bg_card"], corner_radius=12,
                                          border_width=2, border_color=COLORS["status_stopped"])
        self._status_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self._status_dot = ctk.CTkLabel(self._status_card, text="●", font=("Segoe UI", 28),
                                         text_color=COLORS["status_stopped"])
        self._status_dot.pack(padx=20, pady=(16, 0))
        self._status_label = ctk.CTkLabel(self._status_card, text="STOPPED",
                                           font=("Segoe UI", 14, "bold"), text_color=COLORS["status_stopped"])
        self._status_label.pack(padx=20)
        self._uptime_label = ctk.CTkLabel(self._status_card, text="--:--:--",
                                           font=FONTS["mono_lg"], text_color=COLORS["text_muted"])
        self._uptime_label.pack(padx=20, pady=(0, 16))

        # Stats Card
        stats_card = ctk.CTkFrame(top, fg_color=COLORS["bg_card"], corner_radius=12,
                                   border_width=1, border_color=COLORS["border"])
        stats_card.grid(row=0, column=1, sticky="nsew", padx=(0, 12))

        ctk.CTkLabel(stats_card, text="📊  Statistik Sesi",
                     font=FONTS["title_sm"], text_color=COLORS["accent_blue"]).pack(padx=16, pady=(12, 8), anchor="w")

        stats_grid = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_grid.pack(fill="x", padx=16, pady=(0, 12))
        stats_grid.columnconfigure((0, 1, 2, 3), weight=1)

        self._stat_buy = self._make_stat(stats_grid, "🟢 BUY", "0", 0)
        self._stat_sell = self._make_stat(stats_grid, "🔴 SELL", "0", 1)
        self._stat_exec = self._make_stat(stats_grid, "⚡ Eksekusi", "0", 2)
        self._stat_err = self._make_stat(stats_grid, "❌ Error", "0", 3)

        # Mode indicator
        from gui.config_manager import BotConfigManager
        cfg = BotConfigManager.load()
        is_demo = cfg.get("PAKAI_DEMO", True)
        mode_text = "🎮 DEMO (Testnet)" if is_demo else "💰 REAL MONEY"
        mode_color = COLORS["accent_green"] if is_demo else COLORS["accent_red"]
        ctk.CTkLabel(stats_card, text=f"Mode: {mode_text}",
                     font=FONTS["label_bold"], text_color=mode_color).pack(padx=16, pady=(0, 8), anchor="w")

        # Control Buttons
        ctrl = ctk.CTkFrame(top, fg_color=COLORS["bg_card"], corner_radius=12,
                             border_width=1, border_color=COLORS["border"])
        ctrl.grid(row=0, column=2, sticky="nsew")

        ctk.CTkLabel(ctrl, text="Kontrol", font=FONTS["title_sm"],
                     text_color=COLORS["text_secondary"]).pack(padx=16, pady=(12, 8))

        self._start_btn = ctk.CTkButton(ctrl, text="▶  START BOT", command=self._start_bot,
                                         height=50, width=180,
                                         fg_color=COLORS["accent_green"], hover_color="#2ea043",
                                         text_color="white", corner_radius=10, font=("Segoe UI", 14, "bold"))
        self._start_btn.pack(padx=16, pady=(0, 8))

        self._stop_btn = ctk.CTkButton(ctrl, text="⏹  STOP BOT", command=self._stop_bot,
                                        height=50, width=180,
                                        fg_color=COLORS["bg_hover"], hover_color=COLORS["accent_red"],
                                        text_color=COLORS["text_muted"], corner_radius=10, font=("Segoe UI", 14, "bold"),
                                        state="disabled")
        self._stop_btn.pack(padx=16, pady=(0, 8))

        ctk.CTkButton(ctrl, text="📊  Buka Dashboard", command=self._open_dashboard,
                      height=36, width=180, **button_secondary()).pack(padx=16, pady=(0, 4))
        ctk.CTkButton(ctrl, text="📋  Lihat Log File", command=self._open_log_file,
                      height=36, width=180, **button_secondary()).pack(padx=16, pady=(0, 12))

        # ── BOTTOM: Log Viewer ────────────────────────────────────────────────
        log_header = ctk.CTkFrame(self, fg_color="transparent")
        log_header.pack(fill="x", padx=20, pady=(0, 4))

        ctk.CTkLabel(log_header, text="📋  Live Bot Log",
                     font=FONTS["title_sm"], text_color=COLORS["text_primary"]).pack(side="left")

        # Log filter
        self._log_filter = ctk.StringVar(value="ALL")
        ctk.CTkOptionMenu(log_header, variable=self._log_filter,
                          values=["ALL", "INFO", "WARNING", "ERROR"],
                          width=100, height=28,
                          fg_color=COLORS["bg_card"], button_color=COLORS["bg_hover"],
                          dropdown_fg_color=COLORS["bg_secondary"], text_color=COLORS["text_primary"],
                          dropdown_text_color=COLORS["text_primary"], font=FONTS["body_sm"],
                          corner_radius=4).pack(side="right", padx=(0, 8))

        ctk.CTkButton(log_header, text="🗑 Clear", width=70, height=28,
                      command=self._clear_log,
                      fg_color=COLORS["bg_card"], hover_color=COLORS["bg_hover"],
                      text_color=COLORS["text_secondary"], corner_radius=4, font=FONTS["body_sm"]).pack(side="right", padx=(0, 4))

        ctk.CTkButton(log_header, text="💾 Export", width=70, height=28,
                      command=self._export_log,
                      fg_color=COLORS["bg_card"], hover_color=COLORS["bg_hover"],
                      text_color=COLORS["text_secondary"], corner_radius=4, font=FONTS["body_sm"]).pack(side="right", padx=(0, 4))

        # Search
        self._search_var = ctk.StringVar()
        ctk.CTkEntry(log_header, textvariable=self._search_var, height=28, width=160,
                     placeholder_text="🔍 Cari di log...",
                     fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                     text_color=COLORS["text_primary"], border_width=1, corner_radius=4,
                     font=FONTS["body_sm"]).pack(side="right", padx=(0, 8))

        # Log textbox
        self._log_box = ctk.CTkTextbox(
            self, fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
            border_color=COLORS["border"], border_width=1, corner_radius=8,
            font=FONTS["mono_sm"], wrap="word",
        )
        self._log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self._log_box.configure(state="disabled")

        # Initial hint
        self._append_log("[GUI] Bot Control siap. Tekan ▶ START BOT untuk memulai.", "INFO")
        self._append_log("[GUI] Pastikan API Keys sudah dikonfigurasi di halaman Setup.", "INFO")

    def _make_stat(self, parent, label: str, value: str, col: int):
        f = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=6)
        f.grid(row=0, column=col, padx=4, pady=4, sticky="ew")
        ctk.CTkLabel(f, text=label, font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(pady=(6, 0))
        val_lbl = ctk.CTkLabel(f, text=value, font=FONTS["title_md"], text_color=COLORS["text_primary"])
        val_lbl.pack(pady=(0, 6))
        return val_lbl

    # ─── BOT CONTROL ─────────────────────────────────────────────────────────

    def _start_bot(self):
        from gui.bot_runner import get_bot_runner
        runner = get_bot_runner()

        self._append_log("[GUI] ▶ Memulai bot...", "INFO")
        ok, msg = runner.start_bot(self._on_log_received)

        if ok:
            self._append_log(f"[GUI] ✅ {msg}", "INFO")
            self._update_status_ui(running=True)
        else:
            self._append_log(f"[GUI] ❌ {msg}", "ERROR")

    def _stop_bot(self):
        from gui.bot_runner import get_bot_runner
        runner = get_bot_runner()

        self._append_log("[GUI] ⏹ Menghentikan bot...", "WARNING")
        ok, msg = runner.stop_bot()

        if ok:
            self._append_log(f"[GUI] ✅ {msg}", "INFO")
        else:
            self._append_log(f"[GUI] ❌ {msg}", "ERROR")
        self._update_status_ui(running=False)

    def _open_dashboard(self):
        from gui.bot_runner import get_bot_runner
        runner = get_bot_runner()
        ok, msg = runner.start_dashboard()
        self._append_log(f"[GUI] {'✅' if ok else '❌'} {msg}", "INFO" if ok else "ERROR")

    def _open_log_file(self):
        from gui.bot_runner import get_bot_runner
        get_bot_runner().open_log_file()

    # ─── LOG HANDLING ────────────────────────────────────────────────────────

    def _on_log_received(self, line: str):
        """Callback dipanggil dari thread bot. Schedule ke main thread."""
        self.after(0, lambda l=line: self._append_log(l, self._detect_level(l)))

    def _detect_level(self, line: str) -> str:
        lower = line.lower()
        if "error" in lower or "❌" in line or "failed" in lower or "crash" in lower:
            return "ERROR"
        elif "warning" in lower or "⚠" in line or "warn" in lower:
            return "WARNING"
        return "INFO"

    def _append_log(self, line: str, level: str = "INFO"):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{ts}] {line}"

        color_map = {
            "ERROR":   COLORS["accent_red"],
            "WARNING": COLORS["accent_yellow"],
            "INFO":    COLORS["text_primary"],
        }
        color = color_map.get(level, COLORS["text_primary"])

        with self._log_lock:
            self._log_lines.append((formatted, level, color))
            # Batasi 2000 baris
            if len(self._log_lines) > 2000:
                self._log_lines = self._log_lines[-1500:]

        self._refresh_log_display()

    def _refresh_log_display(self):
        filter_val = self._log_filter.get()
        search_val = self._search_var.get().lower()

        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")

        with self._log_lock:
            lines = list(self._log_lines)

        for text, level, color in lines:
            if filter_val != "ALL" and level != filter_val:
                continue
            if search_val and search_val not in text.lower():
                continue
            self._log_box.insert("end", text + "\n")

        self._log_box.configure(state="disabled")
        self._log_box.see("end")

    def _clear_log(self):
        with self._log_lock:
            self._log_lines.clear()
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    def _export_log(self):
        from tkinter import filedialog
        from datetime import datetime
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("Log", "*.log")],
            initialfile=f"bot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if path:
            with self._log_lock:
                lines = list(self._log_lines)
            with open(path, "w", encoding="utf-8") as f:
                for text, _, _ in lines:
                    f.write(text + "\n")

    # ─── STATUS UPDATE LOOP ──────────────────────────────────────────────────

    def _update_status_ui(self, running: bool):
        if running:
            self._status_card.configure(border_color=COLORS["status_running"])
            self._status_dot.configure(text_color=COLORS["status_running"])
            self._status_label.configure(text="RUNNING", text_color=COLORS["status_running"])
            self._start_btn.configure(state="disabled", fg_color=COLORS["bg_hover"],
                                       text_color=COLORS["text_muted"])
            self._stop_btn.configure(state="normal", fg_color=COLORS["accent_red"],
                                      hover_color="#d73a49", text_color="white")
        else:
            self._status_card.configure(border_color=COLORS["status_stopped"])
            self._status_dot.configure(text_color=COLORS["status_stopped"])
            self._status_label.configure(text="STOPPED", text_color=COLORS["status_stopped"])
            self._uptime_label.configure(text="--:--:--")
            self._start_btn.configure(state="normal", fg_color=COLORS["accent_green"],
                                       hover_color="#2ea043", text_color="white")
            self._stop_btn.configure(state="disabled", fg_color=COLORS["bg_hover"],
                                      text_color=COLORS["text_muted"])
            self._stat_buy.configure(text="0")
            self._stat_sell.configure(text="0")
            self._stat_exec.configure(text="0")
            self._stat_err.configure(text="0")

    def _start_status_update(self):
        """Polling status setiap 1 detik."""
        def _tick():
            try:
                from gui.bot_runner import get_bot_runner
                runner = get_bot_runner()
                running = runner.is_running()

                # Update uptime
                if running:
                    self._uptime_label.configure(text=runner.get_uptime())
                    stats = runner.session_stats
                    self._stat_buy.configure(text=str(stats["buy_signals"]))
                    self._stat_sell.configure(text=str(stats["sell_signals"]))
                    self._stat_exec.configure(text=str(stats["executions"]))
                    self._stat_err.configure(text=str(stats["errors"]))
                    # Jika stopped unexpectedly
                    if self._stop_btn.cget("state") == "normal" and not running:
                        self._update_status_ui(False)
                        self._append_log("[GUI] ⚠️ Bot berhenti tidak terduga. Cek log untuk detail.", "WARNING")
            except Exception:
                pass

        def loop():
            _tick()
            self.after(1000, loop)

        self.after(1000, loop)
