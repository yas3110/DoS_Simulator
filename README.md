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
