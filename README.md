# 🤖 Easy Peasy Trading Bot: AI Vision & Logic Sniper

<div align="center">
<img width="1919" height="940" alt="Image" src="https://github.com/user-attachments/assets/0f9d5322-015d-45bc-8029-6ac10fbe55b0" />

<img width="1392" height="935" alt="Image" src="https://github.com/user-attachments/assets/fc443b1f-f7f8-4d60-b217-bf9886549505" />

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/c35c8b34-5762-4242-98ba-4907fe6a762f" />

  <br />
  
  ![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
  ![Binance](https://img.shields.io/badge/Binance-Futures-yellow?style=for-the-badge&logo=binance)
  ![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
  ![AI Brain](https://img.shields.io/badge/Brain-Configurable%20AI-blueviolet?style=for-the-badge)
  ![Vision AI](https://img.shields.io/badge/Vision-Configurable%20AI-ff69b4?style=for-the-badge)
  ![Architecture](https://img.shields.io/badge/Architecture-Facade%20%2B%20Orchestrator-informational?style=for-the-badge)
  ![Tests](https://img.shields.io/badge/Tests-39%2B%20Files-brightgreen?style=for-the-badge)
  ![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
  ![License](https://img.shields.io/badge/License-PolyForm%20Noncommercial-5D6D7E?style=for-the-badge)
</div>

---

## 📖 Tentang Easy Peasy Bot (Multi AI Edition)

**Easy Peasy Trading Bot** adalah sistem trading **Hybrid Multi-AI** tercanggih yang menggabungkan analisis logika, tekstual, dan kemampuan visual (computer vision) untuk menguasai market crypto.

Dibangun di atas arsitektur **Triple AI Core** dengan pola desain **Facade + Orchestrator**, bot ini tidak hanya menghitung angka, tapi juga "membaca" narasi berita dan "melihat" struktur market secara visual layaknya trader pro.

### 🧠 The Triple AI Core
1.  **Strategic Brain (Logic AI)**: Otak utama yang mengambil keputusan BUY/SELL/WAIT berdasarkan data teknikal, on-chain, dan sentimen secara holistik. Mendukung **Reasoning Tokens** untuk proses berpikir yang lebih mendalam dan transparan. Default: `Arcee Trinity Large`.
2.  **Visual Cortex (Vision AI)**: Modul Vision yang menganalisis chart candlestick real-time untuk mendeteksi pola murni (Flags, Pennants, Divergence) dan validasi struktur market. Default: `Llama-4-Maverick`.
3.  **Sentiment Analyst (Text AI)**: Melakukan scanning berita global, news RSS, dan Fear & Greed index untuk menentukan "Market Vibe" saat ini. Menganalisis divergensi **Smart Money vs Retail Sentiment**.

> 💡 **Semua model AI 100% configurable!** Ubah model kapan saja di `config.py` (`AI_MODEL_NAME`, `AI_VISION_MODEL`, `AI_SENTIMENT_MODEL`). Bebas pakai model dari **OpenRouter, DeepSeek, Anthropic, Gemini, atau provider manapun** yang compatible dengan OpenAI API format.

---

## 🚀 Fitur Utama & Keunggulan

### 1. ⚖️ Dual Execution Plan (Anti-Bias AI)
Bot tidak lagi menebak arah. Untuk setiap koin, bot menghitung dua skenario sekaligus:
*   **Scenario A (Long Case)**: Jika market bullish, di mana titik entry, SL, dan TP terbaik?
*   **Scenario B (Short Case)**: Jika market bearish, di mana titik entry, SL, dan TP terbaik?
AI akan memilih skenario yang memiliki probabilitas tertinggi berdasarkan data, menghilangkan bias subjektif.

### 2. 👁️ Vision AI Pattern Recognition
Integrasi Computer Vision yang canggih:
*   **Chart Rendering**: Otomatis mencetak chart teknikal lengkap dengan indikator.
*   **Validasi Pola**: AI Vision memvalidasi apakah ada pola reversal atau continuation.
*   **MACD Divergence Detection**: Deteksi visual divergensi harga vs momentum.
*   **Retry & Validation**: Output Vision AI divalidasi otomatis dengan keyword check dan panjang minimum, dengan retry otomatis jika output tidak valid.

### 3. 🛡️ Multi-Strategy AI System

Bot tidak hanya mengandalkan satu strategi! AI akan **memilih strategi terbaik** berdasarkan kondisi market saat itu:

| Strategi | Kondisi Optimal | Cara Kerja |
|----------|-----------------|------------|
| **LIQUIDITY_REVERSAL_MASTER** | Sweep rejection di Pivot S1/R1 | Entry saat harga menyapu liquidity zone lalu berbalik |
| **PULLBACK_CONTINUATION** | Trend kuat dengan pullback ke EMA | Entry saat pullback di uptrend atau bounce di downtrend |
| **BREAKDOWN_FOLLOW** | Breakout dengan volume tinggi | Follow momentum breakout dari level S1/R1 |

#### 🏆 Strategi Unggulan: Liquidity Hunt Specialist (PROVEN!)

Bot menggunakan strategi **Liquidity Hunt Specialist** yang fokus mencari titik balik di area "Stop Run" dan "Liquidity Grab" — zona di mana market maker sering memburu stop loss retail trader sebelum membalikkan arah.

**💡 Konsep Strategi**
1. **Deteksi Liquidity Zone**: Identifikasi area di mana banyak stop loss berkumpul
2. **Tunggu "Sweep"**: Sabar menunggu harga menyapu zona likuiditas
3. **Entry saat Reversal**: Masuk posisi setelah konfirmasi pembalikan arah
4. **Risk Terkontrol**: SL ketat di bawah swing low/high terdekat

#### 📚 Strategy Library (7 Strategi Terdokumentasi)
Bot dilengkapi dengan **7 file strategi** di `src/strategies/` yang mendokumentasikan berbagai pendekatan trading secara detail, mulai dari Swing Daily Trend, Reversal Sniper, hingga Pullback Scalp.

### 4. 🪙 Smart Per-Coin Configuration
Setiap koin dalam daftar pantau dapat dikustomisasi secara spesifik:
*   **Specific Keywords**: News filtering yang lebih akurat per aset.
*   **BTC Correlation Toggle**: Opsi untuk mengikuti atau mengabaikan tren Bitcoin.
*   **Custom Leverage & Margin**: Pengaturan risiko berbeda untuk setiap koin.

### 5. 📑 Dynamic Prompt Generation
Sistem prompt AI yang cerdas dan adaptif:
*   **Toggle-able Market Orders**: Jika `ENABLE_MARKET_ORDERS = False`, AI hanya akan diberikan opsi Limit Order (Liquidity Hunt) untuk meminimalkan slippage dan fee.
*   **Contextual Hiding**: Jika korelasi BTC rendah, data BTC akan disembunyikan agar AI fokus pada price action independen koin tersebut.
*   **🔒 Prompt Injection Prevention** *(NEW!)*: Data eksternal dari RSS feeds dibungkus dalam tag `<external_data>` yang aman, dengan instruksi keamanan eksplisit agar AI tidak mengikuti instruksi berbahaya yang mungkin disisipkan dalam berita.

### 6. 📢 Pro-Grade Notifications & Real-Time Dashboard
Notifikasi sistem dan Web GUI Dashboard yang mendetail:
*   **ROI Calculation**: Menampilkan persentase keuntungan/kerugian berdasarkan modal dan leverage.
*   **Real-time Updates**: Notifikasi saat order dipasang (Limit), saat terisi (Filled), dan saat menyentuh TP/SL.
*   **WebSocket-Driven**: Semua update data dan chart didorong secara instan oleh event WebSocket.

### 7. 📰 Smart News Filtering System
Sistem filter berita cerdas yang memastikan AI hanya menerima informasi relevan:

**Mekanisme Filtering:**
*   **Kategori Makro (Prioritas 1)**: Berita tentang Fed, inflasi, regulasi - maksimal 4 berita
*   **Kategori Koin Spesifik (Prioritas 2)**: Berita langsung tentang koin yang dianalisis - minimal 6 berita
*   **Kategori BTC Correlation (Prioritas 3)**: Berita Bitcoin untuk non-BTC coins - maksimal 5 berita

**Keunggulan:**
*   ✅ Menghindari "noise" dari berita tidak relevan
*   ✅ Mencegah AI berhalusinasi karena informasi campur aduk
*   ✅ Keyword customizable per koin di `config.py`
*   ✅ Sumber berita dari 18+ RSS feeds internasional & Indonesia

### 8. 🔄 Intelligent Trailing Stop Loss — *Dual Mode!*

Bot menyediakan **dua mode trailing stop** yang dapat dipilih via konfigurasi:

#### Mode A: Native Trailing Stop (Binance API) — *NEW!*
Trailing stop yang dieksekusi langsung oleh server Binance. Keunggulan:
*   **Zero Latency**: Stop dimonitor oleh server exchange, bukan bot lokal.
*   **Auto-Activation**: Dipasang otomatis 60 detik setelah order terisi.
*   **Activation Price**: Otomatis dihitung di 80% jarak dari entry menuju TP, agar trailing tidak aktif terlalu dini.
*   **Callback Rate**: Dapat dikonfigurasi antara 0.1% - 5.0%.
*   **Crash-Proof**: Tetap aktif meskipun bot mati.

#### Mode B: Software Trailing Stop (Custom)
Trailing stop custom yang lebih fleksibel, dimonitor via WebSocket:
*   Aktif saat harga bergerak **80%** menuju TP.
*   SL otomatis naik/turun mengikuti harga dengan jarak 0.1%.
*   Minimal profit 0.5% dikunci saat trailing aktif.
*   Cooldown update 3 detik untuk menghindari spam API.

**Ilustrasi (LONG Position, Software Mode):**
```
Entry: $100 | TP: $110 | SL Awal: $97
Harga naik ke $108 (80% ke TP) → Trailing Aktif!
- SL baru: $107.89 (0.1% di bawah harga tertinggi)
Harga naik ke $109 → SL naik ke $108.89
Harga turun ke $108.95 → SL tetap $108.89 (terkunci!)
Harga turun ke $108.89 → Posisi ditutup dengan profit ~8.9%
```

> 💡 **Pilih mode di `config.py`**: Set `USE_NATIVE_TRAILING = True` untuk mode Binance, atau `False` untuk mode Software.

### 9. 📏 Wick Rejection Analysis — *NEW!*
Sistem deteksi candle rejection menggunakan analisis proporsi body vs wick:
*   **Otomatis mendeteksi** candle dengan wick besar (> 2x body) sebagai sinyal rejection.
*   **Configurable Parameters**: Rasio minimum body, multiplier wick, dan zero-body fallback.
*   **Thread-Safe**: Kalkulasi dilakukan via static function, aman untuk concurrent processing.

### 10. 📐 Market Structure Detection — *NEW!*
Deteksi struktur market (Higher High, Higher Low, Lower High, Lower Low) secara otomatis:
*   Menggunakan **scipy.signal.argrelextrema** untuk menemukan swing points.
*   Deteksi trend berdasarkan pola HH/HL (Bullish) atau LH/LL (Bearish).
*   Minimum 50 bars data untuk akurasi optimal.
*   Hasilnya digunakan sebagai filter makro untuk keputusan AI.

### 11. 💰 Dynamic Position Sizing — *NEW!*
Sistem ukuran posisi yang adaptif:
*   **Static Mode**: Menggunakan jumlah USDT tetap per trade (default $10).
*   **Dynamic Mode (Compounding)**: Menggunakan persentase saldo wallet per trade (default 3%).
*   **Safety Floor**: Minimum order $5 (sesuai aturan Binance).
*   **Per-Coin Override**: Setiap koin bisa punya `amount` dan `leverage` sendiri.

### 12. 🧠 AI Reasoning Tokens — *NEW!*
Fitur reasoning yang memungkinkan AI menunjukkan proses berpikirnya:
*   **Configurable Effort**: 6 level: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`.
*   **Optional Display**: Reasoning bisa ditampilkan atau disembunyikan dari response.
*   **Logging**: Proses reasoning AI bisa dicatat ke log untuk debugging.

### 13. 📈 Multi-Timeframe Technical Analysis
Arsitektur analisis 3-layer untuk presisi maksimal:

| Layer | Timeframe | Fungsi | Indikator |
|-------|-----------|--------|------------|
| **TREND** | 4H | Arah tren besar | EMA 50, ADX |
| **SETUP** | 1H | Deteksi pola | MACD |
| **EXECUTION** | 15M | Entry timing | RSI, StochRSI, Bollinger Bands, ATR |

Dilengkapi dengan:
*   **Pivot Points** (Classic) untuk level S1/R1
*   **Wick Rejection** untuk konfirmasi reversal
*   **Market Structure** (HH/HL/LH/LL) untuk bias makro
*   **Global Trend Filter** (4H) sebagai filter tertinggi

### 14. ❄️ Cooldown Anti-FOMO/Revenge Trading
Mekanisme pendinginan otomatis setelah trade selesai:
*   **Setelah PROFIT**: Jeda 1 jam sebelum re-entry di koin yang sama
*   **Setelah LOSS**: Jeda 2 jam untuk mencegah revenge trading

### 15. ⏰ Limit Order Expiry System
Pembersihan otomatis limit order yang tidak terisi:
*   Order yang pending > 2 jam akan **auto-cancel**
*   Mencegah order "zombie" yang menggantung
*   Sinkronisasi real-time dengan exchange via WebSocket

### 16. 📓 Cancelled & Expired Trade Logging — *NEW!*
Pencatatan setup trading yang tidak tereksekusi:
*   **Cancelled Trades**: Order yang di-cancel sebelum terisi.
*   **Expired Trades**: Limit order yang kedaluwarsa setelah 2 jam.
*   **Dashboard Visibility**: Ditampilkan di dashboard untuk analisis frekuensi setup.
*   Tidak mempengaruhi kalkulasi win rate atau PnL.

### 17. 🐋 On-Chain Whale Detection
Deteksi transaksi whale secara real-time via WebSocket:
*   Threshold: > $1,000,000 USDT
*   Pelacakan per-koin (bukan global)
*   Integrasi dengan Stablecoin Inflow dari DeFiLlama
*   De-duplication window 5 detik untuk mencegah spam notifikasi

### 18. 📚 Order Book Depth Analysis
Analisis kedalaman order book untuk deteksi buying/selling pressure:
*   Range analisis: 2% dari current price
*   Kalkulasi bid/ask volume dalam USDT
*   Imbalance percentage untuk konfirmasi momentum

### 19. 📊 Real-Time Streamlit Dashboard — *Enhanced!*
Dashboard interaktif berbasis web untuk memantau performa trading secara real-time:
*   **Equity Curve**: Grafik pertumbuhan modal (floating & closed PnL).
*   **Win/Loss Distribution**: Pie chart rasio kemenangan.
*   **PnL Analysis**: Breakdown profit per koin dan per strategi.
*   **Activity Heatmap**: Visualisasi jam dan hari trading paling aktif.
*   **Trade History**: Tabel riwayat trade lengkap dengan filter.
*   **📅 PnL Calendar** *(NEW!)*: Kalender bulanan yang menampilkan PnL harian.
*   **📉 Drawdown Analysis** *(NEW!)*: Grafik drawdown dari equity peak.
*   **🔗 Correlation Analysis** *(NEW!)*: Visualisasi korelasi antar data trading (model AI, strategi, dll).
*   **🔄 Exit Type Analysis** *(NEW!)*: Distribusi exit type (TP/SL/Trailing), PnL per exit type, dan KPI perbandingan trailing vs non-trailing.
*   **🤖 Model Performance** *(NEW!)*: Analisis performa per model AI yang digunakan.
*   **📊 Distribution Analysis** *(NEW!)*: Visualisasi distribusi statistik hasil trading.
*   **🔍 Exit Type Filter** *(NEW!)*: Filter sidebar tambahan untuk memfilter berdasarkan jenis exit.
*   **Share PnL Card**: Terintegrasi langsung dengan detail teknikal per trade.
*   **🔒 XSS Protection**: Semua data yang dirender di HTML sudah di-sanitasi (escape) untuk mencegah stored XSS.

### 20. 🖼️ Aesthetic PnL Card Generator
Otomatis membuat kartu PnL (Profit & Loss) yang siap dipamerkan:
*   **Gradient Background**: Tampilan modern dengan warna dinamis (Hijau/Merah) sesuai hasil trade.
*   **QR Code Integration**: Tautan verifikasi atau referral link yang dapat discan.
*   **User Branding**: Foto profil dan username kustom yang diambil dari `pnl_config.json`.
*   **Watermark Support**: Opsi untuk menambahkan logo komunitas atau watermark transparan.

### 21. 📓 Automated Trade Journaling (MongoDB Powered)
Sistem pencatatan jurnal trading profesional yang kini didukung oleh **MongoDB**:
*   **Database Storage**: Menyimpan ribuan history trade tanpa lag menggunakan NoSQL Database.
*   **Data Lengkap**: Mencatat Entry, Exit, PnL, ROI, Fee, dan Durasi Trade.
*   **AI Rationale**: Menyimpan alasan entry dan prompt yang digunakan AI untuk evaluasi strategi.
*   **Technical Snapshot**: Menyimpan nilai indikator (RSI, MACD, EMA) saat entry untuk analisis post-trade.
*   **Config Snapshot**: Menyimpan konfigurasi yang digunakan (ATR Multiplier SL/TP, dll).
*   **Trailing Stop Data** *(NEW!)*: Menyimpan data trailing lengkap per trade — `exit_type`, `trailing_was_active`, `trailing_sl_final`, `trailing_high/low`, `activation_price`, dan `sl_price_initial`.
*   **Seamless Integration**: Terhubung langsung ke Dashboard Streamlit via koneksi database real-time.
*   **Auto-Validation**: MongoDB URI divalidasi otomatis saat startup, termasuk cek format `mongodb://` / `mongodb+srv://`.

---

## 🏗️ Arsitektur & Code Quality — *NEW!*

### Facade Pattern (Executor Module)
Module executor telah di-refactor menjadi arsitektur **Facade Pattern** untuk pemeliharaan yang lebih mudah:

```
OrderExecutor (Facade)
 ├── TradeTracker      → State tracking (posisi aktif, cache)
 ├── PositionManager   → Sinkronisasi posisi dengan exchange
 ├── RiskManager       → Kalkulasi risiko & dynamic sizing
 ├── SafetyManager     → SL/TP, Trailing Stop (Native & Software)
 ├── OrderManager      → Eksekusi order (Limit/Market)
 ├── OrderSyncManager  → Pembersihan pending orders
 └── OrderCallbacks    → WebSocket event handlers
```

Setiap komponen memiliki **Single Responsibility** dan dapat di-test secara independen, sementara `OrderExecutor` menjaga backward compatibility sebagai facade.

### Orchestrator Pattern (Main Loop)
File `main.py` telah di-refactor dari satu fungsi monolitik menjadi **orchestrator** yang mendelegasikan ke fungsi-fungsi helper:
*   `_initialize_exchange()` / `_initialize_modules()` — Setup
*   `_run_periodic_updates()` — Scheduled tasks
*   `_check_trade_exclusions()` — Filtering
*   `_apply_traditional_filters()` — Pre-AI filter
*   `_prepare_and_execute_trade()` — Execution

### Thread-Safe Static Functions
Semua kalkulasi teknikal berat di `market_data.py` telah di-extract menjadi **static functions** yang thread-safe:
*   `_calculate_pivot_points_static()`
*   `_calculate_market_structure_static()`
*   `_calculate_wick_rejection_static()`
*   `_calculate_tech_data_threaded()` — Dijalankan di thread terpisah via `asyncio.to_thread()`

### Named Tuples for Type Safety
Penggunaan `NamedTuple` (seperti `Candle`) untuk merepresentasikan data OHLCV, menggantikan list/tuple biasa demi kejelasan kode.

---

## 🛠️ Instalasi & Konfigurasi

### Persyaratan Sistem & API
*   **Python 3.10+** (Wajib)
*   **pip** dan **venv** (tools Python bawaan)
*   **Git** untuk clone repository
*   **MongoDB Database**: Connection URI (Localhost atau MongoDB Atlas)
*   **Akun Binance Futures**: API Key & Secret Key (Enable Futures Trading & Read)
*   **AI Provider API**: Key dari [OpenRouter](https://openrouter.ai/) atau DeepSeek
*   **CoinMarketCap API**: Key untuk analisis data fundamental & berita
*   *(Opsional)* **Binance Testnet**: API Key khusus jika ingin menggunakan uang monopoli

---

### 💻 Instalasi di Windows

<details>
<summary>Klik untuk melihat langkah-langkah Windows</summary>

**1. Install Python 3.10+**
- Download dari [python.org/downloads](https://www.python.org/downloads/)
- ⚠️ **PENTING**: Centang "Add Python to PATH" saat instalasi!
- Verifikasi: Buka PowerShell/CMD, ketik: `python --version`

**2. Clone Repository**
```powershell
cd C:\Projects  # atau folder pilihan kamu
git clone https://github.com/KaleksananBarqi/Bot-Trading-Easy-Peasy.git
cd Bot-Trading-Easy-Peasy
```

**3. Buat Virtual Environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

**4. Install Dependencies**
```powershell
pip install -e .
```

**5. Setup MongoDB & Konfigurasi**
- Install MongoDB Community Server atau siapkan cluster MongoDB Atlas.
- Buat file `.env` di root folder (gunakan `copy .env.example .env`)
- Isi `MONGO_URI` dan `MONGO_DB_NAME` di file `.env`.
- (Opsional) Jika punya data lama di CSV, jalankan migrasi:
  ```powershell
  python scripts/migrate_history.py
  ```
- Isi semua API Key yang diperlukan lainnya.
- Ubah pengaturan di `src/config.py` sesuai kebutuhan

**6. Jalankan Bot**
```powershell
python src/main.py

# Untuk menjalankan Dashboard:
streamlit run streamlit/dashboard.py
```

</details>

---

### 🍎 Instalasi di macOS

<details>
<summary>Klik untuk melihat langkah-langkah macOS</summary>

**1. Install Python 3.10+ via Homebrew**
```bash
# Install Homebrew (jika belum ada)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Verifikasi
python3 --version
```

**2. Clone Repository**
```bash
cd ~/Projects  # atau folder pilihan kamu
git clone https://github.com/KaleksananBarqi/Bot-Trading-Easy-Peasy.git
cd Bot-Trading-Easy-Peasy
```

**3. Buat Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**4. Install Dependencies**
```bash
pip install -e .
```

**5. Setup MongoDB & Konfigurasi**
- Install MongoDB Community Server via Homebrew:
  ```bash
  brew tap mongodb/brew
  brew install mongodb-community@7.0
  brew services start mongodb/brew/mongodb-community
  ```
- Buat file `.env` di root folder
- Isi `MONGO_URI` dan `MONGO_DB_NAME` di file `.env`.
- (Opsional) Migrasi data CSV lama:
  ```bash
  python scripts/migrate_history.py
  ```
- Isi semua API Key yang diperlukan
- Ubah pengaturan di `src/config.py` sesuai kebutuhan

**6. Jalankan Bot**
```bash
python src/main.py

# Untuk menjalankan Dashboard:
streamlit run streamlit/dashboard.py
```

</details>

---

### 🐧 Instalasi di Linux Server (Ubuntu/Debian)

<details>
<summary>Klik untuk melihat langkah-langkah Linux Server</summary>

**1. Update Sistem & Install Dependencies**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.10 python3.10-venv python3-pip git screen -y
```

**2. Clone Repository**
```bash
cd /opt  # atau /home/username
sudo git clone https://github.com/KaleksananBarqi/Bot-Trading-Easy-Peasy.git
sudo chown -R $USER:$USER Bot-Trading-Easy-Peasy
cd Bot-Trading-Easy-Peasy
```

**3. Buat Virtual Environment**
```bash
python3.10 -m venv venv
source venv/bin/activate
```

**4. Install Dependencies**
```bash
pip install --upgrade pip
pip install -e .
```

**5. Setup MongoDB & Konfigurasi**
- Install MongoDB Server:
  ```bash
  sudo apt install -y mongodb
  sudo systemctl start mongodb
  sudo systemctl enable mongodb
  ```
- Buat file `.env` dari template:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Isi `MONGO_URI` (biasanya `mongodb://localhost:27017/`) dan parameter lain.
- (Opsional) Migrasi data CSV:
  ```bash
  python scripts/migrate_history.py
  ```
- Simpan: Ctrl+X, Y, Enter

**6. Jalankan Bot (Background dengan Screen)**
```bash
# Jalankan dalam screen session
screen -S trading-bot
python src/main.py

# (Opsional) Jalankan Dashboard di session screen terpisah:
# screen -S dashboard
# streamlit run streamlit/dashboard.py

# Lepas dari session: Ctrl+A, D
# Kembali ke session: screen -r trading-bot
# Lihat daftar session: screen -ls
```

**7. (Opsional) Systemd Service untuk Auto-Start**
```bash
sudo nano /etc/systemd/system/trading-bot.service
```

Isi file service (sesuaikan user & path):
```ini
[Unit]
Description=Easy Peasy Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/Bot-Trading-Easy-Peasy
ExecStart=/opt/Bot-Trading-Easy-Peasy/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Aktifkan service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

</details>

---

## 📊 Struktur Proyek

```text
📂 Bot-Trading-Easy-Peasy/
 ├── 📂 src/                          # 🚀 Source Code Utama
 │    ├── 📂 modules/                 # Modul Logika Inti
 │    │    ├── 📂 executor_impl/      # [NEW] Komponen Executor (Facade)
 │    │    │    ├── 🔄 tracker.py            # Trade State Tracking
 │    │    │    ├── 📍 positions.py          # Position Management & Sync
 │    │    │    ├── ⚖️ risk.py               # Risk Calculations & Dynamic Sizing
 │    │    │    ├── 🛡️ safety.py             # SL/TP & Trailing Stop (Native + Software)
 │    │    │    ├── 📦 orders.py             # Order Execution (Limit/Market)
 │    │    │    ├── 🔁 sync.py              # Pending Order Synchronization
 │    │    │    └── 📡 order_callbacks.py    # WebSocket Order Event Handlers
 │    │    ├── 🧠 ai_brain.py               # Otak Utama AI (+ Reasoning Tokens)
 │    │    ├── ⚙️ executor.py               # [REFACTORED] Facade Pattern
 │    │    ├── 📓 journal.py                # [NEW] Trade Journaling
 │    │    ├── 🗄️ mongo_manager.py          # [NEW] MongoDB Connection Manager
 │    │    ├── 👁️ pattern_recognizer.py     # Vision AI Engine
 │    │    ├── 📊 market_data.py            # [ENHANCED] Data & Indicators + Static Functions
 │    │    ├── 🗞️ sentiment.py              # Analisis Berita & RSS
 │    │    └── 🐋 onchain.py               # Deteksi Whale & Stablecoin Inflow
 │    ├── 📂 strategies/              # [NEW] 📚 Dokumentasi Strategi (7 file)
 │    │    ├── 📋 liquidity sweep strategy 15m.md
 │    │    ├── 📋 pullback sniper scalp.md
 │    │    ├── 📋 Swing_Daily_Trend.md
 │    │    ├── 📋 Swing_Reversal_Sniper.md
 │    │    └── ... (dan lainnya)
 │    ├── 📂 utils/                   # Fungsi Pembantu
 │    │    ├── 🧮 calc.py                   # Kalkulasi Dual Scenarios & Risk
 │    │    ├── 📝 prompt_builder.py         # Konstruktor Prompt AI Dinamis
 │    │    ├── 🖼️ pnl_generator.py          # PnL Card Generator
 │    │    └── 🛠️ helper.py                 # Logger & Tele Utils
 │    ├── ⚙️ config.py                      # PUSAT KONFIGURASI (+ Auto-Validation)
 │    └── 🚀 main.py                        # [REFACTORED] Orchestrator Pattern
 ├── 📂 streamlit/                    # 📊 Dashboard Analytics Suite
 │    └── 📊 dashboard.py             # Dashboard (Calendar, Correlation, Drawdown)
 ├── 📂 scripts/                      # 🛠️ Script Utilitas
 │    ├── 📜 migrate_history.py       # Migrasi Data CSV ke MongoDB
 │    ├── 📜 migrate_exit_type.py     # [NEW] Backfill Exit Type pada Trade Historis
 │    └── 📜 test_trailing_live.py    # [NEW] Test Trailing Stop Secara Live
 ├── 📂 assets/                       # 🖼️ Aset Statis
 │    ├── 📂 fonts/                   # Font Kustom untuk PnL Card
 │    └── 📂 icons/                   # Ikon & Logo Exchange
 ├── 📂 tests/                        # 🧪 Automated Testing (39+ test files)
 └── 📦 pyproject.toml                # Manajemen Dependensi Modern
```

---

## 🧪 Automated Testing

Proyek ini dilengkapi dengan **39+ automated test files** untuk memastikan kualitas kode:

```bash
# Menjalankan semua tests
python -m pytest tests/

# Menjalankan test spesifik
python -m pytest tests/test_trailing_logic.py
```

**Test Coverage:**
*   ✅ Trailing Stop Logic
*   ✅ News Filtering System
*   ✅ Pattern Recognition Validation
*   ✅ Limit Order Expiry
*   ✅ Profit/Loss Calculation
*   ✅ Market Data Optimization
*   ✅ Benchmark Performance Tests
*   ✅ **Prompt Injection Prevention** *(NEW!)*
*   ✅ **Market Structure Detection** *(NEW!)*
*   ✅ **Wick Rejection Analysis** *(NEW!)*
*   ✅ **Dynamic Position Sizing** *(NEW!)*
*   ✅ **MongoDB URI Validation** *(NEW!)*
*   ✅ **AI Brain Decision Making** *(NEW!)*
*   ✅ **Notification Safety** *(NEW!)*
*   ✅ **Executor Refactor Verification** *(NEW!)*
*   ✅ **Trailing Journal Integration** *(NEW!)*

---

## 🔒 Keamanan

Bot ini mengimplementasikan beberapa lapisan keamanan:

| Layer | Deskripsi |
|-------|-----------|
| **Prompt Injection Prevention** | Data RSS/berita di-wrap dalam tag `<external_data>` dengan instruksi keamanan eksplisit |
| **XSS Protection** | Semua data di dashboard di-escape menggunakan `html.escape()` sebelum rendering |
| **Config Validation** | MongoDB URI divalidasi format dan scheme-nya saat startup |
| **Environment Variables** | Semua credential disimpan di `.env`, tidak pernah hardcoded |
| **Notification Safety** | Sanitasi teks pesan dan integrasi logger lokal/Web GUI |

---

## 🤝 Kontribusi
Kami terbuka untuk perbaikan strategi, optimasi AI, atau dokumentasi. Silakan ajukan **Pull Request** atau buka **Issue** jika menemukan bug.

---

## ⚠️ Disclaimer
**Trading crypto futures melibatkan risiko finansial yang besar.** Bot ini adalah alat bantu berbasis AI, bukan jaminan keuntungan. **AI bisa berhalusinasi** atau salah sinyal. Gunakan modal yang siap hilang dan aktifkan fitur risk management di `config.py`.

---
**Developed with ☕ & 🤖 by [Kaleksanan Barqi Aji Massani](https://github.com/KaleksananBarqi)**