from __future__ import annotations

from mautrix.bridge.config import BaseBridgeConfig
from mautrix.util.config import ConfigUpdateHelper


class Config(BaseBridgeConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        super().do_update(helper)
        copy, copy_dict, base = helper

        copy("bridge.username_template")
        copy("wazo.api_token")
        copy("wazo.api_url")
