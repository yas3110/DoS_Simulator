# simulate_and_plot.py
"""
Simule un trafic (arrivées Poisson) vers ServerModel, trace 2 graphiques
et exporte les métriques dans un CSV.

Fichiers produits (dossier plots/):
 - load_percent.png
 - queue_length.png
 - metrics.csv     (colonnes: time_s, load_percent, queue_len)

Usage:
    python simulate_and_plot.py
"""

import os
import csv
import time
import numpy as np
import matplotlib.pyplot as plt
from server_model import ServerModel, RequestEvent

# ---------- PARAMÈTRES MODIFIABLES ----------
DURATION_S = 60.0          # durée totale (secondes)
DT = 0.5                   # pas de simulation (secondes)
ATTACKERS = 5              # nb d'attaquants simulés
RATE_PER_ATTACKER = 4.0    # req/s par attaquant (moyenne)
MEAN_COST = 1.5            # coût moyen d'une requête (exponentielle)
SERVER_CAPACITY = 40.0     # capacité du serveur (unités de coût / s)
OUTPUT_DIR = "plots"       # dossier de sortie
SEED = 12345               # graine RNG (reproductible)
# --------------------------------------------

def ensure_output_dir(path: str) -> None:
    """Crée le dossier s'il n'existe pas."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def run_simulation():
    """Exécute la simulation et retourne listes (times, loads, queue_lens)."""
    steps = int(DURATION_S / DT)
    rng = np.random.default_rng(SEED)
    srv = ServerModel(processing_capacity_per_sec=SERVER_CAPACITY)

    times = []
    loads = []
    queue_lens = []

    for i in range(steps):
        t = i * DT
        # Nombre d'arrivées pendant l'intervalle DT (loi de Poisson).
        lam = ATTACKERS * RATE_PER_ATTACKER * DT
        arrivals = int(rng.poisson(lam=lam))
        for _ in range(arrivals):
            cost = float(rng.exponential(MEAN_COST))
            srv.enqueue(RequestEvent(timestamp=time.time(), cost=cost))

        stats = srv.step(dt=DT)
        _, load = srv.get_state()

        times.append(t)
        loads.append(load)
        queue_lens.append(stats['queue_len'])

    return times, loads, queue_lens

def save_csv(times, loads, queue_lens, outdir):
    """Enregistre les séries temporelles dans plots/metrics.csv."""
    ensure_output_dir(outdir)
    csv_path = os.path.join(outdir, "metrics.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["time_s", "load_percent", "queue_len"])
        for t, l, q in zip(times, loads, queue_lens):
            writer.writerow([f"{t:.2f}", f"{l:.3f}", q])
    print(f"Saved {csv_path}")

def save_plots(times, loads, queue_lens, outdir):
    """Trace et enregistre les graphiques PNG."""
    ensure_output_dir(outdir)

    # Graphique 1 : charge (%)
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(times, loads)
    ax1.set_xlabel("Temps (s)")
    ax1.set_ylabel("Charge serveur (%)")
    ax1.set_title("Charge serveur (%) vs Temps")
    ax1.grid(True)
    fig1.tight_layout()
    p1 = os.path.join(outdir, "load_percent.png")
    fig1.savefig(p1, dpi=200)
    print(f"Saved {p1}")

    # Graphique 2 : longueur de file
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(times, queue_lens)
    ax2.set_xlabel("Temps (s)")
    ax2.set_ylabel("Longueur de la file (nb requêtes)")
    ax2.set_title("Longueur de file vs Temps")
    ax2.grid(True)
    fig2.tight_layout()
    p2 = os.path.join(outdir, "queue_length.png")
    fig2.savefig(p2, dpi=200)
    print(f"Saved {p2}")

def main():
    print("Running simulation...")
    times, loads, queue_lens = run_simulation()
    print("Saving CSV and plots...")
    save_csv(times, loads, queue_lens, OUTPUT_DIR)
    save_plots(times, loads, queue_lens, OUTPUT_DIR)
    print("Done.")

if __name__ == "__main__":
    main()
