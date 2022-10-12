from __future__ import annotations

from mautrix.bridge import BasePuppet
from mautrix.types import UserID
from mautrix.appservice import IntentAPI
from mautrix.util.simple_template import SimpleTemplate

from .config import Config
from .db.puppet import Puppet as DBPuppet


class Puppet(DBPuppet, BasePuppet):
    by_pk: dict[int, Puppet] = {}
    by_custom_mxid: dict[UserID, Puppet] = {}
    hs_domain: str
    mxid_template: SimpleTemplate[int]

    config: Config

    default_mxid_intent: IntentAPI
    default_mxid: UserID

    @classmethod
    async def get_by_mxid(cls, mxid: UserID) -> BasePuppet:
        pass

    @classmethod
    async def get_by_custom_mxid(cls, mxid: UserID) -> BasePuppet:
        pass

    async def save(self) -> None:
        pass
