from typing import Annotated
from fastapi import APIRouter, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from routers.clases_threads import Monitores_Conexion as cm, Recorders as cr
import uuid
import glob
import json
import os
import asyncio

flug_router = APIRouter()

templates_path = os.path.join(os.path.dirname(__file__), "../templates/")
templates = Jinja2Templates(directory=templates_path)
file_path = "Users.json"


control = cm.MonitorControl()

"""Controlador para el monitor q nos indicara si hay internet ,esta clase esta definida en el modulo Monitores_Conexion"""
clients = []


def obtener_control():
    return control


# Para manejar el envio de notifcaciones
async def genera_notification(queue: asyncio.Queue):
    while True:
        message = await queue.get()
        yield f"data:{message}\n\n"


async def send_notification(message: str):
    for client in clients:
        await client.put(message)
    return


@flug_router.get("/notifications")
async def notifications(request: Request):
    try:
        queue = asyncio.Queue()
        clients.append(queue)

        return StreamingResponse(
            genera_notification(queue), media_type="text/event-stream"
        )
    except asyncio.CancelledError:
        clients.remove(queue)
        print("cliente removido")
    return


# Endpoint para crear usuario
@flug_router.post("/create_user")
async def save_user(
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
            return RedirectResponse(url=f"/registrar", status_code=303)
    else:
        return RedirectResponse(url=f"/registrar", status_code=303)

    return RedirectResponse(url=f"datos/{email}", status_code=303)


# Endpoint para el login del usuario
@flug_router.post("/login")
async def save_user(email: Annotated[str, Form()], password: Annotated[str, Form()]):

    with open(file_path, "r") as file:
        data = json.load(file)
    user = [usuario for usuario in data["usuarios"] if usuario["email"] == email]
    if user:
        if user[0]["password"] == password:
            return RedirectResponse(url=f"datos/{email}", status_code=303)
        else:
            return RedirectResponse(url=f"/", status_code=303)
    else:
        return RedirectResponse(url=f"/", status_code=303)


# Para llegar lo q seria la pagina donde se muestran las principales interacciones
@flug_router.get("/datos/{email}", tags=["recorder"])
def get_recorders(request: Request, email: str):
    with open(file_path, "r") as file:
        data = json.load(file)
    rutas = [ruta for ruta in data["rutas"] if ruta["email"] == email]
    return templates.TemplateResponse(
        "datos.html", {"request": request, "rutas": rutas, "email": email}
    )


# Para crear las rutas q son necesarios para los hilos
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
@flug_router.delete("/eliminar/{id}", tags=["recorder"])
async def delete_ruta(id: str):
    with open(file_path, "r") as file:
        data = json.load(file)
    for ruta in data["rutas"]:
        if ruta["id"] == id:
            data["rutas"].remove(ruta)
            break
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    return await send_notification(f"Ruta {id} eliminada")


# Para dar inicio al proceso  de grabacion
@flug_router.post("/Ejecution/{id}", tags=["Ejecucion"])
async def ejecutandose(
    id: str,
    control: cm.MonitorControl = Depends(obtener_control),
):
    await send_notification("Iniciando")
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
                path_to_imgs="C:/THALIA/Proyectos/trabajando con fastapi/Flugtracker/static/imgs",
            )
            control.iniciar(thread=worker, url=ruta["url"], time_wait=20, time_out=20)
            break


# Para detener el proceso de grabacion
@flug_router.get("/detener_ejecution", tags=["Ejecucion"])
async def detener_ejecucion(control: cm.MonitorControl = Depends(obtener_control)):
    control.detener()
    direc = "C:/THALIA/Proyectos/trabajando con fastapi/Flugtracker/static/imgs"
    name = "airplane-routes-and-stars-vector-1109381.jpg"
    files = glob.glob(os.path.join(direc, "*"))
    for file in files:
        if os.path.basename(file) != name:
            os.remove(file)
    return await send_notification("Detenido")
