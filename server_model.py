# server_model.py
"""
Module ServerModel pour le simulateur DoS (simulation locale, pas de réseau).

API :
- RequestEvent(timestamp: float, cost: float)
- ServerModel(processing_capacity_per_sec=50.0, warning_threshold=70.0, overload_threshold=90.0)
    - enqueue(req)
    - step(dt) -> dict
    - get_state() -> (state_str, current_load_percent)
    - reset()

Thread-safe : la file est protégée par un verrou.
"""
import time
import threading
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Tuple

@dataclass
class RequestEvent:
    """Représente une requête simulée (timestamp d'émission + coût simulé)."""
    timestamp: float
    cost: float  # unités de coût (simulées)

class ServerModel:
    """Modèle simple de serveur traitant une file de RequestEvent."""
    def __init__(self, processing_capacity_per_sec: float = 50.0,
                 warning_threshold: float = 70.0,
                 overload_threshold: float = 90.0):
        self.capacity = float(processing_capacity_per_sec)
        self.warning_threshold = float(warning_threshold)
        self.overload_threshold = float(overload_threshold)

        self.queue: Deque[RequestEvent] = deque()
        self.processed = 0           # nombre total de requêtes traitées
        self.lock = threading.Lock()
        self.current_load = 0.0      # estimation en pourcentage
        self.latencies: List[float] = []  # latences enregistrées (sec)
        self.dropped = 0             # réservé si on ajoute de la perte

    def enqueue(self, req: RequestEvent) -> None:
        """Ajouter une requête à la file (thread-safe)."""
        if not isinstance(req, RequestEvent):
            raise TypeError("req must be RequestEvent")
        with self.lock:
            self.queue.append(req)

    def step(self, dt: float = 1.0) -> dict:
        """
        Simuler le traitement pendant dt secondes.
        Retourne un dict de statistiques :
        {
         'processed': int,            # nb d'éléments traités ce pas
         'queue_len': int,            # longueur de la file après traitement
         'processed_cost': float,     # coût total traité ce pas
         'queued_cost': float,        # coût total restant dans la file
         'avg_latency': float|None,   # moyenne des dernières latences (sec)
         'current_load_percent': float
        }
        """
        if dt <= 0:
            raise ValueError("dt must be > 0")

        with self.lock:
            capacity = self.capacity * dt
            processed_cost = 0.0
            processed_count = 0
            now = time.time()

            # Traiter tant que la prochaine requête tient dans la capacité restante
            while self.queue and (processed_cost + self.queue[0].cost) <= capacity:
                req = self.queue.popleft()
                processed_cost += req.cost
                processed_count += 1
                self.processed += 1
                # stocker la latence (temps entre enqueue et traitement)
                self.latencies.append(max(0.0, now - req.timestamp))

            # coût total en attente après traitement
            queued_cost = sum(r.cost for r in self.queue)

            # estimation simple de la charge = queued_cost / capacity (en %)
            if capacity > 0:
                load_ratio = queued_cost / capacity
                load_percent = load_ratio * 100.0
            else:
                load_percent = 100.0 if queued_cost > 0 else 0.0

            # limiter la valeur maximale pour affichage
            self.current_load = max(0.0, min(load_percent, 1000.0))

            avg_latency = None
            if self.latencies:
                avg_latency = sum(self.latencies[-100:]) / min(len(self.latencies), 100)

            return {
                'processed': processed_count,
                'queue_len': len(self.queue),
                'processed_cost': processed_cost,
                'queued_cost': queued_cost,
                'avg_latency': avg_latency,
                'current_load_percent': self.current_load,
            }

    def get_state(self) -> Tuple[str, float]:
        """Renvoie l'état textuel et la charge actuelle."""
        load = self.current_load
        if load < self.warning_threshold:
            return ("NORMAL", load)
        elif load < self.overload_threshold:
            return ("CHARGÉ", load)
        else:
            return ("SURCHARGÉ", load)

    def reset(self) -> None:
        """Réinitialise la file et les compteurs (thread-safe)."""
        with self.lock:
            self.queue.clear()
            self.processed = 0
            self.current_load = 0.0
            self.latencies = []
            self.dropped = 0
