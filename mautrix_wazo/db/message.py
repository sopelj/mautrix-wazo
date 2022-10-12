from typing import ClassVar

from attr import dataclass
from mautrix.types import EventID, RoomID
from mautrix.util.async_db import Database


@dataclass
class Message:
    db: ClassVar[Database]

    mxid: EventID
    mx_room: RoomID

    columns = 'mxid, mx_room'
