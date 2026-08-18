from worlds.AutoWorld import World, WebWorld
from BaseClasses import Item, ItemClassification, Tutorial
from .Items import CursedWordsItem, item_name_groups_lookup, item_name_to_id_lookup, item_table, generate_items, generate_filler_items
from .Locations import location_name_to_id_lookup, location_table
from .Options import CursedWordsOptions
from .Regions import CursedWordsRegion, region_table, generate_regions
from .Rules import generate_all_group_thresholds, CROWN_NAMES, generate_goal_events, generate_goal
import logging
import math
from typing import Any, Dict, List, Set, Tuple

class CursedWordsWeb(WebWorld):

    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Cursed Words randomizer connected to an Archipelago Multiworld",
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
        self.character_tags: List[str] = [
            *self.options.characters.value
        ]

        self.option_tags: List[str] = [
            *([self.options.shuffle_grid_size.display_name] if self.options.shuffle_grid_size.value else []),
            *([self.options.shuffle_inventory_slots.display_name] if self.options.shuffle_inventory_slots.value else []),
            *([self.options.shuffle_item_rarities.display_name] if self.options.shuffle_item_rarities.value else []),
            *([self.options.shuffle_locked_tile_positions.display_name] if self.options.shuffle_locked_tile_positions.value else []),
            *([self.options.bosssanity.display_name] if self.options.bosssanity.value else []),
            *([self.options.shopsanity.display_name] if self.options.shopsanity.value else []),
            *(["Crowns"] + list(CROWN_NAMES[:self.options.crowns.value]) if self.options.crowns.value else []),
            *([self.options.michael.display_name] if self.options.michael.value else []),
            
            # Additional tag inclusions go here
        ]

        logging.info(f"Selected option tags: {self.option_tags}")

        # Randomly select starting character
        self.start_character: str = self.random.choice(
            self.options.starting_character.value
        )

        # logging.info(f"Randomly selected '{self.start_character}' as starting character")

        # Pre-collect starting character so it's always in the initial state
        self.multiworld.push_precollected(self.create_item(self.start_character))
        
        # Pre-collect 12 common, generic starting stamps
        eligible_starting_stamps: List[str] = [
            stamp.name for stamp in item_table
            if len(stamp.character_tags) == 0
            and len(stamp.option_tags) == 0
            and "Stamps" in stamp.groups
            and stamp.metadata.get("rarity", 0) == 0
        ]

        for stamp in self.random.sample(eligible_starting_stamps, 12):
            self.multiworld.push_precollected(self.create_item(stamp))

        # Pre-collect 12 common, generic starting stickers
        eligible_starting_stickers: List[str] = [
            sticker.name for sticker in item_table
            if len(sticker.character_tags) == 0
            and len(sticker.option_tags) == 0
            and "Stickers" in sticker.groups
            and sticker.metadata.get("rarity", 0) == 0
        ]

        for sticker in self.random.sample(eligible_starting_stickers, 12):
            self.multiworld.push_precollected(self.create_item(sticker))

        # logging.info(f"Starting inventory from pool: {self.options.start_inventory_from_pool.value}")

        # Calculate the "critical" Character/Crown/Stage/Sticker-Stamp thresholds
        self.group_thresholds: Dict[str, Dict[str, int]] = generate_all_group_thresholds(item_name_groups_lookup)

        # If 'Progressive Tile Positions' is enabled, generate tile positions
        self.selected_tile_positions = []
        if self.options.shuffle_locked_tile_positions.value:
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
        if not hasattr(self, 'tags'):
            self.tags = []
        return generate_filler_items(self, 1)[0]

    def create_regions(self):
        """Create all applicable regions for the configured multiworld."""
        generate_regions(self)
        generate_goal_events(self)

    def set_rules(self):
         """Set access rules for regions, locations and goals."""
         generate_goal(self)

    def fill_slot_data(self) -> Dict[str, Any]:
        """Populate the slot data to send to the client."""

        # Add required options data
        slot_data: Dict[str, any] = self.options.as_dict(
            "characters",
            "crowns",
            "deathlink",
            "goal",
            "shuffle_grid_size",
            "shuffle_inventory_slots",
            "shuffle_item_rarities",
            "shuffle_locked_tile_positions",
            "shopsanity",
            "shopsanity_cost",
        )

        slot_data.update({
            "shuffle_locked_tile_positions_coords": self.selected_tile_positions,
        })

        return slot_data