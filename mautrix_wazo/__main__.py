from __future__ import annotations

from .wazo import app as wazo_app
from aiohttp.web import AppRunner, TCPSite
from mautrix.bridge import Bridge
from mautrix.types import RoomID, UserID

from .db import init as init_db, upgrade_table
from .config import Config
from .matrix import MatrixHandler
from .user import User
from .portal import Portal
from .puppet import Puppet
from . import __version__ as version


class WazoHandler:
    pass


class WazoBridge(Bridge):
    name = "mautrix-wazo"
    module = "mautrix_wazo"
    command = "python -m mautrix-wazo"
    description = "A Matrix-Wazo puppeting bridge."
    repo_url = "https://github.com/sopelj/mautrix-wazo"
    version = version
    markdown_version = f'[{version}](https://github.com/sopelj/mautrix-wazo/releases/tag/{version})'
    config_class = Config
    matrix_class = MatrixHandler
    upgrade_table = upgrade_table

    wazo_class = WazoHandler

    wazo_runner: AppRunner
    config: Config
    matrix: MatrixHandler
    wazo: WazoHandler

    def prepare_db(self) -> None:
        super().prepare_db()
        init_db(self.db)

    def prepare_bridge(self) -> None:
        # inject bridge into application server
        app = wazo_app.init()
        app["bridge"] = self
        self.wazo_runner = AppRunner(app)
        super().prepare_bridge()

    async def get_user(self, user_id: UserID, create: bool = True) -> User:
        return await User.get_by_mxid(user_id, create=create)

    async def get_portal(self, room_id: RoomID) -> Portal:
        return await Portal.get_by_mxid(room_id)

    async def get_puppet(self, user_id: UserID, create: bool = False) -> Puppet:
        return await Puppet.get_by_mxid(user_id, create=create)

    async def get_double_puppet(self, user_id: UserID) -> Puppet:
        return await Puppet.get_by_custom_mxid(user_id)

    def is_bridge_ghost(self, user_id: UserID) -> bool:
        return bool(Puppet.get_id_from_mxid(user_id))

    async def count_logged_in_users(self) -> int:
        return 1

    async def start(self) -> None:
        User.init_cls(self)
        Puppet.init_cls(self)
        Portal.init_cls(self)

        async def wazo_http_startup():
            self.log.info("Starting wazo webhook server")
            await self.wazo_runner.setup()
            site = TCPSite(self.wazo_runner, "0.0.0.0", 5000)

            await site.start()
            self.log.debug("Wazo webhook server site: %s", site.name)

        self.add_startup_actions(wazo_http_startup())
        await super().start()

    def prepare_stop(self) -> None:
        self.add_shutdown_actions(self.wazo_runner.cleanup())


WazoBridge().run()
