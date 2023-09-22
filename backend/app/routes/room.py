from fastapi import APIRouter, Request
from app.models.room import Room
from datetime import datetime
import pytz

router = APIRouter()
tz = pytz.timezone('Asia/Taipei')

@router.post("/create_room")
async def generate_room(request: Request):
    room = Room(
        status=0,
        sid_list=[],
        created_timestamp=datetime.now(tz),
        updated_timestamp=datetime.now(tz),
    )
    await room.save()
    return room.id
