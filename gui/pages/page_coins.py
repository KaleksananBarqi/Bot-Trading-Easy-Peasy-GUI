"""
page_coins.py — Halaman 2: Daftar Koin (Watchlist Editor).
Table editor visual untuk DAFTAR_KOIN di config.py
"""

import customtkinter as ctk
import json
from gui.theme import COLORS, FONTS, entry_style, button_primary, button_secondary, button_success, button_danger, frame_section, make_section_header


CATEGORY_OPTIONS = ["KING", "Layer1", "AI", "Meme", "DeFi", "Gaming", "Other"]
MARGIN_OPTIONS = ["isolated", "cross"]


class CoinRowEditor(ctk.CTkFrame):
    """Row editor untuk satu koin dalam tabel."""

    def __init__(self, parent, coin_data: dict, on_delete, row_num: int, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_secondary"] if row_num % 2 == 0 else COLORS["bg_card"],
                         corner_radius=6, **kwargs)
        self._on_delete = on_delete
        self._build(coin_data)

    def _build(self, data: dict):
        self.columnconfigure(1, weight=2)
        self.columnconfigure(6, weight=2)

        row = 0

        # ── Symbol ────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Symbol", font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(row=0, column=0, padx=(12, 4), pady=(8, 0), sticky="w")
        self.symbol_var = ctk.StringVar(value=data.get("symbol", "BTC/USDT"))
        ctk.CTkEntry(self, textvariable=self.symbol_var, width=120, height=30, placeholder_text="BTC/USDT", **entry_style()).grid(row=1, column=0, padx=(12, 4), pady=(0, 8), sticky="w")

        # ── Category ──────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Kategori", font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(row=0, column=1, padx=4, pady=(8, 0), sticky="w")
        self.cat_var = ctk.StringVar(value=data.get("category", "Layer1"))
        ctk.CTkOptionMenu(self, variable=self.cat_var, values=CATEGORY_OPTIONS, width=100, height=30,
                          fg_color=COLORS["bg_card"], button_color=COLORS["bg_hover"],
                          dropdown_fg_color=COLORS["bg_secondary"], text_color=COLORS["text_primary"],
                          dropdown_text_color=COLORS["text_primary"], font=FONTS["body_sm"]).grid(row=1, column=1, padx=4, pady=(0, 8), sticky="w")

        # ── Leverage ──────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Leverage", font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(row=0, column=2, padx=4, pady=(8, 0), sticky="w")
        self.lev_var = ctk.StringVar(value=str(data.get("leverage", 10)))
        ctk.CTkEntry(self, textvariable=self.lev_var, width=65, height=30, **entry_style()).grid(row=1, column=2, padx=4, pady=(0, 8), sticky="w")

        # ── Margin Type ───────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Margin", font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(row=0, column=3, padx=4, pady=(8, 0), sticky="w")
        self.margin_var = ctk.StringVar(value=data.get("margin_type", "isolated"))
        ctk.CTkOptionMenu(self, variable=self.margin_var, values=MARGIN_OPTIONS, width=90, height=30,
                          fg_color=COLORS["bg_card"], button_color=COLORS["bg_hover"],
                          dropdown_fg_color=COLORS["bg_secondary"], text_color=COLORS["text_primary"],
                          dropdown_text_color=COLORS["text_primary"], font=FONTS["body_sm"]).grid(row=1, column=3, padx=4, pady=(0, 8), sticky="w")

        # ── Amount ────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Amount (USDT)", font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(row=0, column=4, padx=4, pady=(8, 0), sticky="w")
        self.amount_var = ctk.StringVar(value=str(data.get("amount", 10)))
        ctk.CTkEntry(self, textvariable=self.amount_var, width=80, height=30, **entry_style()).grid(row=1, column=4, padx=4, pady=(0, 8), sticky="w")

        # ── BTC Corr ──────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="BTC Corr", font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(row=0, column=5, padx=4, pady=(8, 0), sticky="w")
        self.btc_corr_var = ctk.BooleanVar(value=data.get("btc_corr", True))
        ctk.CTkSwitch(self, variable=self.btc_corr_var, text="", width=46, height=24,
                      progress_color=COLORS["accent_green"], button_color=COLORS["text_primary"],
                      fg_color=COLORS["bg_hover"]).grid(row=1, column=5, padx=4, pady=(0, 8), sticky="w")

        # ── Keywords ──────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Keywords (pisah koma)", font=FONTS["caption"], text_color=COLORS["text_muted"]).grid(row=0, column=6, padx=4, pady=(8, 0), sticky="w")
        kw_str = ", ".join(data.get("keywords", []))
        self.keywords_var = ctk.StringVar(value=kw_str)
        ctk.CTkEntry(self, textvariable=self.keywords_var, height=30, placeholder_text="bitcoin, btc, ...", **entry_style()).grid(row=1, column=6, padx=4, pady=(0, 8), sticky="ew")

        # ── Delete Button ─────────────────────────────────────────────────
        ctk.CTkButton(self, text="🗑", width=34, height=30, command=self._on_delete,
                      fg_color=COLORS["accent_red_dim"], hover_color=COLORS["accent_red"],
                      text_color=COLORS["accent_red"], corner_radius=6, font=FONTS["body_sm"]).grid(row=1, column=7, padx=(4, 12), pady=(0, 8))

    def get_data(self) -> dict:
        kw_raw = self.keywords_var.get().strip()
        keywords = [k.strip() for k in kw_raw.split(",") if k.strip()]
        try:
            lev = int(self.lev_var.get())
        except ValueError:
            lev = 10
        try:
            amt = float(self.amount_var.get())
        except ValueError:
            amt = 10.0
        return {
            "symbol": self.symbol_var.get().strip().upper(),
            "category": self.cat_var.get(),
            "leverage": lev,
            "margin_type": self.margin_var.get(),
            "amount": amt,
            "btc_corr": self.btc_corr_var.get(),
            "keywords": keywords,
        }


class PageCoins(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self._rows: list[CoinRowEditor] = []
        self._build()
        self._load()

    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 0))

        ctk.CTkLabel(header, text="🪙  Daftar Koin (Watchlist)",
                     font=FONTS["title_xl"], text_color=COLORS["text_primary"]).pack(side="left", anchor="w")

        # Action buttons — kanan atas
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(btn_frame, text="➕  Tambah Koin", command=self._add_row, height=36,
                      **button_secondary()).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_frame, text="💾  Simpan", command=self._save, height=36,
                      **button_success()).pack(side="left")

        ctk.CTkLabel(self, text="Setiap koin dapat dikonfigurasi leverage, amount, dan keywords berita secara spesifik.",
                     font=FONTS["body_md"], text_color=COLORS["text_secondary"], anchor="w"
                     ).pack(fill="x", padx=20, pady=(4, 16))

        self._save_lbl = ctk.CTkLabel(self, text="", font=FONTS["body_md"],
                                       text_color=COLORS["accent_green"])
        self._save_lbl.pack(anchor="w", padx=20)

        # Column headers
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"], corner_radius=6)
        hdr.pack(fill="x", padx=20, pady=(0, 4))
        hdr.columnconfigure(6, weight=1)

        for i, (col, width) in enumerate([
            ("Symbol", 120), ("Kategori", 100), ("Leverage", 65),
            ("Margin", 90), ("Amount (USDT)", 80), ("BTC Corr", 65),
            ("Keywords", 0), ("", 34)
        ]):
            ctk.CTkLabel(hdr, text=col, font=FONTS["label_bold"],
                         text_color=COLORS["text_muted"], anchor="w"
                         ).grid(row=0, column=i, padx=(12 if i == 0 else 4, 4), pady=6, sticky="w")

        # Scrollable rows container
        self._list_frame = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_primary"],
            scrollbar_button_color=COLORS["bg_hover"]
        )
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _add_row(self, data: dict = None):
        if data is None:
            data = {"symbol": "NEW/USDT", "category": "Layer1", "leverage": 10,
                    "margin_type": "isolated", "amount": 10, "btc_corr": True, "keywords": []}
        idx = len(self._rows)

        def on_delete(row_ref=None):
            if row_ref in self._rows:
                self._rows.remove(row_ref)
                row_ref.destroy()

        row = CoinRowEditor(self._list_frame, data, lambda: None, idx)
        row.pack(fill="x", pady=2)
        # Fix delete closure
        row._on_delete = lambda r=row: self._delete_row(r)
        # Patch the button inside the row to re-bind
        for widget in row.winfo_children():
            if isinstance(widget, ctk.CTkButton) and "🗑" in widget.cget("text"):
                widget.configure(command=lambda r=row: self._delete_row(r))
        self._rows.append(row)

    def _delete_row(self, row: CoinRowEditor):
        if row in self._rows:
            self._rows.remove(row)
            row.destroy()

    def _load(self):
        from gui.config_manager import BotConfigManager
        cfg = BotConfigManager.load()
        coins = cfg.get("DAFTAR_KOIN", [])
        for coin in coins:
            self._add_row(coin)

    def _save(self):
        from gui.config_manager import BotConfigManager
        coins = [row.get_data() for row in self._rows]
        ok = BotConfigManager.save({"DAFTAR_KOIN": coins})
        if ok:
            self._save_lbl.configure(text=f"✅ {len(coins)} koin tersimpan!", text_color=COLORS["accent_green"])
        else:
            self._save_lbl.configure(text="❌ Gagal menyimpan!", text_color=COLORS["accent_red"])
        self.after(3000, lambda: self._save_lbl.configure(text=""))
