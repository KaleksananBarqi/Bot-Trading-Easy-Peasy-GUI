"""
page_ai.py — Halaman 3: AI Settings (Triple AI Core + RSS + Strategi).
"""

import customtkinter as ctk
from gui.theme import COLORS, FONTS, entry_style, button_primary, button_secondary, button_success, frame_section, make_section_header, switch_style, slider_style, dropdown_style


TIMEFRAME_OPTIONS = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "8h", "12h", "1d"]
INTERVAL_OPTIONS = ["30m", "1h", "2h", "4h", "8h", "12h", "24h"]
REASONING_OPTIONS = ["none", "minimal", "low", "medium", "high", "xhigh"]


class PageAI(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self._cfg = {}
        self._build()
        self._load()

    def _build(self):
        # Scrollable
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_primary"], scrollbar_button_color=COLORS["bg_hover"]
        )
        self._scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(self._scroll, text="🧠  AI & Strategi",
                     font=FONTS["title_xl"], text_color=COLORS["text_primary"], anchor="w").pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(self._scroll, text="Konfigurasi Triple AI Core: Logic AI, Vision AI, dan Sentiment Analyst.",
                     font=FONTS["body_md"], text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(0, 16))

        # Tabs
        self._tabview = ctk.CTkTabview(
            self._scroll, height=800,
            fg_color=COLORS["bg_secondary"],
            segmented_button_fg_color=COLORS["bg_tertiary"],
            segmented_button_selected_color=COLORS["accent_blue"],
            segmented_button_selected_hover_color="#4c94e8",
            segmented_button_unselected_color=COLORS["bg_tertiary"],
            segmented_button_unselected_hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"],
        )
        self._tabview.pack(fill="both", expand=True, pady=(0, 8))

        self._tabview.add("🧠 Logic AI")
        self._tabview.add("👁 Vision AI")
        self._tabview.add("📰 Sentiment AI")
        self._tabview.add("⏱ Timeframe")
        self._tabview.add("📡 RSS & Berita")

        self._build_logic_ai_tab(self._tabview.tab("🧠 Logic AI"))
        self._build_vision_ai_tab(self._tabview.tab("👁 Vision AI"))
        self._build_sentiment_tab(self._tabview.tab("📰 Sentiment AI"))
        self._build_timeframe_tab(self._tabview.tab("⏱ Timeframe"))
        self._build_rss_tab(self._tabview.tab("📡 RSS & Berita"))

        # Save
        sep = ctk.CTkFrame(self._scroll, height=1, fg_color=COLORS["border"])
        sep.pack(fill="x", pady=16)

        save_row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        save_row.pack(fill="x")
        self._save_lbl = ctk.CTkLabel(save_row, text="", font=FONTS["body_md"], text_color=COLORS["accent_green"])
        self._save_lbl.pack(side="left", padx=(0, 12))
        ctk.CTkButton(save_row, text="💾  Simpan Pengaturan AI", command=self._save, height=42, width=220,
                      **button_success()).pack(side="right")

    # ─── TAB: LOGIC AI ───────────────────────────────────────────────────────

    def _build_logic_ai_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(scroll, "Otak Utama (Decision Maker)")

        self._model_name = self._make_entry(scroll, "Model AI (Logic)", "arcee-ai/trinity-large-preview:free",
                                            "Model dari OpenRouter/DeepSeek/Anthropic/Gemini (OpenAI-compatible format)")
        self._temp = self._make_slider(scroll, "Temperature", 0.0, 1.0, 0.0, 0.1,
                                       "0.0 = Logis & Konsisten | 1.0 = Kreatif & Berhalusinasi")
        self._conf_threshold = self._make_slider(scroll, "Confidence Threshold (%)", 0, 100, 65, 1,
                                                  "Minimal keyakinan AI (%) untuk eksekusi trade")
        self._app_title = self._make_entry(scroll, "App Title (Header AI)", "Bot Trading Easy Peasy")
        self._app_url = self._make_entry(scroll, "App URL (Header AI)", "https://github.com/KaleksananBarqi/Bot-Trading-Easy-Peasy")

        make_section_header(scroll, "🧠 Reasoning Tokens")
        ctk.CTkLabel(scroll, text="Aktifkan fitur berpikir mendalam pada model yang mendukungnya.",
                     font=FONTS["body_sm"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 8))

        self._reasoning_enabled = self._make_toggle(scroll, "Enable Reasoning", False)
        self._reasoning_effort = self._make_dropdown(scroll, "Reasoning Effort", REASONING_OPTIONS, "medium")
        self._reasoning_exclude = self._make_toggle(scroll, "Exclude Reasoning dari Response (hanya proses internal)", False)
        self._reasoning_log = self._make_toggle(scroll, "Log Reasoning ke File", True)

    # ─── TAB: VISION AI ──────────────────────────────────────────────────────

    def _build_vision_ai_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(scroll, "👁 Visual Cortex — Chart Pattern Recognition")
        ctk.CTkLabel(scroll, text="AI Vision menganalisis chart candlestick dan mendeteksi divergence MACD.",
                     font=FONTS["body_sm"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 8))

        self._vision_enabled = self._make_toggle(scroll, "Enable Pattern Recognition (Vision AI)", True)
        self._vision_model = self._make_entry(scroll, "Vision Model", "meta-llama/llama-4-maverick",
                                               "Model dengan kemampuan vision/multimodal")
        self._vision_temp = self._make_slider(scroll, "Vision Temperature", 0.0, 1.0, 0.0, 0.1)
        self._vision_max_tokens = self._make_spinbox(scroll, "Vision Max Tokens", 50, 2000, 300,
                                                      "Naikkan jika output terpotong")
        self._pattern_max_retries = self._make_spinbox(scroll, "Max Retry jika Output Invalid", 0, 10, 2)
        self._pattern_min_length = self._make_spinbox(scroll, "Min Panjang Output (karakter)", 10, 500, 50)

    # ─── TAB: SENTIMENT AI ───────────────────────────────────────────────────

    def _build_sentiment_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(scroll, "📰 Sentiment Analyst — Analisa Berita & Market Mood")
        ctk.CTkLabel(scroll, text="Menganalisis Smart Money (Whale) vs Retail Sentiment, Fear & Greed, dan RSS feeds.",
                     font=FONTS["body_sm"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 8))

        self._sentiment_enabled = self._make_toggle(scroll, "Enable Sentiment Analysis", True)
        self._sentiment_model = self._make_entry(scroll, "Sentiment Model", "arcee-ai/trinity-large-preview:free",
                                                  "Gunakan model yang lebih murah/cepat untuk sentimen")
        self._sentiment_interval = self._make_dropdown(scroll, "Interval AI Analysis", INTERVAL_OPTIONS, "1h")
        self._sentiment_update = self._make_dropdown(scroll, "Interval Update Data Raw (RSS/OnChain)", INTERVAL_OPTIONS, "1h")

        make_section_header(scroll, "🐋 On-Chain & Whale Detection")
        ctk.CTkLabel(scroll, text="Data OnChain diambil dari DefiLlama.", font=FONTS["body_sm"],
                     text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 8))

        self._whale_threshold = self._make_spinbox(scroll, "Whale Threshold (USDT)", 100000, 100000000, 1000000, "Transaksi > nilai ini dianggap whale")
        self._whale_history = self._make_spinbox(scroll, "Whale History Limit", 1, 100, 10)
        self._whale_dedup = self._make_spinbox(scroll, "Whale Dedup Window (detik)", 1, 60, 5)
        self._stablecoin_threshold = self._make_slider(scroll, "Stablecoin Inflow Threshold (%)", 0.01, 1.0, 0.05, 0.01)

    # ─── TAB: TIMEFRAME ──────────────────────────────────────────────────────

    def _build_timeframe_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(scroll, "⏱ Multi-Timeframe Analysis")
        ctk.CTkLabel(scroll, text="Analisis 3-layer: Trend (4H) → Setup (1H) → Eksekusi (15M).",
                     font=FONTS["body_sm"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 8))

        # Info card
        info = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        info.pack(fill="x", pady=(0, 12))
        rows = [
            ("TREND", "4H", "Arah tren besar (EMA 50, ADX)"),
            ("SETUP", "1H", "Deteksi pola (MACD)"),
            ("EXECUTION", "15M", "Entry timing (RSI, StochRSI, BB, ATR)"),
        ]
        for layer, tf, desc in rows:
            r = ctk.CTkFrame(info, fg_color="transparent")
            r.pack(fill="x", padx=12, pady=4)
            ctk.CTkLabel(r, text=f"  {layer}", font=FONTS["label_bold"], text_color=COLORS["accent_blue"], width=90, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=tf, font=FONTS["mono_md"], text_color=COLORS["accent_yellow"], width=40, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=desc, font=FONTS["body_sm"], text_color=COLORS["text_secondary"], anchor="w").pack(side="left", padx=8)

        self._tf_trend = self._make_dropdown(scroll, "Timeframe TREND (Filter Global)", TIMEFRAME_OPTIONS, "4h")
        self._limit_trend = self._make_spinbox(scroll, "Candle Limit TREND", 50, 1000, 500)
        self._tf_setup = self._make_dropdown(scroll, "Timeframe SETUP (Pola Chart)", TIMEFRAME_OPTIONS, "1h")
        self._limit_setup = self._make_spinbox(scroll, "Candle Limit SETUP", 50, 500, 100)
        self._tf_exec = self._make_dropdown(scroll, "Timeframe EKSEKUSI (Entry Timing)", TIMEFRAME_OPTIONS, "15m")
        self._limit_exec = self._make_spinbox(scroll, "Candle Limit EKSEKUSI", 50, 500, 300)

    # ─── TAB: RSS & BERITA ───────────────────────────────────────────────────

    def _build_rss_tab(self, tab):
        self._rss_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self._rss_scroll.pack(fill="both", expand=True, padx=12, pady=12)

        make_section_header(self._rss_scroll, "📡 RSS Feed Sources")
        ctk.CTkLabel(self._rss_scroll, text="Sumber berita untuk analisis sentimen. Satu URL per baris.",
                     font=FONTS["body_sm"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 8))

        # RSS text area
        self._rss_text = ctk.CTkTextbox(
            self._rss_scroll, height=200, fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"], border_color=COLORS["border"],
            border_width=1, corner_radius=6, font=FONTS["mono_sm"],
        )
        self._rss_text.pack(fill="x", pady=(0, 12))

        make_section_header(self._rss_scroll, "📊 News Filtering Config")
        self._news_max_per_src = self._make_spinbox(self._rss_scroll, "Max Berita Per Sumber", 1, 100, 15)
        self._news_max_total = self._make_spinbox(self._rss_scroll, "Max Total Berita", 10, 1000, 200)
        self._news_retention = self._make_spinbox(self._rss_scroll, "Retention Limit", 1, 100, 15)
        self._news_max_age = self._make_spinbox(self._rss_scroll, "Max Usia Berita (jam)", 1, 168, 24)
        self._news_coin_min = self._make_spinbox(self._rss_scroll, "Min Berita Koin Spesifik", 1, 50, 6)
        self._news_btc_max = self._make_spinbox(self._rss_scroll, "Max Berita BTC", 1, 30, 5)
        self._news_macro_max = self._make_spinbox(self._rss_scroll, "Max Berita Makro", 1, 30, 4)

        make_section_header(self._rss_scroll, "🌍 Macro Keywords")
        ctk.CTkLabel(self._rss_scroll, text="Keywords untuk mendeteksi berita makroekonomi (pisah koma).",
                     font=FONTS["body_sm"], text_color=COLORS["text_muted"], anchor="w").pack(fill="x", pady=(0, 4))
        self._macro_keywords = ctk.CTkEntry(self._rss_scroll, height=34, **entry_style())
        self._macro_keywords.pack(fill="x", pady=(0, 12))

    # ─── WIDGET HELPERS ──────────────────────────────────────────────────────

    def _make_entry(self, parent, label: str, default: str = "", hint: str = ""):
        ctk.CTkLabel(parent, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(8, 0))
        if hint:
            ctk.CTkLabel(parent, text=hint, font=FONTS["caption"],
                         text_color=COLORS["text_muted"], anchor="w").pack(fill="x")
        var = ctk.StringVar(value=default)
        entry = ctk.CTkEntry(parent, textvariable=var, height=34, **entry_style())
        entry.pack(fill="x", pady=(2, 4))
        return var

    def _make_slider(self, parent, label: str, min_v, max_v, default, step, hint: str = ""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(row, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(side="left")
        val_lbl = ctk.CTkLabel(row, text=str(default), font=FONTS["mono_sm"],
                                text_color=COLORS["accent_blue"], width=50)
        val_lbl.pack(side="right")

        var = ctk.DoubleVar(value=default)
        steps = int((max_v - min_v) / step)

        def on_change(v, vl=val_lbl, s=step):
            rounded = round(float(v) / s) * s
            vl.configure(text=f"{rounded:.2f}")

        slider = ctk.CTkSlider(parent, from_=min_v, to=max_v, number_of_steps=steps,
                                variable=var, command=on_change, **slider_style())
        slider.pack(fill="x", pady=(2, 0))
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

    def _make_dropdown(self, parent, label: str, options: list, default: str):
        ctk.CTkLabel(parent, text=label, font=FONTS["label_bold"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x", pady=(8, 0))
        var = ctk.StringVar(value=default)
        ctk.CTkOptionMenu(parent, variable=var, values=options, height=34, anchor="w",
                          **dropdown_style()).pack(fill="x", pady=(2, 4))
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
                    var.set(str(int(v) if v == int(v) else v))
            except ValueError:
                pass
        def dec():
            try:
                v = float(var.get()) - 1
                if v >= min_v:
                    var.set(str(int(v) if v == int(v) else v))
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

    # ─── LOAD / SAVE ─────────────────────────────────────────────────────────

    def _load(self):
        from gui.config_manager import BotConfigManager
        cfg = BotConfigManager.load()

        self._model_name.set(cfg.get("AI_MODEL_NAME", "arcee-ai/trinity-large-preview:free"))
        self._temp.set(cfg.get("AI_TEMPERATURE", 0.0))
        self._conf_threshold.set(cfg.get("AI_CONFIDENCE_THRESHOLD", 65))
        self._app_title.set(cfg.get("AI_APP_TITLE", "Bot Trading Easy Peasy"))
        self._app_url.set(cfg.get("AI_APP_URL", ""))
        self._reasoning_enabled.set(cfg.get("AI_REASONING_ENABLED", False))
        self._reasoning_effort.set(cfg.get("AI_REASONING_EFFORT", "medium"))
        self._reasoning_exclude.set(cfg.get("AI_REASONING_EXCLUDE", False))
        self._reasoning_log.set(cfg.get("AI_LOG_REASONING", True))

        self._vision_enabled.set(cfg.get("USE_PATTERN_RECOGNITION", True))
        self._vision_model.set(cfg.get("AI_VISION_MODEL", "meta-llama/llama-4-maverick"))
        self._vision_temp.set(cfg.get("AI_VISION_TEMPERATURE", 0.0))
        self._vision_max_tokens.set(str(cfg.get("AI_VISION_MAX_TOKENS", 300)))
        self._pattern_max_retries.set(str(cfg.get("PATTERN_MAX_RETRIES", 2)))
        self._pattern_min_length.set(str(cfg.get("PATTERN_MIN_ANALYSIS_LENGTH", 50)))

        self._sentiment_enabled.set(cfg.get("ENABLE_SENTIMENT_ANALYSIS", True))
        self._sentiment_model.set(cfg.get("AI_SENTIMENT_MODEL", "arcee-ai/trinity-large-preview:free"))
        self._sentiment_interval.set(cfg.get("SENTIMENT_ANALYSIS_INTERVAL", "1h"))
        self._sentiment_update.set(cfg.get("SENTIMENT_UPDATE_INTERVAL", "1h"))
        self._whale_threshold.set(str(cfg.get("WHALE_THRESHOLD_USDT", 1000000)))
        self._whale_history.set(str(cfg.get("WHALE_HISTORY_LIMIT", 10)))
        self._whale_dedup.set(str(cfg.get("WHALE_DEDUP_WINDOW_SECONDS", 5)))
        self._stablecoin_threshold.set(cfg.get("STABLECOIN_INFLOW_THRESHOLD_PERCENT", 0.05))

        self._tf_trend.set(cfg.get("TIMEFRAME_TREND", "4h"))
        self._limit_trend.set(str(cfg.get("LIMIT_TREND", 500)))
        self._tf_setup.set(cfg.get("TIMEFRAME_SETUP", "1h"))
        self._limit_setup.set(str(cfg.get("LIMIT_SETUP", 100)))
        self._tf_exec.set(cfg.get("TIMEFRAME_EXEC", "15m"))
        self._limit_exec.set(str(cfg.get("LIMIT_EXEC", 300)))

        rss_urls = cfg.get("RSS_FEED_URLS", [])
        self._rss_text.delete("1.0", "end")
        self._rss_text.insert("1.0", "\n".join(rss_urls))

        self._news_max_per_src.set(str(cfg.get("NEWS_MAX_PER_SOURCE", 15)))
        self._news_max_total.set(str(cfg.get("NEWS_MAX_TOTAL", 200)))
        self._news_retention.set(str(cfg.get("NEWS_RETENTION_LIMIT", 15)))
        self._news_max_age.set(str(cfg.get("NEWS_MAX_AGE_HOURS", 24)))
        self._news_coin_min.set(str(cfg.get("NEWS_COIN_SPECIFIC_MIN", 6)))
        self._news_btc_max.set(str(cfg.get("NEWS_BTC_MAX", 5)))
        self._news_macro_max.set(str(cfg.get("NEWS_MACRO_MAX", 4)))

        macro_kw = cfg.get("MACRO_KEYWORDS", [])
        self._macro_keywords.delete(0, "end")
        self._macro_keywords.insert(0, ", ".join(macro_kw))

    def _save(self):
        from gui.config_manager import BotConfigManager

        rss_raw = self._rss_text.get("1.0", "end").strip()
        rss_urls = [u.strip() for u in rss_raw.splitlines() if u.strip()]

        macro_raw = self._macro_keywords.get().strip()
        macro_kw = [k.strip() for k in macro_raw.split(",") if k.strip()]

        data = {
            "AI_MODEL_NAME": self._model_name.get(),
            "AI_TEMPERATURE": round(self._temp.get(), 2),
            "AI_CONFIDENCE_THRESHOLD": int(float(self._conf_threshold.get())),
            "AI_APP_TITLE": self._app_title.get(),
            "AI_APP_URL": self._app_url.get(),
            "AI_REASONING_ENABLED": self._reasoning_enabled.get(),
            "AI_REASONING_EFFORT": self._reasoning_effort.get(),
            "AI_REASONING_EXCLUDE": self._reasoning_exclude.get(),
            "AI_LOG_REASONING": self._reasoning_log.get(),
            "USE_PATTERN_RECOGNITION": self._vision_enabled.get(),
            "AI_VISION_MODEL": self._vision_model.get(),
            "AI_VISION_TEMPERATURE": round(self._vision_temp.get(), 2),
            "AI_VISION_MAX_TOKENS": int(self._vision_max_tokens.get()),
            "PATTERN_MAX_RETRIES": int(self._pattern_max_retries.get()),
            "PATTERN_MIN_ANALYSIS_LENGTH": int(self._pattern_min_length.get()),
            "ENABLE_SENTIMENT_ANALYSIS": self._sentiment_enabled.get(),
            "AI_SENTIMENT_MODEL": self._sentiment_model.get(),
            "SENTIMENT_ANALYSIS_INTERVAL": self._sentiment_interval.get(),
            "SENTIMENT_UPDATE_INTERVAL": self._sentiment_update.get(),
            "WHALE_THRESHOLD_USDT": int(self._whale_threshold.get()),
            "WHALE_HISTORY_LIMIT": int(self._whale_history.get()),
            "WHALE_DEDUP_WINDOW_SECONDS": int(self._whale_dedup.get()),
            "STABLECOIN_INFLOW_THRESHOLD_PERCENT": round(self._stablecoin_threshold.get(), 4),
            "TIMEFRAME_TREND": self._tf_trend.get(),
            "LIMIT_TREND": int(self._limit_trend.get()),
            "TIMEFRAME_SETUP": self._tf_setup.get(),
            "LIMIT_SETUP": int(self._limit_setup.get()),
            "TIMEFRAME_EXEC": self._tf_exec.get(),
            "LIMIT_EXEC": int(self._limit_exec.get()),
            "RSS_FEED_URLS": rss_urls,
            "NEWS_MAX_PER_SOURCE": int(self._news_max_per_src.get()),
            "NEWS_MAX_TOTAL": int(self._news_max_total.get()),
            "NEWS_RETENTION_LIMIT": int(self._news_retention.get()),
            "NEWS_MAX_AGE_HOURS": int(self._news_max_age.get()),
            "NEWS_COIN_SPECIFIC_MIN": int(self._news_coin_min.get()),
            "NEWS_BTC_MAX": int(self._news_btc_max.get()),
            "NEWS_MACRO_MAX": int(self._news_macro_max.get()),
            "MACRO_KEYWORDS": macro_kw,
        }

        ok = BotConfigManager.save(data)
        if ok:
            self._save_lbl.configure(text="✅ Pengaturan AI tersimpan!", text_color=COLORS["accent_green"])
        else:
            self._save_lbl.configure(text="❌ Gagal menyimpan!", text_color=COLORS["accent_red"])
        self.after(3000, lambda: self._save_lbl.configure(text=""))
