from dataclasses import dataclass
from BaseClasses import ItemClassification
from .classes.Constants import CHARACTER_NAMES
from .Items import item_table
from Options import Choice, DeathLink, ItemSet, OptionList, OptionSet, PerGameCommonOptions, Range, StartInventoryPool, Toggle
from .Regions import region_table
from typing import List

# Pre-defined keys
_character_names = list(CHARACTER_NAMES)
# _filler_item_names: List[str] = [ item.name for item in item_table if item.classification == ItemClassification.filler.value ]

_stamp_names: List[str] = [ item.name for item in item_table if "Stamps" in item.groups ]
_sticker_names: List[str] = [ item.name for item in item_table if "Stickers" in item.groups ]

class Characters(OptionList):
    """
    Select the character(s) to include in the seed.

    Using [ "Rodman", "Nina Nix", "Hayley Bayles" ] etc. will select these specific characters as playable.
    Using [ "All" ] will select all characters as playable.

    NOTE: Currently only Rodman, Nina Nix, Hayley Bayles, Sam Gambit, Bones the Dog and Octacles are implemented.
          Additional characters will be added soon.
    """
    display_name = "Characters"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = _character_names

class StartingCharacter(OptionList):
    """
    Select the character to start with.

    Using [ "Rodman", "Nina Mix", "Hayley Bayles" ] etc. will randomly select one of these specific characters as your starting character.
    Using [ "Random" ] will randomly select one character from <Characters> as your starting character.

    NOTE: Characters not included in <Characters> will be ignored and never selected as your starting character.
          If no characters match, it will default to 'Random'.
    """
    display_name = "Starting Character"
    valid_keys_casefold = False
    valid_keys = [ "Random" ] + _character_names
    default = [ "Random" ]

class Crowns(Choice):
    """
    Select the highest Crown Tier to include in the seed - each Tier will ALWAYS include all tiers below it.
        E.g. Selecting <Crowns> = 'pink' will also include orange, yellow and purple.

    This setting adds the following to the seed:
      - '<Character>: Progressive Crown' items to the item pool, each unlocking the next crown tier for the specified character.
      - (<Characters> * <Crowns> * 15) locations to the location pool, one for every Encounter/Stage/Crown/Character combination.
            E.g. Selecting <Crowns> = 'red' and <Characters> = 'All' will add 630 locations.
    """
    display_name = "Crowns"
    option_none = 0
    option_purple = 1
    option_yellow = 2
    option_orange = 3
    option_pink = 4
    option_green = 5
    option_blue = 6
    option_red = 7
    default = option_none

class Michael(Toggle):
    """
    Adds a secret Stage 6 encounter with Michael as the boss, for each selected character.

    One of the two selectable bosses at the end of each Crown tier stage is 'cursed' - defeating it grants a Fairy.
    Collecting all 5 Fairies within a single Crown tier run and completing that tier's Stage 5 unlocks Stage 6,
    where Michael can be fought. Michael only needs to be defeated once, on any crown tier (earliest being Purple).

    NOTE: Requires <Crowns> to be set to at least 'Purple', since Michael can only be reached via a Crown tier.
          If enabled while <Crowns> is 'None', <Crowns> will automatically be set to 'Purple'.
    """
    display_name = "Michael"
    default = False

class Goal(Choice):
    """
    Select the goal for the seed.

    - runs: Beat at least one run with all <Characters>
    - michael: Beat <Michael> at least once with all <Characters>
    - crowns: Beat the highest <Crowns> run at least once with all <Characters>

    NOTE: If <Goal> = 'michael' but <Michael> = 'False', then <Michael> will be forced to 'True'.
          If <Goal> = 'crowns' but <Crowns> = 'none', then <Crowns> will be forced to 'purple'.
    """

    display_name = "Goal"
    option_runs = 0
    option_michael = 1
    option_crowns = 2

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
    characters: Characters
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
    crowns: Crowns
    michael: Michael

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

        # If <Goal> = 'Michael' but <Michael> = 'False' OR <Goal> = 'Crowns' but <Crowns> = 'None', revert to <Goal> = 'Runs'
        if (self.goal.value == Goal.option_michael and not self.michael.value) or (self.goal.value == Goal.option_crowns and self.crowns.value == Crowns.option_none):
            self.goal.value = Goal.option_runs
        
        # If <Michael> = 'True' but <Crowns> = 'None', set <Crowns> to 'Purple' as Michael requires at least Purple Crown access.
        if self.michael.value and self.crowns.value == Crowns.option_none:
            self.crowns.value = Crowns.option_purple        