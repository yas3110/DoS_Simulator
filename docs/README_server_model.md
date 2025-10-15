# 🧠 Module `ServerModel` — Simulation et analyse du comportement serveur

## 🎯 Introduction
Le module **`ServerModel`** constitue le cœur logique du simulateur d’attaque par déni de service (DoS).  
Il reproduit le comportement d’un **serveur virtuel** recevant un flux de requêtes, afin d’étudier l’impact d’une surcharge de trafic sur ses performances.  
Cette approche permet d’observer les effets d’une attaque DoS sans exposer de système réel, tout en offrant une compréhension concrète du phénomène.

---

## ⚙️ Objectif du module
Ce module a pour but de modéliser le fonctionnement d’un serveur soumis à un trafic intense.  
Il gère la réception, la file d’attente et le traitement des requêtes en fonction d’une capacité maximale prédéfinie.  
L’objectif est de mesurer :
- la charge du serveur (%),
- la taille de la file d’attente,
- la latence moyenne de traitement,
- et les transitions entre états : **Normal**, **Chargé**, **Surchargé**.

---

## 🧩 Structure et fonctionnement interne

### 📄 Classe `RequestEvent`
Représente une requête simulée :
| Attribut | Description |
|-----------|-------------|
| `timestamp` | Moment de génération de la requête |
| `cost` | Coût de traitement (unité abstraite de charge CPU) |

### ⚙️ Classe `ServerModel`
Composants principaux :
| Élément | Description |
|----------|-------------|
| `capacity` | Capacité maximale de traitement (unités/seconde) |
| `queue` | File des requêtes en attente |
| `current_load` | Charge instantanée du serveur |
| `latencies` | Historique des latences observées |
| `warning_threshold` | Seuil d’alerte (70 % par défaut) |
| `overload_threshold` | Seuil de surcharge (90 % par défaut) |

Méthodes principales :
| Méthode | Rôle |
|----------|------|
| `enqueue(req)` | Ajoute une requête à la file d’attente |
| `step(dt)` | Simule le traitement pendant *dt* secondes |
| `get_state()` | Retourne l’état du serveur (NORMAL / CHARGÉ / SURCHARGÉ) |
| `reset()` | Réinitialise le modèle |

---

## 🧪 Exemple d’utilisation

```python
from server_model import ServerModel, RequestEvent
import time

server = ServerModel(processing_capacity_per_sec=40.0)
request = RequestEvent(timestamp=time.time(), cost=2.0)

server.enqueue(request)
stats = server.step(dt=1.0)
state, load = server.get_state()

print(f"État du serveur : {state}, Charge : {load:.2f}%")
print(stats)
