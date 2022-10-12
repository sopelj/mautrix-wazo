from __future__ import annotations

from typing import ClassVar

from attr import dataclass
from mautrix.types import UserID
from mautrix.util.async_db import Database

from ..types import WazoID


@dataclass
class User:
    db: ClassVar[Database]

    mxid: UserID
    wazo_id: WazoID

    columns = 'mxid, wazo_id'
