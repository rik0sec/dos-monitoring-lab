# 🛡 DoS Monitoring Lab

Lab simulasi **Denial of Service (DoS) attack** beserta **dashboard monitoring real-time** untuk mendeteksi anomali traffic, dibangun menggunakan Python (Flask) dan Locust. Project ini dibuat sebagai bahan pembelajaran konsep keamanan jaringan — mulai dari simulasi serangan, deteksi traffic mencurigakan, hingga visualisasi metrik server secara langsung.

> ⚠️ **Disclaimer**: Project ini dibuat **khusus untuk tujuan edukasi** di lingkungan lab/lokal. Dilarang digunakan untuk menyerang server, jaringan, atau sistem milik pihak lain tanpa izin. Penulis tidak bertanggung jawab atas penyalahgunaan tools ini.

---

## 📌 Tentang Project

Project ini terdiri dari 3 komponen utama yang saling terhubung:

1. **Target Website** (`target/website.py`) — Web server Flask sederhana dengan dua jenis endpoint: endpoint ringan (`/fast`) dan endpoint berat (`/heavy`, mensimulasikan komputasi CPU-intensif & query lambat). Server ini menghitung jumlah request masuk dan menyajikan dashboard monitoring secara real-time.
2. **Attack Simulator** (`scripts/attack.py`) — Script yang mensimulasikan HTTP flood attack menggunakan multi-threading, mengukur baseline response time, lalu membandingkannya dengan response time saat server dibanjiri request.
3. **Load Tester** (`scripts/locustfile.py`) — Skenario load testing menggunakan [Locust](https://locust.io/) untuk mensimulasikan banyak user mengakses target secara bersamaan dengan pola traffic yang lebih realistis.

Dashboard monitoring menampilkan metrik secara real-time, antara lain:
- Total request & request per second (RPS)
- CPU & RAM usage server (via `psutil`)
- Threat level otomatis (`LOW` → `MEDIUM` → `HIGH` → `CRITICAL`) berdasarkan RPS
- Log request terbaru & log deteksi serangan
- Grafik tren traffic (Chart.js)

---

## 📸 Screenshot

| Dashboard — Normal Traffic | Dashboard — Under Attack |
|---|---|
| ![Normal](docs/screenshots/01-dashboard-normal.png) | ![Under Attack](docs/screenshots/05-dashboard-under-attack.png) |

> Lihat lebih banyak screenshot di folder [`docs/screenshots`](docs/screenshots).

---

## 🧱 Arsitektur Sistem

```
┌─────────────────┐        HTTP Flood        ┌──────────────────────┐
│  attack.py       │ ────────────────────────▶│                       │
│  (Multi-thread   │                           │   target/website.py  │
│   HTTP Flood)    │                           │   - /fast             │
└─────────────────┘                           │   - /heavy             │
                                               │   - /stats (dashboard) │
┌─────────────────┐        Load Test          │                       │
│  locustfile.py   │ ────────────────────────▶│                       │
│  (Locust load    │                           └──────────────────────┘
│   testing)        │                                     │
└─────────────────┘                                     ▼
                                              Real-time Monitoring
                                              Dashboard (Browser)
```

Penjelasan lebih detail ada di [`docs/architecture.md`](docs/architecture.md).

---

## 🛠 Tech Stack

| Komponen | Teknologi |
|---|---|
| Backend / Target Website | Python, Flask |
| Dashboard Frontend | HTML, Bootstrap 5, Chart.js |
| Monitoring Sistem | `psutil` (CPU & RAM usage) |
| Attack Simulator | Python (`requests`, `threading`, `colorama`) |
| Load Testing | [Locust](https://locust.io/) |

---

## 📂 Struktur Folder

```
dos-monitoring-lab/
├── docs/
│   ├── architecture.md       # Penjelasan arsitektur sistem
│   ├── installation.md       # Panduan instalasi & setup
│   ├── testing.md            # Panduan menjalankan testing/attack demo
│   ├── petunjuk.html
│   └── screenshots/          # Dokumentasi visual dashboard
├── scripts/
│   ├── attack.py             # Simulator HTTP flood attack
│   └── locustfile.py         # Skenario load testing (Locust)
├── target/
│   └── website.py            # Target website + dashboard monitoring
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🚀 Instalasi & Cara Menjalankan

### 1. Clone repository
```bash
git clone https://github.com/rik0sec/dos-monitoring-lab.git
cd dos-monitoring-lab
```

### 2. Buat virtual environment (opsional tapi direkomendasikan)
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Jalankan target website
```bash
python target/website.py
```
Dashboard monitoring bisa diakses di: `http://localhost:5004`

### 5. Jalankan simulasi attack (di terminal terpisah)
```bash
python scripts/attack.py --threads 20 --requests 100 --target fast
```

Parameter yang tersedia:
| Argumen | Default | Keterangan |
|---|---|---|
| `--threads` | 10 | Jumlah thread paralel |
| `--requests` | 100 | Total request yang dikirim (maks 20000) |
| `--target` | fast | Endpoint target: `fast` atau `heavy` |

### 6. (Opsional) Jalankan load testing dengan Locust
```bash
locust -f scripts/locustfile.py --host=http://localhost:5004
```
Lalu buka `http://localhost:8089` untuk mengatur jumlah user simulasi dan melihat hasil load test.

Panduan lebih lengkap tersedia di [`docs/installation.md`](docs/installation.md) dan [`docs/testing.md`](docs/testing.md).

---

## 🎯 Fitur Deteksi Otomatis

Server secara otomatis mengklasifikasikan kondisi traffic berdasarkan RPS (request per second):

| RPS | Threat Level | Status |
|---|---|---|
| < 15 | LOW | Normal |
| 15–50 | MEDIUM | High Traffic |
| 50–120 | HIGH | Possible DoS Activity |
| > 120 | CRITICAL | Critical DoS Attack Detected |

---

## 🔒 Rekomendasi Mitigasi DoS

Sebagai bagian dari pembelajaran, script `attack.py` juga menampilkan ringkasan teknik mitigasi DoS, di antaranya:
- Rate limiting (Nginx / Flask-Limiter)
- Connection limit per IP
- Timeout agresif untuk koneksi idle
- Load balancer & CDN/WAF (Cloudflare, AWS Shield)
- IP blocking otomatis (Fail2ban, iptables)
- CAPTCHA saat traffic tinggi

---

## 📚 Tujuan Pembelajaran

Project ini dibuat untuk memahami:
- Cara kerja serangan DoS pada level aplikasi (application layer)
- Cara membangun sistem monitoring & deteksi anomali traffic secara real-time
- Perbedaan dampak serangan pada endpoint ringan vs endpoint berat (CPU-intensive)
- Dasar-dasar load testing menggunakan Locust

---

## 👤 Author

**rik0sec** 
Project ini dibuat sebagai bagian dari pembelajaran mandiri di bidang Cyber Security.

---

## 📄 Lisensi

Project ini menggunakan lisensi [MIT](LICENSE).