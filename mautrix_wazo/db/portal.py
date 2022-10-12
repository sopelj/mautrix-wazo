from __future__ import annotations

from typing import ClassVar

from attr import dataclass
from mautrix.util.async_db import Database


@dataclass
class Portal:
    db: ClassVar[Database]
