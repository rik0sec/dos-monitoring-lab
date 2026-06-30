# Panduan Testing & Demo — DoS Monitoring Lab

Dokumen ini menjelaskan skenario-skenario yang bisa dijalankan untuk mendemonstrasikan sistem monitoring dan deteksi DoS.

Pastikan kamu sudah mengikuti [`installation.md`](installation.md) dan `target/website.py` sudah berjalan di `http://localhost:5004` sebelum melanjutkan.

---

## Skenario 1 — Traffic Normal (Baseline)

Tujuan: melihat tampilan dashboard dalam kondisi normal sebelum ada serangan.

1. Jalankan `target/website.py`.
2. Buka dashboard di browser: `http://localhost:5004`.
3. Akses endpoint `/fast` beberapa kali secara manual (refresh browser atau buka di tab baru).
4. Perhatikan dashboard: `Status` akan menunjukkan **NORMAL**, `Threat Level` = **LOW**, banner berwarna hijau.

📸 Referensi: `docs/screenshots/01-dashboard-normal.png`

---

## Skenario 2 — HTTP Flood Attack (Endpoint Ringan)

Tujuan: mensimulasikan serangan flood pada endpoint `/fast` dan melihat reaksi sistem deteksi.

```bash
python scripts/attack.py --threads 20 --requests 200 --target fast
```

Yang perlu diamati:

- Di **terminal attack.py**: baseline response time, progress bar flood, lalu hasil analisis (throughput, avg/P95/max response time, persentase degradasi).
- Di **dashboard**: `RPS` naik drastis, `Threat Level` berubah dari LOW → MEDIUM → HIGH/CRITICAL, banner berubah warna (kuning/oranye/merah), serta muncul entry baru di tabel **Threat Detection Logs**.

📸 Referensi: `docs/screenshots/04-attack-terminal.png`, `docs/screenshots/05-dashboard-under-attack.png`

---

## Skenario 3 — Slow Request Attack (Endpoint Berat)

Tujuan: melihat dampak serangan pada endpoint yang sudah berat secara komputasi (`/heavy`), mensimulasikan kondisi seperti Slowloris/slow query attack.

Skenario ini otomatis dijalankan setelah Skenario 2 selesai (bagian `demo_slowloris_concept()` di `attack.py`), atau bisa diuji manual:

```bash
python scripts/attack.py --threads 10 --requests 50 --target heavy
```

Yang perlu diamati: response time pada endpoint `/heavy` jauh lebih tinggi dibanding `/fast` meski dengan jumlah request yang sama, karena setiap request menahan thread server lebih lama (delay + komputasi prima).

---

## Skenario 4 — Load Testing dengan Locust

Tujuan: menguji ketahanan server dengan pola traffic yang lebih realistis (bertahap, bukan flood instan).

```bash
locust -f scripts/locustfile.py --host=http://localhost:5004
```

1. Buka `http://localhost:8089`.
2. Isi jumlah **Number of users** (contoh: 50) dan **Spawn rate** (contoh: 5 user/detik).
3. Klik **Start swarming**.
4. Amati grafik response time & request per second di UI Locust, sambil membandingkan dengan dashboard monitoring di `http://localhost:5004`.
5. Klik **Stop** untuk menghentikan test.

📸 Referensi: `docs/screenshots/06-ab-test.png`

---

## Skenario 5 — Recovery / Setelah Serangan

Tujuan: melihat bagaimana sistem kembali normal setelah traffic flood berhenti.

1. Hentikan semua proses attack/load test.
2. Tunggu ±10 detik.
3. Perhatikan dashboard: `Status` kembali ke **NORMAL**, dan muncul entry **"Attack Ended"** di tabel Threat Detection Logs.

📸 Referensi: `docs/screenshots/07-dashboard-after.png`

---

## Ringkasan Parameter `attack.py`

| Argumen | Default | Keterangan |
|---|---|---|
| `--threads` | 10 | Jumlah thread paralel yang mengirim request |
| `--requests` | 100 | Total request yang dikirim (maksimum 20000, dibatasi `MAX_REQUESTS`) |
| `--target` | fast | Endpoint yang diserang: `fast` atau `heavy` |

## Catatan Etika & Keamanan

- Semua pengujian **hanya boleh dilakukan terhadap `target/website.py` milik sendiri**, di lingkungan lokal/lab.
- Jangan mengarahkan `attack.py` atau `locustfile.py` ke server, domain, atau alamat IP milik pihak lain tanpa izin eksplisit — hal tersebut dapat melanggar hukum.
- Project ini murni untuk pembelajaran konsep DoS dan sistem deteksi traffic anomali.