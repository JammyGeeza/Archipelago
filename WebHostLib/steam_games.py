import os

import yaml
import datetime

from pony.orm import Database, Optional, PrimaryKey, Required, db_session

import Utils

# ------------------------------------------------------------------
# Dedicated connection to your Postgres server.
#
# This is intentionally a SEPARATE Database() instance from the one
# in WebHostLib/models.py (which is Archipelago's own room/seed/slot
# database). It's also separate from whatever connection multiserver.py
# opens - that's a different OS process and can't share this one
# regardless.
#
# Only the username/password are secret, so only those two are read
# from config.yaml. Everything else (host, database, schema) is a
# plain literal here - deliberately not routed through config.
#
# config.yaml still needs:
#   PG_USER: "multiserver"
#   PG_PASSWORD: "your-real-password"
#
# The config.yaml read itself is done directly here (not via Flask's
# app.config) because this module can get imported through more than
# one path at startup (e.g. via WebHostLib.options -> misc -> here,
# which happens BEFORE app.config.from_file() has run inside
# get_app()). A plain YAML read has no dependency on Flask's own
# bootstrap order, so it works no matter which path gets here first.
#
# Mirrors WebHost.py's own config.yaml lookup exactly, including its
# fallback to Utils.user_path() if the file isn't found relative to
# the current working directory.
# ------------------------------------------------------------------

_configpath = os.path.abspath("config.yaml")
if not os.path.exists(_configpath):
    _configpath = os.path.abspath(Utils.user_path("config.yaml"))

_config = {}
if os.path.exists(_configpath):
    with open(_configpath) as _f:
        _config = yaml.safe_load(_f) or {}

db = Database()

db.bind(
    provider="postgres",
    #host="host.docker.internal",
    host="gregipelago.com",
    user=_config.get("PG_USER"),
    password=_config.get("PG_PASSWORD"),
    database="hetzner",
    connect_timeout=10,
    sslmode="require",
    options="-c search_path=gregipelago",
)


class SteamGame(db.Entity):
    """Maps an Archipelago world's display name (exactly as it
    appears in the supported-games list) to how it should be checked.

    Deliberately keyed by game name, not AppID, because some AppIDs
    cover multiple AP games (e.g. DOOM 1993 and DOOM II share 2280).

    platform is one of:
      'steam'    - steam_appid is required, checked live against Steam
      'emulator' - not purchasable/ownable, no steam_appid
      'other'    - itch.io / GOG / Battle.net / etc purchase, can't
                   be verified, no steam_appid
      'native'   - free AP-community download (e.g. APdoku), no
                   steam_appid - gets its own category, distinct
                   from an owned Steam game
    """

    _table_ = ("gregipelago", "steam_games")

    id = PrimaryKey(int, auto=True)
    game_name = Required(str, unique=True)
    steam_appid = Optional(int, index=True)
    platform = Required(str, default="steam")


class NewroomSend(db.Entity):
    """Room-creation log, moved here from misc.py's own previously-
    separate Database()/bind() - that block had the identical
    app.config import-order problem SteamGame just had, and having
    a THIRD independent connection to the same Postgres server in
    one process was the underlying cause repeating itself. One
    shared, self-contained db connection for everything in this file.
    """

    _table_ = ("gregipelago", "roomdata")

    id = PrimaryKey(int, auto=True)
    roomid = Required(str)
    timestamp = Required(datetime.datetime, default=lambda: datetime.datetime.now(datetime.UTC))


db.generate_mapping(create_tables=False)


@db_session
def send_newroom(roomid):
    NewroomSend(roomid=roomid)