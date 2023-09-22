import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.socket_io import sio
from app.database import initiate_database
from app.routes.socket import MyCustomNamespace
from app.routes.room import router as RoomRouter

app = FastAPI()

sio.register_namespace(MyCustomNamespace("/chat"))
sio_asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_route("/socket.io/", route=sio_asgi_app, methods=["GET", "POST"])
app.add_websocket_route("/socket.io/", sio_asgi_app)
app.include_router(RoomRouter, tags=["Room"], prefix="/room")

@app.on_event("startup")
async def start_database():
    await initiate_database()
