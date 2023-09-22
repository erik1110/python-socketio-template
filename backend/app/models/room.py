from beanie import Document
from datetime import datetime
from pydantic import Extra
from typing import Optional, List
import pytz

tz = pytz.timezone('Asia/Taipei')

class Room(Document):
    status: int
    sid_list: Optional[List[str]]
    created_timestamp: datetime
    updated_timestamp: datetime
