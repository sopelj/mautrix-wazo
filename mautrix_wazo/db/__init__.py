from __future__ import annotations

from mautrix.util.async_db import Database

from .upgrade import upgrade_table
from .user import User
from .message import Message
from .portal import Portal
from .puppet import Puppet


def init(db: Database) -> None:
    for table in (User, Message, Portal, Puppet):
        table.db = db


__all__ = (
    "upgrade_table",
    "init",
    "Message",
    "Portal",
    "Puppet",
    "User",
)