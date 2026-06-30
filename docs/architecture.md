# Arsitektur Sistem — DoS Monitoring Lab

Dokumen ini menjelaskan arsitektur dan alur kerja sistem secara teknis.

## 1. Gambaran Umum

Sistem ini terdiri dari tiga komponen independen yang saling berinteraksi melalui HTTP, semuanya dijalankan di lingkungan lokal (localhost / jaringan lab):

```
┌─────────────────────┐                ┌──────────────────────────────┐
│   scripts/attack.py  │   HTTP Flood   │                                │
│   (Attack Simulator) │───────────────▶│                                │
└─────────────────────┘                │                                │
                                        │     target/website.py          │
┌─────────────────────┐   Load Test    │     (Flask Application)        │
│  scripts/locustfile  │───────────────▶│                                │
│   (Locust Workers)   │                │  ┌──────────────────────────┐ │
└─────────────────────┘                │  │  /fast   (light endpoint) │ │
                                        │  │  /heavy  (heavy endpoint) │ │
                                        │  │  /stats  (JSON metrics)   │ │
                                        │  │  /       (dashboard UI)   │ │
                                        │  └──────────────────────────┘ │
                                        └────────────────┬───────────────┘
                                                          │
                                                          ▼
                                          ┌───────────────────────────────┐
                                          │   Browser — Realtime Dashboard │
                                          │   (polling /stats tiap 1 detik)│
                                          └───────────────────────────────┘
```

## 2. Komponen

### 2.1 Target Website (`target/website.py`)

Web server berbasis **Flask**, berjalan di port `5004`, dengan tanggung jawab:

- **Menerima & mencatat request** — setiap request yang masuk dihitung melalui hook `before_request`, lalu dicatat ke dalam log (struktur `deque` dengan kapasitas terbatas, sehingga memory tetap stabil meskipun traffic tinggi).
- **Menyediakan endpoint uji**:
  - `GET /fast` — endpoint ringan, langsung mengembalikan response, digunakan untuk mensimulasikan traffic normal/HTTP flood biasa.
  - `GET /heavy` — endpoint berat, melakukan komputasi mencari bilangan prima (CPU-bound) ditambah `time.sleep()` (mensimulasikan I/O blocking seperti query database lambat). Parameter `delay` dan `factor` mengatur tingkat keberatan request.
- **Menghitung metrik secara real-time** di endpoint `GET /stats`:
  - Total request, RPS (request per second, dihitung dari selisih counter setiap polling)
  - CPU & RAM usage (via library `psutil`)
  - Threat level otomatis berdasarkan nilai RPS
  - Riwayat traffic (untuk grafik) dan riwayat deteksi serangan
- **Dashboard UI** disajikan langsung dari endpoint `/` (HTML inline, styling Bootstrap 5, grafik menggunakan Chart.js). Dashboard melakukan polling ke `/stats` setiap 1 detik (`setInterval`) untuk update data secara real-time tanpa reload halaman.

### 2.2 Attack Simulator (`scripts/attack.py`)

Script command-line yang mensimulasikan **HTTP flood attack**:

1. **Baseline measurement** — mengukur response time normal (sebelum serangan) dengan beberapa sample request.
2. **Flood phase** — membuat banyak thread (`threading`) yang masing-masing mengirim request secara terus-menerus ke endpoint target hingga jumlah request yang ditentukan (`--requests`) habis. Progress ditampilkan secara live di terminal.
3. **Analisis hasil** — membandingkan response time saat flood dengan baseline, menghitung throughput (req/detik), average/P95/max response time, lalu menyimpulkan tingkat degradasi performa server.
4. **Demo tambahan**: simulasi konsep *slow request attack* dengan membanjiri endpoint `/heavy`, serta menampilkan ringkasan teknik mitigasi DoS di akhir eksekusi.

Terdapat hard limit `MAX_REQUESTS` sebagai pengaman agar demo tidak menghasilkan beban berlebihan secara tidak sengaja.

### 2.3 Load Tester (`scripts/locustfile.py`)

Menggunakan framework **Locust** untuk mensimulasikan banyak *virtual user* yang mengakses target secara paralel dengan pola traffic yang lebih realistis (bertahap naik/turun, bukan flood instan). Cocok digunakan untuk menguji ketahanan server pada skenario load testing standar, sebagai pembanding terhadap skenario *attack* murni di `attack.py`.

## 3. Alur Deteksi Serangan

Logika deteksi berjalan di dalam endpoint `/stats` setiap kali dashboard melakukan polling:

1. Hitung `current_rps` = selisih total request dibanding polling sebelumnya.
2. Klasifikasikan `threat_level` berdasarkan ambang batas RPS:

   | RPS | Threat Level |
   |---|---|
   | < 15 | LOW |
   | 15 – 50 | MEDIUM |
   | 50 – 120 | HIGH |
   | > 120 | CRITICAL |

3. Jika `current_rps > 80` dan belum dalam status "attack active", sistem mencatat event baru ke `attack_history` dan menambah `attack_count`.
4. Status serangan dianggap berakhir jika tidak ada lonjakan RPS tinggi dalam 10 detik terakhir, lalu dicatat event "Attack Ended".

Pendekatan ini sederhana (threshold-based, bukan machine learning), sesuai dengan tujuan project sebagai lab pembelajaran konsep dasar deteksi anomali traffic.

## 4. Teknologi yang Digunakan

| Layer | Teknologi |
|---|---|
| Web Server / Backend | Python 3, Flask |
| Monitoring Sistem | psutil |
| Dashboard Frontend | HTML, Bootstrap 5, Chart.js (CDN) |
| Attack Simulation | Python (`requests`, `threading`, `queue`, `colorama`) |
| Load Testing | Locust |

## 5. Batasan & Catatan

- Sistem ini berjalan single-process dan menyimpan semua data di memory (tidak ada database persisten) — data akan hilang saat server di-restart.
- Deteksi serangan bersifat sederhana (threshold RPS), tidak membedakan IP/source individual, sehingga tidak cocok untuk produksi — murni untuk simulasi & pembelajaran.
- Seluruh komponen dirancang untuk dijalankan di jaringan lokal/lab, bukan untuk diarahkan ke server pihak ketiga.