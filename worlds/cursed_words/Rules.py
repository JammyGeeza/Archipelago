from BaseClasses import Item, ItemClassification, Location, Region
from rule_builder.rules import Has
from typing import Dict, Tuple
from worlds.AutoWorld import World
from .classes.Constants import CHARACTER_NAMES, CROWN_NAMES, STAGE_PERCENTAGES
from .Options import Goal

def generate_stage_thresholds(percentages: Tuple[float, ...], total: int) -> Dict[str, int]:
    """Create the Stage 1-5 'critical' item thresholds, resolved in the access rules."""
    stage_names = [f"stage_{n}" for n in range(1, 6)]
    return {name: round(total * percent) for name, percent in zip(stage_names, percentages)}

def generate_all_group_thresholds(item_name_groups: Dict[str, set]) -> Dict[str, Dict[str, int]]:
    """Generate the Sticker / Stamp synergy thresholds for each character"""

    thresholds: Dict[str, Dict[str, int]] = {}
    
    for character in CHARACTER_NAMES:
        for kind in ("Stickers", "Stamps"):
            group = f"{character}: {kind} Synergy"
            total = len(item_name_groups.get(group, set()))
            thresholds[group] = generate_stage_thresholds(STAGE_PERCENTAGES[character], total)

    return thresholds

def generate_goal_events(world: World):
    """Create goal event locations and items for each goal character."""

    # Select region suffix based on goal in player YAML options
    match world.options.goal.value:
        case Goal.option_runs:
            region_name = "Stage 5"
        case Goal.option_michael:
            region_name = "Michael"
        case Goal.option_crowns:
            region_name = f"{CROWN_NAMES[world.options.crowns.value - 1]} Crown - Stage 5"
        case _:
            raise Exception(f"Unhandled goal value: {world.options.goal.value}")

    # Add victory item for each character in player YAML options
    for character in world.options.goal_characters.value:

        region: Region = world.multiworld.get_region(f"{character}: {region_name}", world.player)

        event: Location = Location(world.player, f"Beat {region_name} with {character}", None, region)
        event.place_locked_item(Item("Victory", ItemClassification.progression, None, world.player))

        region.locations.append(event)

def generate_goal(world: World):
    """Set the goal completion rule."""
    world.set_completion_rule(Has("Victory", len(world.options.goal_characters.value)))