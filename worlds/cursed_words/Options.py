from dataclasses import dataclass
from BaseClasses import ItemClassification, Options
# from .Enums import GoalType
from .Items import item_table
import logging
from Options import Choice, OptionDict, OptionList, ItemDict, PerGameCommonOptions, StartInventoryPool, Toggle
from .Regions import region_table
from typing import Dict, List

# Pre-defined keys
_character_names = [ "First Character" ]
_filler_item_names: List[str] = [ item.name for item in item_table if item.classification == ItemClassification.filler.value ]

class Goal(OptionList):
    """
    Character(s) required to win runs with to complete your goal.
    Use [ "All" ] to set all characters as required
    Use [ "First Character", "Nina Nix", "Hayley Bayles" ] etc. to select a custom set of characters.
    """
    display_name = "Goal"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = [ "All" ]

class Characters(OptionList):
    """
    Character(s) to include as playable in your session.
    Use [ "All" ] to include all characters as playable.
    Use [ "First Character", "Nina Nix", "Hayley Bayles" ] etc. to select a custom set of characters as playable.
    Selections from <Goal> will always be automatically included.
    """
    display_name = "Characters"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _character_names
    default = [ "All" ]

class StartingCharacter(OptionList):
    """
    The character to start the randomizer with - selection MUST MATCH character(s) from the <Character> option.
    Use [ "Nina Mix" ] to select a specific character to start with.
    Use [ "First Character", "Nina Mix", "Hayley Bayles" ] etc. to randomly select one from the list.
    Use [ "Random" ] to randomly select a character.
    """
    display_name = "Starting Characters"
    valid_keys_casefold = False
    valid_keys = [ "Random" ] + _character_names
    default = [ "Random" ]

class Mapsanity(Toggle):
    """
    All steps within each stage are included as location checks for each character.
    """
    display_name = "Mapsanity"
    default = 0

@dataclass
class CursedWordsOptions(PerGameCommonOptions):
    """"""
    goal: Goal
    characters: Characters
    starting_character: StartingCharacter
    mapsanity: Mapsanity

    # Built-in
    start_inventory_from_pool: StartInventoryPool

    def resolve_options(self):
        """Resolve options to ensure successful generation."""

        logging.info(f"Goal selection: {self.goal.value}")

        # Check if 'All' exists in Goal options
        if "All" in self.goal.value:
            logging.info(f"'All' entry found, requiring all characters for goal...")
            self.goal.value = _character_names

        logging.info(f"Character selection: {self.characters.value}")

        # Check if 'All' exists in Characters option
        if "All" in self.characters.value:
            logging.info(f"'All' entry found, including all characters...")
            self.characters.value = _character_names
        
        # Include characters from goal selection if missing from character selection
        for goal_character in [gc for gc in self.goal.value if gc not in self.characters.value ]:
            logging.info(f"'{goal_character}' goal character not defined in character inclusion, adding...")
            self.characters.value.append(goal_character)

        logging.info(f"Starting character selection: {self.starting_character.value}")

        # Check if 'Random' exists in Starting Character option
        if "Random" in self.starting_character.value:
            logging.info(f"'Random' entry found, including all characters from <Character> selection...")
            self.starting_character.value = self.characters.value

        # Remove characters from 'Starting Character' that don't match 'Characters' option
        mismatching_start_characters = [ sc for sc in self.starting_character.value if sc not in self.characters.value ]
        for mismatch in mismatching_start_characters:
            logging.info(f"'{mismatch}' not present in included characters, removing...")
            self.starting_character.value.remove(mismatch)

        # If no starting characters remain, default to Random
        if len(self.starting_character.value) == 0:
            logging.info("No starting characters defined, defaulting to 'Random'...")
            self.starting_character.value = self.characters.value