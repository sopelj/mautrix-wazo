from __future__ import annotations

from mautrix import bridge as br
from mautrix.bridge import BaseUser, BasePortal, BasePuppet
from mautrix.types import UserID, RoomID
from mautrix.util.bridge_state import BridgeState

from .db.user import User as DBUser
from .types import WazoUserId


class UserError(Exception):
    pass


class User(DBUser, BaseUser):
    async def is_logged_in(self) -> bool:
        pass

    async def get_puppet(self) -> BasePuppet | None:
        pass

    async def get_portal_with(self, puppet: br.BasePuppet, create: bool = True) -> BasePortal | None:
        pass

    async def get_direct_chats(self) -> dict[UserID, list[RoomID]]:
        pass

    async def get_bridge_states(self) -> list[BridgeState]:
        pass

    @classmethod
    def get_by_wazo_id(cls, wazo_user_id: WazoUserId, create=True):
        # TODO: get or create/register a user object representing a wazo and matrix user
        if create:
            return cls(wazo_id=wazo_user_id)
        else:
            raise UserError

