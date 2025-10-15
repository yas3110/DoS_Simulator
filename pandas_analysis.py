# pandas_analysis.py
"""
Analyse rapide des résultats :
 - moyenne mobile de la charge
 - CDF des latences si disponible, sinon CDF de la longueur de file
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Dossier/scénario à analyser (modifie au besoin)
SCENARIO_DIR = "plots/baseline"
METRICS_CSV = os.path.join(SCENARIO_DIR, "metrics.csv")
LAT_CSV = os.path.join(SCENARIO_DIR, "latencies.csv")

WINDOW = 5   # taille de fenêtre pour moyenne mobile (en pas)

def moving_average_plot(df, outpath):
    df = df.copy()
    df["load_ma"] = df["load_percent"].rolling(WINDOW, min_periods=1).mean()

    plt.figure(figsize=(10,4))
    plt.plot(df["time_s"], df["load_percent"], label="charge (%)")
    plt.plot(df["time_s"], df["load_ma"], label=f"moyenne mobile ({WINDOW})", linestyle="--")
    plt.xlabel("Temps (s)")
    plt.ylabel("Charge serveur (%)")
    plt.title("Charge serveur (%) et moyenne mobile")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    print(f"Saved {outpath}")

def cdf_plot_from_series(series, xlabel, title, outpath):
    x = np.sort(series.values.astype(float))
    y = np.linspace(0, 1, len(x), endpoint=True)
    plt.figure(figsize=(10,4))
    plt.plot(x, y)
    plt.xlabel(xlabel)
    plt.ylabel("CDF")
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    print(f"Saved {outpath}")

def main():
    if not os.path.exists(METRICS_CSV):
        raise FileNotFoundError(f"Metrics file not found: {METRICS_CSV}")

    df = pd.read_csv(METRICS_CSV)
    # moyennes mobiles
    moving_average_plot(df, os.path.join(SCENARIO_DIR, "load_ma.png"))

    # CDF latence si dispo
    if os.path.exists(LAT_CSV):
        lat = pd.read_csv(LAT_CSV)["latency_s"]
        cdf_plot_from_series(lat, "Latence (s)", "CDF des latences", os.path.join(SCENARIO_DIR, "latency_cdf.png"))
    else:
        # sinon CDF de la longueur de file (proxy de congestion)
        cdf_plot_from_series(df["queue_len"], "Longueur de file", "CDF de la longueur de file", os.path.join(SCENARIO_DIR, "queue_cdf.png"))

if __name__ == "__main__":
    main()
