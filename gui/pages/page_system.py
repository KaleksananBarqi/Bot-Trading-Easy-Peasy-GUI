"""
page_system.py — Halaman 5: Sistem & Database.
"""

import customtkinter as ctk
from gui.theme import COLORS, FONTS, entry_style, button_success, button_danger, make_section_header, slider_style


class PageSystem(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self._build()
        self._load()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 0))
        ctk.CTkLabel(hdr, text="⚙️  Sistem & Database",
                     font=FONTS["title_xl"], text_color=COLORS["text_primary"]).pack(side="left")
        self._save_lbl = ctk.CTkLabel(hdr, text="", font=FONTS["body_md"], text_color=COLORS["accent_green"])
        self._save_lbl.pack(side="right", padx=(0, 12))
        ctk.CTkButton(hdr, text="💾  Simpan", command=self._save, height=36, width=120, **button_success()).pack(side="right")

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_primary"], scrollbar_button_color=COLORS["bg_hover"])
        self._scroll.pack(fill="both", expand=True, padx=20, pady=12)

        # ── MODE TRADING ─────────────────────────────────────────────────────
        make_section_header(self._scroll, "🌐 Mode Environment")

        mode_card = ctk.CTkFrame(self._scroll, fg_color=COLORS["bg_card"], corner_radius=12, border_width=2, border_color=COLORS["border"])
        mode_card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(mode_card, text="Mode Trading", font=FONTS["title_md"],
                     text_color=COLORS["text_primary"]).pack(padx=20, pady=(16, 8), anchor="w")

        self._mode_seg = ctk.CTkSegmentedButton(
            mode_card,
            values=["🎮  Demo (Testnet)", "💰  Real Money"],
            command=self._on_mode_change,
            selected_color=COLORS["accent_green"],
            selected_hover_color="#2ea043",
            unselected_color=COLORS["bg_tertiary"],
            unselected_hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"],
            font=("Segoe UI", 13, "bold"),
            height=46,
        )
        self._mode_seg.pack(padx=20, pady=(0, 8), fill="x")

        self._mode_hint = ctk.CTkLabel(
            mode_card,
            text="🎮 Mode Demo menggunakan Binance Testnet — uang monopoli, aman untuk testing.",
            font=FONTS["body_sm"], text_color=COLORS["text_secondary"], anchor="w", wraplength=600
        )
        self._mode_hint.pack(padx=20, pady=(0, 16), anchor="w")

        # ── MONGODB ──────────────────────────────────────────────────────────
        make_section_header(self._scroll, "🗄️ Database MongoDB")
        ctk.CTkLabel(self._scroll, text="Nama database dan collection untuk menyimpan riwayat trade.",
                     font=FONTS["body_sm"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 8))

        self._db_name = self._make_entry(self._scroll, "Nama Database", "bot_trading_easy_peasy")
        self._col_name = self._make_entry(self._scroll, "Nama Collection", "trades_02_2026",
                                           "Ganti nama collection saat mulai bulan/periode baru")

        ctk.CTkLabel(self._scroll, text="💡  MongoDB URI dikonfigurasi di halaman Setup & API Keys.",
                     font=FONTS["caption"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 12))

        # ── PERFORMA SYSTEM LOOP ─────────────────────────────────────────────
        make_section_header(self._scroll, "⚡ Performa System Loop")
        ctk.CTkLabel(self._scroll, text="Pengaturan ini jarang perlu diubah. Ubah hanya jika ada masalah performa.",
                     font=FONTS["body_sm"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 8))

        grid = ctk.CTkFrame(self._scroll, fg_color=COLORS["bg_secondary"], corner_radius=8)
        grid.pack(fill="x", pady=(0, 16))
        grid.columnconfigure((0, 1), weight=1)

        params_left = [
            ("Concurrency Limit (Worker Thread)", "CONCURRENCY_LIMIT", 20),
            ("Loop Sleep Delay (detik)", "LOOP_SLEEP_DELAY", 1),
            ("Error Sleep Delay (detik)", "ERROR_SLEEP_DELAY", 5),
            ("Loop Skip Delay (detik)", "LOOP_SKIP_DELAY", 2),
        ]
        params_right = [
            ("Safety Monitor Interval (detik)", "SAFETY_MONITOR_INTERVAL", 60),
            ("API Request Timeout (detik)", "API_REQUEST_TIMEOUT", 10),
            ("API RecvWindow Binance (ms)", "API_RECV_WINDOW", 10000),
            ("WebSocket Keep-Alive (detik)", "WS_KEEP_ALIVE_INTERVAL", 1800),
        ]

        self._sys_vars = {}
        for col_idx, params in enumerate([params_left, params_right]):
            for row_idx, (label, key, default) in enumerate(params):
                f = ctk.CTkFrame(grid, fg_color="transparent")
                f.grid(row=row_idx, column=col_idx, padx=12, pady=6, sticky="ew")
                ctk.CTkLabel(f, text=label, font=FONTS["label_bold"],
                             text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")
                var = ctk.StringVar(value=str(default))
                ctk.CTkEntry(f, textvariable=var, height=32, **entry_style()).pack(fill="x", pady=(2, 0))
                self._sys_vars[key] = var

    # ─── HELPERS ─────────────────────────────────────────────────────────────

    def _make_entry(self, parent, label: str, default: str = "", hint: str = ""):
        ctk.CTkLabel(parent, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(8, 0))
        if hint:
            ctk.CTkLabel(parent, text=hint, font=FONTS["caption"],
                         text_color=COLORS["text_muted"], anchor="w").pack(fill="x")
        var = ctk.StringVar(value=default)
        ctk.CTkEntry(parent, textvariable=var, height=34, **entry_style()).pack(fill="x", pady=(2, 4))
        return var

    def _on_mode_change(self, value: str):
        is_real = "Real" in value
        if is_real:
            self._mode_hint.configure(
                text="⚠️  Mode Real Money: Bot menggunakan dana NYATA di Binance. Pastikan semua konfigurasi sudah benar!",
                text_color=COLORS["accent_red"]
            )
        else:
            self._mode_hint.configure(
                text="🎮 Mode Demo menggunakan Binance Testnet — uang monopoli, aman untuk testing.",
                text_color=COLORS["text_secondary"]
            )

    # ─── LOAD / SAVE ─────────────────────────────────────────────────────────

    def _load(self):
        from gui.config_manager import BotConfigManager
        cfg = BotConfigManager.load()

        is_demo = cfg.get("PAKAI_DEMO", True)
        self._mode_seg.set("🎮  Demo (Testnet)" if is_demo else "💰  Real Money")
        self._on_mode_change(self._mode_seg.get())

        self._db_name.set(cfg.get("MONGO_DB_NAME", "bot_trading_easy_peasy"))
        self._col_name.set(cfg.get("MONGO_COLLECTION_NAME", "trades_02_2026"))

        sys_defaults = {
            "CONCURRENCY_LIMIT": 20,
            "LOOP_SLEEP_DELAY": 1,
            "ERROR_SLEEP_DELAY": 5,
            "LOOP_SKIP_DELAY": 2,
            "SAFETY_MONITOR_INTERVAL": 60,
            "API_REQUEST_TIMEOUT": 10,
            "API_RECV_WINDOW": 10000,
            "WS_KEEP_ALIVE_INTERVAL": 1800,
        }
        for key, default in sys_defaults.items():
            if key in self._sys_vars:
                self._sys_vars[key].set(str(cfg.get(key, default)))

    def _save(self):
        from gui.config_manager import BotConfigManager

        is_demo = "Demo" in self._mode_seg.get()
        data = {
            "PAKAI_DEMO": is_demo,
            "MONGO_DB_NAME": self._db_name.get().strip(),
            "MONGO_COLLECTION_NAME": self._col_name.get().strip(),
        }
        for key, var in self._sys_vars.items():
            try:
                data[key] = int(var.get())
            except ValueError:
                data[key] = var.get()

        ok = BotConfigManager.save(data)
        if ok:
            self._save_lbl.configure(text="✅ Tersimpan!", text_color=COLORS["accent_green"])
        else:
            self._save_lbl.configure(text="❌ Gagal!", text_color=COLORS["accent_red"])
        self.after(3000, lambda: self._save_lbl.configure(text=""))
