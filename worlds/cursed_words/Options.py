from dataclasses import dataclass
from BaseClasses import ItemClassification
from .classes.Constants import CHARACTER_NAMES
from .Items import item_table
from Options import Choice, DeathLink, ItemSet, OptionDict, OptionError, OptionList, OptionSet, PerGameCommonOptions, Range, StartInventoryPool, Toggle
from .Regions import region_table
from typing import List
import logging

# Pre-defined keys
_character_names = list(CHARACTER_NAMES)
_stamp_names: List[str] = [ item.name for item in item_table if "Stamps" in item.groups ]
_sticker_names: List[str] = [ item.name for item in item_table if "Stickers" in item.groups ]
_filler_item_names: List[str] = [ item.name for item in item_table if item.classification == ItemClassification.filler.value ]
_trap_item_names: List[str] = [ item.name for item in item_table if item.classification == ItemClassification.trap.value ]

class Characters(OptionList):
    """
    Select the character(s) to include - characters are 'unlocked' by receiving each character as an item.
    
    EXAMPLES:
    [ "Bones the Dog" ] will only include Bones the Dog as a playable character.
    [ "Rodman", "Nina Nix", "Hayley Bayles" ] will include only Rodman, Nina Nix and Hayley Bayles as playable characters.
    [ "All" ] will include all supported characters as playable characters.

    If an empty list is provided, it will be treated as [ "All" ].

    NOTE: Currently only supports Rodman, Nina Nix, Hayley Bayles, Sam Gambit, Bones the Dog and Octacles.
          Additional characters will be supported in a future update.
    """
    display_name = "Characters"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = _character_names

    def verify(self, world, player_name, plando_options):
        super().verify(world, player_name, plando_options)

        # If empty list, replace with 'All'
        if len(self.value) == 0:
            self.value = [ "All" ]

        # If 'All' is present, replace with all supported characters
        if "All" in self.value:
            self.value = list(_character_names)

        # Remove any duplicate names
        self.value = list(set(self.value) & set(_character_names))

class StartingCharacter(OptionList):
    """
    Select which of your selected <Characters> to start with.

    EXAMPLES:
    [ "Octacles" ] will guarantee Octacles as the starting character.
    [ "Nina Mix", "Hayley Bayles", "Bones the Dog" ] will randomly select one of Nina Nix, Hayley Bayles or Bones the Dog as the starting character.
    [ "Random" ] will randomly select one character from the <Characters> option as the starting character.

    Any names that do not match the characters selected in the <Characters> option will be ignored.
    If an empty list is provided or no characters match, it will be treated as [ "Random" ]
    
    NOTE: Currently only supports Rodman, Nina Nix, Hayley Bayles, Sam Gambit, Bones the Dog and Octacles.
          Additional characters will be supported in a future update.
    """
    display_name = "Starting Character"
    valid_keys_casefold = False
    valid_keys = [ "Random" ] + _character_names
    default = [ "Random" ]

    def verify(self, world, player_name, plando_options):
        super().verify(world, player_name, plando_options)

        # If empty list, replace with 'Random'
        if len(self.value) == 0:
            self.value = [ "Random" ]

        # If 'Random' is present, switch to all supported characters
        if "Random" in self.value:
            self.value = list(_character_names)

        # Remove any duplicate names
        self.value = list(set(self.value) & set(_character_names))

class Goal(Choice):
    """
    Select the condition that the character(s) must reach to achieve the goal.

    Runs    -> All <Goal Characters> must successfully beat at least one run.
    Michael -> All <Goal Characters> must successfully beat Michael at least once.
    Crowns  -> All <Goal Characters> must beat the highest <Crowns> tier at least once.
    
    Michael goal requires <Michael> = 'True' and will be automatically adjusted if prerequisite not met.
    Crowns goal requires <Crowns> = 'Purple' (or higher) and will be automatically adjusted to 'Purple' if prerequisite not met.
    """

    display_name = "Goal"
    option_runs = 0
    option_michael = 1
    option_crowns = 2
    default = 0

class GoalCharacters(OptionList):
    """
    Select which of your selected <Characters> must complete the <Goal> condition to goal.

    EXAMPLES:
    [ "Sam Gambit" ] will require only Sam Gambit to complete the condition to goal.
    [ "Nina Mix", "Hayley Bayles", "Bones the Dog" ] will require Nina Nix, Hayley Bayles and Bones the Dog to complete the condition to goal.
    [ "All" ] will require all characters selected in the <Characters> option to complete the condition to goal.

    Any names that do not match the characters selected in the <Characters> option will be ignored.
    If an empty list is provided or no characters match, it will be treated as [ "All" ]

    NOTE: Currently only supports Rodman, Nina Nix, Hayley Bayles, Sam Gambit, Bones the Dog and Octacles.
          Additional characters will be supported in a future update.
    """
    display_name = "Goal Characters"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = _character_names

    def verify(self, world, player_name, plando_options):
        super().verify(world, player_name, plando_options)

        # If empty list, replace with 'Random'
        if len(self.value) == 0:
            self.value = [ "All" ]

        # If 'All' is present, switch to all supported characters
        if "All" in self.value:
            self.value = list(_character_names)

        # Remove any duplicate names
        self.value = list(set(self.value) & set(_character_names))

class Crowns(Choice):
    """
    Include locations for clearing all stages up to a maximum Crown tier for all selected <Characters>.

    Crown Tiers are unlocked by receiving '{Character}: Progressive Crown' items which make the next Crown Tier reachable for each selected <Characters>.
    The selected Crown tier will include ALL CROWN TIERS BELOW IT because crown progression remains as per vanilla (you must beat Purple before you can move on to Yellow etc).
    
    EXAMPLES:
    None    -> Does not include any Crown tiers.
    Yellow  -> Includes Purple and Yellow Crown tiers.
    Green   -> Includes Purple, Yellow, Orange, Pink and Green tiers.

    NOTE: If <Goal> = 'Crowns' and this setting is 'None', it will be automatically adjusted to 'Purple' to ensure generation succeeds.

    WARNING: This setting will add (<Characters> count * <Crowns> count * 15) locations to your location pool.
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

class Michael(Toggle):
    """
    Include locations for obtaining 5 Fairies and beating Michael for all selected <Characters>.

    NOTE: The earliest Michael can be reached is via a Purple Crown run so if <Crowns> = 'None', it will be automatically adjusted to 'Purple' to ensure generation succeeds.
          This means each of your selected <Characters> will need to receive one '{Character}: Progressive Crown' to reach Michael.
    
    WARNING: This setting will add (<Characters> count * 8) locations to your location pool.
    """
    display_name = "Include Michael"
    default = False

class ShuffleGridSize(Toggle):
    """
    Grid are reduced to 3x3 Tiles.
    2x 'Progressive Grid Size' items are added to the item pool which increase the grid size to 4x4 and then 5x5.
    """
    display_name = "Shuffle Grid Size"
    default = False

class ShuffleInventorySlots(Toggle):
    """
    Your inventory starts with all Sticker and Stamp Slots locked.
    5x 'Progressive Sticker Slot' and 5x 'Progressive Stamp Slot' items are added to the item pool, each unlocking one respective slot.
    """
    display_name = "Shuffle Inventory Slots"
    default = False

class ShuffleItemRarities(Toggle):
    """
    The shop only stocks items of 'Common' rarity.
    2x 'Progressive Item Rarity' items are added to the item pool which allow 'Rare' and then 'Legendary' items to be stocked.
    """
    display_name = "Shuffle Item Rarities"
    default = False

class ShuffleLockedTilePositions(Toggle):
    """
    Grids have 10 fixed tile positions removed, making them un-usable.
    10x 'Progressive Tile Position' items are added to the item pool, each unlocking a tile position.

    NOTE: The 10 positions are selected and balanced across the entire potential 5x5 grid size, meaning that
          any reduced grid sizes (from bosses or the <ShuffleGridSize> option) are still playable.
    """
    display_name = "Shuffle Locked Tile Positions"
    default = False

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

class Bosssanity(Toggle):
    """
    Add locations for defeating each "standard" boss type (Axolotl, Badger, Bat etc.)
    
    WARNING: This setting will add 15 locations to your location pool.
    """
    display_name = "Boss-sanity"
    default = False

class Pinsanity(Toggle):
    """
    Add locations for upgrading the Left and Right sides of each <Characters> Pin

    WARNING: This setting will add (<Characters> count * 8) locations to your location pool.

    NOTE: Does not currently support pin upgrade locations for the Michael stage.
          Support may be added in a future update
    """
    display_name = "Pinsanity"
    default = False

class Shopsanity(Toggle):
    """
    Add custom shopsanity items to the shop which can be purchased as locations.

    NOTE: Locations are split as evenly as possible across both the Stickers and the Stamps sections of the shop.
          Shopsanity items have a 33% chance to appear in the first slot of each section resoectively.
    """
    display_name = "Shopsanity"
    default = False

class ShopsanityLimit(Range):
    """
    Choose how many <Shopsanity> items will be added to the shop (and adds this many locations to your location pool).

    NOTE: If <Shopsanity> = 'False' then this setting will be ignored.
    """
    display_name = "Shopsanity Limit"
    range_start = 1
    range_end = 30
    default = 20

class ShopsanityCost(Range):
    """
    How much each <Shopsanity> item will cost to purchase.

    NOTE: If <Shopsanity> = 'False' then this setting will be ignored.
    """
    display_name = "Shopsanity Cost"
    range_start = 5
    range_end = 25
    default = 12

class Tilesanity(Toggle):
    """
    Add locations for both Buying and Submitting each Tile Colour and Glyph Type.

    WARNING: This setting will add 26 locations to your location pool.

    NOTE: Does not currently support the Purple, White, Gold, Pink, Green, Cactus and Glitch colours.
          Does not currently support the Item glyph type.
          Support may be added in a future update.
    """
    display_name = "Tilesanity"
    default = False

class TrapPercentage(Range):
    """
    Customise percentage of Filler items in the item pool that are replaced with Trap items.

    0       -> Will not include trap items in the item pool.
    1 - 100 -> Will replace XX% of filler items in the item pool with trap items.

    E.g. If your seed contains 20 Filler items and this value is set to '25', then 4 (25% of 20)
         filler items will be replaced with trap items.
    """
    display_name = "Trap Percentage"
    min = 0
    max = 100
    default = 20

class TrapWeighting(OptionDict):
    """
    Customise how often each Trap item can appear in the item pool, relative to the other Trap items.
    This setting will be ignored if <Trap Percentage> = '0'

    Higher numbers appear more often, lower numbers appear less often, '0' will exclude it entirely.
    Items removed from the list will default to '1'.

    At least one item must have a value greater than '0'.
    
    E.g: { "$1": 3, "Consumable Tile": 1, "Extra Re-Roll": 0 }
         Makes '$1' three times more likely to appear than 'Consumable Tile' and 'Extra-Re-Roll' is excluded entirely.
         All unlisted items will be equally as likely to appear as 'Consumable Tile'.
    """
    display_name = "Trap Weighting"
    valid_keys = frozenset(_trap_item_names)
    default = { key: 1 for key in valid_keys }

    def verify(self, world, player_name, plando_options):
        super().verify(world, player_name, plando_options)

        # Check that no values are below 0
        if self.value and any(weight < 0 for weight in self.value.values()):
            raise OptionError(f"{player_name}: Trap Weighting values cannot be set to a negative number.")

        # Check that at least one value is above 0
        if self.value and not any(weight > 0 for weight in self.value.values()):
            raise OptionError(f"{player_name}: Trap Weighting values cannot all be set to 0.")

class FillerWeighting(OptionDict):
    """
    Customise how often each Filler item can appear in the item pool, relative to the other Filler items.
    
    Higher numbers appear more often, lower numbers appear less often, '0' will exclude it entirely.
    Items removed from the list will default to '1'.

    At least one item must have a value greater than '0'.
    
    E.g: { "$1": 3, "Consumable Tile": 1, "Extra Re-Roll": 0 }
         Makes '$1' three times more likely to appear than 'Consumable Tile' and 'Extra-Re-Roll' is excluded entirely.
         All unlisted items will be equally as likely to appear as 'Consumable Tile'.
    """
    display_name = "Filler Weighting"
    valid_keys = frozenset(_filler_item_names)
    default = { key: 1 for key in valid_keys }

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

    goal: Goal
    goal_characters: GoalCharacters

    michael: Michael
    crowns: Crowns
    shuffle_grid_size: ShuffleGridSize
    shuffle_inventory_slots: ShuffleInventorySlots
    shuffle_item_rarities: ShuffleItemRarities
    shuffle_locked_tile_positions: ShuffleLockedTilePositions
    deathlink: DeathLink
    
    guaranteed_stamps: GuaranteedStamps
    guaranteed_stickers: GuaranteedStickers
    
    bosssanity: Bosssanity
    pinsanity: Pinsanity
    shopsanity: Shopsanity
    shopsanity_limit: ShopsanityLimit
    shopsanity_cost: ShopsanityCost
    tilesanity: Tilesanity
    
    trap_percentage: TrapPercentage
    trap_weighting: TrapWeighting
    filler_weighting: FillerWeighting

    # Built-in
    start_inventory_from_pool: StartInventoryPool

    def _resolve_character_option(self, option: OptionList, wildcard: str):
        """
        Resolve a character option against the selected <Characters> option.
        """
        # If wildcard present, set to selected <Characters>, otherwise ignore un-selected <Characters>
        if wildcard in option.value:
            option.value = self.characters.value

        # Remove characters not present in the selected <Characters> option.
        option.value = list(set(option.value) & set(self.characters.value))

        # If now empty, revert to selected <Characters>
        if len(option.value) == 0:
            option.value = self.characters.value


    def resolve_options(self):
        """Resolve options to ensure successful generation."""

        # ========== Character Selections ==========
        
        self._resolve_character_option(self.starting_character, "Random")
        self._resolve_character_option(self.goal_characters, "All")

        # ========== Goal Selection ==========

        # If goal is 'Michael' but Michael is not enabled, prevent generation.
        if self.goal.value == Goal.option_michael and not self.michael.value:
            logging.warning(f"<Goal> option was set to 'Michael' but the <Michael> option was disabled - the <Michael> option has been automatically adjusted to 'True'.")
            self.michael.value = True
        
        # If goal is 'Crowns' but Crowns is not enabled, prevent generation.
        if self.goal.value == Goal.option_crowns and self.crowns.value == Crowns.option_none:
            logging.warning(f"<Goal> option was set to 'Crowns' but the <Crowns> option was set to 'None' - the <Crowns> option has been automatically adjusted to 'Purple'.")
            self.crowns.value = Crowns.option_purple

        # If <Michael> option is 'true', force crowns to 'Purple' if it isn't already
        if self.michael.value and self.crowns.value == Crowns.option_none:
            logging.warning(f"<Michael> option was set to 'True' but the <Crowns> option was set to 'None' - the <Crowns> option has been automatically adjusted to 'Purple'.")
            self.crowns.value = Crowns.option_purple