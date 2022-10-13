from asyncpg import Connection
from mautrix.util.async_db import UpgradeTable

upgrade_table = UpgradeTable()


@upgrade_table.register(description="Latest revision", upgrades_to=1)
async def upgrade_latest(conn: Connection) -> None:
    await conn.execute(
        """CREATE TABLE portal (
            wazo_uuid     TEXT PRIMARY_KEY,
            mxid          TEXT
        )"""
    )
    await conn.execute(
        """CREATE TABLE "user" (
            mxid           TEXT PRIMARY KEY,
            wazo_uuid      TEXT
        )"""
    )
    await conn.execute(
        """CREATE TABLE puppet (
            wazo_uuid     TEXT PRIMARY KEY,
            first_name    TEXT,
            last_name     TEXT,
            username      TEXT
        )"""
    )
    await conn.execute(
        """CREATE TABLE message (
            mxid     TEXT PRIMARY KEY,
            mx_room  TEXT NOT NULL,
            wazo_uuid  TEXT,
            wazo_room_uuid  TEXT,
            content TEXT,
            timestamp BIGINT
        )"""
    )
