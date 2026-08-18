"""
page_risk.py — Halaman 4: Risk Manager, Trailing Stop, dan Indikator Teknikal.
"""

import customtkinter as ctk
from gui.theme import COLORS, FONTS, entry_style, button_success, frame_section, make_section_header, switch_style, slider_style, dropdown_style


class PageRisk(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self._build()
        self._load()

    def _build(self):
        # Title
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 0))
        ctk.CTkLabel(hdr, text="💰  Risk Manager & Eksekusi",
                     font=FONTS["title_xl"], text_color=COLORS["text_primary"]).pack(side="left", anchor="w")
        self._save_lbl = ctk.CTkLabel(hdr, text="", font=FONTS["body_md"], text_color=COLORS["accent_green"])
        self._save_lbl.pack(side="right", padx=(0, 12))
        ctk.CTkButton(hdr, text="💾  Simpan", command=self._save, height=36, width=120, **button_success()).pack(side="right")

        ctk.CTkLabel(self, text="Atur ukuran posisi, stop loss, trailing stop, dan semua indikator teknikal.",
                     font=FONTS["body_md"], text_color=COLORS["text_secondary"], anchor="w"
                     ).pack(fill="x", padx=20, pady=(4, 12))

        # Tabs
        self._tabs = ctk.CTkTabview(
            self, height=680,
            fg_color=COLORS["bg_secondary"],
            segmented_button_fg_color=COLORS["bg_tertiary"],
            segmented_button_selected_color=COLORS["accent_blue"],
            segmented_button_selected_hover_color="#4c94e8",
            segmented_button_unselected_color=COLORS["bg_tertiary"],
            segmented_button_unselected_hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"],
        )
        self._tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._tabs.add("📏 Position Size")
        self._tabs.add("🛡 SL & TP")
        self._tabs.add("🔄 Trailing Stop")
        self._tabs.add("❄️ Anti-FOMO")
        self._tabs.add("📊 Indikator")
        self._tabs.add("₿ BTC Correlation")

        self._build_size_tab(self._tabs.tab("📏 Position Size"))
        self._build_sltp_tab(self._tabs.tab("🛡 SL & TP"))
        self._build_trailing_tab(self._tabs.tab("🔄 Trailing Stop"))
        self._build_antifomo_tab(self._tabs.tab("❄️ Anti-FOMO"))
        self._build_indicators_tab(self._tabs.tab("📊 Indikator"))
        self._build_btc_tab(self._tabs.tab("₿ BTC Correlation"))

    # ─── POSITION SIZE ───────────────────────────────────────────────────────

    def _build_size_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(scroll, "Ukuran Posisi")

        mode_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        mode_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(mode_frame, text="Mode Sizing", font=FONTS["label_bold"], text_color=COLORS["text_secondary"]).pack(padx=12, pady=(10, 4), anchor="w")
        self._use_dynamic = ctk.BooleanVar(value=False)
        size_seg = ctk.CTkSegmentedButton(mode_frame, values=["Static (USDT Tetap)", "Dynamic (% Saldo)"],
                                           command=lambda v: self._use_dynamic.set(v == "Dynamic (% Saldo)"),
                                           selected_color=COLORS["accent_blue"],
                                           selected_hover_color="#4c94e8",
                                           unselected_color=COLORS["bg_hover"],
                                           unselected_hover_color=COLORS["bg_tertiary"],
                                           text_color=COLORS["text_primary"],
                                           font=FONTS["body_md"])
        size_seg.pack(padx=12, pady=(0, 10), fill="x")
        size_seg.set("Static (USDT Tetap)")
        self._size_seg = size_seg

        self._default_amount = self._make_entry_row(scroll, "USDT Per Trade (Static)", "10", "Jumlah USDT tetap untuk setiap trade")
        self._risk_percent = self._make_slider(scroll, "% Risk Per Trade (Dynamic)", 0.1, 20.0, 3.0, 0.1, "Persentase dari total saldo wallet")
        self._min_order = self._make_entry_row(scroll, "Minimal Order (USDT)", "5", "Batas minimum order Binance ($5)")
        self._default_leverage = self._make_spinbox(scroll, "Default Leverage", 1, 125, 10)
        self._margin_type = self._make_dropdown(scroll, "Default Margin Type", ["isolated", "cross"], "isolated",
                                                 "isolated = risiko terbatas | cross = gabungan saldo")
        self._max_pos_cat = self._make_spinbox(scroll, "Max Posisi Per Kategori", 1, 20, 5)

    # ─── SL & TP ─────────────────────────────────────────────────────────────

    def _build_sltp_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(scroll, "Stop Loss & Take Profit")

        self._default_sl = self._make_slider(scroll, "Default SL % (Fallback)", 0.001, 0.10, 0.015, 0.001,
                                              "Digunakan jika ATR gagal dihitung")
        self._default_tp = self._make_slider(scroll, "Default TP % (Fallback)", 0.001, 0.20, 0.025, 0.001)

        make_section_header(scroll, "ATR-Based Dynamic SL/TP", "Rekomendasi: ATR lebih akurat dari % tetap")
        self._atr_period = self._make_spinbox(scroll, "ATR Period", 1, 50, 14)
        self._atr_sl = self._make_slider(scroll, "ATR Multiplier SL (Jarak SL dari Entry)", 0.1, 10.0, 1.0, 0.1,
                                          "SL = Entry ± (ATR × multiplier)")
        self._atr_tp = self._make_slider(scroll, "ATR Multiplier TP (Risk Reward Ratio)", 0.1, 20.0, 3.0, 0.1,
                                          "TP = Entry ± (ATR × multiplier). Default 3x → RR 1:3")
        self._trap_sl = self._make_slider(scroll, "Safety SL (Liquidity Hunt)", 0.5, 10.0, 2.0, 0.1,
                                           "SL lebih lebar untuk setup Liquidity Hunt agar tidak kena fake sweep")

        make_section_header(scroll, "Error Handling Order")
        self._order_retries = self._make_spinbox(scroll, "Max Retry Pasang SL/TP", 1, 10, 3)
        self._order_retry_delay = self._make_spinbox(scroll, "Jeda Retry (detik)", 1, 30, 2)

    # ─── TRAILING STOP ───────────────────────────────────────────────────────

    def _build_trailing_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(scroll, "Trailing Stop Loss — Dual Mode")

        self._enable_trailing = self._make_toggle(scroll, "Enable Trailing Stop (Master Switch)", True)

        # Mode selector
        mode_info = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        mode_info.pack(fill="x", pady=(8, 12))
        ctk.CTkLabel(mode_info, text="Mode Trailing Stop", font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"]).pack(padx=12, pady=(10, 4), anchor="w")
        self._trailing_mode_seg = ctk.CTkSegmentedButton(
            mode_info, values=["🏦 Native (Binance Server)", "💻 Software (Bot Custom)"],
            selected_color=COLORS["accent_blue"], selected_hover_color="#4c94e8",
            unselected_color=COLORS["bg_hover"], unselected_hover_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"], font=FONTS["body_md"]
        )
        self._trailing_mode_seg.pack(padx=12, pady=(0, 4), fill="x")

        # Native mode info
        native_card = ctk.CTkFrame(mode_info, fg_color=COLORS["accent_blue_dim"], corner_radius=6)
        native_card.pack(padx=12, pady=(0, 10), fill="x")
        ctk.CTkLabel(native_card, text="🏦 Native: Zero-latency, crash-proof, dimonitor server Binance",
                     font=FONTS["body_sm"], text_color=COLORS["accent_blue"]).pack(padx=10, pady=6, anchor="w")

        # Software mode info
        soft_card = ctk.CTkFrame(mode_info, fg_color=COLORS["bg_tertiary"], corner_radius=6)
        soft_card.pack(padx=12, pady=(0, 10), fill="x")
        ctk.CTkLabel(soft_card, text="💻 Software: Lebih fleksibel, dimonitor bot via WebSocket, butuh bot aktif",
                     font=FONTS["body_sm"], text_color=COLORS["text_secondary"]).pack(padx=10, pady=6, anchor="w")

        make_section_header(scroll, "🏦 Pengaturan Native Mode (Binance)")
        self._trailing_delay = self._make_spinbox(scroll, "Activation Delay (detik)", 0, 600, 60,
                                                   "Bot menunggu X detik setelah order terisi sebelum pasang trailing")
        self._trailing_callback = self._make_slider(scroll, "Callback Rate (%)", 0.1, 5.0, 0.1, 0.1,
                                                     "Jarak trail dari harga tertinggi/terendah")

        make_section_header(scroll, "💻 Pengaturan Software Mode")
        self._trailing_activation = self._make_slider(scroll, "Activation Threshold (%)", 0.5, 1.0, 0.8, 0.05,
                                                       "Trailing aktif saat harga sudah 80% menuju TP")
        self._trailing_min_profit = self._make_slider(scroll, "Min Profit Lock (%)", 0.001, 0.05, 0.005, 0.001,
                                                       "Minimal profit yang dikunci saat trailing aktif")
        self._trailing_cooldown = self._make_spinbox(scroll, "Update Cooldown (detik)", 1, 60, 3,
                                                      "Interval minimum antara update SL ke exchange")

    # ─── ANTI-FOMO ───────────────────────────────────────────────────────────

    def _build_antifomo_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(scroll, "❄️ Anti-FOMO & Anti-Revenge Trading")
        ctk.CTkLabel(scroll, text="Mekanisme cooldown otomatis untuk mencegah overtrading setelah trade selesai.",
                     font=FONTS["body_sm"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 12))

        self._cooldown_profit = self._make_spinbox(scroll, "Cooldown Setelah PROFIT (detik)", 0, 86400, 3600,
                                                    "Default: 3600 = 1 jam")
        self._cooldown_loss = self._make_spinbox(scroll, "Cooldown Setelah LOSS (detik)", 0, 86400, 7200,
                                                  "Default: 7200 = 2 jam (lebih lama untuk cegah revenge)")

        make_section_header(scroll, "📋 Order Execution Rules")
        self._enable_market = self._make_toggle(scroll, "Enable Market Orders", False)
        ctk.CTkLabel(scroll, text="⚠️  Jika False: Bot hanya gunakan Limit Order (Liquidity Hunt) untuk menghindari slippage.",
                     font=FONTS["caption"], text_color=COLORS["accent_yellow"], anchor="w").pack(fill="x", pady=(0, 8))
        self._limit_expiry = self._make_spinbox(scroll, "Limit Order Expiry (detik)", 300, 86400, 7200,
                                                 "Default: 7200 = 2 jam. Order yang belum terisi akan di-cancel otomatis.")

    # ─── INDICATORS ──────────────────────────────────────────────────────────

    def _build_indicators_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(scroll, "RSI (Relative Strength Index)")
        self._rsi_period = self._make_spinbox(scroll, "RSI Period", 1, 50, 14)
        self._rsi_oversold = self._make_slider(scroll, "RSI Oversold", 10, 50, 35, 1, "Sinyal potensial long/reversal")
        self._rsi_overbought = self._make_slider(scroll, "RSI Overbought", 50, 90, 65, 1, "Sinyal potensial short/reversal")
        self._rsi_deep_os = self._make_slider(scroll, "RSI Deep Oversold (Ekstrim)", 5, 40, 25, 1, "Reversal sangat kuat")
        self._rsi_deep_ob = self._make_slider(scroll, "RSI Deep Overbought (Ekstrim)", 60, 95, 75, 1, "Reversal sangat kuat")

        make_section_header(scroll, "EMA (Exponential Moving Average)")
        self._ema_fast = self._make_spinbox(scroll, "EMA Fast", 1, 50, 7)
        self._ema_slow = self._make_spinbox(scroll, "EMA Slow", 5, 200, 21)
        self._ema_trend = self._make_spinbox(scroll, "EMA Trend Major (4H filter)", 10, 500, 50)

        make_section_header(scroll, "StochRSI")
        self._stoch_len = self._make_spinbox(scroll, "StochRSI Length", 1, 50, 14)
        self._stoch_k = self._make_spinbox(scroll, "StochRSI K Smoothing", 1, 20, 3)
        self._stoch_d = self._make_spinbox(scroll, "StochRSI D Smoothing", 1, 20, 3)

        make_section_header(scroll, "MACD")
        self._macd_fast = self._make_spinbox(scroll, "MACD Fast", 1, 50, 12)
        self._macd_slow = self._make_spinbox(scroll, "MACD Slow", 10, 100, 26)
        self._macd_signal = self._make_spinbox(scroll, "MACD Signal", 1, 30, 9)

        make_section_header(scroll, "Bollinger Bands")
        self._bb_length = self._make_spinbox(scroll, "BB Length", 5, 100, 20)
        self._bb_std = self._make_slider(scroll, "BB Std Deviation", 0.5, 5.0, 2.0, 0.5)

        make_section_header(scroll, "Volume & Order Book")
        self._vol_ma = self._make_spinbox(scroll, "Volume MA Period", 1, 100, 20)
        self._vol_spike = self._make_slider(scroll, "Volume Spike Multiplier", 1.0, 5.0, 1.5, 0.1,
                                             "Volume harus ≥ X × rata-rata untuk konfirmasi")
        self._ob_range = self._make_slider(scroll, "Order Book Depth Range (%)", 0.01, 0.10, 0.02, 0.01)

        make_section_header(scroll, "Wick Rejection Analysis")
        self._wick_mult = self._make_slider(scroll, "Wick Multiplier", 1.0, 10.0, 2.0, 0.5,
                                             "Wick harus > X × body untuk dianggap rejection")
        self._wick_min_body = self._make_entry_row(scroll, "Min Body Ratio", "0.01")
        self._wick_min_ref = self._make_entry_row(scroll, "Min Body Reference", "0.00000001")

        make_section_header(scroll, "Market Structure")
        self._min_bars_ms = self._make_spinbox(scroll, "Min Bars untuk Market Structure", 10, 500, 50,
                                                "Minimum bar data untuk hitung HH/HL/LH/LL")
        self._adx_period = self._make_spinbox(scroll, "ADX Period (Kekuatan Trend)", 1, 50, 14)

    # ─── BTC CORRELATION ─────────────────────────────────────────────────────

    def _build_btc_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(scroll, "₿ Bitcoin King Effect")
        ctk.CTkLabel(scroll, text="Bot menggunakan tren Bitcoin sebagai filter makro untuk koin-koin lain.",
                     font=FONTS["body_sm"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 8))

        self._use_btc_corr = self._make_toggle(scroll, "Gunakan Korelasi BTC sebagai Filter Makro", True)
        self._btc_ema = self._make_spinbox(scroll, "BTC EMA Period", 1, 200, 50)
        self._corr_threshold = self._make_slider(scroll, "Correlation Threshold (High)", 0.1, 1.0, 0.8, 0.05,
                                                  "Nilai ≥ threshold = korelasi tinggi, analisis BTC ditampilkan ke AI")
        self._corr_period = self._make_spinbox(scroll, "Correlation Calculation Period (candle)", 5, 200, 30)

    # ─── WIDGET HELPERS ──────────────────────────────────────────────────────

    def _make_entry_row(self, parent, label: str, default: str = "", hint: str = ""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(row, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(side="left")
        var = ctk.StringVar(value=default)
        ctk.CTkEntry(row, textvariable=var, width=140, height=34, **entry_style()).pack(side="right")
        if hint:
            ctk.CTkLabel(parent, text=hint, font=FONTS["caption"],
                         text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 2))
        return var

    def _make_slider(self, parent, label: str, min_v, max_v, default, step, hint: str = ""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(row, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(side="left")
        steps = max(1, int((max_v - min_v) / step))
        var = ctk.DoubleVar(value=default)
        val_lbl = ctk.CTkLabel(row, text=str(default), font=FONTS["mono_sm"],
                                text_color=COLORS["accent_blue"], width=60)
        val_lbl.pack(side="right")

        def on_change(v, vl=val_lbl, s=step):
            rounded = round(float(v) / s) * s
            vl.configure(text=f"{rounded:.4f}" if s < 0.01 else f"{rounded:.3f}" if s < 0.1 else f"{rounded:.2f}" if s < 1 else f"{rounded:.0f}")

        ctk.CTkSlider(parent, from_=min_v, to=max_v, number_of_steps=steps,
                      variable=var, command=on_change, **slider_style()).pack(fill="x", pady=(2, 0))
        if hint:
            ctk.CTkLabel(parent, text=hint, font=FONTS["caption"],
                         text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 4))
        return var

    def _make_toggle(self, parent, label: str, default: bool = False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        var = ctk.BooleanVar(value=default)
        ctk.CTkSwitch(row, text=label, variable=var, font=FONTS["body_md"],
                      text_color=COLORS["text_primary"],
                      progress_color=COLORS["accent_green"],
                      button_color=COLORS["text_primary"],
                      fg_color=COLORS["bg_hover"]).pack(side="left")
        return var

    def _make_spinbox(self, parent, label: str, min_v, max_v, default, hint: str = ""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(row, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(side="left")
        var = ctk.StringVar(value=str(default))
        entry = ctk.CTkEntry(row, textvariable=var, width=90, height=34, **entry_style())
        entry.pack(side="right")

        def inc():
            try:
                v = float(var.get()) + 1
                if v <= max_v:
                    var.set(str(int(v) if float(v) == int(v) else v))
            except ValueError:
                pass
        def dec():
            try:
                v = float(var.get()) - 1
                if v >= min_v:
                    var.set(str(int(v) if float(v) == int(v) else v))
            except ValueError:
                pass

        ctk.CTkButton(row, text="▲", width=28, height=16, command=inc,
                      fg_color=COLORS["bg_hover"], hover_color=COLORS["border"],
                      text_color=COLORS["text_secondary"], corner_radius=4, font=FONTS["caption"]).pack(side="right", padx=(0, 2))
        ctk.CTkButton(row, text="▼", width=28, height=16, command=dec,
                      fg_color=COLORS["bg_hover"], hover_color=COLORS["border"],
                      text_color=COLORS["text_secondary"], corner_radius=4, font=FONTS["caption"]).pack(side="right", padx=(0, 2))

        if hint:
            ctk.CTkLabel(parent, text=hint, font=FONTS["caption"],
                         text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 2))
        return var

    def _make_dropdown(self, parent, label: str, options: list, default: str, hint: str = ""):
        ctk.CTkLabel(parent, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(8, 0))
        var = ctk.StringVar(value=default)
        ctk.CTkOptionMenu(parent, variable=var, values=options, height=34, anchor="w",
                          **dropdown_style()).pack(fill="x", pady=(2, 4))
        if hint:
            ctk.CTkLabel(parent, text=hint, font=FONTS["caption"],
                         text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 4))
        return var

    # ─── LOAD / SAVE ─────────────────────────────────────────────────────────

    def _load(self):
        from gui.config_manager import BotConfigManager
        cfg = BotConfigManager.load()

        # Size
        self._use_dynamic.set(cfg.get("USE_DYNAMIC_SIZE", False))
        self._size_seg.set("Dynamic (% Saldo)" if cfg.get("USE_DYNAMIC_SIZE") else "Static (USDT Tetap)")
        self._default_amount.set(str(cfg.get("DEFAULT_AMOUNT_USDT", 10)))
        self._risk_percent.set(cfg.get("RISK_PERCENT_PER_TRADE", 3))
        self._min_order.set(str(cfg.get("MIN_ORDER_USDT", 5)))
        self._default_leverage.set(str(cfg.get("DEFAULT_LEVERAGE", 10)))
        self._margin_type.set(cfg.get("DEFAULT_MARGIN_TYPE", "isolated"))
        self._max_pos_cat.set(str(cfg.get("MAX_POSITIONS_PER_CATEGORY", 5)))

        # SL/TP
        self._default_sl.set(cfg.get("DEFAULT_SL_PERCENT", 0.015))
        self._default_tp.set(cfg.get("DEFAULT_TP_PERCENT", 0.025))
        self._atr_period.set(str(cfg.get("ATR_PERIOD", 14)))
        self._atr_sl.set(cfg.get("ATR_MULTIPLIER_SL", 1.0))
        self._atr_tp.set(cfg.get("ATR_MULTIPLIER_TP1", 3.0))
        self._trap_sl.set(cfg.get("TRAP_SAFETY_SL", 2.0))
        self._order_retries.set(str(cfg.get("ORDER_SLTP_RETRIES", 3)))
        self._order_retry_delay.set(str(cfg.get("ORDER_SLTP_RETRY_DELAY", 2)))

        # Trailing
        self._enable_trailing.set(cfg.get("ENABLE_TRAILING_STOP", True))
        self._trailing_mode_seg.set("🏦 Native (Binance Server)" if cfg.get("USE_NATIVE_TRAILING", True) else "💻 Software (Bot Custom)")
        self._trailing_delay.set(str(cfg.get("TRAILING_ACTIVATION_DELAY", 60)))
        self._trailing_callback.set(cfg.get("TRAILING_CALLBACK_RATE", 0.001) * 100)
        self._trailing_activation.set(cfg.get("TRAILING_ACTIVATION_THRESHOLD", 0.80))
        self._trailing_min_profit.set(cfg.get("TRAILING_MIN_PROFIT_LOCK", 0.005))
        self._trailing_cooldown.set(str(cfg.get("TRAILING_SL_UPDATE_COOLDOWN", 3)))

        # Anti-FOMO
        self._cooldown_profit.set(str(cfg.get("COOLDOWN_IF_PROFIT", 3600)))
        self._cooldown_loss.set(str(cfg.get("COOLDOWN_IF_LOSS", 7200)))
        self._enable_market.set(cfg.get("ENABLE_MARKET_ORDERS", False))
        self._limit_expiry.set(str(cfg.get("LIMIT_ORDER_EXPIRY_SECONDS", 7200)))

        # Indicators
        self._rsi_period.set(str(cfg.get("RSI_PERIOD", 14)))
        self._rsi_oversold.set(cfg.get("RSI_OVERSOLD", 35))
        self._rsi_overbought.set(cfg.get("RSI_OVERBOUGHT", 65))
        self._rsi_deep_os.set(cfg.get("RSI_DEEP_OVERSOLD", 25))
        self._rsi_deep_ob.set(cfg.get("RSI_DEEP_OVERBOUGHT", 75))
        self._ema_fast.set(str(cfg.get("EMA_FAST", 7)))
        self._ema_slow.set(str(cfg.get("EMA_SLOW", 21)))
        self._ema_trend.set(str(cfg.get("EMA_TREND_MAJOR", 50)))
        self._stoch_len.set(str(cfg.get("STOCHRSI_LEN", 14)))
        self._stoch_k.set(str(cfg.get("STOCHRSI_K", 3)))
        self._stoch_d.set(str(cfg.get("STOCHRSI_D", 3)))
        self._macd_fast.set(str(cfg.get("MACD_FAST", 12)))
        self._macd_slow.set(str(cfg.get("MACD_SLOW", 26)))
        self._macd_signal.set(str(cfg.get("MACD_SIGNAL", 9)))
        self._bb_length.set(str(cfg.get("BB_LENGTH", 20)))
        self._bb_std.set(cfg.get("BB_STD", 2.0))
        self._vol_ma.set(str(cfg.get("VOL_MA_PERIOD", 20)))
        self._vol_spike.set(cfg.get("VOLUME_SPIKE_MULTIPLIER", 1.5))
        self._ob_range.set(cfg.get("ORDERBOOK_RANGE_PERCENT", 0.02))
        self._wick_mult.set(cfg.get("WICK_REJECTION_MULTIPLIER", 2.0))
        self._wick_min_body.set(str(cfg.get("WICK_REJECTION_MIN_BODY_RATIO", 0.01)))
        self._wick_min_ref.set(str(cfg.get("WICK_REJECTION_MIN_BODY_REF", 0.00000001)))
        self._min_bars_ms.set(str(cfg.get("MIN_BARS_MARKET_STRUCTURE", 50)))
        self._adx_period.set(str(cfg.get("ADX_PERIOD", 14)))

        # BTC Corr
        self._use_btc_corr.set(cfg.get("USE_BTC_CORRELATION", True))
        self._btc_ema.set(str(cfg.get("BTC_EMA_PERIOD", 50)))
        self._corr_threshold.set(cfg.get("CORRELATION_THRESHOLD_BTC", 0.8))
        self._corr_period.set(str(cfg.get("CORRELATION_PERIOD", 30)))

    def _save(self):
        from gui.config_manager import BotConfigManager

        data = {
            "USE_DYNAMIC_SIZE": self._use_dynamic.get(),
            "DEFAULT_AMOUNT_USDT": float(self._default_amount.get()),
            "RISK_PERCENT_PER_TRADE": round(self._risk_percent.get(), 1),
            "MIN_ORDER_USDT": float(self._min_order.get()),
            "DEFAULT_LEVERAGE": int(self._default_leverage.get()),
            "DEFAULT_MARGIN_TYPE": self._margin_type.get(),
            "MAX_POSITIONS_PER_CATEGORY": int(self._max_pos_cat.get()),
            "DEFAULT_SL_PERCENT": round(self._default_sl.get(), 4),
            "DEFAULT_TP_PERCENT": round(self._default_tp.get(), 4),
            "ATR_PERIOD": int(self._atr_period.get()),
            "ATR_MULTIPLIER_SL": round(self._atr_sl.get(), 2),
            "ATR_MULTIPLIER_TP1": round(self._atr_tp.get(), 2),
            "TRAP_SAFETY_SL": round(self._trap_sl.get(), 2),
            "ORDER_SLTP_RETRIES": int(self._order_retries.get()),
            "ORDER_SLTP_RETRY_DELAY": int(self._order_retry_delay.get()),
            "ENABLE_TRAILING_STOP": self._enable_trailing.get(),
            "USE_NATIVE_TRAILING": "Native" in self._trailing_mode_seg.get(),
            "TRAILING_ACTIVATION_DELAY": int(self._trailing_delay.get()),
            "TRAILING_CALLBACK_RATE": round(self._trailing_callback.get() / 100, 4),
            "TRAILING_ACTIVATION_THRESHOLD": round(self._trailing_activation.get(), 2),
            "TRAILING_MIN_PROFIT_LOCK": round(self._trailing_min_profit.get(), 4),
            "TRAILING_SL_UPDATE_COOLDOWN": int(self._trailing_cooldown.get()),
            "COOLDOWN_IF_PROFIT": int(self._cooldown_profit.get()),
            "COOLDOWN_IF_LOSS": int(self._cooldown_loss.get()),
            "ENABLE_MARKET_ORDERS": self._enable_market.get(),
            "LIMIT_ORDER_EXPIRY_SECONDS": int(self._limit_expiry.get()),
            "RSI_PERIOD": int(self._rsi_period.get()),
            "RSI_OVERSOLD": int(self._rsi_oversold.get()),
            "RSI_OVERBOUGHT": int(self._rsi_overbought.get()),
            "RSI_DEEP_OVERSOLD": int(self._rsi_deep_os.get()),
            "RSI_DEEP_OVERBOUGHT": int(self._rsi_deep_ob.get()),
            "EMA_FAST": int(self._ema_fast.get()),
            "EMA_SLOW": int(self._ema_slow.get()),
            "EMA_TREND_MAJOR": int(self._ema_trend.get()),
            "STOCHRSI_LEN": int(self._stoch_len.get()),
            "STOCHRSI_K": int(self._stoch_k.get()),
            "STOCHRSI_D": int(self._stoch_d.get()),
            "MACD_FAST": int(self._macd_fast.get()),
            "MACD_SLOW": int(self._macd_slow.get()),
            "MACD_SIGNAL": int(self._macd_signal.get()),
            "BB_LENGTH": int(self._bb_length.get()),
            "BB_STD": round(self._bb_std.get(), 1),
            "VOL_MA_PERIOD": int(self._vol_ma.get()),
            "VOLUME_SPIKE_MULTIPLIER": round(self._vol_spike.get(), 1),
            "ORDERBOOK_RANGE_PERCENT": round(self._ob_range.get(), 3),
            "WICK_REJECTION_MULTIPLIER": round(self._wick_mult.get(), 1),
            "WICK_REJECTION_MIN_BODY_RATIO": float(self._wick_min_body.get()),
            "WICK_REJECTION_MIN_BODY_REF": float(self._wick_min_ref.get()),
            "MIN_BARS_MARKET_STRUCTURE": int(self._min_bars_ms.get()),
            "ADX_PERIOD": int(self._adx_period.get()),
            "USE_BTC_CORRELATION": self._use_btc_corr.get(),
            "BTC_EMA_PERIOD": int(self._btc_ema.get()),
            "CORRELATION_THRESHOLD_BTC": round(self._corr_threshold.get(), 2),
            "CORRELATION_PERIOD": int(self._corr_period.get()),
        }

        ok = BotConfigManager.save(data)
        if ok:
            self._save_lbl.configure(text="✅ Tersimpan!", text_color=COLORS["accent_green"])
        else:
            self._save_lbl.configure(text="❌ Gagal!", text_color=COLORS["accent_red"])
        self.after(3000, lambda: self._save_lbl.configure(text=""))
