from __future__ import annotations

import contextlib
from typing import cast, TYPE_CHECKING
from uuid import UUID

from mautrix.bridge import BasePuppet
from mautrix.types import UserID
from mautrix.appservice import IntentAPI
from mautrix.util.simple_template import SimpleTemplate
from yarl import URL
from aiohttp import ClientSession

from .config import Config
from .db.puppet import Puppet as DBPuppet
from .types import WazoUUID

if TYPE_CHECKING:
    from .__main__ import WazoBridge


class Puppet(DBPuppet, BasePuppet):
    hs_domain: str
    mxid_template: SimpleTemplate[str]
    bridge: WazoBridge

    config: Config

    default_mxid_intent: IntentAPI
    default_mxid: UserID

    by_uuid: dict[WazoUUID, Puppet] = {}

    @classmethod
    def init_cls(cls, bridge: "SignalBridge") -> None:
        cls.config = bridge.config
        cls.loop = bridge.loop
        cls.mx = bridge.matrix
        cls.az = bridge.az
        cls.hs_domain = cls.config["homeserver.domain"]
        cls.mxid_template = SimpleTemplate(
            cls.config["bridge.username_template"],
            "userid",
            prefix="@",
            suffix=f":{cls.hs_domain}",
            type=str,
        )
        cls.homeserver_url_map = {
            server: URL(url)
            for server, url in cls.config["bridge.double_puppet_server_map"].items()
        }
        cls.allow_discover_url = cls.config["bridge.double_puppet_allow_discovery"]
        cls.login_shared_secret_map = {
            server: secret.encode("utf-8")
            for server, secret in cls.config["bridge.login_shared_secret_map"].items()
        }
        cls.login_device_name = "Wazo Bridge"

    @classmethod
    def get_id_from_mxid(cls, mxid: UserID) -> WazoUUID | None:
        identifier = cls.mxid_template.parse(mxid)
        if not identifier:
            return None
        try:
            return WazoUUID(str(UUID(identifier)).lower())
        except ValueError:
            return None

    @classmethod
    def get_mxid_from_id(cls, uuid: WazoUUID) -> UserID:
        return UserID(cls.mxid_template.format_full(uuid))

    @classmethod
    async def get_by_mxid(cls, mxid: UserID, create=True) -> Puppet | None:
        wazo_uuid = cls.get_id_from_mxid(mxid)
        if not wazo_uuid:
            return None
        puppet = await cls.get_by_uuid(wazo_uuid)
        if puppet:
            cls.by_uuid[wazo_uuid] = puppet
            return puppet
        if create is True:
            return await cls._create_puppet_by_uuid(wazo_uuid)
        return None

    @classmethod
    async def get_by_custom_mxid(cls, mxid: UserID) -> Puppet:
        pass

    @classmethod
    async def _get_wazo_user_info(cls, uuid: WazoUUID) -> dict[str, str]:
        base_url = cls.bridge.config['wazo.api_url']
        headers = {'X-Auth-Token': cls.bridge.config['wazo.api_token']}

        async with ClientSession() as session:
            async with session.get(f'{base_url}/confd/1.1/api/users/{uuid}', headers=headers) as response:
                return await response.json()

    @classmethod
    async def get_by_uuid(cls, uuid: WazoUUID, create=True) -> Puppet | None:
        with contextlib.suppress(KeyError):
            return cls.by_uuid[uuid]

        puppet = cast(cls, await super().get_by_uuid(uuid))
        if puppet is not None:
            puppet.by_uuid[uuid] = puppet
            return puppet

        if create:
            return await cls._create_puppet_by_uuid(uuid)
        return None

    async def save(self) -> None:
        await self.update()

    @classmethod
    async def _create_puppet_by_uuid(cls, wazo_uuid):
        user_info = await cls._get_wazo_user_info(wazo_uuid)
        puppet = cls(
            wazo_uuid=wazo_uuid,
            first_name=user_info['firstname'],
            last_name=user_info['lastname'],
            username=user_info['username'] or user_info['email'],
        )
        await puppet.insert()
        cls.by_uuid[wazo_uuid] = puppet
        return puppet
