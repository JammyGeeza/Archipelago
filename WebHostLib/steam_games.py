from pony.orm import Database, PrimaryKey, Required, Optional
 
from . import app
 
db = Database()
 
db.bind(
    provider="postgres",
    host="host.docker.internal",
    user=app.config.get("PG_USER"),
    password=app.config.get("PG_PASSWORD"),
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
      'itch'     - itch.io purchase, can't be verified, no steam_appid
      'native'   - free AP-community download (e.g. APdoku), no
                   steam_appid - treated the same as "owned" since
                   anyone can grab it for free
    """
 
    _table_ = ("gregipelago", "steam_games")
 
    id = PrimaryKey(int, auto=True)
    game_name = Required(str, unique=True)
    steam_appid = Optional(int, index=True)
    platform = Required(str, default="steam")
 
 
db.generate_mapping(create_tables=False)
