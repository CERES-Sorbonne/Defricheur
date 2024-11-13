# Défricheur

Le défricheur est un site d'annotation participative et gamifiée de défigements, en français.
S'inscrivant dans le projet de thèse de Julien Besançon (lien), il est développé conjointement avec d'autres membres du CERES.

Bien que la tâche d'annotation initiale soit celle du défigement, nous pensons que le site pourrait être adapté à d'autres tâches d'annotation.

---

**Table des matières**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

### Développement
Pour installer le défricheur en mode développement, vous pouvez cloner le dépôt git et accéder au dossier du projet :
```bash
git clone https://github.com/CERES-Sorbonne/Defricheur.git
cd Defricheur
```

Il vous faudra, par la suite, fournir un fichier `.env_defricheur` à la racine du projet, contenant les variables d'environnement suivantes :
```bash
SECRET_KEY= # OBLIGATOIRE | Clé secrète pour jwt, à générer avec un outil en ligne
FOLDER= # Facultatif | Chemin vers le dossier du projet, permet de lancer le script de démarrage depuis un autre répertoire, à condition que le fichier .env soit dans ce répertoire
DEFRICHEUR_PORT= # Facultatif | Port sur lequel le serveur doit écouter, par défaut 8000
```

Vous pouvez ensuite lancer le serveur de développement avec la commande suivante :
```bash
bash start_defricheur.sh
```

### PyPi
Le défricheur n'est pour l'instant pas disponible sur PyPi, vous pouvez cependant l'installer en mode développement (voir ci-dessus).

## Usage
Une fois configuré (fichier `.env_defricheur` à la racine du projet), puis lancé à l'aide du script `start_defricheur.sh`, le défricheur est accessible à l'adresse [http://localhost:8000](http://localhost:8000) (ou à l'adresse configurée dans le fichier `.env_defricheur`).

Le défricheur est conçu pour annoter des tweets, les données sont actuellement attendues sous forme de quatre fichiers json, un pour les tweets de contrôle, un pour les tweets d'entraînement, un pour les tweets de test et un pour les seeds : 
```json
{
    "id_du_tweet": {
        // Les clés suivantes sont obligatoires pour chaque tweet
        "text": "texte du tweet",
        "seed_id": "id de la seed, de l'expression que l'on souhaite reconnaître",
        // Les clés suivantes sont obligatoires pour les tweets de contrôle et d'entraînement
        "UMWE_identified": "booléeen indiquant si une expression défigée est identifiée",
        "MWE_recognized": "booléeen indiquant si une expression figée est reconnue",
        // Les clés suivantes sont obligatoires pour les tweets d'entraînement
        "correction": "explication des réponses précédentes",
    }
}
```
Et un autre fichier json contenant les seeds:
```json
{
    "id_de_la_seed": {
        "content": "expression à reconnaître",
        "total": n // nombre total d'occurrences de l'expression dans le corpus
    }
}
```

## License
Le défricheur est distribué sous les termes de la licence [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html).
