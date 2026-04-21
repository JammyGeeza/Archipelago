from worlds.AutoWorld import World, WebWorld
from BaseClasses import Item, ItemClassification, Tutorial
from .Items import CursedWordsItem, item_name_to_id_lookup, item_table, create_items, create_filler_items
from .Locations import location_name_to_id_lookup
from .Options import CursedWordsOptions
from .Regions import CursedWordsRegion, region_table, create_regions
import logging
from typing import Any, Dict, List

class CursedWorldsWeb(WebWorld):

    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Cursed Worlds randomizer connected to an Archipelago Multiworld",
        "English",
        "setup_en.md",
        "setup\en",
        ["JammyGeeza"]
    )]
    theme = "jungle"


class CursedWordsWorld(World):
    """
    Cursed Words - [Description Here]
    """

    game = "Cursed Words"
    web = CursedWorldsWeb()
    topology_present = False

    options_dataclass = CursedWordsOptions
    options: CursedWordsOptions

    item_name_to_id = item_name_to_id_lookup
    location_name_to_id = location_name_to_id_lookup

    def generate_early(self):
        """Perform actions before generation."""

        # Resolve options to ensure generation is successful
        self.options.resolve_options()

        # Gather inclusions for run (determines what items/locations/regions to include in the run)
        self.inclusions: List[str] = self.options.characters.value

        # Add 'Mapsanity' as an inclusion if toggled on
        if self.options.mapsanity.value:
            self.inclusions.append("Mapsanity")

        logging.info(f"Selecting starting character ...")

        # Randomly select starting character
        self.start_character: str = self.random.choice(
            self.options.starting_character.value
        )

        logging.info(f"Selected '{self.start_character}' as starting character")

        # Add character as starting item from pool
        self.options.start_inventory_from_pool.value.update({ f"{self.start_character}": 1 })

        logging.info(f"Starting inventory from pool: {self.options.start_inventory_from_pool.value}")

    def create_items(self):
        """Create all items for the item pool."""
        create_items(self)

    def create_item(self, name: str) -> Item:
        """Create an item - used when StartInventoryPool pre-collects an item."""
        item_model: CursedWordsItem = next(item for item in item_table if item.name == name)
        return Item(item_model.name, item_model.classification, item_model.id, self.player)
    
    def create_filler(self):
        """Create a filler item - used when StartInventoryPool needs to fill a gap created by pre-collected items."""
        return create_filler_items(self, 1)[0]

    def create_regions(self):
        """Create all applicable regions for the configured multiworld."""
        create_regions(self)

    def set_rules(self):
         """Set access rules for regions, locations and goals."""
        #  set_goal(self.multiworld, self.player)

    def fill_slot_data(self) -> Dict[str, Any]:
        """Populate the slot data to send to the client."""

        # Add required options data
        slot_data: Dict[str, any] = self.options.as_dict(
            "goal",
            "characters",
        )

        return slot_data