# Configuration des fichiers JSON
import json
import os.path
import random

FIGEMENTS = os.path.join(os.path.dirname(__file__), 'data', "expressions.json")
DEFIGEMENTS = os.path.join(os.path.dirname(__file__), 'data', "defigements.json")


def init_files():
    if not os.path.exists(FIGEMENTS):
        with open(FIGEMENTS, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not os.path.exists(DEFIGEMENTS):
        with open(DEFIGEMENTS, 'w', encoding='utf-8') as f:
            json.dump({}, f)


def get_figements() -> dict[str, str]:
    with open(FIGEMENTS, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_defigements() -> dict[str, dict]:
    with open(DEFIGEMENTS, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_defigements(defigements):
    with open(DEFIGEMENTS, 'w', encoding='utf-8') as f:
        json.dump(defigements, f)


def add_defigement(figement_id: int, defigement_str: str):
    defigements = get_defigements()
    if defigements == {}:
        new_id = 0
    else:
        new_id = len(list(defigements.keys()))
    defigements[str(new_id)] = {'text': defigement_str, 'figement_id': figement_id, 'count': 0}
    save_defigements(defigements)


def change_count_defigement(defigement_id: int, good: bool):
    incr = 1 if good else -1
    defigements = get_defigements()
    defigements[str(defigement_id)]['count'] += incr
    save_defigements(defigements)


def get_random_figement():
    figements = get_figements()
    chosen_id = random.choice(list(figements.keys()))
    return {'id': chosen_id, 'text': figements[chosen_id]}

def get_ordered_defigements():
    defigements = get_defigements()
    return sorted(defigements.items(), key=lambda x: x[1]["count"], reverse=True)