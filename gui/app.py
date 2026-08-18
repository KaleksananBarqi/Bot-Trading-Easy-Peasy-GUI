"""
app.py — Main window + sidebar navigasi untuk Easy Peasy Bot GUI.
"""

import customtkinter as ctk
import sys
import os
from gui.theme import COLORS, FONTS


NAV_ITEMS = [
    ("🔑  Setup & API Keys",     "api_keys"),
    ("🪙  Daftar Koin",           "coins"),
    ("🧠  AI & Strategi",         "ai"),
    ("💰  Risk & Eksekusi",       "risk"),
    ("⚙️  Sistem & Database",     "system"),
    ("🖼️  PnL Card",              "pnl_card"),
    ("─────────────────",         None),  # Separator
    ("🚀  Bot Control",           "bot_control"),
    ("📚  Library Strategi",      "strategies"),
]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── Window config ────────────────────────────────────────────────────
        self.title("🤖  Easy Peasy Trading Bot — Control Panel")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg_primary"])

        # Icon (optional, skip jika tidak ada)
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        self._pages: dict = {}
        self._current_page = None
        self._nav_buttons: dict = {}

        self._build_layout()
        self._navigate("bot_control")  # Default: halaman Bot Control

    # ─── LAYOUT ──────────────────────────────────────────────────────────────

    def _build_layout(self):
        """Bangun layout utama: sidebar (kiri) + content area (kanan)."""
        # Main container
        self._container = ctk.CTkFrame(self, fg_color="transparent")
        self._container.pack(fill="both", expand=True)
        self._container.columnconfigure(1, weight=1)
        self._container.rowconfigure(0, weight=1)

        # Sidebar
        self._build_sidebar()

        # Content area (right side)
        self._content_area = ctk.CTkFrame(
            self._container, fg_color=COLORS["bg_primary"], corner_radius=0
        )
        self._content_area.grid(row=0, column=1, sticky="nsew")
        self._content_area.columnconfigure(0, weight=1)
        self._content_area.rowconfigure(0, weight=1)

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self._container,
            fg_color=COLORS["sidebar_bg"],
            corner_radius=0,
            border_width=0,
            width=228,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.pack_propagate(False)

        # ── Logo / App Name ───────────────────────────────────────────────────
        logo_frame = ctk.CTkFrame(sidebar, fg_color=COLORS["bg_secondary"], corner_radius=0)
        logo_frame.pack(fill="x")

        ctk.CTkLabel(
            logo_frame, text="🤖",
            font=("Segoe UI", 28), text_color=COLORS["accent_blue"]
        ).pack(pady=(16, 0))

        ctk.CTkLabel(
            logo_frame, text="Easy Peasy Bot",
            font=("Segoe UI", 14, "bold"), text_color=COLORS["text_primary"]
        ).pack(pady=(2, 0))

        ctk.CTkLabel(
            logo_frame, text="Trading Control Panel",
            font=FONTS["caption"], text_color=COLORS["text_muted"]
        ).pack(pady=(0, 16))

        # Bot status indicator (mini)
        self._sidebar_status = ctk.CTkLabel(
            logo_frame, text="● STOPPED",
            font=FONTS["label_bold"], text_color=COLORS["status_stopped"]
        )
        self._sidebar_status.pack(pady=(0, 12))

        # ── Navigation ────────────────────────────────────────────────────────
        nav_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent",
                                             scrollbar_button_color=COLORS["bg_hover"])
        nav_scroll.pack(fill="both", expand=True, padx=8, pady=12)

        for i, (label, page_key) in enumerate(NAV_ITEMS):
            if page_key is None:
                # Separator
                ctk.CTkLabel(nav_scroll, text="─" * 20, font=FONTS["caption"],
                             text_color=COLORS["text_muted"]).pack(pady=4, padx=8)
                continue

            btn = ctk.CTkButton(
                nav_scroll,
                text=label,
                command=lambda k=page_key: self._navigate(k),
                height=40,
                anchor="w",
                fg_color="transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_secondary"],
                corner_radius=8,
                font=FONTS["nav_item"],
            )
            btn.pack(fill="x", pady=2)
            self._nav_buttons[page_key] = btn

        # ── Bottom: Version ───────────────────────────────────────────────────
        ctk.CTkLabel(sidebar, text="v1.0.0 GUI  |  Easy Peasy",
                     font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(side="bottom", pady=12)

        # ── Status update loop ────────────────────────────────────────────────
        self._update_sidebar_status()

    # ─── NAVIGATION ──────────────────────────────────────────────────────────

    def _navigate(self, page_key: str):
        if page_key not in self._pages:
            self._pages[page_key] = self._create_page(page_key)

        # Hide current page
        if self._current_page:
            self._current_page.grid_remove()

        # Show new page
        page = self._pages[page_key]
        page.grid(row=0, column=0, sticky="nsew")
        self._current_page = page

        # Update nav button active state
        for key, btn in self._nav_buttons.items():
            if key == page_key:
                btn.configure(
                    fg_color=COLORS["accent_blue_dim"],
                    text_color=COLORS["accent_blue"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                )

    def _create_page(self, page_key: str) -> ctk.CTkFrame:
        """Lazy-load halaman saat pertama kali diakses."""
        parent = self._content_area

        if page_key == "api_keys":
            from gui.pages.page_api_keys import PageApiKeys
            return PageApiKeys(parent)
        elif page_key == "coins":
            from gui.pages.page_coins import PageCoins
            return PageCoins(parent)
        elif page_key == "ai":
            from gui.pages.page_ai import PageAI
            return PageAI(parent)
        elif page_key == "risk":
            from gui.pages.page_risk import PageRisk
            return PageRisk(parent)
        elif page_key == "system":
            from gui.pages.page_system import PageSystem
            return PageSystem(parent)
        elif page_key == "pnl_card":
            from gui.pages.page_pnl_card import PagePnlCard
            return PagePnlCard(parent)
        elif page_key == "bot_control":
            from gui.pages.page_bot_control import PageBotControl
            return PageBotControl(parent)
        elif page_key == "strategies":
            from gui.pages.page_strategies import PageStrategies
            return PageStrategies(parent)
        else:
            placeholder = ctk.CTkFrame(parent, fg_color=COLORS["bg_primary"])
            ctk.CTkLabel(placeholder, text=f"Halaman '{page_key}' belum tersedia.",
                         font=FONTS["title_md"], text_color=COLORS["text_muted"]).pack(expand=True)
            return placeholder

    # ─── STATUS UPDATE ────────────────────────────────────────────────────────

    def _update_sidebar_status(self):
        """Update status bot di sidebar setiap 2 detik."""
        def tick():
            try:
                from gui.bot_runner import get_bot_runner
                running = get_bot_runner().is_running()
                if running:
                    self._sidebar_status.configure(text="● RUNNING", text_color=COLORS["status_running"])
                else:
                    self._sidebar_status.configure(text="● STOPPED", text_color=COLORS["status_stopped"])
            except Exception:
                pass
            self.after(2000, tick)

        self.after(2000, tick)

    # ─── LIFECYCLE ───────────────────────────────────────────────────────────

    def run(self):
        """Jalankan aplikasi."""
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.mainloop()

    def _on_close(self):
        """Pastikan bot distop sebelum keluar."""
        try:
            from gui.bot_runner import get_bot_runner
            runner = get_bot_runner()
            if runner.is_running():
                runner.stop_bot()
            runner.stop_dashboard()
        except Exception:
            pass
        self.destroy()
        sys.exit(0)
