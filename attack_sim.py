import numpy as np
import time
import logging
from datetime import datetime
from typing import Literal

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


# Tests unitaires simples
def test_attacker():
    """Teste les différents modes d'attaque."""
    
    print("=== Test Mode Constant ===")
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


if __name__ == '__main__':
    test_attacker()
