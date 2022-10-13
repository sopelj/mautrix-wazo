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

    wazo_uuid: WazoUUID
    mxid: RoomID | None = None

    async def insert(self) -> None:
        await self.db.execute('INSERT INTO portal (mxid, wazo_uuid) VALUES ($1, $2)', self.mxid, self.wazo_uuid)

    async def delete(self) -> None:
        await self.db.execute('DELETE FROM portal WHERE mxid = $1', self.mxid)

    @classmethod
    async def get_by_wazo_id(cls, wazo_id: WazoUUID):
        row = await cls.db.fetchrow("SELECT * FROM portal where wazo_uuid = $1", wazo_id)
        if row:
            return cls(mxid=row["mxid"], wazo_uuid=row["wazo_uuid"])

    async def update(self):
        await self.db.execute(
            "UPDATE portal SET wazo_uuid=$1, mxid=$2 WHERE wazo_uuid=$1",
            self.wazo_uuid,
            self.mxid,
        )
