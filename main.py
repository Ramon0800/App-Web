from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, StreamingResponse
from routers.flug_router import flug_router, send_notification
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
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


# Para añadidr los datos q seran pasados al grabador
@app.get("/anadir/{email}", tags=["Home"], response_class=HTMLResponse)
def anadir(request: Request, email: str):
    return templates.TemplateResponse(
        "anadir_ruta.html", {"request": request, "email": email}
    )


# Endpoint para enviar imagen al cliente
@app.get("/events")
async def events():
    try:

        async def event_generator():
            cont = 0
            exist_imgs = set(os.listdir("static/imgs"))
            while True:
                act_imgs = set(os.listdir("static/imgs"))
                new_imgs = act_imgs - exist_imgs
                if new_imgs:
                    cont += 1
                    for img in new_imgs:
                        image_url = f"http://127.0.0.1:8000/static/imgs/{img}"
                        yield f"data:{image_url}\n\n"
                    await send_notification("Nuevo frame añadido")
                    exist_imgs = act_imgs
                await asyncio.sleep(5)

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except asyncio.CancelledError:
        print("Envio de imagenes detenido")


app.include_router(prefix="/flug", router=flug_router)
