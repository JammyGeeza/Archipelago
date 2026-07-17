from BaseClasses import Item, ItemClassification, Location, Region
import logging
from rule_builder.rules import Has
from typing import Dict, List, Tuple
from worlds.AutoWorld import World
from worlds.generic.Rules import set_rule
from .Locations import CursedWordsLocation
from .Regions import CursedWordsRegion

# Most relevant Sticker / Stamp groups per character
CHARACTER_BUILD_GROUPS: Dict[str, List[str]] = {
    "Rodman": [ "Blue Scattering", "Blue Scoring", "Red Scattering", "Red Scoring" ],
    "Nina Nix": [ "Shiny Scattering", "Shiny Scoring", "Void Scattering", "Void Scoring" ],
    "Hayley Bayles": [ "Number Scattering", "Number Scoring" ],
    "Sam Gambit": [ "Chess Scattering", "Chess Scoring" ],
    "Bones the Dog": [ "Card Scattering", "Card Scoring" ],
    "Octacles": [ "Cursed Scattering", "Cursed Scoring" ]
}

# The 'standard' threshold for group Sticker / Stamp requirements
STANDARD_GROUP_THRESHOLD: Tuple[float, float, float, float, float] = (0.0, 0.10, 0.25, 0.50, 0.75)

# Group-specific overrides for group Sticker / Stamp requirements
# 'Cursed' groups are a combination of other groups, so should be trimmed down in comparison to the others
GROUP_THRESHOLD_OVERRIDES: Dict[str, Tuple[float, float, float, float, float]] = {
    "Cursed Scattering": (0.0, 0.10, 0.20, 0.30, 0.40),
    "Cursed Scoring": (0.0, 0.20, 0.30, 0.40, 0.60)
}

def generate_stage_thresholds(group: str, total: int) -> Dict[str, int]:
    percentages = GROUP_THRESHOLD_OVERRIDES.get(group, STANDARD_GROUP_THRESHOLD)
    stage_names = ["stage_1", "stage_2", "stage_3", "stage_4", "stage_5"]
    return {name: round(total * pct) for name, pct in zip(stage_names, percentages)}

def generate_goal_events(world: World):
    """Create goal event locations and items for each goal character."""

    for goal_character in world.options.goal.value:

        region: Region = world.multiworld.get_region(f"{goal_character}: Stage 5", world.player)

        event: Location = Location(world.player, goal_character, None, region)
        event.place_locked_item(Item("Victory", ItemClassification.progression, None, world.player))

        region.locations.append(event)


def generate_goal(world: World):
    """Set the goal completion rule."""

    world.set_completion_rule(Has("Victory", len(world.options.goal.value)))