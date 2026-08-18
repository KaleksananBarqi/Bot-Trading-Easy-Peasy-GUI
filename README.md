# 🤖 Easy Peasy Trading Bot: AI Vision, Logic & Web GUI Control Center

<div align="center">
  <img width="1919" height="940" alt="Easy Peasy Trading Bot Web Dashboard" src="https://github.com/user-attachments/assets/0f9d5322-015d-45bc-8029-6ac10fbe55b0" />

  <br />
  <br />

  ![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
  ![Binance Futures](https://img.shields.io/badge/Binance-Futures-F0B90B?style=for-the-badge&logo=binance&logoColor=black)
  ![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
  ![AI Brain](https://img.shields.io/badge/Brain-Triple%20AI%20Core-8A2BE2?style=for-the-badge)
  ![Vision AI](https://img.shields.io/badge/Vision-Computer%20Vision-FF1493?style=for-the-badge)
  ![Architecture](https://img.shields.io/badge/Architecture-Facade%20%2B%20Orchestrator-00BFFF?style=for-the-badge)
  ![Tests](https://img.shields.io/badge/Tests-39%2B%20Files-32CD32?style=for-the-badge)
  ![Status](https://img.shields.io/badge/Status-Active%20v2.0-00E676?style=for-the-badge)
  ![License](https://img.shields.io/badge/License-PolyForm%20Noncommercial-5D6D7E?style=for-the-badge)
</div>

---

## 📖 Tentang Easy Peasy Trading Bot (Next-Gen AI & Web GUI Edition)

**Easy Peasy Trading Bot** adalah ekosistem trading otomatis **Hybrid Multi-AI** tercanggih untuk **Binance Futures**, kini dilengkapi dengan **Modern Web GUI Dashboard & Engine Control Center** berbasis **FastAPI + SSE (Server-Sent Events)** dan **Vanilla JS/HTML5/CSS3**.

Bot ini mengombinasikan keunggulan **Triple AI Core** (Logic Brain, Vision AI, dan NLP Sentiment), analisis kuantitatif multi-timeframe, deteksi mikrostruktur market (Wick Rejection & Market Structure Swing Points), serta manajemen risiko pro-grade dengan arsitektur **Facade + Orchestrator Pattern**.

> ⚡ **Kini Lebih Mudah Dikontrol!** Seluruh operasi bot—mulai dari *Ignition/Halt Engine*, pemantauan hardware (CPU/RAM/Uptime), live SSE log streaming, tracking posisi aktif, hingga kustomisasi parameter `gui_config.json` dan `.env`—dapat dilakukan langsung dari browser secara **real-time dengan sistem hot-reload** tanpa perlu menyentuh baris kode.

---

## 🧠 The Triple AI Core + Reasoning Engine

Bot beroperasi menggunakan 3 lapis kecerdasan buatan terdedikasi yang saling memvalidasi (*triple confluence*):

```
                     ┌────────────────────────────────────────┐
                     │          TRIPLE AI CORE ENGINE         │
                     └───────────────────┬────────────────────┘
                                         │
       ┌─────────────────────────────────┼─────────────────────────────────┐
       │                                 │                                 │
       ▼                                 ▼                                 ▼
┌──────────────┐                 ┌──────────────┐                 ┌──────────────┐
│  LOGIC AI    │                 │  VISION AI   │                 │ SENTIMENT AI │
│  (AI Brain)  │                 │(Visual Cortex)│                │  (NLP Text)  │
├──────────────┤                 ├──────────────┤                 ├──────────────┤
│ • Decision   │                 │ • Candlestick│                 │ • 18+ Global │
│   Maker      │                 │   Chart Scan │                 │   RSS Feeds  │
│ • Reasoning  │                 │ • Pattern    │                 │ • Fear &     │
│   Tokens     │                 │   Validation │                 │   Greed      │
│ • Dual Anti- │                 │ • MACD       │                 │ • Smart Money│
│   Bias Plan  │                 │   Divergence │                 │   vs Retail  │
└──────┬───────┘                 └──────┬───────┘                 └──────┬───────┘
       │                                │                                │
       └────────────────────────────────┼────────────────────────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │ ORCHESTRATOR & FACADE ENGINE│
                         │   (High-Probability Trade)  │
                         └─────────────────────────────┘
```

1. **Strategic Brain (Logic AI)**: Otak utama pengambil keputusan `BUY`, `SELL`, atau `WAIT` berdasarkan perpaduan data teknikal, on-chain, dan sentimen. Mendukung **AI Reasoning Tokens** (`none`, `minimal`, `low`, `medium`, `high`, `xhigh`) untuk proses berpikir mendalam dan transparan.
2. **Visual Cortex (Vision AI)**: Modul Computer Vision yang merender chart candlestick real-time dan menganalisis struktur pola visual (Flags, Reversals, Liquidity Grabs, MACD Divergence) lengkap dengan validasi kata kunci dan mekanisme *auto-retry*.
3. **Sentiment Analyst (Text AI)**: Memindai berita global dari 18+ RSS feeds, Fear & Greed Index, dan data On-Chain DeFiLlama secara berkala. Menganalisis perbedaan bias antara **Smart Money vs Retail Sentiment** dengan proteksi anti-prompt injection.

> 💡 **100% Provider-Agnostic & Configurable!** Anda bebas menggunakan model apapun dari **OpenRouter, DeepSeek, Anthropic Claude, OpenAI, Google Gemini, atau Local LLM** yang kompatibel dengan format OpenAI API.

---

## 🖥️ Local Web Dashboard & GUI Control Center

Antarmuka web interaktif lokal berbasis **FastAPI** dengan desain cyber-dark glassmorphism, responsive, dan ultra-ringan:

```
Akses Dashboard: http://localhost:8000
Jalankan Server: python run_web.py
```

<div align="center">
  <img width="1392" height="935" alt="Trading Bot Terminal & Sentiment Monitor" src="https://github.com/user-attachments/assets/fc443b1f-f7f8-4d60-b217-bf9886549505" />
</div>

### 🎛️ Fitur-Fitur Utama Web GUI:

| Halaman / Panel | Deskripsi & Fungsi Utama |
|---|---|
| **🕹️ Engine Control Center** | Tombol **START ENGINE** dan **HALT ENGINE** instan dengan eksekusi *background thread safe*. Dilengkapi indikator status live (*Online/Offline*) dan uptime. |
| **📈 System Hardware Monitor** | Menampilkan utilisasi **CPU (%)** dan konsumsi **RAM (MB Working Set)** secara real-time via API native kernel OS. |
| **⚡ Live Terminal Streamer** | Streaming log live dari `bot_trading.log` menggunakan teknologi **Server-Sent Events (SSE)**. Dilengkapi buffer 80 baris awal (32 KB), color coded syntax, search filter, auto-scroll, dan toggle pause. |
| **🌐 AI Market Sentiment Hub** | Menampilkan skor sentimen real-time (-100 s/d +100), Mood Market (Bullish/Bearish/Neutral), Market Phase, Fear & Greed Gauge, Stablecoin Inflow tracker, ringkasan berita terkini, dan grafik tren historis menggunakan **Chart.js**. |
| **📊 Live Trade Positions** | Tabel posisi aktif Binance Futures real-time: Symbol, Side (LONG/SHORT), Entry Price, Mark Price, Unrealized PnL (USDT & %), serta status Trailing Stop aktif. |
| **⚙️ Visual Config & Secrets Editor** | Editor konfigurasi visual untuk mengubah seluruh parameter `gui_config.json` dan `.env` (API Keys, Leverage, Risk %, Multi-Timeframes, Indikator, AI Models) dengan fitur **Hot-Reloading** tanpa perlu restart aplikasi. |

---

## 🚀 Fitur Trading Kuantitatif & Logika Eksekusi

### 1. ⚖️ Dual Execution Plan (Anti-Bias AI)
Bot tidak menebak-nebak arah market secara sepihak. Untuk setiap koin, bot secara paralel menghitung dua skenario:
* **Scenario A (Bullish Setup)**: Titik entry ideal, Stop Loss berbasis swing/ATR, dan Take Profit bertingkat.
* **Scenario B (Bearish Setup)**: Titik entry short, Stop Loss rejection, dan Take Profit target liquidity.
AI Brain kemudian memilih skenario dengan probabilitas matematika dan konfluensi teknikal tertinggi.

### 2. 🔄 Intelligent Dual-Mode Trailing Stop Loss

Bot menyediakan **dua mode trailing stop** yang fleksibel dan crash-proof:

```
   [ ENTRY: $100 ] ─────────────► [ TRIGGER: $108 (80% ke TP) ] ─────────────► [ TP: $110 ]
                                                │
                                                ▼
                                    Trailing Stop AKTIF!
                                    SL Baru: $107.89 (0.1% Trail)
                                    Min. Profit 0.5% Terkunci
```

* **Mode A: Native Trailing Stop (Binance API Server-Level)**:
  * Dieksekusi langsung di server exchange Binance (*Zero Latency*).
  * Auto-aktivasi 60 detik setelah order terisi pada 80% jarak menuju TP.
  * Tetap aktif dan aman menjaga posisi meskipun koneksi bot lokal terputus.
* **Mode B: Software Trailing Stop (WebSocket-Driven)**:
  * Dimonitor lokal via WebSocket feed berkecepatan tinggi.
  * SL otomatis dinaikkan/diturunkan mengikuti harga dengan callback rate 0.1% dan pengunci profit minimum 0.5%.
  * Dilengkapi interval cooldown 3 detik untuk mencegah throttling API.

### 3. 📏 Price Action Engine: Wick Rejection & Market Structure
* **Wick Rejection Analysis**: Mengukur proporsi wick vs candle body (> 2x body) untuk mendeteksi penolakan harga institusional dan area *absorption*.
* **Market Structure Detection (Scipy Powered)**: Mengidentifikasi swing points (Higher High, Higher Low, Lower High, Lower Low) menggunakan `scipy.signal.argrelextrema` minimal 50 bars untuk menentukan tren makro.
* **Classic Pivot Points**: Kalkulasi otomatis Support (S1/S2), Resistance (R1/R2), dan Pivot Point (P) sebagai level acuan likuiditas.

### 4. 📊 3-Layer Multi-Timeframe Confluence

| Layer | Timeframe | Peran Utama | Indikator Kunci |
|---|---|---|---|
| **TREND LAYER** | **4H / 1D** | Menentukan bias dan arah tren besar | EMA 50, ADX Trend Strength |
| **SETUP LAYER** | **1H / 4H** | Validasi momentum dan pembentukan pola | MACD Histogram, Bollinger Bands |
| **EXECUTION LAYER** | **15M / 1H** | Penentuan titik presisi entry & exit | RSI, StochRSI, ATR Dynamic SL/TP |

### 5. 📚 Multi-Strategy System & Strategy Library
Bot dilengkapi dengan 7 file blueprint strategi di `src/strategies/`:
1. `liquidity sweep strategy 15m.md` — Strategi pemburu stop run & liquidity sweep di level S1/R1.
2. `pullback sniper scalp.md` — Entry presisi saat harga pullback menuju EMA dinamis.
3. `Swing_Daily_Trend.md` — Penunggang tren swing berbasis konfirmasi candle harian.
4. `Swing_Reversal_Sniper.md` — Deteksi titik balik ekstrem dengan divergensi RSI/MACD.
5. `wr 85 persen 15m.md` — High win-rate scalp setup dengan konfirmasi multi-indikator.
6. `aval strategy.md` & `ai role.md` — Panduan operasional dan role-play instruksi AI.

### 6. 💰 Dynamic Position Sizing & Compounding
* **Static Mode**: Menggunakan jumlah USDT tetap per trade (contoh: $10/trade).
* **Dynamic Mode**: Menghitung ukuran posisi secara dinamis berdasarkan persentase saldo wallet (contoh: 3% compounding).
* **Safety Floor**: Batas minimum order $5 USDT sesuai regulasi Binance Futures.
* **Per-Coin Customization**: Override custom leverage, margin type (*isolated/cross*), dan allocation per koin.

### 7. 🛡️ Disiplin Trading & Proteksi Akun
* **Anti-FOMO & Revenge Trading Cooldown**: Jeda otomatis 1 jam setelah trade profit dan 2 jam setelah trade loss sebelum boleh membuka posisi baru pada koin yang sama.
* **Limit Order Expiry System**: Pembersihan otomatis limit order yang tidak tersentuh market dalam waktu 2 jam (`LIMIT_ORDER_EXPIRY_SECONDS = 7200`) untuk mencegah order menggantung (*zombie orders*).
* **Tracking Setup Batal & Expired**: Setiap order yang dicancel/expired dicatat terpisah tanpa merusak statistik win-rate jurnal.

### 8. 🐋 Whale Order Flow & Order Book Depth
* **Whale Transaction Detection**: Pelacakan transaksi besar (> $1,000,000 USDT) secara real-time via WebSocket Binance dengan window deduplikasi 5 detik.
* **Order Book Imbalance (2% Range)**: Menganalisis ketebalan bid vs ask volume untuk membaca tekanan beli/jual institusi.

---

## 🗄️ Automated Trade Journaling (MongoDB Powered)

Seluruh histori transaksi dicatat otomatis ke dalam database NoSQL **MongoDB** untuk analisis performa mendalam:

```json
{
  "symbol": "BTC/USDT",
  "side": "BUY",
  "entry_price": 64250.0,
  "exit_price": 66177.5,
  "pnl_usdt": 57.82,
  "roi_percent": 30.0,
  "exit_type": "TRAILING_STOP",
  "trailing_sl_final": 66177.5,
  "ai_rationale": "Liquidity sweep terkonfirmasi di Pivot S1 dengan divergensi bullish MACD 15M...",
  "technical_snapshot": {
    "rsi_15m": 31.4,
    "macd_hist": 0.0042,
    "ema_50": 63980.0
  },
  "timestamp_entry": "2026-08-18T14:30:00Z"
}
```

* **Snapshot Lengkap**: Menyimpan indikator teknikal saat entry, alasan keputusan AI (*AI Rationale*), prompt snapshot, fee, durasi trade, dan detail pergerakan Trailing Stop.
* **Script Utilitas Database**:
  * `python scripts/migrate_history.py` — Migrasi histori lama dari file CSV ke MongoDB.
  * `python scripts/migrate_exit_type.py` — Backfill kategori tipe exit pada data historis.
  * `python scripts/test_trailing_live.py` — Verifikasi live testing mekanisme Trailing Stop.

---

## 🏗️ Arsitektur Sistem & Rekayasa Perangkat Lunak

```text
Bot-Trading-Easy-Peasy-GUI/
 ├── run_web.py                        # 🚀 Entry Point Utama (FastAPI Server)
 ├── gui_config.json                   # ⚙️ File Konfigurasi GUI (Hot-Reload)
 ├── web_app/                          # 🌐 Local Web Dashboard Architecture
 │    ├── main.py                      # FastAPI Application Instance & Routes
 │    ├── api/                         # REST & SSE API Routers
 │    │    ├── bot_router.py           # Start/Stop Engine & SSE Log Streaming
 │    │    ├── config_router.py        # JSON Config & .env Secrets Handler
 │    │    ├── data_router.py          # Sentiment, Positions & System Metrics API
 │    │    └── bot_control_flag.py     # Thread Control Interrupter
 │    └── frontend/                    # UI Static Files
 │         ├── index.html              # Modern Cyber Dashboard UI
 │         ├── style.css               # Glassmorphism & Cyber Dark Theme
 │         └── app.js                  # SSE Client, Chart.js & State Manager
 ├── src/                              # 🧠 Core Algorithmic Trading Engine
 │    ├── config.py                    # Master Config dengan Prioritas GUI Override
 │    ├── main.py                      # Orchestrator Loop Utama
 │    ├── modules/                     # Modular Sub-engines
 │    │    ├── ai_brain.py             # Strategic Logic AI + Reasoning Tokens
 │    │    ├── pattern_recognizer.py   # Vision AI & Chart Analyzer
 │    │    ├── sentiment.py            # RSS News & NLP Sentiment Analyzer
 │    │    ├── market_data.py          # Data Fetcher & Thread-Safe Static Indicators
 │    │    ├── mongo_manager.py        # MongoDB Connection Manager & Validator
 │    │    ├── journal.py              # Trade Journal Recorder
 │    │    ├── onchain.py              # Whale Flow & Stablecoin Inflow
 │    │    ├── executor.py             # Facade Pattern Order Executor
 │    │    └── executor_impl/          # Facade Sub-components
 │    │         ├── tracker.py         # Position & State Tracking
 │    │         ├── positions.py       # Exchange Position Sync
 │    │         ├── risk.py            # Dynamic Position Sizing & Sizing Math
 │    │         ├── safety.py          # SL/TP & Dual Trailing Stop Engine
 │    │         ├── orders.py          # Limit/Market Execution Engine
 │    │         ├── sync.py            # Pending Order Cleaner & Sync
 │    │         └── order_callbacks.py # WebSocket Stream Event Handlers
 │    ├── strategies/                  # 📚 Dokumentasi 7 Strategi Trading
 │    └── utils/                       # Utility Functions
 │         ├── calc.py                 # Dual Scenario Math & Dynamic Risk
 │         ├── prompt_builder.py       # Dynamic Prompt Constructor + Jailbreak Guard
 │         ├── pnl_generator.py        # Aesthetic PnL Card Generator
 │         └── helper.py               # Logger & Async Helpers
 ├── tests/                            # 🧪 Automated Pytest Suite (39+ Files)
 └── scripts/                          # 🛠️ Migration & Testing Scripts
```

### Pola Desain Utama:
1. **Facade Pattern (`OrderExecutor`)**: Membungkus kompleksitas manajemen order, posisi, kalkulasi risiko, trailing stop, dan sinkronisasi ke dalam satu antarmuka bersih.
2. **Orchestrator Pattern (`main.py`)**: Memisahkan siklus hidup bot ke dalam fungsi-fungsi modular yang terisolasi (`_initialize_exchange`, `_run_periodic_updates`, `_check_trade_exclusions`, `_prepare_and_execute_trade`).
3. **Thread-Safe Static Calculations**: Indikator teknikal berat dijalankan sebagai fungsi statis murni yang aman dieksekusi secara asinkron via `asyncio.to_thread()`.
4. **Hot-Reload Config Management**: Membaca `gui_config.json` pada setiap iterasi atau perubahan GUI tanpa memerlukan restart proses Python.

---

## 🛠️ Panduan Instalasi & Penggunaan

### Persyaratan Sistem
* **Python 3.10 atau lebih baru** (Direkomendasikan Python 3.11/3.12)
* **MongoDB** (Lokal Community Server atau MongoDB Atlas gratis)
* **Akun Binance Futures** (API Key & Secret Key dengan izin Futures Trading)
* **AI Provider API Key** (OpenRouter, DeepSeek, OpenAI, atau Gemini)
* *(Opsional)* **CoinMarketCap API Key** untuk data koin & berita tambahan

---

### 💻 1. Panduan Instalasi di Windows

<details>
<summary>▶️ Klik untuk melihat langkah-langkah instalasi Windows</summary>

#### Langkah 1: Clone Repository & Buat Virtual Environment
Buka **PowerShell** atau **Command Prompt**:
```powershell
cd C:\Projek\Koding  # atau direktori pilihan Anda
git clone https://github.com/KaleksananBarqi/Bot-Trading-Easy-Peasy-GUI.git
cd Bot-Trading-Easy-Peasy-GUI

python -m venv venv
.\venv\Scripts\Activate
```

#### Langkah 2: Install Dependensi
```powershell
pip install -r requirements.txt
# atau menggunakan mode editable:
pip install -e .
```

#### Langkah 3: Setup Konfigurasi Environment (`.env`)
Salin file template `.env.example` menjadi `.env`:
```powershell
copy src\.env.example .env
```
Buka file `.env` dan isi credential Anda:
```ini
# Binance Credentials (Gunakan Testnet untuk latihan tanpa risiko)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
BINANCE_TESTNET_KEY=your_testnet_key_here
BINANCE_TESTNET_SECRET=your_testnet_secret_here

# AI Model Provider (OpenRouter / DeepSeek / OpenAI / Gemini)
AI_API_KEY=your_ai_api_key_here
AI_BASE_URL=https://openrouter.ai/api/v1

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=bot_trading_easy_peasy

# CoinMarketCap (Opsional)
CMC_API_KEY=your_cmc_api_key_here
```

#### Langkah 4: Jalankan Local Web Dashboard
```powershell
python run_web.py
```
Buka browser Anda dan akses:
👉 **`http://localhost:8000`**

Klik tombol **START ENGINE** di dashboard untuk memulai bot trading!

</details>

---

### 🍎 2. Panduan Instalasi di macOS

<details>
<summary>▶️ Klik untuk melihat langkah-langkah instalasi macOS</summary>

#### Langkah 1: Install Python & MongoDB via Homebrew
```bash
brew install python@3.11 mongodb-community@7.0
brew services start mongodb-community
```

#### Langkah 2: Clone Repository & Buat Virtual Environment
```bash
git clone https://github.com/KaleksananBarqi/Bot-Trading-Easy-Peasy-GUI.git
cd Bot-Trading-Easy-Peasy-GUI

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Langkah 3: Konfigurasi & Jalankan Dashboard
```bash
cp src/.env.example .env
# Edit .env dengan text editor favorit (nano, code, dsb)
nano .env

# Jalankan Web GUI:
python3 run_web.py
```
Buka browser di `http://localhost:8000`.

</details>

---

### 🐧 3. Panduan Instalasi di Linux Server (Ubuntu/Debian)

<details>
<summary>▶️ Klik untuk melihat langkah-langkah Linux Server</summary>

#### Langkah 1: Persiapan Environment
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip git mongodb -y
sudo systemctl enable --now mongodb
```

#### Langkah 2: Clone & Setup
```bash
cd /opt
sudo git clone https://github.com/KaleksananBarqi/Bot-Trading-Easy-Peasy-GUI.git
sudo chown -R $USER:$USER /opt/Bot-Trading-Easy-Peasy-GUI
cd /opt/Bot-Trading-Easy-Peasy-GUI

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp src/.env.example .env
nano .env
```

#### Langkah 3: Menjalankan Background Service (Systemd)
Buat service systemd agar web dashboard dan bot otomatis menyala saat server reboot:
```bash
sudo nano /etc/systemd/system/tradingbot.service
```

Isi dengan konfigurasi berikut:
```ini
[Unit]
Description=Easy Peasy Trading Bot Web GUI
After=network.target mongodb.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/Bot-Trading-Easy-Peasy-GUI
ExecStart=/opt/Bot-Trading-Easy-Peasy-GUI/venv/bin/python run_web.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Aktifkan service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tradingbot
sudo systemctl start tradingbot
sudo systemctl status tradingbot
```

</details>

---

## 🧪 Automated Testing Suite

Proyek ini memiliki cakupan pengujian otomatis dengan **39+ file test** menggunakan `pytest` untuk menjamin stabilitas trading:

```bash
# Menjalankan seluruh test suite
pytest tests/

# Menjalankan test spesifik untuk logika trailing stop
pytest tests/test_trailing_logic.py

# Menjalankan test verifikasi sistem keamanan & prompt injection
pytest tests/test_prompt_injection_prevention.py
```

### Cakupan Pengujian:
* ✅ **Trailing Stop Engine**: Logika Native Binance API & Software Mode.
* ✅ **Prompt Injection Prevention**: Pengamanan token & pembungkusan `<external_data>`.
* ✅ **Market Structure & Wick Rejection**: Algoritma swing detection & rasio wick.
* ✅ **Dynamic Position Sizing**: Perhitungan compounding vs static sizing.
* ✅ **AI Brain Decision & Fallback**: Validasi parsing output JSON AI dan reasoning tokens.
* ✅ **Order Execution & Lifecycle**: Limit Order Expiry, SL/TP retries, dan Trailing journal.
* ✅ **MongoDB Manager**: Validasi skema koneksi dan error recovery.

---

## 🔒 Standar Keamanan & Proteksi Sistem

| Layer Keamanan | Mekanisme Proteksi |
|---|---|
| **Prompt Injection Defense** | Seluruh data eksternal dari RSS feed dan berita dibungkus dalam tag `<external_data>` dengan instruksi isolasi ketat untuk mencegah serangan *indirect prompt injection*. |
| **XSS & Injection Protection** | Seluruh output log dan variabel pada Web Dashboard di-escape secara aman untuk mencegah injeksi skrip berbahaya di browser. |
| **Credentials Isolation** | Seluruh API Key dan rahasia akun tersimpan di `.env` (termasuk diabaikan oleh `.gitignore`) dan dimuat secara aman ke memory. |
| **Circuit Breakers & Cooldown** | Jeda paksa pasca-profit dan pasca-loss untuk melindungi modal dari *overtrading* dan volatilitas ekstrem. |

---

## 🤝 Kontribusi

Kami sangat menyambut kontribusi dari komunitas kuantitatif dan pengembang!
1. Fork repository ini.
2. Buat branch fitur baru (`git checkout -b feature/StrategiKeren`).
3. Commit perubahan Anda (`git commit -m 'Menambahkan strategi baru'`).
4. Push ke branch (`git push origin feature/StrategiKeren`).
5. Buat **Pull Request**.

---

## ⚠️ Disclaimer Finansial

> **PERINGATAN**: Trading instrumen crypto futures mengandung risiko kerugian finansial yang tinggi dan leverage dapat melipatgandakan kerugian maupun keuntungan. Bot ini disediakan untuk tujuan riset, edukasi, dan otomasi teknologi. Selalu gunakan akun **Testnet / Demo** sebelum menggunakan dana riil. Tidak ada jaminan keuntungan dan pengembang tidak bertanggung jawab atas segala kerugian yang timbul akibat penggunaan perangkat lunak ini.

---

<div align="center">
  <b>Dikembangkan dengan dedikasi & kecerdasan buatan oleh <a href="https://github.com/KaleksananBarqi">Kaleksanan Barqi Aji Massani</a></b>
  <br />
  <sub>Copyright © 2026 Easy Peasy Trading Bot Ecosystem. All rights reserved.</sub>
</div>