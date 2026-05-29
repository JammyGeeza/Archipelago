from dataclasses import dataclass
from BaseClasses import ItemClassification, Options
# from .Enums import GoalType
from .Items import item_table
import logging
from Options import DeathLink, OptionList, PerGameCommonOptions, Range, StartInventoryPool, Toggle
from .Regions import region_table
from typing import Dict, List

# Pre-defined keys
_character_names = [ "Rodman", "Nina Nix", "Hayley Bayles", "Bones the Dog", "Sam Gambit", "Octacles" ]
_filler_item_names: List[str] = [ item.name for item in item_table if item.classification == ItemClassification.filler.value ]

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

class Lengthsanity(Toggle):
    """
    Add location checks for submitting words with specified tile lengths.
    Words submitted must match the exact length to complete each check.
    
    EXAMPLES:
    - Submitting a word with 4 tiles will ONLY check 'Word Length 4'
    - Submitting a word with 8 tiles will ONLY check 'Word Length 8'
    """
    display_name = "Lengthsanity"
    default = False

class LengthsanityLimit(Range):
    """
    The highest word length to include as a <lengthsanity> location check.
    Lengthsanity checks are clamped at intervals of 1 and will add all checks up to the limit.

    EXAMPLES:
    - Setting the limit to 7 will add checks for word lengths of 1, 2, 3, ... 6 and 7
    - Setting the limit to 13 will add checks for word lengths of 1, 2, 3 ... 12 and 13

    NOTE: This setting is ignored if <lengthsanity> is 'False'
    """
    display_name = "Lengthsanity Limit"
    range_start = 1
    range_end = 15
    default = 12

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

class ShuffleTilePositions(Toggle):
    """
    The grid starts with 10 randomly selected tile positions being 'locked', making them un-selectable, and adds 10
    'Progressive Tile Position' items to the pool, each unlocking one locked tile position.
    """
    display_name = "Shuffle Tile Positions"
    default = False

class Scoresanity(Toggle):
    """
    Add location checks for submitting words with a total word score greater than specified amounts.
    Words submitted must have a score greater than or equal to the score for each check.
    
    EXAMPLES:
    - Submitting a word with a score of 125 will check 'Word Score > 100'
    - Submitting a word with a score of 886 will check all of 'Word Score > 100', 'Word Score > 200' ... 'Word Score > 700' and 'Word Score > 800'
    """
    display_name = "Scoresanity"
    default = False

class ScoresanityLimit(Range):
    """
    The highest word score to include as a <scoresanity> location check.
    Scoresanity checks are clamped to intervals of 100 and will add all checks up to the limit.
    
    EXAMPLES:
    - Setting the limit to 789 will add score checks for word scores 100, 200, 300, ... 600 and 700
    - Setting the limit to 4318 will add score checks for word scores 100, 200, 300, ... 4200 and 4300

    NOTE: This setting is ignored if <scoresanity> is set to 'False'.
    """
    display_name = "Scoresanity Limit"
    range_start = 100
    range_end = 3000
    default = 1000

class Shopsanity(Toggle):
    """
    Add items to the shop that can be purchased to check locations.
    """
    display_name = "Shopsanity"
    default = False

class ShopsanityLimit(Range):
    """
    The total amount of shop locations that will be available to purchase.

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
    deathlink: DeathLink
    lengthsanity: Lengthsanity
    lengthsanity_limit: LengthsanityLimit
    shuffle_grid_size: ShuffleGridSize
    shuffle_inventory_slots: ShuffleInventorySlots
    shuffle_tile_positions: ShuffleTilePositions
    scoresanity: Scoresanity
    scoresanity_limit: ScoresanityLimit
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