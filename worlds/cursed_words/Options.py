from dataclasses import dataclass
from BaseClasses import ItemClassification, Options
# from .Enums import GoalType
from .Items import item_table
import logging
from Options import DeathLink, ItemSet, OptionList, OptionSet, PerGameCommonOptions, Range, StartInventoryPool, Toggle
from .Regions import region_table
from typing import Dict, List

# Pre-defined keys
_character_names = [ "Rodman", "Nina Nix", "Hayley Bayles", "Bones the Dog", "Sam Gambit", "Octacles" ]
_filler_item_names: List[str] = [ item.name for item in item_table if item.classification == ItemClassification.filler.value ]

_stamp_names: List[str] = [ item.name for item in item_table if "Stamps" in item.groups ]
_sticker_names: List[str] = [ item.name for item in item_table if "Stickers" in item.groups ]

class PlayableCharacters(OptionList):
    """
    Select character(s) to include as playable.

    Using [ "Rodman", "Nina Nix", "Hayley Bayles" ] etc. will select these specific characters as playable.
    Using [ "All" ] will select all characters as playable.
    """
    display_name = "Playable Characters"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = [ "All" ]

class StartingCharacter(OptionList):
    """
    Select the character to start with.

    Using [ "Rodman", "Nina Mix", "Hayley Bayles" ] etc. will randomly select one of these specific characters as your starting character.
    Using [ "Random" ] will randomly select one character from <Playable Characters> as your starting character.

    NOTE: Characters not included in <Playable Characters> will be ignored and never selected as your starting character.
          If no characters match, it will default to 'Random'.
    """
    display_name = "Starting Character"
    valid_keys_casefold = False
    valid_keys = [ "Random" ] + _character_names
    default = [ "Random" ]

class Goal(OptionList):
    """
    Select character(s) required to win runs with to complete your goal.

    Use [ "Rodman", "Nina Nix", "Hayley Bayles" ] etc. will select these three specific characters as required to goal.
    Use [ "All" ] will select all characters from <Playable Characters> as required to goal.

    NOTE: Characters not included in <Playable Characters> will be ignored and never selected as a goal requirement character.
          If no characters match, it will default to 'All'.
    """
    display_name = "Goal"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = [ "All" ]

class GuaranteedStickers(ItemSet):
    """
    Due to the large number of available stickers, most stickers are attributed to specific <Characters> to help ensure that
    stickers in the pool will synergise with the selected characters. This means that some stickers may not appear in the
    item pool if its character(s) have not been selected in the <Characters> option.

    If there are any stickers you want to guarantee are in the item pool please add them here.
    You can select a maximum of 10 Stickers, any stickers after the 10th will not be guaranteed.
    """
    display_name = "Guaranteed Stickers"
    valid_keys = frozenset(_sticker_names)
    convert_name_groups = False

    def verify(self, world, player_name, plando_options):
        super().verify(world, player_name, plando_options)

        # Remove duplicates, if any
        seen = []
        for name in self.value:
            if name not in seen:
                seen.append(name)
        self.value = seen

        # Trim any stickers over the 10 limit
        if len(self.value) > 10:
            self.value = seen[:10]

class GuaranteedStamps(OptionSet):
    """
    Due to the large number of available stamps, most stamps are attributed to specific <Characters> to help ensure that
    stamps in the pool will synergise with the selected characters. This means that some stamps may not appear in the
    item pool if its character(s) have not been selected in the <Characters> option.

    If there are any stamps you want to guarantee are in the item pool please add them here.
    You can select a maximum of 10 Stickers, any stamps after the 10th will not be guaranteed.
    """
    display_name = "Guaranteed Stamps"
    valid_keys = frozenset(_stamp_names)
    convert_name_groups = False

    def verify(self, world, player_name, plando_options):
        super().verify(world, player_name, plando_options)

        # Remove duplicates, if any
        seen = []
        for name in self.value:
            if name not in seen:
                seen.append(name)
        self.value = seen

        # Trim any stamps over the 10 limit
        if len(self.value) > 10:
            self.value = seen[:10]

class ShuffleGridSize(Toggle):
    """
    The grid starts as 3x3 tiles and adds two 'Progressive Grid Size' items to the pool, each increasing the grid size
    to 4x4 and then 5x5 tiles.
    """
    display_name = "Shuffle Grid Size"
    default = False

class ShuffleInventorySlots(Toggle):
    """
    Your inventory has all Sticker and Stamp Slots locked and cannot be used.
    5x 'Progressive Sticker Slot' and 5x 'Progressive Stamp Slot' items are added to the item pool, each unlocking one respective slot.
    """
    display_name = "Shuffle Inventory Slots"
    default = False

class ShuffleItemRarities(Toggle):
    """
    Adds two 'Progressive Item Rarity' items to the pool which will allow higher rarity items to appear in the shop.
    """
    display_name = "Shuffle Item Rarities"
    default = False

class ShuffleLockedTilePositions(Toggle):
    """
    The grid starts with 10 randomly selected tile positions being 'locked', making them un-selectable.
    Adds 10 'Progressive Tile Position' items to the pool, each unlocking one locked tile position.
    """
    display_name = "Shuffle Locked Tile Positions"
    default = False

class Bosssanity(Toggle):
    """
    Add checks for defeating each individual main boss.
    
    NOTE: Does not currently include Sandy, Cretacious Meg, Human Boy, Beans or Michael.
          Will be added in a future update.
    """
    display_name = "Boss-sanity"
    default = False

class Shopsanity(Toggle):
    """
    Add items to the shop that can be purchased to check locations.
    """
    display_name = "Shopsanity"
    default = False

class ShopsanityLimit(Range):
    """
    How many shop locations will be available for purchase.
    NOTE: This setting will be ignored if <shopsanity> is 'false'.
    """
    display_name = "Shopsanity Limit"
    range_start = 1
    range_end = 30
    default = 20

class ShopsanityCost(Range):
    """
    How much each shop location will cost to purchase.
    NOTE: This setting is ignored if <shopsanity> is 'false'.
    """
    display_name = "Shopsanity Cost"
    range_start = 5
    range_end = 25
    default = 12

@dataclass
class CursedWordsOptions(PerGameCommonOptions):
    """"""
    characters: PlayableCharacters
    starting_character: StartingCharacter
    goal: Goal
    guaranteed_stamps: GuaranteedStamps
    guaranteed_stickers: GuaranteedStickers
    deathlink: DeathLink
    shuffle_grid_size: ShuffleGridSize
    shuffle_inventory_slots: ShuffleInventorySlots
    shuffle_item_rarities: ShuffleItemRarities
    shuffle_locked_tile_positions: ShuffleLockedTilePositions
    bosssanity: Bosssanity
    shopsanity: Shopsanity
    shopsanity_limit: ShopsanityLimit
    shopsanity_cost: ShopsanityCost

    # Built-in
    start_inventory_from_pool: StartInventoryPool

    def resolve_options(self):
        """Resolve options to ensure successful generation."""

        # logging.info(f"Playable Characters selection: {self.characters.value}")

        # Revert to default if empty list provided
        if len(self.characters.value) == 0:
            self.characters.value = self.characters.default

        # Check if 'All' exists in Characters option
        if "All" in self.characters.value:
            # logging.info(f"  -> 'All' found, including all characters...")
            self.characters.value = _character_names

        # logging.info(f"Starting character selection: {self.starting_character.value}")
        
        # Revert to default if empty list provided
        if len(self.starting_character.value) == 0:
            self.starting_character.value = self.starting_character.default  

        # Check if 'Random' exists in Starting Character option
        if "Random" in self.starting_character.value:
            # logging.info(f"  -> 'Random' found, selecting all characters from <Playable Characters> selection...")
            self.starting_character.value = self.characters.value
        else:
            # logging.info(f"  -> Removing characters not included in <Playable Characters>...")
            self.starting_character.value = list(set(self.starting_character.value) & set(self.characters.value))

        # Revert to 'Random' if no characters remain
        if len(self.starting_character.value) == 0:
            # logging.info(f"  -> No matching characters selected, defaulting to 'Random'...")
            self.starting_character.value = self.characters.value    

        # logging.info(f"Goal selection: {self.goal.value}")

        # Revert to default if empty list provided
        if len(self.goal.value) == 0:
            self.goal.value = self.characters.default

        # Check if 'All' exists in Goal options
        if "All" in self.goal.value:
            # logging.info(f"  -> 'All' found, requiring all <Playable Characters> for goal...")
            self.goal.value = self.characters.value
        else:
            # logging.info(f"  -> Removing characters not included in <Playable Characters>...")
            self.goal.value = list(set(self.starting_character.value) & set(self.characters.value))
        
        if len(self.goal.value) == 0:
            # logging.info(f"  -> No matching characters selected, defaulting to 'All'...")
            self.goal.value = self.characters.value