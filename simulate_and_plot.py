# simulate_and_plot.py
"""
Script d'intégration : simule des arrivées (Poisson) vers ServerModel,
collecte les métriques et sauve deux graphiques PNG :
 - plots/load_percent.png
 - plots/queue_length.png

Usage:
    python simulate_and_plot.py
"""
import os
import time
from dataclasses import dataclass
from collections import deque
from typing import Deque, List, Tuple

import numpy as np
import matplotlib.pyplot as plt

# importer le module server (assure-toi que server_model.py est dans le même dossier)
from server_model import ServerModel, RequestEvent

# ---------- CONFIGURATION ----------
DURATION_S = 60.0            # durée totale (s)
DT = 0.5                     # pas de simulation (s)
ATTACKERS = 5                # nb d'attaquants simulés
RATE_PER_ATTACKER = 4.0      # req/s par attaquant (moyenne)
MEAN_COST = 1.5              # coût moyen d'une requête (exponentielle)
SERVER_CAPACITY = 40.0       # capacité units/sec du serveur
OUTPUT_DIR = "plots"         # dossier de sortie pour les PNG
SEED = 12345                 # graine RNG pour reproductibilité
# -----------------------------------

def ensure_output_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def run_simulation_and_collect():
    steps = int(DURATION_S / DT)
    rng = np.random.default_rng(SEED)
    srv = ServerModel(processing_capacity_per_sec=SERVER_CAPACITY)

    times = []
    loads = []
    queue_lens = []

    for i in range(steps):
        t = i * DT
        # nombre d'arrivées Poisson pendant DT
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

def plot_and_save(times, loads, queue_lens, outdir):
    ensure_output_dir(outdir)

    # Plot charge (%)
    fig1, ax1 = plt.subplots(figsize=(10,4))
    ax1.plot(times, loads)
    ax1.set_xlabel("Temps (s)")
    ax1.set_ylabel("Charge serveur (%)")
    ax1.set_title("Charge serveur (%) vs Temps")
    ax1.grid(True)
    fig1.tight_layout()
    load_path = os.path.join(outdir, "load_percent.png")
    fig1.savefig(load_path, dpi=200)
    print(f"Saved {load_path}")

    # Plot longueur de file
    fig2, ax2 = plt.subplots(figsize=(10,4))
    ax2.plot(times, queue_lens)
    ax2.set_xlabel("Temps (s)")
    ax2.set_ylabel("Longueur de la file (nb requêtes)")
    ax2.set_title("Longueur de file vs Temps")
    ax2.grid(True)
    fig2.tight_layout()
    queue_path = os.path.join(outdir, "queue_length.png")
    fig2.savefig(queue_path, dpi=200)
    print(f"Saved {queue_path}")

def main():
    print("Running simulation...")
    times, loads, queue_lens = run_simulation_and_collect()
    print("Plotting and saving...")
    plot_and_save(times, loads, queue_lens, OUTPUT_DIR)
    print("Done.")

if __name__ == "__main__":
    main()
