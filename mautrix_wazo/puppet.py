from __future__ import annotations

from uuid import UUID

from mautrix.bridge import BasePuppet
from mautrix.types import UserID
from mautrix.appservice import IntentAPI
from mautrix.util.simple_template import SimpleTemplate
from yarl import URL

from .config import Config
from .db.puppet import Puppet as DBPuppet
from .types import WazoUUID


class Puppet(DBPuppet, BasePuppet):
    by_pk: dict[int, Puppet] = {}
    by_custom_mxid: dict[UserID, Puppet] = {}
    hs_domain: str
    mxid_template: SimpleTemplate[str]

    config: Config

    default_mxid_intent: IntentAPI
    default_mxid: UserID

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
    async def get_by_mxid(cls, mxid: UserID) -> BasePuppet | None:
        wazo_uuid = cls.get_id_from_mxid(mxid)
        if not wazo_uuid:
            return None
        return await cls.get_by_uuid(wazo_uuid)

    @classmethod
    async def get_by_custom_mxid(cls, mxid: UserID) -> BasePuppet:
        pass

    async def save(self) -> None:
        await self.update()
