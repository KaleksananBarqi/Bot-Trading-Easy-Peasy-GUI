# Bot Trading Easy Peasy GUI

Aplikasi bot trading otomatis untuk **Binance Futures** berbasis Python yang dilengkapi dengan antarmuka **Web Dashboard lokal (FastAPI)**, analisis teknikal multi-timeframe, konfirmasi setup berbasis model AI (LLM & Vision), serta sistem manajemen risiko.

---

## 📌 Daftar Isi
- [Gambaran Umum](#-gambaran-umum)
- [Fitur Utama](#-fitur-utama)
- [Arsitektur Proyek](#-arsitektur-proyek)
- [Prasyarat Sistem](#-prasyarat-sistem)
- [Panduan Instalasi](#-panduan-instalasi)
- [Konfigurasi](#-konfigurasi)
- [Menjalankan Aplikasi](#-menjalankan-aplikasi)
- [Pengujian (Testing)](#-pengujian-testing)
- [Disclaimer](#-disclaimer)

---

## 📖 Gambaran Umum

Bot Trading Easy Peasy dirancang untuk mengotomatisasi proses analisis pasar, pengambilan keputusan, eksekusi order, hingga pencatatan jurnal trading pada Binance Futures. 

Alur kerja sistem secara garis besar:
1. **Pengumpulan Data Pasar**: Mengambil data candlestick multi-timeframe (Trend, Setup, Execution), order book, dan indikator teknikal secara real-time via CCXT/WebSockets.
2. **Kalkulasi & Analisis Teknikal**: Menghitung indikator (EMA, RSI, StochRSI, MACD, Bollinger Bands, ATR), deteksi Price Action (Wick Rejection, Pivot Points, Swing High/Low), serta sentimen pasar.
3. **Validasi AI (Opsional)**: Mengirimkan snapshot data teknikal dan visualisasi chart ke model AI (OpenRouter, DeepSeek, OpenAI, Gemini, dll.) untuk mengonfirmasi validitas setup sebelum order dikirim.
4. **Eksekusi & Manajemen Risiko**: Mengeksekusi order (Market/Limit), mengatur Stop Loss & Take Profit otomatis, mengaktifkan Trailing Stop, serta menerapkan cooldown pasca-transaksi.
5. **Monitoring & Web GUI**: Memberikan kontrol penuh melalui antarmuka web lokal untuk memantau status engine, live log streaming (SSE), open positions, dan mengubah konfigurasi secara instan (*hot-reload*).
6. **Jurnal Database**: Menyimpan histori transaksi dan analisis teknikal ke MongoDB.

---

## ⚡ Fitur Utama

### 1. Web Dashboard & Control Center
- **Engine Control**: Tombol Start dan Stop bot trading yang berjalan di background thread.
- **Live Log Streaming**: Log konsol real-time melalui *Server-Sent Events* (SSE) dengan fitur filter dan auto-scroll.
- **Live Position & Metrics**: Memantau posisi aktif, Unrealized PnL, harga entry/mark price, serta penggunaan CPU dan RAM.
- **Visual Config Editor**: Pengaturan parameter trading (`gui_config.json`) dan kredensial (`.env`) langsung dari browser dengan dukungan *hot-reload*.

### 2. Analisis Teknikal Multi-Timeframe
- **3-Layer Timeframe**:
  - *Trend Layer* (misal: 1D / 4H) untuk menentukan bias tren besar.
  - *Setup Layer* (misal: 4H / 1H) untuk mendeteksi pembentukan pola dan momentum.
  - *Execution Layer* (misal: 1H / 15M) untuk presisi titik entry dan exit.
- **Indikator Komprehensif**: EMA (Fast/Slow/Trend), RSI, Stochastic RSI, MACD, Bollinger Bands, ADX, dan ATR.
- **Price Action Engine**: Deteksi penolakan harga (*Wick Rejection*), Classic Pivot Points (P, S1, S2, R1, R2), dan titik swing struktur pasar (*Higher High, Lower Low*).

### 3. Konfirmasi AI (LLM & Vision)
- **Logika Keputusan**: Menganalisis skenario pergerakan harga dan memvalidasi probabilitas setup sebelum eksekusi.
- **Vision Chart Analysis**: Merender gambar chart candlestick dan menganalisis struktur pola secara visual.
- **Provider Fleksibel**: Kompatibel dengan API berstandar OpenAI (OpenRouter, DeepSeek, OpenAI, Google Gemini, Ollama/Local LLM).
- **Proteksi Prompt**: Sanitasi data eksternal untuk mencegah *prompt injection*.

### 4. Manajemen Risiko & Proteksi Modal
- **Position Sizing**: Pilihan ukuran posisi statis (USDT tetap) atau dinamis (% persentase modal).
- **Dual-Mode Trailing Stop**:
  - *Native Mode*: Menggunakan fitur Trailing Stop bawaan exchange Binance.
  - *Software Mode*: Monitoring lokal via WebSocket dengan kustomisasi callback rate dan profit lock.
- **Anti-Overtrading**: Cooldown otomatis setelah posisi ditutup (jeda waktu terpisah untuk kondisi profit dan loss).
- **Limit Order Expiry**: Pembatalan otomatis order limit yang belum tersentuh market setelah durasi tertentu.

### 5. Jurnal Trading Otomatis (MongoDB)
- Menyimpan detail trade: harga entry/exit, realisasi PnL, ROI %, durasi, alasan setup AI, dan snapshot indikator teknikal saat order dibuat.

---

## 📁 Arsitektur Proyek

```text
Bot-Trading-Easy-Peasy-GUI/
├── run_web.py                 # Entry point untuk menjalankan Web Dashboard lokal
├── gui_config.json            # File konfigurasi parameter trading (hot-reload)
├── requirements.txt           # Daftar dependensi Python
├── web_app/                   # Modul Web Dashboard (FastAPI)
│   ├── main.py                # Server FastAPI & mounting static files
│   ├── api/                   # Router API (kontrol bot, config, log stream, data)
│   └── frontend/              # Antarmuka web (HTML, CSS, JS)
├── src/                       # Core Trading Engine
│   ├── main.py                # Loop utama trading & orchestrator siklus hidup bot
│   ├── config.py              # Handler konfigurasi sistem
│   ├── modules/               # Modul fungsional bot
│   │   ├── ai_brain.py        # Integrasi LLM untuk analisis keputusan
│   │   ├── pattern_recognizer.py # Analisis chart visual (Vision AI)
│   │   ├── sentiment.py       # Analisis sentimen berita & pasar
│   │   ├── market_data.py     # Pengambilan data pasar & kalkulasi indikator
│   │   ├── executor.py        # Manajemen eksekusi order (Facade pattern)
│   │   ├── journal.py         # Pencatatan jurnal trading
│   │   ├── mongo_manager.py   # Koneksi & operasi database MongoDB
│   │   └── executor_impl/     # Komponen pendukung eksekutor order
│   ├── strategies/            # Dokumentasi referensi strategi trading
│   └── utils/                 # Fungsi bantuan (matematika, helper, prompt builder)
├── tests/                     # Unit test otomatis (Pytest)
└── scripts/                   # Skrip utilitas & migrasi data
```

---

## 💻 Prasyarat Sistem

Sebelum memulai, pastikan perangkat Anda telah memenuhi persyaratan berikut:
- **Python**: Versi `3.10` atau lebih baru (Disarankan `3.11` / `3.12`).
- **MongoDB**: MongoDB Community Server lokal atau MongoDB Atlas (opsional, untuk pencatatan jurnal).
- **Akun Binance**: Memiliki API Key & Secret Key dengan izin trading **Futures** (disarankan mencoba di Testnet terlebih dahulu).
- **Provider AI**: API Key untuk LLM (misal: OpenRouter, DeepSeek, OpenAI, atau Gemini).

---

## 🚀 Panduan Instalasi

### 1. Clone Repository & Buat Virtual Environment
```bash
# Clone repository
git clone https://github.com/KaleksananBarqi/Bot-Trading-Easy-Peasy-GUI.git
cd Bot-Trading-Easy-Peasy-GUI

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate
# Windows (CMD):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate
```

### 2. Install Dependensi
```bash
pip install -r requirements.txt
```

### 3. Setup File Konfigurasi `.env`
Salin template konfigurasi environment:
```bash
# Windows:
copy src\.env.example .env

# Linux / macOS:
cp src/.env.example .env
```

Buka file `.env` dengan text editor dan lengkapi konfigurasi akun Anda:
```ini
# Kredensial Binance (Trading Riil)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# Kredensial Binance (Testnet / Demo)
BINANCE_TESTNET_KEY=your_testnet_api_key
BINANCE_TESTNET_SECRET=your_testnet_secret_key

# Konfigurasi AI Provider (OpenRouter / DeepSeek / OpenAI / Gemini)
AI_API_KEY=your_ai_api_key
AI_BASE_URL=https://openrouter.ai/api/v1

# Konfigurasi Database MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=bot_trading_easy_peasy

# CoinMarketCap API (Opsional)
CMC_API_KEY=your_cmc_api_key
```

---

## ⚙️ Konfigurasi Trading (`gui_config.json`)

Parameter operasional trading dapat diatur melalui file `gui_config.json` atau langsung diedit melalui menu **Settings** di Web Dashboard tanpa perlu me-restart server:

| Parameter | Default | Keterangan |
|---|---|---|
| `PAKAI_DEMO` | `true` | `true` untuk Binance Futures Testnet, `false` untuk Live Trading. |
| `DEFAULT_AMOUNT_USDT` | `10` | Jumlah margin per posisi (jika `USE_DYNAMIC_SIZE` bernilai `false`). |
| `USE_DYNAMIC_SIZE` | `false` | Menghitung ukuran posisi berdasarkan persentase modal. |
| `RISK_PERCENT_PER_TRADE` | `3` | Persentase saldo modal per trade jika dynamic size aktif. |
| `DEFAULT_LEVERAGE` | `10` | Tingkat leverage default untuk setiap pair. |
| `DEFAULT_MARGIN_TYPE` | `"isolated"` | Tipe margin (`isolated` atau `cross`). |
| `ENABLE_TRAILING_STOP` | `false` | Mengaktifkan fitur trailing stop loss. |
| `USE_NATIVE_TRAILING` | `false` | `true` untuk trailing stop exchange Binance, `false` untuk software trailing. |
| `LIMIT_ORDER_EXPIRY_SECONDS` | `7200` | Batas waktu order limit dibatalkan jika belum terisi (2 jam). |
| `COOLDOWN_IF_PROFIT` | `3600` | Waktu jeda (detik) sebelum membuka posisi baru setelah profit. |
| `COOLDOWN_IF_LOSS` | `7200` | Waktu jeda (detik) sebelum membuka posisi baru setelah loss. |
| `TIMEFRAME_TREND` | `"1d"` | Timeframe acuan tren utama. |
| `TIMEFRAME_SETUP` | `"4h"` | Timeframe acuan pola/setup. |
| `TIMEFRAME_EXEC` | `"1h"` | Timeframe eksekusi entry/exit. |

---

## ▶️ Menjalankan Aplikasi

### Menjalankan Web Dashboard (Disarankan)
Jalankan server web lokal dengan perintah:
```bash
python run_web.py
```

Setelah server aktif, buka browser dan kunjungi:
👉 **`http://localhost:8000`**

Di dashboard web:
1. Pastikan status konfigurasi dan kredensial sudah benar.
2. Klik tombol **Start Engine** untuk memulai proses analisa dan trading bot.
3. Anda dapat memantau log pergerakan bot secara langsung pada panel **Live Terminal**.
4. Klik tombol **Halt Engine** jika ingin menghentikan operasional bot kapan saja.

---

## 🧪 Pengujian (Testing)

Proyek ini dilengkapi dengan unit test menggunakan `pytest`. Jalankan perintah berikut untuk memvalidasi fungsi sistem:

```bash
# Menjalankan seluruh pengujian
pytest tests/

# Menjalankan pengujian spesifik logika trailing stop
pytest tests/test_trailing_logic.py

# Menjalankan pengujian proteksi prompt injection
pytest tests/test_prompt_injection_prevention.py
```

---

## ⚠️ Disclaimer

> **PERINGATAN RISIKO**: Perdagangan instrumen derivatif kripto (Futures) memiliki tingkat risiko yang sangat tinggi dan dapat mengakibatkan hilangnya seluruh modal Anda karena efek leverage. Perangkat lunak ini disediakan semata-mata untuk tujuan penelitian, edukasi, dan otomatisasi teknis. Selalu lakukan pengujian menyeluruh pada akun **Testnet / Demo** sebelum mempertimbangkan penggunaan dana riil. Penulis dan kontributor tidak bertanggung jawab atas segala kerugian finansial yang terjadi akibat penggunaan aplikasi ini.

---

<div align="center">
  <sub>Lisensi: PolyForm Noncommercial | Dibuat untuk otomasi trading yang terstruktur dan terukur.</sub>
</div>