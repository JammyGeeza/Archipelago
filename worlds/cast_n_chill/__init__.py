from worlds.AutoWorld import World, WebWorld
from BaseClasses import Item, ItemClassification, Tutorial
from .Items import CastNChillItem, item_name_to_id_lookup, item_table, get_items, get_filler_items
from .Locations import location_name_to_id_lookup
from .Options import CastNChillOptions
from .Regions import CastNChillRegion, region_table, set_regions
from .Rules import set_goal
import logging
from typing import Any, Dict

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

    def generate_early(self):
        """Perform actions before generation."""

        # Resolve options to ensure generation is successful
        self.options.resolve_options()

        logging.info(f"Selecting starting spot ...")

        # Randomly select the starting spot
        self.starting_spot: str = self.random.choices(
            population=list(self.options.starting_spot.keys()),
            weights=list(self.options.starting_spot.values()),
            k=1
        )[0]

        logging.info(f"Selected starting spot: {self.starting_spot}")

        # Add starting spot license to the starting items
        starting_region: CastNChillRegion = next(region for region in region_table if region.name == self.starting_spot)
        self.options.start_inventory_from_pool.value.update(starting_region.starting_inventory)

        logging.info(f"Added {self.starting_spot} to starting inventory")

    def create_items(self):
        """Create all items for the item pool."""
        logging.info(f"Creating items...")
        self.multiworld.itempool = get_items(self.multiworld, self.player)

    def create_item(self, name: str) -> Item:
        """Create an item - used when StartInventoryPool pre-collects an item."""
        item_model: CastNChillItem = next(item for item in item_table if item.name == name)
        return Item(item_model.name, item_model.classification, item_model.id, self.player)
    
    def create_filler(self):
        """Create a filler item - used when StartInventoryPool needs to fill a gap created by pre-collected items."""
        return get_filler_items(self.multiworld, self.player, 1)[0]

    def create_regions(self):
        """Create all applicable regions for the configured multiworld."""
        set_regions(self.multiworld, self.player)

    def set_rules(self):
         """Set access rules for regions, locations and goals."""
         set_goal(self.multiworld, self.player)

    def fill_slot_data(self) -> Dict[str, Any]:
        """Populate the slot data to send to the client."""

        slot_data: Dict[str, Any] = {}
        
        # Add required options data
        slot_data = self.options.as_dict(
            "goal",
            "spots"
        )

        # Add any additional required data
        slot_data.update({
            "starting_spot": self.starting_spot
        })

        return slot_data