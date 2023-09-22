import json
import pytz
import socketio
from app.core.socket_io import sio
from app.models.room import Room
from bson import ObjectId
from datetime import datetime

tz = pytz.timezone('Asia/Taipei')
namespace = "/chat"

async def handle_response(status, message, sid_list):
    response = {
        'status': status,
        'message': message,
    }
    json_string = json.dumps(response)

    for sid in sid_list:
        await sio.emit("sys", json_string, room=sid, namespace=namespace)

class MyCustomNamespace(socketio.AsyncNamespace):
    def on_connect(self, sid, data):
        print("connect ", sid)

    async def on_disconnect(self, sid):
        print("disconnect ", sid)
        room = await Room.find_one({"sid_list": {"$in": [sid]}})
        if room is not None:
            room.sid_list.remove(sid)
            await room.update({"$set": {"sid_list": room.sid_list,
                                        "status": 0}})
            await handle_response(status="Success",
                                  message=f"The user ({sid}) is disconnected!",
                                  sid_list=room.sid_list)
        else:
            await handle_response(status="Fail", 
                                  message="The user is never show in the rooms before!",
                                  sid_list=[sid])

    async def on_join(self, sid, rid):
        print("join:", sid)
        if not ObjectId.is_valid(rid):
            await handle_response(status="Fail",
                                  message="Invalid roomId",
                                  sid_list=[sid])
        room = await Room.get(ObjectId(rid))
        if room is None:
            await handle_response(status="Fail",
                                  message="The room is not found!",
                                  sid_list=[sid])
        else:
            sid_list = room.sid_list
            if sid in sid_list:
                await handle_response(status="Fail",
                                    message=f"User({sid}) have already joined the room.",
                                    sid_list=sid_list)
            elif room.status != 0:
                sid_list.append(sid)
                await handle_response(status="Fail",
                                    message=f"User({sid}) cannot join the room because the room is full.",
                                    sid_list=sid_list)
            elif room.status == 0 and len(sid_list)==0:
                sid_list.append(sid)
                update_data = {
                    "updated_timestamp": datetime.now(tz),
                    "sid_list": [sid],
                }
                await room.update({"$set": update_data})
                await handle_response(status="Success",
                                    message=f"User({sid}) 1st join the room.",
                                    sid_list=sid_list)
            elif room.status == 0 and len(sid_list)==1:
                sid_list.append(sid)
                update_data = {
                    "updated_timestamp": datetime.now(tz),
                    "sid_list": sid_list,
                    "status": 1,
                }
                await room.update({"$set": update_data})
                await handle_response(status="Success",
                                message=f"User({sid}) 2nd join the room.",
                                sid_list=sid_list)
            else:
                await handle_response(status="Fail",
                                    message=f"User({sid}) cannot join the room because the status is wrong.",
                                    sid_list=sid_list)
        
    async def on_msg(self, sid, data):
        room = await Room.find_one({"sid_list": {"$in": [sid]}})
        if room is None:
            await handle_response(status="Fail",
                                    message=f"The room is not found.",
                                    sid_list=[sid])
        else:
            sid_list = room.sid_list
            if len(sid_list) == 2:
                if isinstance(data, str) and data == "new_guest" and room.status == 1:
                    for sid in sid_list:
                        await sio.emit("msg", "new_guest", room=sid, namespace=namespace)
                    update_data = {
                        "updated_timestamp": datetime.now(tz),
                        "status": 2,
                    }
                    await room.update({"$set": update_data})
                    await handle_response(status="Success",
                                        message=f"New guest({sid}) is ready.",
                                        sid_list=sid_list)
                elif isinstance(data, str) and data == "play" and room.status == 2:
                    update_data = {
                        "updated_timestamp": datetime.now(tz),
                        "status": 3,
                    }
                    await room.update({"$set": update_data})
                    for sid in sid_list:
                        await sio.emit("msg", data, room=sid, namespace=namespace)
                    await handle_response(status="Success",
                                        message=f"The user({sid}) starts to play",
                                        sid_list=sid_list)
                else:
                    await handle_response(status="Fail",
                                        message=f"Wrong msg or status!",
                                        sid_list=sid_list)
            else:
                await handle_response(status="Fail",
                                        message=f"Not enough users!",
                                        sid_list=sid_list)
