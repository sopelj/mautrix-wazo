from __future__ import annotations

from mautrix import bridge as br
from mautrix.bridge import BaseUser, BasePortal, BasePuppet
from mautrix.types import UserID, RoomID
from mautrix.util.bridge_state import BridgeState
from aiohttp import ClientSession

from .db.user import User as DBUser
from .types import WazoUUID


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

    async def get_wazo_user_info(self, uuid: WazoUUID):
        base_url = self.bridge.config['wazo.api_url']
        headers = {'X-Auth-Token': self.bridge.config['wazo.api_token']}

        async with ClientSession() as session:
            async with session.get(f'{base_url}/confd/1.1/api/users/{uuid}', headers=headers) as response:
                return await response.json()

    @classmethod
    def get_by_wazo_id(cls, wazo_user_id: WazoUUID, create=True):
        # TODO: get or create/register a user object representing a wazo and matrix user
        if create:
            return cls(wazo_uuid=wazo_user_id)
        else:
            raise UserError

