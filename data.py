# Configuration des fichiers JSON
import json
import os.path
import random

FIGEMENTS = os.path.join(os.path.dirname(__file__), 'data', "expressions.json")
DEFIGEMENTS = os.path.join(os.path.dirname(__file__), 'data', "defigements.json")
USERS = os.path.join(os.path.dirname(__file__), 'data', "users.json")


def init_files():
    if not os.path.exists(FIGEMENTS):
        with open(FIGEMENTS, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not os.path.exists(DEFIGEMENTS):
        with open(DEFIGEMENTS, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not os.path.exists(USERS):
        with open(USERS, 'w', encoding='utf-8') as f:
            json.dump({}, f)


def get_users():
    with open(USERS, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_figements() -> dict[str, str]:
    with open(FIGEMENTS, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_defigements() -> dict[str, dict]:
    global all_defigements
    with open(DEFIGEMENTS, 'r', encoding='utf-8') as f:
        all_defigements = json.load(f)
        return all_defigements


def save_defigements(defigements):
    global all_defigements
    with open(DEFIGEMENTS, 'w', encoding='utf-8') as f:
        json.dump(defigements, f, indent=4)
        all_defigements = defigements

def save_users(users):
    with open(USERS, 'w', encoding='utf-8') as f:
        json.dump(users, f)

def add_defigement(figement_id: int, defigement_str: str, user_id: int):
    defigements = get_defigements()
    if defigements == {}:
        new_id = 0
    else:
        new_id = len(list(defigements.keys()))
    # tester si cet utilisateur a déjà posté ce défigement
    for defigment in defigements.values():
        if defigment['text'] == defigement_str and user_id == defigment['user'] and figement_id == defigment['figement_id']:
            raise ValueError('Cet utilisateur a déjà ajouté ce défiement')

    defigements[str(new_id)] = {'text': defigement_str, 'figement_id': figement_id, 'count': 0, 'user': user_id, 'upvoted': {}}
    save_defigements(defigements)


def change_count_defigement(defigement_id: int, good: bool, user_id: int):
    incr = 1 if good else -1
    user_id = str(user_id)
    defigements = get_defigements()
    defigement = defigements[str(defigement_id)]
    if user_id in defigement['upvoted']:
        # en gros si l'utilisateur rappuie sur un bouton sur lequel il a déjà appuyé on annule son vote
        if defigement['upvoted'][user_id] == incr:
            incr = -defigement['upvoted'][user_id]
            del defigements[str(defigement_id)]['upvoted'][user_id]
        else:
            defigements[str(defigement_id)]['upvoted'][user_id] = incr
            incr *= 2
    else:
        defigements[str(defigement_id)]['upvoted'][user_id] = incr
    defigements[str(defigement_id)]['count'] += incr
    save_defigements(defigements)
    return defigements[str(defigement_id)]['count']


def get_random_figement():
    figements = get_figements()
    chosen_id = random.choice(list(figements.keys()))
    return {'id': chosen_id, 'text': figements[chosen_id]}


def get_ordered_defigements(figement_id):
    defigements = all_defigements
    if figement_id is not None:
        defigements = {k: d for k, d in defigements.items() if d['figement_id'] == figement_id}
    return sorted(defigements.items(), key=lambda x: x[1]["count"], reverse=True)


def get_user_from_id(id: int, users):
    for user in users.values():
        if user['id'] == id:
            return user['username']


def get_user_scores() -> list[dict]:
    defigements = all_defigements
    user_scores = {}
    users = get_users()
    # Parcourir tous les défigements
    for defigement in defigements.values():
        user_id = defigement.get("user")
        count = defigement.get("count", 0)

        # Mettre à jour le score de l'utilisateur
        if user_id is not None:
            user_scores[user_id] = user_scores.get(user_id, 0) + count

    # Trier les utilisateurs par score cumulé
    sorted_user_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)

    # Créer la liste résultante
    result = [{"user": get_user_from_id(user_id, users), "score": score} for user_id, score in sorted_user_scores]

    return result


all_defigements = get_defigements()
