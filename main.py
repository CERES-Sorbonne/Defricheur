# main.py

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from data import init_files, get_random_figement, add_defigement, change_count_defigement, get_ordered_defigements

app = FastAPI()
templates = Jinja2Templates(directory="templates")

init_files()  # Assurez-vous que les fichiers JSON sont initialisés


# Route pour afficher le formulaire d'ajout de défigement
@app.get("/", response_class=HTMLResponse)
async def read_add_defigement(request: Request):
    random_defigement = get_random_figement()
    return templates.TemplateResponse(
        "add_defigement.html",
        {"request": request, "defigement": random_defigement},
    )


# Route pour ajouter un défigement
@app.post("/add_defigement/")
async def create_defigement(defigement_str: str = Form(...), figement_id: int = Form(...)):
    add_defigement(figement_id, defigement_str)
    return {"message": "Défigement ajouté avec succès"}


# Route pour évaluer un défigement
@app.post("/rate_defigement/{defigement_id}/{good}")
async def rate_defigement(defigement_id: int, good: bool):
    change_count_defigement(defigement_id, good)
    return {"message": "Le défigement a été évalué avec succès"}


# Route pour afficher tous les défigements triés par count
@app.get("/all", response_class=HTMLResponse)
async def read_all_defigements(request: Request):
    ordered_defigements = get_ordered_defigements()
    return templates.TemplateResponse(
        "all_defigements.html",
        {"request": request, "ordered_defigements": ordered_defigements},
    )
