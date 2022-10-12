from mautrix import bridge as br
from mautrix.bridge import BaseUser, BasePortal, BasePuppet
from mautrix.types import UserID, RoomID
from mautrix.util.bridge_state import BridgeState

from .db.user import User as DBUser


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

