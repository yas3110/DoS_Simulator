import numpy as np
import time
import logging
from datetime import datetime
from typing import Literal
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Attacker:
    """
    Classe pour simuler une attaque par déni de service (DoS).
    
    Attributs:
        attack_mode (str): Mode d'attaque ('constant', 'poisson', 'burst')
        num_attackers (int): Nombre d'attaquants simultanés
        request_rate (float): Taux de requêtes par seconde
        duration (float): Durée de l'attaque en secondes
        burst_intensity (float): Intensité pour le mode burst
    """
    
    def __init__(
        self,
        attack_mode: Literal['constant', 'poisson', 'burst'] = 'constant',
        num_attackers: int = 10,
        request_rate: float = 100.0,
        duration: float = 60.0,
        burst_intensity: float = 5.0
    ):
        """
        Initialise un attaquant DoS.
        
        Args:
            attack_mode: Type d'attaque ('constant', 'poisson', 'burst')
            num_attackers: Nombre d'attaquants
            request_rate: Taux de requêtes par seconde (lambda pour Poisson)
            duration: Durée totale de l'attaque en secondes
            burst_intensity: Multiplicateur pour les bursts
        """
        self.attack_mode = attack_mode
        self.num_attackers = num_attackers
        self.request_rate = request_rate
        self.duration = duration
        self.burst_intensity = burst_intensity
        self.traffic_log = []
        self.is_attacking = False
        
        # Attributs pour les graphes
        self.fig = None
        self.ax = None
        self.line = None
        self.x_data = []
        self.y_data = []
        
        logging.info(f"Attacker initialisé: mode={attack_mode}, attackers={num_attackers}, rate={request_rate}")
    
    def generate_constant_traffic(self, elapsed_time: float) -> int:
        """
        Génère un trafic constant de requêtes.
        
        Args:
            elapsed_time: Temps écoulé depuis le début
            
        Returns:
            Nombre de requêtes pour cet instant
        """
        return int(self.request_rate * self.num_attackers)
    
    def generate_poisson_traffic(self, elapsed_time: float) -> int:
        """
        Génère un trafic selon une distribution de Poisson.
        La distribution de Poisson modélise le nombre d'événements
        se produisant dans un intervalle de temps fixe.
        
        Args:
            elapsed_time: Temps écoulé depuis le début
            
        Returns:
            Nombre de requêtes générées selon Poisson
        """
        # Lambda = taux moyen de requêtes par attaquant
        lam = self.request_rate * self.num_attackers
        return np.random.poisson(lam)
    
    def generate_burst_traffic(self, elapsed_time: float) -> int:
        """
        Génère un trafic en rafales (bursts).
        Alterne entre des périodes de forte activité et de calme.
        
        Args:
            elapsed_time: Temps écoulé depuis le début
            
        Returns:
            Nombre de requêtes pour cet instant
        """
        # Période de burst: 5 secondes
        burst_period = 5.0
        # Calculer si on est dans une phase de burst
        cycle_position = elapsed_time % (burst_period * 2)
        
        if cycle_position < burst_period:
            # Phase de burst intense
            return int(self.request_rate * self.num_attackers * self.burst_intensity)
        else:
            # Phase calme
            return int(self.request_rate * self.num_attackers * 0.2)
    
    def generate_traffic(self, elapsed_time: float) -> int:
        """
        Génère le trafic selon le mode d'attaque configuré.
        
        Args:
            elapsed_time: Temps écoulé depuis le début de l'attaque
            
        Returns:
            Nombre de requêtes générées
        """
        if self.attack_mode == 'constant':
            return self.generate_constant_traffic(elapsed_time)
        elif self.attack_mode == 'poisson':
            return self.generate_poisson_traffic(elapsed_time)
        elif self.attack_mode == 'burst':
            return self.generate_burst_traffic(elapsed_time)
        else:
            raise ValueError(f"Mode d'attaque non reconnu: {self.attack_mode}")
    
    def start_attack(self, callback=None):
        """
        Démarre la simulation d'attaque.
        
        Args:
            callback: Fonction optionnelle appelée à chaque itération
                     avec (elapsed_time, num_requests)
        """
        self.is_attacking = True
        self.traffic_log = []
        start_time = time.time()
        
        logging.info(f"Début de l'attaque {self.attack_mode} - Durée: {self.duration}s")
        
        try:
            while self.is_attacking:
                elapsed_time = time.time() - start_time
                
                # Vérifier si la durée est atteinte
                if elapsed_time >= self.duration:
                    break
                
                # Générer le trafic
                num_requests = self.generate_traffic(elapsed_time)
                
                # Logger l'activité
                log_entry = {
                    'timestamp': datetime.now(),
                    'elapsed_time': elapsed_time,
                    'num_requests': num_requests,
                    'attack_mode': self.attack_mode
                }
                
                self.traffic_log.append(log_entry)
                
                # Callback optionnel pour interface graphique
                if callback:
                    callback(elapsed_time, num_requests)
                
                # Pause courte pour ne pas surcharger (100ms)
                time.sleep(0.1)
                
        except Exception as e:
            logging.error(f"Erreur durant l'attaque: {e}")
        finally:
            self.is_attacking = False
            logging.info("Attaque terminée")
    
    def stop_attack(self):
        """Arrête l'attaque en cours."""
        self.is_attacking = False
        logging.info("Arrêt de l'attaque demandé")
    
    def get_traffic_log(self):
        """
        Retourne le log du trafic généré.
        
        Returns:
            Liste de dictionnaires contenant les logs
        """
        return self.traffic_log
    
    def export_traffic_log(self, filename: str = 'data/traffic_log.csv'):
        """
        Exporte le log du trafic dans un fichier CSV.
        
        Args:
            filename: Chemin du fichier de sortie
        """
        import pandas as pd
        
        if not self.traffic_log:
            logging.warning("Aucun log à exporter")
            return
        
        df = pd.DataFrame(self.traffic_log)
        df.to_csv(filename, index=False)
        logging.info(f"Log exporté vers {filename}")
    
    def get_statistics(self) -> dict:
        """
        Calcule les statistiques du trafic généré.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        if not self.traffic_log:
            return {}
        
        requests = [entry['num_requests'] for entry in self.traffic_log]
        
        stats = {
            'total_requests': sum(requests),
            'avg_requests_per_second': np.mean(requests),
            'max_requests': max(requests),
            'min_requests': min(requests),
            'std_requests': np.std(requests),
            'duration': self.traffic_log[-1]['elapsed_time']
        }
        
        return stats
    
    # ========== MÉTHODES DE GÉNÉRATION DE GRAPHES ==========
    
    def plot_traffic_static(self, filename: str = None, show: bool = True):
        """
        Génère un graphe statique du trafic après l'attaque.
        
        Args:
            filename: Chemin pour sauvegarder le graphe (optionnel)
            show: Afficher le graphe (True par défaut)
        """
        if not self.traffic_log:
            logging.warning("Aucune donnée à afficher")
            return
        
        # Extraire les données
        times = [entry['elapsed_time'] for entry in self.traffic_log]
        requests = [entry['num_requests'] for entry in self.traffic_log]
        
        # Créer le graphe
        plt.figure(figsize=(12, 6))
        plt.plot(times, requests, linewidth=2, color='#e74c3c')
        
        # Configuration du graphe
        plt.title(f'Trafic d\'attaque DoS - Mode: {self.attack_mode}', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Temps écoulé (secondes)', fontsize=12)
        plt.ylabel('Nombre de requêtes', fontsize=12)
        plt.grid(True, alpha=0.3, linestyle='--')
        
        # Ajouter les statistiques
        stats = self.get_statistics()
        stats_text = f"Moyenne: {stats['avg_requests_per_second']:.1f} req/s\n"
        stats_text += f"Max: {stats['max_requests']} req/s\n"
        stats_text += f"Total: {stats['total_requests']} requêtes"
        
        plt.text(0.02, 0.98, stats_text,
                transform=plt.gca().transAxes,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                fontsize=10)
        
        plt.tight_layout()
        
        # Sauvegarder si demandé
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            logging.info(f"Graphe sauvegardé: {filename}")
        
        # Afficher si demandé
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_comparison_modes_improved(self, attackers_list: list, filename: str = None):
        """
        Génère un graphe de comparaison amélioré des modes d'attaque avec statistiques.
        
        Args:
            attackers_list: Liste d'objets Attacker avec traffic_log rempli
            filename: Chemin pour sauvegarder le graphe (optionnel)
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Analyse comparative des modes d\'attaque DoS', 
                     fontsize=16, fontweight='bold', y=0.995)
        
        colors = {'constant': '#e74c3c', 'poisson': '#3498db', 'burst': '#2ecc71'}
        
        # ===== Graphe 1: Superposition complète =====
        ax1 = axes[0, 0]
        for attacker in attackers_list:
            if not attacker.traffic_log:
                continue
            
            times = [entry['elapsed_time'] for entry in attacker.traffic_log]
            requests = [entry['num_requests'] for entry in attacker.traffic_log]
            
            ax1.plot(times, requests, 
                    label=f"{attacker.attack_mode.capitalize()}", 
                    linewidth=2.5,
                    color=colors.get(attacker.attack_mode, '#95a5a6'),
                    alpha=0.8)
        
        ax1.set_title('Comparaison des trafics en temps réel', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Temps écoulé (secondes)', fontsize=11)
        ax1.set_ylabel('Nombre de requêtes', fontsize=11)
        ax1.legend(loc='best', fontsize=10, framealpha=0.95)
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # ===== Graphe 2: Statistiques comparatives (barres) =====
        ax2 = axes[0, 1]
        modes = [a.attack_mode.capitalize() for a in attackers_list if a.traffic_log]
        moyennes = [np.mean([e['num_requests'] for e in a.traffic_log]) 
                    for a in attackers_list if a.traffic_log]
        
        bars = ax2.bar(modes, moyennes, color=[colors.get(a.attack_mode, '#95a5a6') 
                                               for a in attackers_list if a.traffic_log],
                       alpha=0.7, edgecolor='black', linewidth=2)
        
        # Ajouter les valeurs sur les barres
        for bar, val in zip(bars, moyennes):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}\nreq/s', ha='center', va='bottom', fontweight='bold')
        
        ax2.set_title('Comparaison des moyennes', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Moyenne de requêtes/s', fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # ===== Graphe 3: Max par mode =====
        ax3 = axes[1, 0]
        maxs = [max([e['num_requests'] for e in a.traffic_log]) 
                for a in attackers_list if a.traffic_log]
        
        bars = ax3.bar(modes, maxs, color=[colors.get(a.attack_mode, '#95a5a6') 
                                           for a in attackers_list if a.traffic_log],
                       alpha=0.7, edgecolor='black', linewidth=2)
        
        for bar, val in zip(bars, maxs):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(val)}\nreq/s', ha='center', va='bottom', fontweight='bold')
        
        ax3.set_title('Comparaison des pics (Max)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Maximum de requêtes/s', fontsize=11)
        ax3.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # ===== Graphe 4: Tableau statistique texte =====
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        # Créer le tableau de statistiques
        table_data = []
        header = ['Mode', 'Moyenne', 'Max', 'Min', 'Écart-type', 'Total']
        table_data.append(header)
        
        for attacker in attackers_list:
            if not attacker.traffic_log:
                continue
            
            stats = attacker.get_statistics()
            row = [
                attacker.attack_mode.capitalize(),
                f"{stats['avg_requests_per_second']:.1f}",
                f"{int(stats['max_requests'])}",
                f"{int(stats['min_requests'])}",
                f"{stats['std_requests']:.1f}",
                f"{int(stats['total_requests'])}"
            ]
            table_data.append(row)
        
        table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.15, 0.15, 0.15, 0.15, 0.2, 0.2])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Styler l'en-tête
        for i in range(len(header)):
            table[(0, i)].set_facecolor('#34495e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Colorer les lignes selon le mode
        for i, attacker in enumerate(attackers_list, 1):
            if attacker.traffic_log:
                color = colors.get(attacker.attack_mode, '#95a5a6')
                for j in range(len(header)):
                    table[(i, j)].set_facecolor(color)
                    table[(i, j)].set_alpha(0.3)
        
        ax4.set_title('Statistiques détaillées', fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            logging.info(f"Graphe de comparaison amélioré sauvegardé: {filename}")
        
        plt.show()
    
    def init_realtime_plot(self):
        """
        Initialise le graphe pour l'affichage en temps réel.
        À utiliser avant start_attack() avec realtime=True.
        """
        plt.ion()  # Mode interactif
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.line, = self.ax.plot([], [], 'r-', linewidth=2)
        
        self.ax.set_title(f'Trafic DoS en temps réel - Mode: {self.attack_mode}',
                         fontsize=14, fontweight='bold')
        self.ax.set_xlabel('Temps écoulé (secondes)', fontsize=12)
        self.ax.set_ylabel('Nombre de requêtes', fontsize=12)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        
        self.x_data = []
        self.y_data = []
        
        logging.info("Graphe temps réel initialisé")
    
    def update_realtime_plot(self, elapsed_time: float, num_requests: int):
        """
        Met à jour le graphe en temps réel.
        À utiliser comme callback dans start_attack().
        
        Args:
            elapsed_time: Temps écoulé
            num_requests: Nombre de requêtes actuel
        """
        if self.fig is None or self.ax is None:
            logging.warning("Graphe temps réel non initialisé. Appelez init_realtime_plot() d'abord.")
            return
        
        self.x_data.append(elapsed_time)
        self.y_data.append(num_requests)
        
        self.line.set_data(self.x_data, self.y_data)
        
        # Ajuster les limites
        self.ax.set_xlim(0, max(self.x_data) + 1)
        self.ax.set_ylim(0, max(self.y_data) * 1.1)
        
        # Redessiner
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def save_realtime_plot(self, filename: str):
        """
        Sauvegarde le graphe temps réel actuel.
        
        Args:
            filename: Chemin pour sauvegarder le graphe
        """
        if self.fig:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            logging.info(f"Graphe temps réel sauvegardé: {filename}")
        else:
            logging.warning("Aucun graphe temps réel à sauvegarder")
    
    def generate_report_graphs(self, output_dir: str = 'data/graphs'):
        """
        Génère un ensemble complet de graphes pour le rapport.
        
        Args:
            output_dir: Répertoire de sortie pour les graphes
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if not self.traffic_log:
            logging.warning("Aucune donnée pour générer les graphes")
            return
        
        # 1. Graphe principal du trafic
        self.plot_traffic_static(
            filename=f"{output_dir}/traffic_{self.attack_mode}.png",
            show=False
        )
        
        # 2. Histogramme de distribution
        requests = [entry['num_requests'] for entry in self.traffic_log]
        plt.figure(figsize=(10, 6))
        plt.hist(requests, bins=30, color='#3498db', edgecolor='black', alpha=0.7)
        plt.title(f'Distribution des requêtes - Mode: {self.attack_mode}',
                 fontsize=14, fontweight='bold')
        plt.xlabel('Nombre de requêtes', fontsize=12)
        plt.ylabel('Fréquence', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y', linestyle='--')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/histogram_{self.attack_mode}.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Boxplot statistique
        plt.figure(figsize=(8, 6))
        plt.boxplot(requests, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='#2ecc71', alpha=0.7))
        plt.title(f'Analyse statistique - Mode: {self.attack_mode}',
                 fontsize=14, fontweight='bold')
        plt.ylabel('Nombre de requêtes', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y', linestyle='--')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/boxplot_{self.attack_mode}.png",
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"Graphes de rapport générés dans {output_dir}")


# ========== TESTS ==========

def test_attacker():
    """Teste les différents modes d'attaque avec génération de graphes."""
    import os
    os.makedirs('data/graphs', exist_ok=True)
    
    print("=" * 70)
    print("SIMULATION D'ATTAQUE DoS - TESTS AVEC GRAPHES")
    print("=" * 70)
    
    print("\n=== Test Mode Constant ===")
    attacker_constant = Attacker(
        attack_mode='constant',
        num_attackers=5,
        request_rate=10,
        duration=5
    )
    
    attacker_constant.start_attack()
    stats_constant = attacker_constant.get_statistics()
    print(f"Statistiques: {stats_constant}")
    attacker_constant.export_traffic_log('data/test_constant.csv')
    attacker_constant.plot_traffic_static(filename='data/graphs/test_constant.png', show=False)
    
    print("\n=== Test Mode Poisson ===")
    attacker_poisson = Attacker(
        attack_mode='poisson',
        num_attackers=5,
        request_rate=10,
        duration=5
    )
    
    attacker_poisson.start_attack()
    stats_poisson = attacker_poisson.get_statistics()
    print(f"Statistiques: {stats_poisson}")
    attacker_poisson.export_traffic_log('data/test_poisson.csv')
    attacker_poisson.plot_traffic_static(filename='data/graphs/test_poisson.png', show=False)
    
    print("\n=== Test Mode Burst ===")
    attacker_burst = Attacker(
        attack_mode='burst',
        num_attackers=5,
        request_rate=10,
        duration=15,
        burst_intensity=5
    )
    
    attacker_burst.start_attack()
    stats_burst = attacker_burst.get_statistics()
    print(f"Statistiques: {stats_burst}")
    attacker_burst.export_traffic_log('data/test_burst.csv')
    attacker_burst.plot_traffic_static(filename='data/graphs/test_burst.png', show=False)
    
    # Comparaison des modes
    print("\n=== Génération de la comparaison améliorée ===")
    attacker_burst.plot_comparison_modes_improved(
        [attacker_constant, attacker_poisson, attacker_burst],
        filename='data/graphs/comparison_improved.png'
    )
    
    # Générer tous les graphes de rapport pour burst
    print("\n=== Génération des graphes de rapport ===")
    attacker_burst.generate_report_graphs('data/graphs')
    
    print("\n" + "=" * 70)
    print("✅ TESTS TERMINÉS")
    print("=" * 70)
    print(f"📊 Graphes générés dans: data/graphs/")
    print(f"📁 CSV générés dans: data/")
    print("=" * 70)


if __name__ == '__main__':
    test_attacker()