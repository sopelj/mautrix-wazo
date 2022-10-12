from dataclasses import dataclass
from datetime import datetime
from typing import NewType, List

WazoUUID = NewType("WazoUUID", str)

WazoEventId = NewType("WazoEventId", str)

WazoUserId = NewType("WazoUserId", str)

WazoRoomId = NewType("WazoRoomId", str)


@dataclass
class WazoMessage:
    event_id: WazoEventId
    sender_id: WazoUserId
    room_id: WazoRoomId
    created_at: datetime
    content: str
    participants: List[WazoUserId]
