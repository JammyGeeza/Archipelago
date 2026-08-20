from dataclasses import dataclass
from BaseClasses import ItemClassification
from .classes.Constants import CHARACTER_NAMES
from .Items import item_table
from Options import Choice, DeathLink, ItemSet, OptionDict, OptionError, OptionList, OptionSet, PerGameCommonOptions, Range, StartInventoryPool, Toggle
from .Regions import region_table
from typing import List

# Pre-defined keys
_character_names = list(CHARACTER_NAMES)
_stamp_names: List[str] = [ item.name for item in item_table if "Stamps" in item.groups ]
_sticker_names: List[str] = [ item.name for item in item_table if "Stickers" in item.groups ]
_filler_item_names: List[str] = [ item.name for item in item_table if item.classification == ItemClassification.filler.value ]

class Characters(OptionList):
    """
    Select the character(s) to include.

    Using [ "Rodman", "Nina Nix", "Hayley Bayles" ] etc. will select these specific characters as playable.
    Using [ "All" ] will select all supported characters as playable.

    NOTE: Currently only supports Rodman, Nina Nix, Hayley Bayles, Sam Gambit, Bones the Dog and Octacles.
          Additional characters will be supported in a future update.
    """
    display_name = "Characters"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = _character_names

class StartingCharacter(OptionList):
    """
    Select the character to start with.

    Using [ "Octacles" ] or any other single name will guarantee it as your starting character.
    Using [ "Nina Mix", "Hayley Bayles", "Bones the Dog" ] or any other combination of names will randomly select one as your starting character.
    Using [ "Random" ] will randomly select one character from your selected <Characters> as your starting character.

    NOTE: Any character names that are not selected via the <Characters> option will be ignored.
          If no character names match, this setting will default to 'Random'.
    """
    display_name = "Starting Character"
    valid_keys_casefold = False
    valid_keys = [ "Random" ] + _character_names
    default = [ "Random" ]

class Michael(Toggle):
    """
    Include locations for obtaining 5 Fairies and beating all Michael (Stage 6) encounters with each of your selected <Characters>.
    
    NOTE: Since Michael can only be reached via crown runs, this setting requires <Crowns> to be set to at least 'Purple'.
          If <Michael> = 'True' but <Crowns> = 'None', then <Crowns> will be forced to 'Purple'.
    """
    display_name = "Include Michael"
    default = False

class Crowns(Choice):
    """
    Include locations for beating all 5 Stages on each Crown Tier with each of your selected <Characters>.

    Use this setting to select the HIGHEST Crown Tier to include - all tiers below it will also be included.
    E.g. Selecting <Crowns> = 'Pink' will also include Orange, Yellow and Purple.

    Crown Tiers are unlocked by receiving '<Character>: Progressive Crown' items that make the next Crown Tier available for each of your <Characters>.
    Crown Tier progression remains linear as per vanilla - you must beat Purple before moving on to Yellow, etc.

    WARNING: Depending on your settings, this can add an exponential amount of locations to the pool.
             E.g. If <Crowns> = 'Red' and <Characters> = 'All' this will add the maximum of 630 locations. (<Characters> * <Crown Tiers> * 15)
    """
    display_name = "Include Crowns"
    option_none = 0
    option_purple = 1
    option_yellow = 2
    option_orange = 3
    option_pink = 4
    option_green = 5
    option_blue = 6
    option_red = 7
    default = option_none

class Goal(Choice):
    """
    Select the goal for the seed.

    - Runs: Beat at least one run with all selected <Goal Characters>.
    - Michael: Beat <Michael> at least once with all selected <Goal Characters> (requires <Michael> = 'True').
    - Crowns: Beat the highest <Crowns> Tier run at least once with all selected <Characters> (requires <Crowns> = 'Purple' or higher).

    NOTE: If the prerequisite options for 'Michael' or 'Crowns' goals are not met, then <Goal> will be forced back to 'Runs'.
    """

    display_name = "Goal"
    option_runs = 0
    option_michael = 1
    option_crowns = 2

class GoalCharacters(OptionList):
    """
    Select which <Characters> are required to achieve the <Goal> condition in order to reach the goal.

    Using [ "Sam Gambit" ] or any other single name will require only that character to reach the <Goal>.
    Using [ "Rodman", "Hayley Bayles", "Octacles" ] or any other combination of names will require these specific characters to reach the <Goal>.
    Using [ "All" ] will require all selected <Characters> to reach the <Goal>.

    NOTE: Any character names that are not selected via the <Characters> option will be ignored.
          If no character names match, this setting will default to 'All'.
    """
    display_name = "Goal Characters"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = _character_names

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
    Add locations for defeating each boss type (Axolotl, Badger, Bat etc.)
    
    NOTE: Does not currently support beating the boss versions of Sandy, Cretacious Meg, Human Boy or Beans.
          These will be supported in a future update.
    """
    display_name = "Boss-sanity"
    default = False

class Pinsanity(Toggle):
    """
    Add locations for upgrading the Left and Right sides of each <Characters> Pin

    NOTE: Toggling this setting to 'True' will add (<Characters> * 8) locations to the pool.
    """
    display_name = "Pinsanity"
    default = False

class Shopsanity(Toggle):
    """
    Add locations which can be checked by buying special 'Shopsanity' items in the shop.
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

class Tilesanity(Toggle):
    """
    Add locations for buying and submitting each Tile Colour and Glyph Type.

    NOTE: Does not currently support the Purple, White, Gold, Pink, Green, Cactus and Glitch colours, 
          Does not currently support the Item glyph type.
          These will be supported in a future update.
    """
    display_name = "Tilesanity"
    default = False

class FillerWeighting(OptionDict):
    """
    Customise how often each filler item can appear in the item pool, relative to the other filler items.
    
    Higher numbers appear more often, lower numbers appear less often, '0' will exclude it entirely.
    Items removed from the list will default to '1'.

    At least one item must have a value greater than '0'.
    
    E.g: { "$1": 3, "Consumable Tile": 1, "Extra Re-Roll": 0 }
         Makes '$1' three times more likely to appear than 'Consumable Tile' and 'Extra-Re-Roll' is excluded entirely.
         All unlisted items will be equally as likely to appear as 'Consumable Tile'.
    """
    display_name = "Filler Weighting"
    valid_keys = frozenset(_filler_item_names)
    default = {
        "$1": 1,
        "$2": 1,
        "$3": 1,
        "Consumable Tile": 1,
        "Extra Re-roll": 1,
        "Random Tile Boost": 1
    }

    def verify(self, world, player_name, plando_options):
        super().verify(world, player_name, plando_options)

        # Check that no values are below 0
        if self.value and any(weight < 0 for weight in self.value.values()):
            raise OptionError(f"{player_name}: Filler Weighting values cannot be set to a negative number.")

        # Check that at least one value is above 0
        if self.value and not any(weight > 0 for weight in self.value.values()):
            raise OptionError(f"{player_name}: Filler Weighting values cannot all be set to 0.")

@dataclass
class CursedWordsOptions(PerGameCommonOptions):
    """"""
    characters: Characters
    starting_character: StartingCharacter
    michael: Michael
    crowns: Crowns
    goal: Goal
    goal_characters: GoalCharacters
    guaranteed_stamps: GuaranteedStamps
    guaranteed_stickers: GuaranteedStickers
    deathlink: DeathLink
    shuffle_grid_size: ShuffleGridSize
    shuffle_inventory_slots: ShuffleInventorySlots
    shuffle_item_rarities: ShuffleItemRarities
    shuffle_locked_tile_positions: ShuffleLockedTilePositions
    bosssanity: Bosssanity
    pinsanity: Pinsanity
    shopsanity: Shopsanity
    shopsanity_limit: ShopsanityLimit
    shopsanity_cost: ShopsanityCost
    tilesanity: Tilesanity
    filler_weighting: FillerWeighting

    # Built-in
    start_inventory_from_pool: StartInventoryPool

    def _resolve_character_option(self, option: OptionList, wildcard: str):
        """
        Resolve a character option against the selected <Characters> option.
        """
        # If empty list, revert to default
        if len(option.value) == 0:
            option.value = option.default

        # If wildcard present, set to selected <Characters>, otherwise ignore un-selected <Characters>
        if wildcard in option.value:
            option.value = self.characters.value
        else:
            option.value = list(set(option.value) & set(self.characters.value))

        # If now empty, revert to selected <Characters>
        if len(option.value) == 0:
            option.value = self.characters.value


    def resolve_options(self):
        """Resolve options to ensure successful generation."""

        # ***** Character selection *****

        # Revert to default if empty list provided
        if len(self.characters.value) == 0:
            self.characters.value = self.characters.default

        # Check if 'All' exists in Characters option
        if "All" in self.characters.value:
            self.characters.value = _character_names

        # ***** Starting Character selection
        self._resolve_character_option(self.starting_character, "Random")

        # ***** Goal Character selection *****
        self._resolve_character_option(self.goal_characters, "All")

        # If <Goal> = 'Michael' but <Michael> = 'False' OR <Goal> = 'Crowns' but <Crowns> = 'None', revert to <Goal> = 'Runs'
        if (self.goal.value == Goal.option_michael and not self.michael.value) or (self.goal.value == Goal.option_crowns and self.crowns.value == Crowns.option_none):
            self.goal.value = Goal.option_runs

        # logging.info(f"Goal selection: {self.goal.value}")
        
        # If <Michael> = 'True' but <Crowns> = 'None', set <Crowns> to 'Purple' as Michael requires at least Purple Crown access.
        if self.michael.value and self.crowns.value == Crowns.option_none:
            self.crowns.value = Crowns.option_purple

        # logging.info(f"Crowns selection: {self.crowns.value}")