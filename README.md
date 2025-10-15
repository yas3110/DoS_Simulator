## 
 Simulation du serveur

Le module `simulate_and_plot.py` permet de **simuler une attaque DoS** en générant un trafic aléatoire (arrivées de requêtes suivant une loi de Poisson) et en observant la **charge du serveur** dans le temps.

### Fonctionnement
- Le script utilise la classe `ServerModel` du fichier `server_model.py`.
- Il simule plusieurs "attaquants" qui envoient des requêtes vers un serveur virtuel.
- À chaque pas de temps, le serveur traite les requêtes selon sa capacité (`SERVER_CAPACITY`).
- Les métriques collectées sont :
  - `time_s` : temps écoulé en secondes
  - `load_percent` : pourcentage de charge du serveur
  - `queue_len` : taille de la file d’attente (nombre de requêtes non traitées)

### Fichiers générés
Après exécution, le script crée automatiquement le dossier `plots/` contenant :
- **`load_percent.png`** → évolution de la charge du serveur (%) dans le temps  
- **`queue_length.png`** → évolution du nombre de requêtes en attente  
- **`metrics.csv`** → export des données brutes pour exploitation dans Excel ou Python  

### Exécution locale
Depuis la racine du projet :
```bash
python simulate_and_plot.py


###  Utilisation avancée (modifier les paramètres de la simulation)

Le script `simulate_and_plot.py` expose plusieurs constantes en haut du fichier que tu peux ajuster pour tester différents scénarios.  
Ouvre `simulate_and_plot.py` et modifie les valeurs dans la zone **PARAMÈTRES MODIFIABLES** :

```python
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



---

##  Analyse et comparaison de scénarios (scripts avancés)

###  `batch_run.py` — Exécution de plusieurs scénarios

Ce script permet de **simuler plusieurs attaques DoS** automatiquement et de comparer leurs effets sur la charge du serveur.  
Chaque scénario définit :
- un nombre d'attaquants,
- une capacité serveur,
- une durée,
- une intensité de trafic.

Les résultats sont enregistrés dans des sous-dossiers de `plots/`.

#### Exemple de scénarios
| Nom | Nb attaquants | Capacité serveur | Taux req/s | Description |
|------|----------------|------------------|-------------|--------------|
| baseline | 5 | 40 | 4 | Scénario normal |
| heavy_traffic | 10 | 40 | 5 | Fort trafic (attaque DoS probable) |
| weak_server | 5 | 20 | 4 | Serveur sous-dimensionné |

#### Exécution
```bash
python batch_run.py
