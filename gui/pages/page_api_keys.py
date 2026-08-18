"""
page_api_keys.py — Halaman 1: Setup API Keys & Koneksi.
Menggantikan edit manual file .env
"""

import customtkinter as ctk
import threading
from gui.theme import COLORS, FONTS, entry_style, button_primary, button_secondary, button_success, frame_section, make_section_header, label_style


class PageApiKeys(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        from gui.config_manager import EnvManager
        self._env_mgr = EnvManager
        self._entries = {}
        self._status_labels = {}
        self._build()

    # ─── BUILD UI ────────────────────────────────────────────────────────────

    def _build(self):
        # Scrollable container
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_primary"], scrollbar_button_color=COLORS["bg_hover"]
        )
        self._scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Page Title
        ctk.CTkLabel(
            self._scroll, text="🔑  Setup & API Keys",
            font=FONTS["title_xl"], text_color=COLORS["text_primary"], anchor="w"
        ).pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(
            self._scroll, text="Semua API key disimpan aman di file .env — tidak pernah hardcoded.",
            font=FONTS["body_md"], text_color=COLORS["text_secondary"], anchor="w"
        ).pack(fill="x", pady=(0, 20))

        # ── BINANCE ──────────────────────────────────────────────────────────
        make_section_header(self._scroll, "🏦  Binance API", "Untuk trading di akun live")
        self._build_section_fields(self._scroll, [
            ("BINANCE_API_KEY",      "API Key Utama",        True),
            ("BINANCE_SECRET_KEY",   "Secret Key Utama",     True),
            ("BINANCE_TESTNET_KEY",  "Testnet API Key",      True),
            ("BINANCE_TESTNET_SECRET", "Testnet Secret Key", True),
        ])
        self._build_test_button(self._scroll, "🔌  Test Koneksi Binance", self._test_binance)

        # ── TELEGRAM UTAMA ───────────────────────────────────────────────────
        make_section_header(self._scroll, "📨  Telegram — Sinyal Utama", "Notifikasi BUY/SELL/Trade update")
        self._build_section_fields(self._scroll, [
            ("TELEGRAM_TOKEN",             "Bot Token",                 True),
            ("TELEGRAM_CHAT_ID",           "Chat ID",                   False),
            ("TELEGRAM_MESSAGE_THREAD_ID", "Thread ID (Opsional)",      False),
        ])
        self._build_test_button(self._scroll, "📨  Test Telegram Utama", lambda: self._test_telegram("default"))

        # ── TELEGRAM SENTIMEN ────────────────────────────────────────────────
        make_section_header(self._scroll, "📰  Telegram — Sentimen (Opsional)", "Channel terpisah untuk laporan sentimen AI")
        self._build_section_fields(self._scroll, [
            ("TELEGRAM_TOKEN_SENTIMENT",             "Bot Token Sentimen",       True),
            ("TELEGRAM_CHAT_ID_SENTIMENT",           "Chat ID Sentimen",         False),
            ("TELEGRAM_MESSAGE_THREAD_ID_SENTIMENT", "Thread ID Sentimen",       False),
        ])
        self._build_test_button(self._scroll, "📰  Test Telegram Sentimen", lambda: self._test_telegram("sentiment"))

        # ── AI & DATA ────────────────────────────────────────────────────────
        make_section_header(self._scroll, "🤖  AI Provider & Data", "OpenRouter/DeepSeek untuk AI, CoinMarketCap untuk berita")
        self._build_section_fields(self._scroll, [
            ("AI_API_KEY",  "AI API Key (OpenRouter/DeepSeek/dll)", True),
            ("CMC_API_KEY", "CoinMarketCap API Key",                 True),
        ])
        self._build_test_button(self._scroll, "🤖  Test AI API", self._test_ai)

        # ── MONGODB ──────────────────────────────────────────────────────────
        make_section_header(self._scroll, "🗄️  Database MongoDB", "Untuk menyimpan riwayat trade")
        self._build_section_fields(self._scroll, [
            ("MONGO_URI", "MongoDB URI", False),
        ])
        # Hint
        ctk.CTkLabel(
            self._scroll,
            text="💡  Lokal: mongodb://localhost:27017/   |   Atlas: mongodb+srv://user:pass@cluster.mongodb.net/",
            font=FONTS["caption"], text_color=COLORS["text_muted"], anchor="w", wraplength=680
        ).pack(fill="x", pady=(0, 4))
        self._build_test_button(self._scroll, "🗄️  Test MongoDB", self._test_mongodb)

        # ── SIMPAN ───────────────────────────────────────────────────────────
        sep = ctk.CTkFrame(self._scroll, height=1, fg_color=COLORS["border"])
        sep.pack(fill="x", pady=20)

        save_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        save_frame.pack(fill="x", pady=(0, 20))

        self._save_status = ctk.CTkLabel(
            save_frame, text="", font=FONTS["body_md"],
            text_color=COLORS["accent_green"]
        )
        self._save_status.pack(side="left", padx=(0, 12))

        save_btn = ctk.CTkButton(
            save_frame, text="💾  Simpan Semua ke .env",
            command=self._save_all, height=42, width=220,
            **button_success()
        )
        save_btn.pack(side="right")

        # Load existing values
        self._load_values()

    def _build_section_fields(self, parent, fields: list):
        """Build entry fields untuk sebuah section."""
        grid = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=8)
        grid.pack(fill="x", pady=(4, 12), padx=0)
        grid.columnconfigure(1, weight=1)

        for i, (key, label, is_password) in enumerate(fields):
            # Label
            ctk.CTkLabel(
                grid, text=label, font=FONTS["label_bold"],
                text_color=COLORS["text_secondary"], anchor="w", width=220
            ).grid(row=i, column=0, padx=(16, 8), pady=8, sticky="w")

            # Entry
            entry = ctk.CTkEntry(
                grid, show="•" if is_password else "", height=34,
                placeholder_text=f"Masukkan {label}...",
                **entry_style()
            )
            entry.grid(row=i, column=1, padx=(0, 8), pady=8, sticky="ew")
            self._entries[key] = entry

            # Show/Hide toggle untuk password
            if is_password:
                show_var = ctk.BooleanVar(value=False)
                def make_toggle(e=entry, v=show_var):
                    def toggle():
                        v.set(not v.get())
                        e.configure(show="" if v.get() else "•")
                    return toggle
                ctk.CTkButton(
                    grid, text="👁", width=34, height=34,
                    command=make_toggle(),
                    fg_color=COLORS["bg_card"], hover_color=COLORS["bg_hover"],
                    text_color=COLORS["text_secondary"], corner_radius=6, font=FONTS["body_sm"]
                ).grid(row=i, column=2, padx=(0, 12), pady=8)

    def _build_test_button(self, parent, label: str, command):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 12))

        btn = ctk.CTkButton(
            btn_frame, text=label, command=command, height=34, width=200,
            **button_secondary()
        )
        btn.pack(side="left")

        status = ctk.CTkLabel(
            btn_frame, text="", font=FONTS["body_sm"],
            text_color=COLORS["text_secondary"]
        )
        status.pack(side="left", padx=12)

        # Simpan reference status label dari tombol ini
        self._status_labels[label] = status

    # ─── LOAD VALUES ─────────────────────────────────────────────────────────

    def _load_values(self):
        data = self._env_mgr.load()
        for key, entry in self._entries.items():
            val = data.get(key, "")
            entry.delete(0, "end")
            entry.insert(0, val)

    # ─── SAVE ────────────────────────────────────────────────────────────────

    def _save_all(self):
        data = {}
        for key, entry in self._entries.items():
            data[key] = entry.get().strip()
        ok = self._env_mgr.save(data)
        if ok:
            self._save_status.configure(text="✅ Tersimpan!", text_color=COLORS["accent_green"])
        else:
            self._save_status.configure(text="❌ Gagal simpan!", text_color=COLORS["accent_red"])
        self.after(3000, lambda: self._save_status.configure(text=""))

    # ─── CONNECTION TESTS ────────────────────────────────────────────────────

    def _set_status(self, label_text: str, msg: str, is_ok: bool):
        lbl = self._status_labels.get(label_text)
        if lbl:
            color = COLORS["accent_green"] if is_ok else COLORS["accent_red"]
            lbl.configure(text=msg, text_color=color)

    def _test_binance(self):
        from gui.config_manager import test_binance_connection
        self._set_status("🔌  Test Koneksi Binance", "⏳ Testing...", True)
        api = self._entries.get("BINANCE_API_KEY", None)
        sec = self._entries.get("BINANCE_SECRET_KEY", None)
        is_demo = True  # Default aman ke demo
        if not api or not sec:
            return
        a, s = api.get().strip(), sec.get().strip()

        def run():
            ok, msg = test_binance_connection(a, s, is_demo)
            self.after(0, lambda: self._set_status("🔌  Test Koneksi Binance", msg, ok))
        threading.Thread(target=run, daemon=True).start()

    def _test_telegram(self, channel: str):
        from gui.config_manager import test_telegram_connection
        label = "📨  Test Telegram Utama" if channel == "default" else "📰  Test Telegram Sentimen"
        self._set_status(label, "⏳ Testing...", True)
        if channel == "default":
            token = self._entries.get("TELEGRAM_TOKEN", None)
            chat_id = self._entries.get("TELEGRAM_CHAT_ID", None)
        else:
            token = self._entries.get("TELEGRAM_TOKEN_SENTIMENT", None)
            chat_id = self._entries.get("TELEGRAM_CHAT_ID_SENTIMENT", None)
        if not token or not chat_id:
            return
        t, c = token.get().strip(), chat_id.get().strip()

        def run():
            ok, msg = test_telegram_connection(t, c)
            self.after(0, lambda: self._set_status(label, msg, ok))
        threading.Thread(target=run, daemon=True).start()

    def _test_mongodb(self):
        from gui.config_manager import test_mongodb_connection
        self._set_status("🗄️  Test MongoDB", "⏳ Testing...", True)
        uri_entry = self._entries.get("MONGO_URI", None)
        if not uri_entry:
            return
        uri = uri_entry.get().strip()

        def run():
            ok, msg = test_mongodb_connection(uri)
            self.after(0, lambda: self._set_status("🗄️  Test MongoDB", msg, ok))
        threading.Thread(target=run, daemon=True).start()

    def _test_ai(self):
        from gui.config_manager import test_ai_api_connection
        self._set_status("🤖  Test AI API", "⏳ Testing...", True)
        api_entry = self._entries.get("AI_API_KEY", None)
        if not api_entry:
            return
        key = api_entry.get().strip()

        def run():
            ok, msg = test_ai_api_connection(key, "https://openrouter.ai/api/v1", "")
            self.after(0, lambda: self._set_status("🤖  Test AI API", msg, ok))
        threading.Thread(target=run, daemon=True).start()
