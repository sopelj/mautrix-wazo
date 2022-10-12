from __future__ import annotations

from typing import ClassVar

from asyncpg.protocol.protocol import Record
from attr import dataclass
from mautrix.types import UserID
from mautrix.util.async_db import Database

from ..types import WazoUUID


@dataclass
class User:
    db: ClassVar[Database]

    mxid: UserID
    wazo_uuid: WazoUUID

    columns = 'mxid, wazo_uuid'

    async def insert(self) -> None:
        await self.db.execute(
            f'INSERT INTO "user" ({self.columns}) VALUES ($1, $2, $3, $4, $5)',
            self.mxid,
            self.wazo_uuid,
        )

    async def update(self) -> None:
        await self.db.execute(
            'UPDATE "user" SET first_name=$1, last_name=$2, email=$3 WHERE mxid=$4',
            self.mxid
        )

    @classmethod
    def _from_row(cls, row: Record | None) -> User | None:
        if not row:
            return None
        return cls(**row)

    @classmethod
    async def get_by_mxid(cls, mxid: UserID) -> User | None:
        return cls._from_row(
            await cls.db.fetchrow(f'SELECT {cls.columns} FROM "user" WHERE mxid=$1', mxid)
        )

    @classmethod
    async def get_by_uuid(cls, uuid: WazoUUID) -> User | None:
        return cls._from_row(
            await cls.db.fetchrow(f'SELECT {cls.columns} FROM "user" WHERE wazo_uuid=$1', uuid)
        )
