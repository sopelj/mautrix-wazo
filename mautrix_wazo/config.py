from __future__ import annotations

from typing import NamedTuple

from mautrix.bridge.config import BaseBridgeConfig
from mautrix.client import Client
from mautrix.types import UserID
from mautrix.util.config import ConfigUpdateHelper

Permissions = NamedTuple("Permissions", relay=bool, user=bool, admin=bool, level=str)


class Config(BaseBridgeConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        super().do_update(helper)
        copy, copy_dict, base = helper

        copy("bridge.username_template")
        copy("bridge.displayname_template")
        copy("bridge.displayname_preference")
        copy("bridge.autocreate_group_portal")
        copy("bridge.double_puppet_server_map")
        copy("bridge.double_puppet_allow_discovery")

        copy("wazo.api_token")
        copy("wazo.api_url")

        copy_dict("bridge.permissions")
        copy("bridge.command_prefix")

    def _get_permissions(self, key: str) -> Permissions:
        level = self["bridge.permissions"].get(key, "")
        admin = level == "admin"
        user = level == "user" or admin
        relay = level == "relay" or user
        return Permissions(relay, user, admin, level)

    def get_permissions(self, mxid: UserID) -> Permissions:
        permissions = self["bridge.permissions"]
        if mxid in permissions:
            return self._get_permissions(mxid)

        _, homeserver = Client.parse_user_id(mxid)
        if homeserver in permissions:
            return self._get_permissions(homeserver)

        return self._get_permissions("*")
