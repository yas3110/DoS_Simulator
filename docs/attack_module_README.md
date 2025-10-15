# Module de Simulation d’Attaque DoS (`attack_sim.py`)

## 1. Contexte et objectif

Ce document décrit le **Module de Simulation d’Attaque DoS** développé dans le cadre de la **Tâche 2** du projet **DoS_Simulator**.  
L’objectif est de fournir une classe Python capable de simuler différents types d’attaques par déni de service (DoS) et de produire des logs exploitables.

## 2. Structure du module

attack_sim.py
├── imports
│ ├── numpy, time, logging, datetime, typing
│ └── pandas (dans export_traffic_log)
├── Configuration du logging
├── class Attacker
│ ├── init(…)
│ ├── generate_constant_traffic(elapsed_time)
│ ├── generate_poisson_traffic(elapsed_time)
│ ├── generate_burst_traffic(elapsed_time)
│ ├── generate_traffic(elapsed_time)
│ ├── start_attack(callback=None)
│ ├── stop_attack()
│ ├── get_traffic_log()
│ ├── export_traffic_log(filename)
│ └── get_statistics()
└── test_attacker() et bloc if __name__ == '__main__':

## 3. Installation

1. Cloner ou copier le projet `DoS_Simulator` sur votre machine.  
2. Se placer dans le dossier racine :
cd DoS_Simulator
3. Créer et activer l’environnement virtuel :
python3 -m venv venv
source venv/bin/activate
4. Installer les dépendances :
pip install -r requirements.txt

## 4. Dépendances

Le fichier `requirements.txt` contient :

numpy>=1.24.0
matplotlib>=3.7.0
pandas>=2.0.0

## 5. Utilisation de la classe `Attacker`

### 5.1 Import et création de l’objet

from attack_sim import Attacker

attacker = Attacker(
attack_mode='poisson', # 'constant', 'poisson' ou 'burst'
num_attackers=10, # Nombre d’attaquants
request_rate=100.0, # Requêtes par seconde
duration=60.0, # Durée totale (s)
burst_intensity=5.0 # Intensité du burst (mode 'burst' uniquement)
)

### 5.2 Lancer et arrêter l’attaque

Démarrer (bloquant jusqu’à la fin)
attacker.start_attack()

Arrêter prématurément si nécessaire
attacker.stop_attack()

### 5.3 Récupérer et exporter les logs

Obtenir le log sous forme de liste de dictionnaires
logs = attacker.get_traffic_log()

Exporter en CSV (par défaut : data/traffic_log.csv)
attacker.export_traffic_log('data/mon_log.csv')


### 5.4 Obtenir les statistiques

stats = attacker.get_statistics()
print(stats)

Exemple de sortie :
{
'total_requests': 6000,
'avg_requests_per_second': 100.0,
'max_requests': 150,
'min_requests': 90,
'std_requests': 12.5,
'duration': 60.0
}


## 6. Description des modes d’attaque

| Mode     | Comportement                                                                                                   |
|----------|----------------------------------------------------------------------------------------------------------------|
| constant | `num_requests = request_rate × num_attackers`, constant à chaque itération                                     |
| poisson  | `num_requests ~ Poisson(λ)` avec λ = `request_rate × num_attackers`                                             |
| burst    | Cycle de 10 s : <br>• 0–5 s : trafic intense = `request_rate × num_attackers × burst_intensity`<br>• 5–10 s : calme = `request_rate × num_attackers × 0.2` |

## 7. Tests unitaires

Le bloc `test_attacker()` exécute chaque mode avec des paramètres de test et génère :

- `data/test_constant.csv`  
- `data/test_poisson.csv`  
- `data/test_burst.csv`  

Pour exécuter les tests :

python attack_sim.py


## 8. Points d’arrêt de la Tâche 2

La tâche est considérée terminée lorsque :
1. **Le code** de `attack_sim.py` est écrit et validé.  
2. **Les tests unitaires** s’exécutent sans erreur.  
3. **Les fichiers CSV** de logs sont générés dans `data/`.  
4. **La documentation** de ce module (`docs/attack_module_README.md`) est complète.  
5. **Le code** est committé dans Git avec un message clair.

## 9. Bonnes pratiques et recommandations

- Toujours commenter les méthodes et documenter les paramètres.  
- Vérifier régulièrement les logs pour détecter des anomalies de trafic.  
- Utiliser un fichier de configuration externe pour ajuster facilement les paramètres d’attaque.  
- Intégrer `Attacker` dans une interface graphique ou un orchestrateur global (`main.py`).  

---

*Fin de la documentation du module `attack_sim.py`.*  
