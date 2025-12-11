from worlds.AutoWorld import World, WebWorld
from BaseClasses import Tutorial
from .Items import item_name_to_id_lookup
from .Locations import location_name_to_id_lookup
from .Options import CastNChillOptions

class CastNChillWeb(WebWorld):

    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Cast n Chill randomizer connected to an Archipelago Multiworld",
        "English",
        "setup_en.md",
        "setup\en",
        ["JammyGeeza"]
    )]
    theme = "jungle"


class CastNChillWorld(World):
    """
    Cast n Chill - [Description Here]
    """

    game = "Cast n Chill"
    web = CastNChillWeb()
    topology_present = False

    options_dataclass = CastNChillOptions
    options: CastNChillOptions

    item_name_to_id = item_name_to_id_lookup
    location_name_to_id = location_name_to_id_lookup

    required_client_version = (0, 6, 5)

