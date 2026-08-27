from worlds.AutoWorld import World, WebWorld
from BaseClasses import Item, Tutorial
from .classes.Constants import CHARACTER_BUILDS, CHARACTER_NAMES, CROWN_NAMES, MONEY_EARNED_THRESHOLDS, WORD_SCORE_THRESHOLDS
from .Items import CursedWordsItem, item_name_groups_lookup, item_name_to_id_lookup, item_table, generate_items, generate_filler_items
from .Locations import location_name_to_id_lookup
from .Options import CursedWordsOptions
from .Regions import generate_regions
from .Rules import generate_all_group_thresholds, generate_goal_events, generate_goal
import logging
import math
from Options import OptionGroup
from typing import Any, Dict, List, Tuple

class CursedWordsWeb(WebWorld):

    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Cursed Words randomizer connected to an Archipelago Multiworld",
        "English",
        "setup_en.md",
        "setup\\en",
        ["JammyGeeza"]
    )]
    theme = "jungle"

    option_groups = [
        OptionGroup("Character Selection", [
            Options.Characters,
            Options.StartingCharacter,
            Options.StickerSynergies,
            Options.StampSynergies,
        ]),
        OptionGroup("Goal", [
            Options.Goal,
            Options.GoalCharacters
        ]),
        OptionGroup("Deathlink", [
            Options.DeathLink
        ]),
        OptionGroup("Core Locations", [
            Options.Crowns,
            Options.Michael,
            Options.MoneyEarned,
            Options.WordLengths,
            Options.WordScores,
        ]),
        OptionGroup("Extra Locations", [
            Options.Bosssanity,
            Options.Pinsanity,
            Options.Shopsanity,
            Options.ShopsanityCost,
            Options.ShopsanityLimit,
            Options.Tilesanity
        ]),
        OptionGroup("Extra Shuffling", [
            Options.ShuffleGridSize,
            Options.ShuffleInventorySlots,
            Options.ShuffleItemRarities,
            Options.ShuffleLockedTilePositions,
        ]),
        OptionGroup("Traps and Filler", [
            Options.TrapPercentage,
            Options.TrapWeighting,
            Options.FillerWeighting,
        ])
    ]


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
            *(["Crowns"] + list(CROWN_NAMES[:self.options.crowns.value]) if self.options.crowns.value else []),
            *(["Michael"] if self.options.michael.value else []),
            *([f"MoneyEarned{v}" for v in MONEY_EARNED_THRESHOLDS if v <= self.options.money_earned.value]),
            *([f"WordLength{v+1}" for v in range(0, self.options.word_lengths.value)]),
            *([f"WordScore{v}" for v in WORD_SCORE_THRESHOLDS if v <= self.options.word_scores.value]),
            *([self.options.shuffle_grid_size.display_name] if self.options.shuffle_grid_size.value else []),
            *([self.options.shuffle_inventory_slots.display_name] if self.options.shuffle_inventory_slots.value else []),
            *([self.options.shuffle_item_rarities.display_name] if self.options.shuffle_item_rarities.value else []),
            *([self.options.shuffle_locked_tile_positions.display_name] if self.options.shuffle_locked_tile_positions.value else []),
            *([self.options.bosssanity.display_name] if self.options.bosssanity.value else []),
            *([self.options.pinsanity.display_name] if self.options.pinsanity.value else []),
            *([self.options.shopsanity.display_name] if self.options.shopsanity.value else []),
            *([self.options.tilesanity.display_name] if self.options.tilesanity.value else []),
            
            # Additional tag inclusions go here
        ]

        # Randomly select starting character
        self.start_character: str = self.random.choice(
            self.options.starting_character.value
        )

        # Pre-collect starting character so it's always in the initial state
        self.multiworld.push_precollected(self.create_item(self.start_character))

        # Compile character synergies
        # NOTE: This is pretty much only here to stop the unit-tests failing, because it seems to bypass the verify step and use YAML
        #       defaults which happens to be [ "Default" ] instead of the actual resolved synergy items...
        def resolve_synergy(character: str, kind: str, raw: Dict[str, List[str]]) -> Tuple[str, ...]:
            build = raw.get(character, ["Default"])
            if "Default" in build or len(build) == 0:
                return tuple(CHARACTER_BUILDS[(character, kind)])
            return tuple(build)

        self.character_synergies: Dict[Tuple[str, str], Tuple[str, ...]] = {}
        for character in CHARACTER_NAMES:
            self.character_synergies[(character, "Stickers")] = resolve_synergy(character, "Stickers", self.options.sticker_synergies.value)
            self.character_synergies[(character, "Stamps")] = resolve_synergy(character, "Stamps", self.options.stamp_synergies.value)

        # Create character sticker / stamp synergy groups
        self.item_name_groups: Dict[str, set] = dict(item_name_groups_lookup)
        for character in CHARACTER_NAMES:
            for kind in ("Stickers", "Stamps"):
                self.item_name_groups[f"{character}: {kind} Synergy"] = set(self.character_synergies[(character, kind)])

        # Create backwards lookup for synergy groups
        self.item_name_to_groups_lookup: Dict[str, List[str]] = {}
        for group_name, member_names in self.item_name_groups.items():
            for member_name in member_names:
                self.item_name_to_groups_lookup.setdefault(member_name, []).append(group_name)

        # Get names of all items from character builds
        selected_character_synergy_names: set = {
            name
            for character in self.character_tags
            for kind in ("Stickers", "Stamps")
            for name in self.character_synergies[(character, kind)]
        }

        # Pre-collect 10 common, generic starting stamps that aren't in the builds
        eligible_starting_stamps: List[str] = [
            stamp.name for stamp in item_table
            if len(stamp.character_tags) == 0
            and len(stamp.option_tags) == 0
            and "Stamps" in stamp.groups
            and stamp.metadata.get("rarity", 0) == 0
            and stamp.name not in selected_character_synergy_names
        ]

        for stamp in self.random.sample(eligible_starting_stamps, 10):
            self.multiworld.push_precollected(self.create_item(stamp))

        # Pre-collect 10 common, generic starting stickers that aren't in the builds
        eligible_starting_stickers: List[str] = [
            sticker.name for sticker in item_table
            if len(sticker.character_tags) == 0
            and len(sticker.option_tags) == 0
            and "Stickers" in sticker.groups
            and sticker.metadata.get("rarity", 0) == 0
            and sticker.name not in selected_character_synergy_names
        ]

        for sticker in self.random.sample(eligible_starting_stickers, 10):
            self.multiworld.push_precollected(self.create_item(sticker))

        # Calculate the "critical" Character/Crown/Stage/Sticker-Stamp thresholds
        self.group_thresholds: Dict[str, Dict[str, int]] = generate_all_group_thresholds(self.item_name_groups)

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

            # Goal
            "goal",
            "goal_characters",

            # Run Options
            "crowns",
            "michael",
            "shuffle_grid_size",
            "shuffle_inventory_slots",
            "shuffle_item_rarities",
            "shuffle_locked_tile_positions",
            "deathlink",

            # Sanities
            "bosssanity",
            "shopsanity",
            "shopsanity_cost",
            "tilesanity",
        )

        slot_data.update({
            "shuffle_locked_tile_positions_coords": self.selected_tile_positions,
        })

        return slot_data