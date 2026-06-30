# Panduan Instalasi — DoS Monitoring Lab

Panduan ini menjelaskan langkah-langkah setup project dari awal hingga siap dijalankan.

## 1. Prasyarat

Pastikan sudah terinstall di komputer kamu:

- **Python 3.9+** — cek dengan:
  ```bash
  python --version
  ```
- **pip** (biasanya sudah include bersama Python)
- **Git** (untuk clone repository)

## 2. Clone Repository

```bash
git clone https://github.com/rik0sec/dos-monitoring-lab.git
cd dos-monitoring-lab
```

## 3. Buat Virtual Environment (Direkomendasikan)

Virtual environment membantu mengisolasi dependency project supaya tidak bentrok dengan package Python lain di komputer kamu.

```bash
python -m venv venv
```

Aktifkan virtual environment:

- **Windows**
  ```bash
  venv\Scripts\activate
  ```
- **Linux / macOS**
  ```bash
  source venv/bin/activate
  ```

Jika berhasil, akan muncul `(venv)` di awal baris terminal.

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Ini akan menginstall:

| Package | Fungsi |
|---|---|
| `Flask` | Web framework untuk target website & dashboard |
| `psutil` | Membaca metrik CPU & RAM penggunaan server |
| `requests` | Mengirim HTTP request dari script attack simulator |
| `colorama` | Pewarnaan output di terminal |
| `locust` | Tools load testing |

## 5. Jalankan Target Website

```bash
python target/website.py
```

Jika berhasil, akan muncul output seperti ini:

```
=======================================================
  [LAB] DoS Target Website
  URL    : http://localhost:5004
  HANYA untuk edukasi di lingkungan lab lokal!
=======================================================
```

Buka browser dan akses **http://localhost:5004** untuk melihat dashboard monitoring real-time.

> 💡 Biarkan terminal ini tetap berjalan (jangan ditutup) selama melakukan testing/attack di langkah berikutnya.

## 6. Jalankan Attack Simulator

Buka terminal baru (tetap di folder project, jangan lupa aktifkan virtual environment lagi jika perlu), lalu jalankan:

```bash
python scripts/attack.py
```

Atau dengan parameter custom:

```bash
python scripts/attack.py --threads 20 --requests 100 --target fast
```

> ⚠️ Pastikan variabel `BASE_URL` di dalam `attack.py` sudah mengarah ke alamat target yang benar (default `http://localhost:5004` jika dijalankan di komputer yang sama).

## 7. Jalankan Load Testing dengan Locust (Opsional)

```bash
locust -f scripts/locustfile.py --host=http://localhost:5004
```

Setelah berjalan, buka **http://localhost:8089** di browser untuk mengatur jumlah simulated user, spawn rate, lalu klik **Start swarming** untuk memulai load test.

## 8. Troubleshooting

| Masalah | Solusi |
|---|---|
| `ModuleNotFoundError` | Pastikan virtual environment aktif dan `pip install -r requirements.txt` sudah dijalankan |
| Port `5004` sudah dipakai | Hentikan proses lain yang memakai port tersebut, atau ubah port di baris terakhir `website.py` (`app.run(..., port=5004)`) |
| `attack.py` gagal connect ke server | Pastikan `target/website.py` sudah berjalan terlebih dahulu dan `BASE_URL` di `attack.py` sudah sesuai |
| Dashboard tidak update | Pastikan tidak ada error di console browser (F12 → Console), dan endpoint `/stats` bisa diakses langsung di browser |

## 9. Langkah Selanjutnya

Setelah instalasi berhasil, lanjutkan ke [`testing.md`](testing.md) untuk panduan menjalankan skenario demo secara lengkap.