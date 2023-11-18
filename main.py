# main.py
from datetime import timedelta
from typing import Annotated, Optional

from fastapi import FastAPI, Request, Form, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from data import init_files, get_random_figement, add_defigement, change_count_defigement, get_ordered_defigements, \
    get_figements, get_user_scores
from users import UserInDB, get_user, Token, authenticate_user, CRED_EXCEPTION, \
    ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, User, validate_user, create_user

app = FastAPI()
templates = Jinja2Templates(directory="templates")

init_files()


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
async def create_defigement(current_user: Annotated[User, Depends(get_current_user)], defigement_str: str = Form(...),  figement_id: int = Form(...)):
    add_defigement(figement_id, defigement_str, current_user.id)
    return {"message": "Défigement ajouté avec succès"}


# Route pour évaluer un défigement
@app.post("/rate_defigement/{defigement_id}/{good}")
async def rate_defigement(current_user: Annotated[User, Depends(get_current_user)], defigement_id: int, good: bool):
    newCount = change_count_defigement(defigement_id, good, current_user.id)
    return {'count': newCount}


# Route pour afficher tous les défigements triés par count
@app.get("/all", response_class=HTMLResponse)
async def read_all_defigements(request: Request, figement_id: Optional[int] = Query(None)):
    ordered_defigements = get_ordered_defigements(figement_id)
    figements = get_figements()
    return templates.TemplateResponse(
        "all_defigements.html",
        {"request": request, "ordered_defigements": ordered_defigements, "figement_id": str(figement_id), "figements": figements},
    )

# Route pour afficher tous les défigements triés par count
@app.get("/users_ranking", response_class=HTMLResponse)
async def read_all_defigements(request: Request):
    ordered_users = get_user_scores()
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": ordered_users},
    )


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    res = await validate_user(user)
    return {'username': user.username, **res}


@app.post("/signup")
async def signup(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = create_user(form_data.username, form_data.password)
    res = await validate_user(user)
    return {'username': user.username, **res}

@app.post('/users/me')
async def get_user_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

