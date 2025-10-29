import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import simulate_and_plot as sim
import arpSpoofing as arps
import matplotlib
matplotlib.use("Agg")
# === Ajout : Variable globale de contrôle ===
arpspoof_running = False


class SimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation Serveur – Interface Graphique")
        self.root.geometry("1050x900")
        self.root.minsize(900, 650)

        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="⚙️ Paramètres de simulation", font=("Segoe UI", 12, "bold")).pack(pady=5)

        params_row = ttk.Frame(main_frame)
        params_row.pack(fill="x", pady=5)

        # DoS à gauche
        dos_frame = ttk.LabelFrame(params_row, text="Paramètres DoS")
        dos_frame.pack(side="left", padx=15, fill="y")
        self.params = {
            "Durée (s)": tk.DoubleVar(value=sim.DURATION_S),
            "Pas de temps (s)": tk.DoubleVar(value=sim.DT),
            "Nb attaquants": tk.IntVar(value=sim.ATTACKERS),
            "Taux req/s/attaquant": tk.DoubleVar(value=sim.RATE_PER_ATTACKER),
            "Coût moyen": tk.DoubleVar(value=sim.MEAN_COST),
            "Capacité serveur": tk.DoubleVar(value=sim.SERVER_CAPACITY),
        }
        for i, (k, v) in enumerate(self.params.items()):
            ttk.Label(dos_frame, text=k, width=16).grid(row=i, column=0, sticky="w", pady=2)
            ttk.Entry(dos_frame, textvariable=v, width=12).grid(row=i, column=1, pady=2, sticky="w")

        # MITM à droite
        mitm_frame = ttk.LabelFrame(params_row, text="Paramètres MITM")
        mitm_frame.pack(side="right", padx=15, fill="y")
        self.mitm_target = tk.StringVar()
        self.mitm_gateway = tk.StringVar()
        ttk.Label(mitm_frame, text="IP cible :", width=12).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(mitm_frame, textvariable=self.mitm_target, width=16).grid(row=0, column=1, pady=2, sticky="w")
        ttk.Label(mitm_frame, text="IP passerelle :", width=12).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(mitm_frame, textvariable=self.mitm_gateway, width=16).grid(row=1, column=1, pady=2, sticky="w")

        # Boutons juste en-dessous
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        ttk.Button(button_frame, text="▶ Lancer la simulation DoS", command=self.start_simulation_dos).pack(side="left", padx=5)
        ttk.Button(button_frame, text="▶ Lancer la simulation MITM", command=self.start_simulation_mitm).pack(side="right", padx=5)
        ttk.Button(button_frame, text="⏹ Arrêter MITM", command=self.stop_simulation_mitm).pack(side="right", padx=5)

        # Log
        self.log = tk.Text(main_frame, height=5, wrap="word", bg="#f4f4f4")
        self.log.pack(fill="x", padx=3, pady=3)
        self.log.insert("end", "Prêt à simuler.\n")

        # Graphiques
        fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 6))
        fig.subplots_adjust(hspace=0.5, top=1)
        fig.tight_layout(pad=6)
        self.canvas = FigureCanvasTkAgg(fig, master=main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

    def log_msg(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.root.update_idletasks()

    def start_simulation_dos(self):
        self.log.delete("1.0", "end")
        self.log_msg("Simulation DoS démarrée...")
        thread = threading.Thread(target=self.run_simulation)
        thread.start()

    def start_simulation_mitm(self):
        self.log.delete("1.0", "end")
        ip_cible = self.mitm_target.get()
        ip_passerelle = self.mitm_gateway.get()
        if not ip_cible or not ip_passerelle:
            self.log_msg("❌ Merci de renseigner les IPs cible et passerelle pour l'attaque MITM !")
            messagebox.showerror("Erreur", "Champs IP cible / passerelle requis pour MITM.")
            return
        self.log_msg(f"Simulation MITM lancée sur cible {ip_cible} via passerelle {ip_passerelle}...")
        thread = threading.Thread(target=self.run_mitm, args=(ip_cible, ip_passerelle))
        thread.start()

    def stop_simulation_mitm(self):
        global arpspoof_running
        self.log_msg("Tentative d'arrêt de l'attaque MITM...")
        arpspoof_running = False

    def run_simulation(self):
        try:
            sim.DURATION_S = self.params["Durée (s)"].get()
            sim.DT = self.params["Pas de temps (s)"].get()
            sim.ATTACKERS = self.params["Nb attaquants"].get()
            sim.RATE_PER_ATTACKER = self.params["Taux req/s/attaquant"].get()
            sim.MEAN_COST = self.params["Coût moyen"].get()
            sim.SERVER_CAPACITY = self.params["Capacité serveur"].get()
            self.log_msg("Calcul en cours...")
            times, loads, queue_lens = sim.run_simulation()
            sim.save_csv(times, loads, queue_lens, sim.OUTPUT_DIR)
            sim.save_plots(times, loads, queue_lens, sim.OUTPUT_DIR)
            self.update_plots(times, loads, queue_lens)
            self.log_msg("✅ Simulation terminée !")
            self.log_msg(f"Résultats enregistrés dans '{os.path.abspath(sim.OUTPUT_DIR)}'")
        except Exception as e:
            self.log_msg(f"❌ Erreur : {e}")
            messagebox.showerror("Erreur", str(e))

    def run_mitm(self, ip_cible, ip_passerelle):
        global arpspoof_running
        import time
        arpspoof_running = True
        try:
            packets = 0
            while arpspoof_running:
                arps.spoofer(ip_cible, ip_passerelle)
                arps.spoofer(ip_passerelle, ip_cible)
                self.log_msg(f"[MITM] Paquets envoyés: {packets}")
                packets += 2
                time.sleep(2)
            arps.restore(ip_cible, ip_passerelle)
            arps.restore(ip_passerelle, ip_cible)
            self.log_msg("✅ MITM arrêté, tables ARP restaurées !")
        except Exception as e:
            self.log_msg(f"❌ Erreur MITM : {e}")
            messagebox.showerror("Erreur MITM", str(e))

    def update_plots(self, times, loads, queue_lens):
        self.ax1.clear()
        self.ax2.clear()
        if times and loads:
            self.ax1.plot(times, loads, color="tab:blue")
        self.ax1.set_title("Charge du serveur (%)", pad=6)
        self.ax1.set_xlabel("Temps (s)")
        self.ax1.set_ylabel("Charge (%)")
        self.ax1.grid(True)
        if times and queue_lens:
            self.ax2.plot(times, queue_lens, color="tab:orange")
        self.ax2.set_title("Longueur de la file d’attente", pad=6)
        self.ax2.set_xlabel("Temps (s)")
        self.ax2.set_ylabel("Requêtes en file")
        self.ax2.grid(True)
        self.canvas.draw_idle()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationGUI(root)
    root.mainloop()