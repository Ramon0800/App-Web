from typing import Annotated
from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import Monitores_Conexion as cm
import Recorders as cr
import uuid
import time as tm
import json
import os

flug_router = APIRouter()

templates_path = os.path.join(os.path.dirname(__file__), "templates/")
templates = Jinja2Templates(directory=templates_path)
file_path = "Users.json"


control = cm.MonitorControl()

"""Controlador para el monitor q nos indicara si hay internet ,esta clase esta definida en el modulo Monitores_Conexionn"""


def obtener_control():
    return control


# Endpoint para crear usuario
@flug_router.post("/create_user")
def save_user(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    confirmpassword: Annotated[str, Form()],
):
    with open(file_path, "r") as file:
        data = json.load(file)
    emails = [usuario["email"] for usuario in data["usuarios"]]
    user = any([True for emaile in emails if emaile == email])
    if user == False:
        if password == confirmpassword:
            new_user = {"email": email, "password": password}
            data["usuarios"].append(new_user)
            with open(file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)
        else:
            print("Las contrasenas no coinciden intentenlo nuevamente")
            return RedirectResponse("/registrar", status_code=303)
    else:
        print("Este usuario ya existe")
        return RedirectResponse("/registrar", status_code=303)
    return RedirectResponse(url=f"datos/{email}", status_code=303)


# Endpoint para el login del usuario
@flug_router.post("/login")
def save_user(email: Annotated[str, Form()], password: Annotated[str, Form()]):
    with open(file_path, "r") as file:
        data = json.load(file)
    user = [usuario for usuario in data["usuarios"] if usuario["email"] == email]
    print(user)

    if user:
        if user[0]["password"] == password:
            return RedirectResponse(url=f"datos/{email}", status_code=303)
        else:
            print("Contrasena incorrecta")
    else:
        print("Este usuario no existe por favor registrate antes de intentar acceder")
    return RedirectResponse("/", status_code=303)


# Para llegar lo q seria la pagina donde se muestran las principales interacciones
@flug_router.get("/datos/{email}", tags=["recorder"])
def get_recorders(request: Request, email: str):
    with open(file_path, "r") as file:
        data = json.load(file)
    rutas = [ruta for ruta in data["rutas"] if ruta["email"] == email]
    return templates.TemplateResponse(
        "datos.html", {"request": request, "rutas": rutas, "email": email}
    )


# Para crear las rutas estas son los datos q son necesarios para los hilos
@flug_router.post("/ruta/{email}", tags=["recorder"])
def create_ruta(
    email: str,
    path: Annotated[str, Form()],
    url: Annotated[str, Form()],
    frames: Annotated[int, Form()],
    width: Annotated[int, Form()],
    heigth: Annotated[int, Form()],
    interval: Annotated[int, Form()],
):
    id = uuid.uuid4()
    id_str = str(id)
    change = path.replace("\\", "/")
    change = f"{change}/output.mp4"
    print(change)
    with open(file_path, "r") as file:
        data = json.load(file)
    new_ruta = {
        "id": id_str,
        "path": change,
        "url": url,
        "frames": frames,
        "width": width,
        "heigth": heigth,
        "interval": interval,
        "email": email,
    }
    data["rutas"].append(new_ruta)
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    return RedirectResponse(url=f"/flug/datos/{email}", status_code=303)


# Para eliminar las rutas
@flug_router.get("/eliminar/{id}/user/{email}", tags=["recorder"])
def delete_ruta(request: Request, id: str, email: str):
    with open(file_path, "r") as file:
        data = json.load(file)
    for ruta in data["rutas"]:
        if ruta["id"] == id:
            data["rutas"].remove(ruta)
            break
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
        return RedirectResponse(url=f"/flug/datos/{email}", status_code=303)


# Para dar inicio al proceso  de grabacion
@flug_router.get("/Ejecution/{id}/user/{email}", tags=["Ejecucion"])
async def ejecutandose(
    request: Request,
    id: str,
    email: str,
    control: cm.MonitorControl = Depends(obtener_control),
):
    with open(file_path, "r") as file:
        data = json.load(file)
    for ruta in data["rutas"]:
        if ruta["id"] == id:
            RECORDING_TIME = 10 * 60 * 60
            worker = cr.PeriodicRecorder(
                PATH_TO_VIDEO=ruta["path"],
                INTERVAL=ruta["interval"],
                frames=ruta["frames"],
                width=ruta["width"],
                heigth=ruta["heigth"],
                url=ruta["url"],
                recording_time=RECORDING_TIME,
            )
            control.iniciar(thread=worker, url=ruta["url"], time_wait=20, time_out=20)
            break
    return RedirectResponse(url=f"/flug/datos/{email}", status_code=303)


# Para detener el proceso de grabacion
@flug_router.get("/detener_ejecution/{email}", tags=["Ejecucion"])
async def detener_ejecucion(
    request: Request, email: str, control: cm.MonitorControl = Depends(obtener_control)
):
    control.detener()
    return RedirectResponse(url=f"/flug/datos/{email}", status_code=303)
