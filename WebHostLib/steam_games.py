from pony.orm import Database, Optional, PrimaryKey, Required

from . import app

# ------------------------------------------------------------------
# Dedicated connection to your Postgres server.
#
# This is intentionally a SEPARATE Database() instance from the one
# in WebHostLib/models.py (which is Archipelago's own room/seed/slot
# database). It's also separate from whatever connection multiserver.py
# opens - that's a different OS process and can't share this one
# regardless. Same shape as your CompleteSend connection.
#
# Credentials come from config.yaml (same mechanism as STEAM_API_KEY)
# instead of being hardcoded here, so the password isn't sitting in
# a source file if this fork is ever pushed anywhere.
#
# ------------------------------------------------------------------

db = Database()

db.bind(
    provider="postgres",
    host="host.docker.internal",
    #host="gregipelago.com",
    user=app.config.get("PG_USER"),
    #user="multiserver",
    password=app.config.get("PG_PASSWORD"),
    #password="strongpassword",
    database="hetzner",
    connect_timeout=10,
    sslmode="require",
    options='-c search_path=gregipelago',
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


db.generate_mapping(create_tables=False)