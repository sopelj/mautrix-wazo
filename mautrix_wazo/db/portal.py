from __future__ import annotations

from typing import ClassVar

from asyncpg.protocol.protocol import Record
from attr import dataclass
from mautrix.util.async_db import Database
from mautrix.types import RoomID

from mautrix_wazo.types import WazoUUID


@dataclass
class Portal:
    db: ClassVar[Database]

    mxid: RoomID | None
    wazo_uuid: WazoUUID

    async def insert(self) -> None:
        await self.db.execute('INSERT INTO portal (mxid, wazo_uuid) VALUES ($1, $2)', self.mxid, self.wazo_uuid)

    async def delete(self) -> None:
        await self.db.execute('DELETE FROM portal WHERE mxid = $1', self.mxid)
