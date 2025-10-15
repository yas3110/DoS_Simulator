# batch_run.py
"""
Lance plusieurs scénarios de simulation et enregistre, pour chacun, dans plots/<scenario>/ :
 - metrics.csv           (time_s, load_percent, queue_len)
 - latencies.csv         (latency_s)  -> pour CDF de latence
 - load_percent.png
 - queue_length.png
 - latency_cdf.png
"""

import os
import time
import numpy as np
import matplotlib.pyplot as plt
from server_model import ServerModel, RequestEvent

# ---------- LISTE DE SCÉNARIOS (modifie librement) ----------
SCENARIOS = [
    {"name": "baseline", "duration_s": 60.0, "dt": 0.5, "attackers": 5, "rate": 4.0, "mean_cost": 1.5, "capacity": 40.0, "seed": 12345},
    {"name": "heavy_traffic", "duration_s": 60.0, "dt": 0.5, "attackers": 10, "rate": 5.0, "mean_cost": 1.5, "capacity": 40.0, "seed": 7},
    {"name": "weak_server", "duration_s": 60.0, "dt": 0.5, "attackers": 5, "rate": 4.0, "mean_cost": 1.5, "capacity": 20.0, "seed": 9},
]
# ------------------------------------------------------------

OUT_ROOT = "plots"

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def run_scenario(cfg: dict):
    """Exécute un scénario et renvoie (times, loads, qlens, latencies)."""
    steps = int(cfg["duration_s"] / cfg["dt"])
    rng = np.random.default_rng(cfg["seed"])
    srv = ServerModel(processing_capacity_per_sec=cfg["capacity"])

    times, loads, qlens = [], [], []

    for i in range(steps):
        t = i * cfg["dt"]
        lam = cfg["attackers"] * cfg["rate"] * cfg["dt"]
        arrivals = int(rng.poisson(lam=lam))
        for _ in range(arrivals):
            cost = float(rng.exponential(cfg["mean_cost"]))
            srv.enqueue(RequestEvent(timestamp=time.time(), cost=cost))

        stats = srv.step(dt=cfg["dt"])
        _, load = srv.get_state()
        times.append(t)
        loads.append(load)
        qlens.append(stats['queue_len'])

    return times, loads, qlens, list(srv.latencies)

def save_csv_metrics(times, loads, qlens, outdir):
    import csv
    ensure_dir(outdir)
    path = os.path.join(outdir, "metrics.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time_s", "load_percent", "queue_len"])
        for t, l, q in zip(times, loads, qlens):
            w.writerow([f"{t:.2f}", f"{l:.6f}", q])
    print(f"Saved {path}")

def save_csv_latencies(latencies, outdir):
    import csv
    ensure_dir(outdir)
    path = os.path.join(outdir, "latencies.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["latency_s"])
        for x in latencies:
            w.writerow([f"{x:.6f}"])
    print(f"Saved {path}")

def save_plots(times, loads, qlens, latencies, outdir):
    ensure_dir(outdir)

    # Charge (%)
    fig1, ax1 = plt.subplots(figsize=(10,4))
    ax1.plot(times, loads)
    ax1.set_xlabel("Temps (s)")
    ax1.set_ylabel("Charge serveur (%)")
    ax1.set_title("Charge serveur (%) vs Temps")
    ax1.grid(True)
    fig1.tight_layout()
    p1 = os.path.join(outdir, "load_percent.png")
    fig1.savefig(p1, dpi=200)
    print(f"Saved {p1}")

    # Longueur de file
    fig2, ax2 = plt.subplots(figsize=(10,4))
    ax2.plot(times, qlens)
    ax2.set_xlabel("Temps (s)")
    ax2.set_ylabel("Longueur de la file (nb requêtes)")
    ax2.set_title("Longueur de file vs Temps")
    ax2.grid(True)
    fig2.tight_layout()
    p2 = os.path.join(outdir, "queue_length.png")
    fig2.savefig(p2, dpi=200)
    print(f"Saved {p2}")

    # CDF des latences
    if latencies:
        x = np.sort(np.array(latencies))
        y = np.linspace(0, 1, len(x), endpoint=True)
        fig3, ax3 = plt.subplots(figsize=(10,4))
        ax3.plot(x, y)
        ax3.set_xlabel("Latence (s)")
        ax3.set_ylabel("CDF")
        ax3.set_title("CDF des latences")
        ax3.grid(True)
        fig3.tight_layout()
        p3 = os.path.join(outdir, "latency_cdf.png")
        fig3.savefig(p3, dpi=200)
        print(f"Saved {p3}")

def main():
    for cfg in SCENARIOS:
        name = cfg["name"]
        outdir = os.path.join(OUT_ROOT, name)
        print(f"\n=== Running scenario: {name} ===")
        times, loads, qlens, latencies = run_scenario(cfg)
        save_csv_metrics(times, loads, qlens, outdir)
        save_csv_latencies(latencies, outdir)
        save_plots(times, loads, qlens, latencies, outdir)
    print("\nAll scenarios completed.")

if __name__ == "__main__":
    main()
