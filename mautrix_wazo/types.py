from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType

WazoUUID = NewType("WazoUUID", str)


@dataclass
class WazoMessage:
    event_id: WazoUUID
    sender_id: WazoUUID
    room_id: WazoUUID
    created_at: datetime
    content: str
    participants: list[WazoUUID]
