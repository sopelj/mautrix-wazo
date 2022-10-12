from dataclasses import dataclass
from datetime import datetime
from typing import NewType, List

WazoID = NewType("WazoID", int)

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
