from __future__ import annotations

from typing import AsyncIterable, Awaitable, TYPE_CHECKING

from mautrix import bridge as br
from mautrix.bridge import BaseUser, BasePortal, BasePuppet
from mautrix.types import UserID, RoomID
from mautrix.util.bridge_state import BridgeState
from aiohttp import ClientSession

from .db.user import User as DBUser
from .types import WazoUUID

if TYPE_CHECKING:
    from .__main__ import WazoBridge


class UserError(Exception):
    pass


class User(DBUser, BaseUser):
    @classmethod
    def init_cls(cls, bridge: "WazoBridge") -> None:
        cls.bridge = bridge
        cls.config = bridge.config
        cls.az = bridge.az
        cls.loop = bridge.loop

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
    async def get_wazo_user_info(cls, uuid: WazoUUID):
        base_url = cls.bridge.config['wazo.api_url']
        headers = {'X-Auth-Token': cls.bridge.config['wazo.api_token']}

        async with ClientSession() as session:
            async with session.get(f'{base_url}/confd/1.1/api/users/{uuid}', headers=headers) as response:
                return await response.json()

    @classmethod
    async def get_by_wazo_id(cls, wazo_user_uuid: WazoUUID, create=True) -> User:
        user = await cls.get_by_uuid(wazo_user_uuid)
        if user is not None:
            return user
        if create:
            user_info = await cls.get_wazo_user_info(wazo_user_uuid)
            cls.bridge.log.info(f'User info: {wazo_user_uuid}:', user_info)
            user = cls(
                wazo_uuid=wazo_user_uuid,
            )
        else:
            raise UserError

