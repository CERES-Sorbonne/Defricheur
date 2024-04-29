from typing import Annotated

from fastapi import Depends, HTTPException, FastAPI, Request, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from .data import getData, saveAnnotation, createUserFile, goNextGoPrevious, tableScores, saveUserData, \
    getUserData, isTutoDoneBack
from .users import authenticate_user, get_current_user, User, validate_user, create_user, UserInDB

app = FastAPI()

origins = [
    "http://defricheur.marceau-h.fr",
    "https://defricheur.marceau-h.fr",
    "http://192.168.2.2",
    "https://192.168.2.2",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

app.mount("/badges", StaticFiles(directory="data/badges"), name="badges")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    response = templates.TemplateResponse(
        "home.html",
        {"request": request}
    )
    ## If you want to disable cache
    # response.headers["Cache-Control"] = "no-cache, no-store"
    # response.headers["Pragma"] = "no-cache"
    # response.headers["Expires"] = "0"
    # response.headers["CDN-Cache-Control"] = "no-cache, no-store"
    return response


@app.get('/informations', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "informations.html",
        {"request": request}
    )


@app.post("/data/", response_class=JSONResponse)
async def get_data(request: Request, current_user: Annotated[UserInDB, Depends(get_current_user)]):
    payload = await request.json()
    if len(payload.values()) > 0:
        data = getData(current_user, payload)
        newBadge = goNextGoPrevious(current_user, payload)
    else:
        newBadge = None
    data = getData(current_user)
    data["newBadge"] = newBadge
    return data


@app.get("/go_previous", response_class=JSONResponse)
async def go_previous(current_user: Annotated[UserInDB, Depends(get_current_user)]):
    newBadge = goNextGoPrevious(current_user, {"order": -1})
    return {"newBadge": newBadge}


@app.get("/annotate", response_class=HTMLResponse)
async def get_task(request: Request):
    return templates.TemplateResponse(
        "annotate.html",
        {"request": request},
    )


@app.post("/annotate/")
async def annotate(current_user: Annotated[UserInDB, Depends(get_current_user)], request: Request):
    data = await request.json()
    saveAnnotation(current_user, data)
    return "success"


@app.post("/login")
async def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    res = await validate_user(user)
    response.set_cookie(key='access-token', value=res['access_token'], httponly=True)
    return {'username': user.username, **res}


@app.post('/logout')
async def logout(request: Request):
    print("logout")
    response = templates.TemplateResponse(
        "home.html",
        {"request": request},
    )
    response.set_cookie(key='access-token', value='', httponly=True)
    response.delete_cookie('access-token', httponly=True)
    return response


@app.post("/signup")
async def signup(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = create_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=409, detail="Username already taken: " + form_data.username)
    else:
        createUserFile(user)
    res = await validate_user(user)
    response.set_cookie(key='access-token', value=res['access_token'], httponly=True)
    return {'username': user.username, **res}


@app.post('/users/me')
async def get_user_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@app.get('/ranking', response_class=HTMLResponse)
async def get_all_users(current_user: Annotated[User, Depends(get_current_user)], request: Request):
    # all_users = get_users_with_scores()
    all_users = tableScores()
    current_user = current_user.id
    all_users.sort(key=lambda x: x['score'], reverse=True)
    return templates.TemplateResponse(
        "users.html",
        {"request": request, 'current_user_id': current_user, 'users': all_users}
    )


@app.get('/secret')
async def get_secret(
        current_user: Annotated[User, Depends(get_current_user)],
        request: Request,
        q: str = Query(None)
):
    userData = getUserData(current_user, dataType="score")

    if q == 'k0nam1':
        badges = userData.get("badges", {})
        if "konami" not in badges:
            userData["badges"].append("konami")
            saveUserData(current_user, userData, dataType="score")
        return {"message": "Secret révélé !", "id": "konami", "newBadge": "konami"}
    else:
        return {"message": "La query string est incorrecte."}


@app.get('/isTutoDone/')
async def isTutoDone(
        current_user: Annotated[User, Depends(get_current_user)]
):
    return isTutoDoneBack(current_user)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn src.main:app --reload
