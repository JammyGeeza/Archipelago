from dataclasses import dataclass
from BaseClasses import ItemClassification, Options
# from .Enums import GoalType
from .Items import item_table
import logging
from Options import Choice, OptionDict, OptionList, ItemDict, PerGameCommonOptions, StartInventoryPool, Toggle
from .Regions import region_table
from typing import Dict, List

# Pre-defined keys
_character_names = [ "Rodman", "Nina Nix", "Hayley Bayles" ]
_filler_item_names: List[str] = [ item.name for item in item_table if item.classification == ItemClassification.filler.value ]

class PlayableCharacters(OptionList):
    """
    Select character(s) to include as playable.

    Use [ "Rodman", "Nina Nix", "Hayley Bayles" ] etc. will all characters in the list as playable.
    Use [ "All" ] will select all characters as playable.
    """
    display_name = "Playable Characters"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = [ "All" ]

class StartingCharacter(OptionList):
    """
    Select the character to start with.

    Use [ "Rodman", "Nina Mix", "Hayley Bayles" ] etc. will select one character from the list as your starting character.
    Use [ "Random" ] will randomly select one character from <Playable Characters> as your starting character.

    NOTE: Manual selections MUST ONLY include characters selected in the <Playable Characters> option.
          If no characters match, it will default to 'Random'.
    """
    display_name = "Starting Character"
    valid_keys_casefold = False
    valid_keys = [ "Random" ] + _character_names
    default = [ "Random" ]

class Goal(OptionList):
    """
    Select character(s) required to win runs with to complete your goal.

    Use [ "Rodman", "Nina Nix", "Hayley Bayles" ] etc. will to select all characters in the list as required to goal.
    Use [ "All" ] will select all characters from <Playable Characters> as required to goal.

    NOTE: Manual selections MUST ONLY include characters selected in the <Playable Characters> option.
          If no characters match, it will default to 'All'.
    """
    display_name = "Goal"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = [ "All" ]

@dataclass
class CursedWordsOptions(PerGameCommonOptions):
    """"""
    characters: PlayableCharacters
    starting_character: StartingCharacter
    goal: Goal

    # Built-in
    start_inventory_from_pool: StartInventoryPool

    def resolve_options(self):
        """Resolve options to ensure successful generation."""

        logging.info(f"Playable Characters selection: {self.characters.value}")

        # Check if 'All' exists in Characters option
        if "All" in self.characters.value:
            logging.info(f"  -> 'All' found, including all characters...")
            self.characters.value = _character_names

        logging.info(f"Starting character selection: {self.starting_character.value}")
        
        # Check if 'Random' exists in Starting Character option
        if "Random" in self.starting_character.value:
            logging.info(f"  -> 'Random' found, selecting all characters from <Playable Characters> selection...")
            self.starting_character.value = self.characters.value
        else:
            logging.info(f"  -> Removing characters not included in <Playable Characters>...")
            self.starting_character.value = list(set(self.starting_character.value) & set(self.characters.value))

        # Revert to 'Random' if no characters remain
        if len(self.starting_character.value) == 0:
            logging.info(f"  -> No matching characters selected, defaulting to 'Random'...")
            self.starting_character.value = self.characters.value    

        logging.info(f"Goal selection: {self.goal.value}")

        # Check if 'All' exists in Goal options
        if "All" in self.goal.value:
            logging.info(f"  -> 'All' found, requiring all <Playable Characters> for goal...")
            self.goal.value = self.characters.value
        else:
            logging.info(f"  -> Removing characters not included in <Playable Characters>...")
            self.goal.value = list(set(self.starting_character.value) & set(self.characters.value))
        
        if len(self.goal.value) == 0:
            logging.info(f"  -> No matching characters selected, defaulting to 'All'...")
            self.goal.value = self.characters.value