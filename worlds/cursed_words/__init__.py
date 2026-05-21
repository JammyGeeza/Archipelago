from worlds.AutoWorld import World, WebWorld
from BaseClasses import Item, ItemClassification, Tutorial
from .Items import CursedWordsItem, item_name_groups_lookup, item_name_to_id_lookup, item_table, generate_items, generate_filler_items
from .Locations import location_name_to_id_lookup, location_table
from .Options import CursedWordsOptions
from .Regions import CursedWordsRegion, region_table, generate_regions
from .Rules import generate_goal
import logging
import math
from typing import Any, Dict, List

class CursedWordsWeb(WebWorld):

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
    web = CursedWordsWeb()
    topology_present = False

    options_dataclass = CursedWordsOptions
    options: CursedWordsOptions

    item_name_to_id = item_name_to_id_lookup
    item_name_groups = item_name_groups_lookup

    location_name_to_id = location_name_to_id_lookup

    def generate_early(self):
        """Perform actions before generation."""

        # Resolve options to ensure generation is successful
        self.options.resolve_options()

        # Gather tags for run (determines what items/locations/regions to include in the run)
        self.tags: List[str] = [
            *self.options.characters.value,
            *([self.options.progressive_grid_size.display_name] if self.options.progressive_grid_size.value else []),
            *([self.options.progressive_tile_positions.display_name] if self.options.progressive_tile_positions.value else []),
            *([self.options.shopsanity.display_name] if self.options.shopsanity.value else [])
            # Additional tag inclusions go here...
        ]

        # logging.info(f"Selecting starting character ...")

        # Randomly select starting character
        self.start_character: str = self.random.choice(
            self.options.starting_character.value
        )

        # logging.info(f"Randomly selected '{self.start_character}' as starting character")

        # Add starting character as starting item from pool
        self.options.start_inventory_from_pool.value = { f"{self.start_character}": 1 }

        # logging.info(f"Starting inventory from pool: {self.options.start_inventory_from_pool.value}")

        # If 'Progressive Tile Positions' is enabled, generate tile positions
        self.selected_tile_positions = []
        if self.options.progressive_tile_positions.value:
            # To attempt to evenly spread locked tiles, split 5x5 grid into concentric 'L' shapes and randomly select
            # more from each larger 'L' shape - this should also mean a 3x3 starting grid from 'Progressive Grid Size'
            # will only ever contain 3 locked tile positions
            self.selected_tile_positions = (
                self.random.sample([[0,0], [0,1], [1,0], [1,1]], 1) +
                self.random.sample([[2,0], [2,1], [2,2], [1,2], [0,2]], 2) +
                self.random.sample([[3,0], [3,1], [3,2], [3,3], [2,3], [1,3], [0,3]], 3) +
                self.random.sample([[4,0], [4,1], [4,2], [4,3], [4,4], [3,4], [2,4], [1,4], [0,4]], 4)
            )

    def create_items(self):
        """Create all items for the item pool."""
        generate_items(self)

    def create_item(self, name: str) -> Item:
        """Create an item - used when StartInventoryPool pre-collects an item."""
        item_model: CursedWordsItem = next(item for item in item_table if item.name == name)
        return Item(item_model.name, item_model.classification, item_model.id, self.player)
    
    def create_filler(self):
        """Create a filler item - used when StartInventoryPool needs to fill a gap created by pre-collected items."""
        return generate_filler_items(self, 1)[0]

    def create_regions(self):
        """Create all applicable regions for the configured multiworld."""
        generate_regions(self)

    def set_rules(self):
         """Set access rules for regions, locations and goals."""
         generate_goal(self)

    def fill_slot_data(self) -> Dict[str, Any]:
        """Populate the slot data to send to the client."""

        # Add required options data
        slot_data: Dict[str, any] = self.options.as_dict(
            "deathlink",
            "goal",
            "progressive_grid_size",
            "shopsanity_location_count",
            "shopsanity_location_cost"
        )

        slot_data.update({
            "progressive_tile_positions": self.selected_tile_positions
        })

        return slot_data