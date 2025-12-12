from worlds.AutoWorld import World, WebWorld
from BaseClasses import Item, Tutorial
from .Items import item_name_to_id_lookup, get_items
from .Locations import location_name_to_id_lookup
from .Options import CastNChillOptions
from .Regions import region_table, get_regions
import logging
from typing import List

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

    def generate_early(self):
        """Perform actions before generation."""

        # Check if no Spots provided in options or 'All' exists
        if len(self.options.spots.value) == 0 or "All" in self.options.spots.value:
            logging.info(f"Either no spots provided in options or 'All' found - adding all spots.")
            self.options.spots.value = [ region.name for region in region_table ]

    def create_items(self):
        """Create all items for the item pool."""
        logging.info(f"Creating items...")
        self.multiworld.itempool = get_items(self.multiworld, self.player)

    def create_regions(self):
        """Create all applicable regions for the configured multiworld."""

        logging.info(f"Creating regions...")
        self.multiworld.regions += get_regions(self.multiworld, self.player)
