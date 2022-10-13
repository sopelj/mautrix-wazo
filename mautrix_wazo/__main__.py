from __future__ import annotations

import os

from aiohttp import web
from mautrix.bridge import Bridge, BaseUser, BasePortal, BasePuppet
from mautrix.types import RoomID, UserID

from .db import init as init_db, upgrade_table
from .config import Config
from .matrix import MatrixHandler
from .wazo import app as wazo_app
from . import __version__ as version


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

    config: Config
    matrix: MatrixHandler

    def prepare_db(self) -> None:
        super().prepare_db()
        init_db(self.db)

    async def get_user(self, user_id: UserID, create: bool = True) -> BaseUser | None:
        pass

    async def get_portal(self, room_id: RoomID) -> BasePortal | None:
        pass

    async def get_puppet(self, user_id: UserID, create: bool = False) -> BasePuppet | None:
        pass

    async def get_double_puppet(self, user_id: UserID) -> BasePuppet | None:
        pass

    def is_bridge_ghost(self, user_id: UserID) -> bool:
        pass

    async def count_logged_in_users(self) -> int:
        pass

    async def start(self) -> None:
        runner = web.AppRunner(wazo_app.app)

        async def wazo_http_startup():
            self.log.info("Starting wazo webhook server")
            await runner.setup()
            site = web.TCPSite(runner, os.getenv("HOST", "0.0.0.0"), os.getenv("PORT", 8000))

            await site.start()
            self.log.debug("Wazo webhook server site: %s", site.name)

        self.add_startup_actions(wazo_http_startup())
        self.add_shutdown_actions(runner.cleanup())
        await super().start()


WazoBridge().run()
