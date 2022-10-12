from __future__ import annotations

from typing import ClassVar

from asyncpg.protocol.protocol import Record
from attr import dataclass
from mautrix.types import EventID, RoomID
from mautrix.util.async_db import Database

from mautrix_wazo.types import WazoUUID


@dataclass
class Message:
    db: ClassVar[Database]

    mxid: EventID
    mx_room: RoomID
    wazo_uuid: WazoUUID
    wazo_room_uuid: WazoUUID
    content: str
    timestamp: int

    columns = 'mxid, mx_room, wazo_uuid, wazo_room_uuid, content, created'

    async def insert(self) -> None:
        await self.db.execute(
            f"INSERT INTO message ({self.columns}) VALUES ($1, $2, $3, $4, $5, $6)",
            self.mxid,
            self.mx_room,
            self.wazo_uuid,
            self.wazo_room_uuid,
            self.content,
            self.timestamp,
        )

    @classmethod
    def _from_row(cls, row: Record | None) -> Message | None:
        if not row:
            return None
        return cls(**row)

    @classmethod
    async def get_by_mxid(cls, mxid: EventID, mx_room: RoomID) -> Message | None:
        return cls._from_row(
            await cls.db.fetchrow(f"SELECT {cls.columns} FROM message WHERE mxid=$1 AND mx_room=$2", mxid, mx_room)
        )
