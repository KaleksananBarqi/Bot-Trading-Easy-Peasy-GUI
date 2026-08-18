"""
page_pnl_card.py — Halaman 6: PnL Card Settings.
Menggantikan edit manual pnl_config.json
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from gui.theme import COLORS, FONTS, entry_style, button_primary, button_secondary, button_success, make_section_header, switch_style, slider_style


class PagePnlCard(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self._build()
        self._load()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 0))
        ctk.CTkLabel(hdr, text="🖼️  PnL Card Settings",
                     font=FONTS["title_xl"], text_color=COLORS["text_primary"]).pack(side="left")
        self._save_lbl = ctk.CTkLabel(hdr, text="", font=FONTS["body_md"], text_color=COLORS["accent_green"])
        self._save_lbl.pack(side="right", padx=(0, 12))
        ctk.CTkButton(hdr, text="💾  Simpan", command=self._save, height=36, width=120, **button_success()).pack(side="right")

        ctk.CTkLabel(self, text="Atur tampilan kartu PnL yang dibagikan setelah trade. Menggantikan pnl_config.json.",
                     font=FONTS["body_md"], text_color=COLORS["text_secondary"], anchor="w"
                     ).pack(fill="x", padx=20, pady=(4, 8))

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_primary"], scrollbar_button_color=COLORS["bg_hover"])
        self._scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ── USER PROFILE ─────────────────────────────────────────────────────
        make_section_header(self._scroll, "👤 User Profile & Branding")

        self._username = self._make_entry("Username", "username")
        self._profile_pic = self._make_file_picker("Foto Profil", "Pilih gambar (JPG/PNG)")
        self._show_qr = self._make_toggle("Tampilkan QR Code", True)
        self._qr_data = self._make_entry("QR Code Data/URL", "https://www.binance.com/en/futures")
        self._ref_code = self._make_entry("Referral Code", "")
        self._ref_title = self._make_entry("Referral Title", "Referral Code")
        self._base_currency = self._make_dropdown("Base Currency", ["USDT", "BUSD", "BTC"], "USDT")

        # ── IMAGES ───────────────────────────────────────────────────────────
        make_section_header(self._scroll, "🖼️ Gambar & Logo")

        self._exchange_logo = self._make_file_picker("Exchange Logo", "Pilih logo exchange")
        self._logo_max_w = self._make_spinbox("Exchange Logo Max Width (px)", 50, 500, 250)
        self._logo_max_h = self._make_spinbox("Exchange Logo Max Height (px)", 20, 300, 100)
        self._watermark = self._make_file_picker("Watermark Image", "Pilih gambar watermark (opsional)")
        self._show_watermark = self._make_toggle("Tampilkan Watermark", False)
        self._right_panel = self._make_file_picker("Right Panel Image", "Gambar latar kanan")
        self._right_panel_opacity = self._make_slider("Right Panel Opacity", 0.0, 1.0, 0.8, 0.05)

        # ── STYLE ────────────────────────────────────────────────────────────
        make_section_header(self._scroll, "🎨 Style & Warna")

        self._theme = self._make_dropdown("Theme", ["dark", "light"], "dark")
        self._layout = self._make_dropdown("Layout Mode", ["landscape", "portrait"], "landscape")

        # Color pickers (simulated dengan entry hex)
        ctk.CTkLabel(self._scroll, text="Warna Gradient Background",
                     font=FONTS["label_bold"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(8, 0))
        grad_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        grad_frame.pack(fill="x", pady=(2, 4))
        self._grad1 = ctk.CTkEntry(grad_frame, placeholder_text="#030201", width=130, height=34, **entry_style())
        self._grad1.pack(side="left", padx=(0, 4))
        self._grad2 = ctk.CTkEntry(grad_frame, placeholder_text="#030201", width=130, height=34, **entry_style())
        self._grad2.pack(side="left", padx=(0, 4))
        self._grad3 = ctk.CTkEntry(grad_frame, placeholder_text="#809ab5", width=130, height=34, **entry_style())
        self._grad3.pack(side="left")

        self._card_bg = self._make_color_entry("Card Background Color", "#1E2329")
        self._text_primary = self._make_color_entry("Text Primary Color", "#EAECEF")
        self._accent_color = self._make_color_entry("Accent Color (Binance Yellow)", "#F0B90B")
        self._up_color = self._make_color_entry("Profit Color (Up)", "#2EBD85")
        self._down_color = self._make_color_entry("Loss Color (Down)", "#F6465D")

        # ── CARD DIMENSIONS ──────────────────────────────────────────────────
        make_section_header(self._scroll, "📐 Dimensi Kartu")

        self._card_w = self._make_spinbox("Width (px)", 400, 3840, 1920)
        self._card_h = self._make_spinbox("Height (px)", 200, 2160, 1080)
        self._card_margin = self._make_spinbox("Margin (px)", 0, 200, 60)
        self._card_radius = self._make_spinbox("Border Radius (px)", 0, 200, 40)

    # ─── WIDGET HELPERS ──────────────────────────────────────────────────────

    def _make_entry(self, label: str, default: str = "", hint: str = ""):
        ctk.CTkLabel(self._scroll, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(8, 0))
        if hint:
            ctk.CTkLabel(self._scroll, text=hint, font=FONTS["caption"],
                         text_color=COLORS["text_muted"], anchor="w").pack(fill="x")
        var = ctk.StringVar(value=default)
        ctk.CTkEntry(self._scroll, textvariable=var, height=34, **entry_style()).pack(fill="x", pady=(2, 4))
        return var

    def _make_color_entry(self, label: str, default: str = ""):
        row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(row, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(side="left")
        var = ctk.StringVar(value=default)
        # Preview swatch
        swatch = ctk.CTkLabel(row, text="   ", fg_color=default if default.startswith("#") else COLORS["bg_card"],
                               width=28, height=28, corner_radius=4)
        swatch.pack(side="right", padx=(4, 0))

        entry = ctk.CTkEntry(row, textvariable=var, width=110, height=34, **entry_style())
        entry.pack(side="right", padx=(0, 4))

        def update_swatch(*args, s=swatch, v=var):
            try:
                hex_val = v.get().strip()
                if hex_val.startswith("#") and len(hex_val) in (4, 7):
                    s.configure(fg_color=hex_val)
            except Exception:
                pass
        var.trace_add("write", update_swatch)
        return var

    def _make_file_picker(self, label: str, placeholder: str = ""):
        ctk.CTkLabel(self._scroll, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(8, 0))
        row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row.pack(fill="x", pady=(2, 4))
        var = ctk.StringVar()
        entry = ctk.CTkEntry(row, textvariable=var, height=34, placeholder_text=placeholder, **entry_style())
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def browse(v=var):
            path = filedialog.askopenfilename(
                title=f"Pilih {label}",
                filetypes=[("Gambar", "*.jpg *.jpeg *.png *.webp"), ("Semua", "*.*")]
            )
            if path:
                # Store relative path from ROOT if possible
                try:
                    from gui.config_manager import ROOT_DIR
                    import os
                    rel = os.path.relpath(path, str(ROOT_DIR)).replace("\\", "/")
                    v.set(rel)
                except ValueError:
                    v.set(path)

        ctk.CTkButton(row, text="📁", width=36, height=34, command=browse,
                      fg_color=COLORS["bg_card"], hover_color=COLORS["bg_hover"],
                      text_color=COLORS["text_secondary"], corner_radius=6, font=FONTS["body_md"]).pack(side="right")
        return var

    def _make_toggle(self, label: str, default: bool):
        row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row.pack(fill="x", pady=4)
        var = ctk.BooleanVar(value=default)
        ctk.CTkSwitch(row, text=label, variable=var, font=FONTS["body_md"],
                      text_color=COLORS["text_primary"],
                      progress_color=COLORS["accent_green"],
                      button_color=COLORS["text_primary"],
                      fg_color=COLORS["bg_hover"]).pack(side="left")
        return var

    def _make_dropdown(self, label: str, options: list, default: str):
        ctk.CTkLabel(self._scroll, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(8, 0))
        var = ctk.StringVar(value=default)
        ctk.CTkOptionMenu(self._scroll, variable=var, values=options, height=34, anchor="w",
                          fg_color=COLORS["bg_card"], button_color=COLORS["bg_hover"],
                          dropdown_fg_color=COLORS["bg_secondary"], text_color=COLORS["text_primary"],
                          dropdown_text_color=COLORS["text_primary"], font=FONTS["body_md"],
                          corner_radius=6).pack(fill="x", pady=(2, 4))
        return var

    def _make_slider(self, label: str, min_v, max_v, default, step):
        row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(row, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(side="left")
        var = ctk.DoubleVar(value=default)
        val_lbl = ctk.CTkLabel(row, text=f"{default:.2f}", font=FONTS["mono_sm"],
                                text_color=COLORS["accent_blue"], width=40)
        val_lbl.pack(side="right")
        steps = int((max_v - min_v) / step)

        def on_change(v, vl=val_lbl, s=step):
            rounded = round(float(v) / s) * s
            vl.configure(text=f"{rounded:.2f}")

        ctk.CTkSlider(self._scroll, from_=min_v, to=max_v, number_of_steps=steps,
                      variable=var, command=on_change, **slider_style()).pack(fill="x", pady=(2, 4))
        return var

    def _make_spinbox(self, label: str, min_v, max_v, default):
        row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(row, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(side="left")
        var = ctk.StringVar(value=str(default))
        ctk.CTkEntry(row, textvariable=var, width=100, height=34, **entry_style()).pack(side="right")
        return var

    # ─── LOAD / SAVE ─────────────────────────────────────────────────────────

    def _load(self):
        from gui.config_manager import PnlConfigManager
        cfg = PnlConfigManager.load()

        u = cfg.get("user", {})
        self._username.set(u.get("username", "username"))
        self._profile_pic.set(u.get("profile_picture_path", ""))
        self._show_qr.set(u.get("show_qr", True))
        self._qr_data.set(u.get("qr_data", ""))
        self._ref_code.set(u.get("referral_code", ""))
        self._ref_title.set(u.get("referral_title", "Referral Code"))
        self._base_currency.set(u.get("base_currency", "USDT"))

        img = cfg.get("images", {})
        self._exchange_logo.set(img.get("exchange_logo_path", ""))
        self._logo_max_w.set(str(img.get("exchange_logo_max_width", 250)))
        self._logo_max_h.set(str(img.get("exchange_logo_max_height", 100)))
        self._watermark.set(img.get("watermark_path", ""))
        self._show_watermark.set(img.get("show_watermark", False))
        self._right_panel.set(img.get("right_panel_image_path", ""))
        self._right_panel_opacity.set(img.get("right_panel_image_opacity", 0.8))

        s = cfg.get("style", {})
        self._theme.set(s.get("theme", "dark"))
        self._layout.set(s.get("layout_mode", "landscape"))
        grads = s.get("bg_gradient_colors", ["#030201", "#030201", "#809ab5"])
        if len(grads) >= 3:
            self._grad1.delete(0, "end"); self._grad1.insert(0, grads[0])
            self._grad2.delete(0, "end"); self._grad2.insert(0, grads[1])
            self._grad3.delete(0, "end"); self._grad3.insert(0, grads[2])
        self._card_bg.set(s.get("card_bg_color", "#1E2329"))
        self._text_primary.set(s.get("text_primary", "#EAECEF"))
        self._accent_color.set(s.get("accent_color", "#F0B90B"))
        self._up_color.set(s.get("up_color", "#2EBD85"))
        self._down_color.set(s.get("down_color", "#F6465D"))

        cs = cfg.get("card_settings", {})
        self._card_w.set(str(cs.get("width", 1920)))
        self._card_h.set(str(cs.get("height", 1080)))
        self._card_margin.set(str(cs.get("margin", 60)))
        self._card_radius.set(str(cs.get("border_radius", 40)))

    def _save(self):
        from gui.config_manager import PnlConfigManager, PNL_CONFIG_PATH
        data = {
            "user": {
                "username": self._username.get(),
                "profile_picture_path": self._profile_pic.get(),
                "show_qr": self._show_qr.get(),
                "qr_data": self._qr_data.get(),
                "referral_code": self._ref_code.get(),
                "referral_title": self._ref_title.get(),
                "base_currency": self._base_currency.get(),
            },
            "images": {
                "exchange_logo_path": self._exchange_logo.get(),
                "exchange_logo_max_width": int(self._logo_max_w.get()),
                "exchange_logo_max_height": int(self._logo_max_h.get()),
                "watermark_path": self._watermark.get(),
                "show_watermark": self._show_watermark.get(),
                "right_panel_image_path": self._right_panel.get(),
                "right_panel_image_opacity": round(self._right_panel_opacity.get(), 2),
            },
            "style": {
                "theme": self._theme.get(),
                "layout_mode": self._layout.get(),
                "bg_gradient_colors": [self._grad1.get(), self._grad2.get(), self._grad3.get()],
                "card_bg_color": self._card_bg.get(),
                "text_primary": self._text_primary.get(),
                "accent_color": self._accent_color.get(),
                "up_color": self._up_color.get(),
                "down_color": self._down_color.get(),
            },
            "fonts": PnlConfigManager.load().get("fonts", {}),
            "card_settings": {
                "width": int(self._card_w.get()),
                "height": int(self._card_h.get()),
                "margin": int(self._card_margin.get()),
                "border_radius": int(self._card_radius.get()),
            },
        }
        ok = PnlConfigManager.save(data)
        if ok:
            self._save_lbl.configure(text="✅ PnL Config tersimpan!", text_color=COLORS["accent_green"])
        else:
            self._save_lbl.configure(text="❌ Gagal!", text_color=COLORS["accent_red"])
        self.after(3000, lambda: self._save_lbl.configure(text=""))
