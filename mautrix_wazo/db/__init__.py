from mautrix.util.async_db import Database

from .upgrade import upgrade_table
from .user import User
from .message import Message


def init(db: Database) -> None:
    for table in (User, Message):
        table.db = db


__all__ = [
    "upgrade_table",
    "init",
    "Message",
    "User",
]