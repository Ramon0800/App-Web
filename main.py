from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from routers import flug_router
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()
static_path = os.path.join(os.path.dirname(__file__), "static/")
templates_path = os.path.join(os.path.dirname(__file__), "templates/")
app.mount("/static", StaticFiles(directory=static_path), "static")
templates = Jinja2Templates(directory=templates_path)

app.title = "Flugtracker"
app.version = "2.0.0"


@app.get("/", tags=["Home"], response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/registrar", tags=["Home"], response_class=HTMLResponse)
def registrar(request: Request):
    return templates.TemplateResponse("registrar.html", {"request": request})


# Para anadidr los datos q seran pasados al grabador
@app.get("/anadir/{email}", tags=["Home"], response_class=HTMLResponse)
def anadir(request: Request, email: str):
    return templates.TemplateResponse(
        "anadir_ruta.html", {"request": request, "email": email}
    )


app.include_router(prefix="/flug", router=flug_router)
