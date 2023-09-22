import socketio
import os 

REDIS_URI = os.environ["REDIS_URI"]
mgr = socketio.AsyncRedisManager(url=REDIS_URI) 
sio = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins="*", client_manager=mgr
)
