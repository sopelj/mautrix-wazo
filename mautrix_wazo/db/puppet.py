from __future__ import annotations

from typing import ClassVar

from asyncpg.protocol.protocol import Record
from attr import dataclass
from mautrix.util.async_db import Database

from mautrix_wazo.types import WazoUUID


@dataclass
class Puppet:
    db: ClassVar[Database]

    wazo_uuid: WazoUUID
    first_name: str
    last_name: str
    username: str

    columns = 'wazo_uuid, first_name, last_name, username'

    async def insert(self) -> None:
        await self.db.execute(
            f"INSERT INTO puppet ({self.columns}) VALUES ($1, $2, $3, $4)",
            self.wazo_uuid,
            self.first_name,
            self.last_name,
            self.username,
        )

    async def update(self):
        await self.db.execute(
            "UPDATE puppet SET first_name=$2, last_name=$3, username=$4 WHERE wazo_uuid=$1",
            self.wazo_uuid,
            self.first_name,
            self.last_name,
            self.username,
        )

    @classmethod
    def _from_row(cls, row: Record | None) -> Puppet | None:
        if not row:
            return None
        return cls(**row)

    @classmethod
    async def get_by_uuid(cls, uuid: WazoUUID) -> Puppet | None:
        return cls._from_row(
            await cls.db.fetchrow(f'SELECT {cls.columns} FROM "user" WHERE wazo_uuid=$1', uuid)
        )
