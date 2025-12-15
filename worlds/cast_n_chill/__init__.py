from worlds.AutoWorld import World, WebWorld
from BaseClasses import Item, ItemClassification, Tutorial
from .Items import CastNChillItem, item_name_to_id_lookup, item_table, get_items
from .Locations import location_name_to_id_lookup
from .Options import CastNChillOptions
from .Regions import region_table, set_regions
from .Rules import set_goal
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

        # Check if no Spots provided or 'All' exists and return to default
        if len(self.options.spots.value) == 0 or "All" in self.options.spots.value:
            logging.warning(f"No spots provided OR 'All' entry found, treating as default.")
            self.options.spots.value = self.options.spots.default

        # Check if no Filler Weights provided and return to default
        if len(self.options.filler_weights.value) == 0:
            logging.warning(f"No filler weights provided, treating as default.")
            self.options.filler_weights.value = self.options.filler_weights.default

    def create_items(self):
        """Create all items for the item pool."""
        logging.info(f"Creating items...")
        self.multiworld.itempool = get_items(self.multiworld, self.player)

    def create_regions(self):
        """Create all applicable regions for the configured multiworld."""
        set_regions(self.multiworld, self.player)

    # TODO: Set goal
    def set_rules(self):
         set_goal(self.multiworld, self.player)
