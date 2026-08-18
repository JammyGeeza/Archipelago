from BaseClasses import Item, ItemClassification, Location, Region
from rule_builder.rules import Has
from typing import Dict, Tuple
from worlds.AutoWorld import World
from .Options import Goal
from .classes.Constants import CHARACTER_NAMES, CROWN_NAMES

# Required Sticker/Stamp item percentages for each stage.
# (Yes, it's gross that it's hard-coded but it makes tweaking them easier in future)
STAGE_PERCENTAGES: Dict[Tuple[str, str], Tuple[float, float, float, float, float]] = {
    ("Rodman", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
    ("Rodman", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
    ("Rodman", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
    ("Rodman", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
    ("Rodman", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
    ("Rodman", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
    ("Rodman", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
    ("Rodman", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),

    ("Nina Nix", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
    ("Nina Nix", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
    ("Nina Nix", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
    ("Nina Nix", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
    ("Nina Nix", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
    ("Nina Nix", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
    ("Nina Nix", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
    ("Nina Nix", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),

    ("Hayley Bayles", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
    ("Hayley Bayles", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
    ("Hayley Bayles", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
    ("Hayley Bayles", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
    ("Hayley Bayles", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
    ("Hayley Bayles", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
    ("Hayley Bayles", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
    ("Hayley Bayles", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),

    ("Sam Gambit", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
    ("Sam Gambit", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
    ("Sam Gambit", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
    ("Sam Gambit", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
    ("Sam Gambit", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
    ("Sam Gambit", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
    ("Sam Gambit", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
    ("Sam Gambit", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),

    ("Bones the Dog", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
    ("Bones the Dog", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
    ("Bones the Dog", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
    ("Bones the Dog", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
    ("Bones the Dog", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
    ("Bones the Dog", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
    ("Bones the Dog", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
    ("Bones the Dog", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),

    ("Octacles", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
    ("Octacles", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
    ("Octacles", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
    ("Octacles", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
    ("Octacles", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
    ("Octacles", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
    ("Octacles", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
    ("Octacles", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),
}


def generate_stage_thresholds(percentages: Tuple[float, ...], total: int) -> Dict[str, int]:
    """Create the Stage 1-5 'critical' item thresholds, resolved in the access rules."""
    stage_names = [f"stage_{n}" for n in range(1, 6)]
    return {name: round(total * percent) for name, percent in zip(stage_names, percentages)}


def generate_all_group_thresholds(item_name_groups: Dict[str, set]) -> Dict[str, Dict[str, int]]:
    """Create the Character x Crown x Stage x Sticker/Stamp item group thresholds, resolved in the access rules."""
    
    # Prepare thresholds
    thresholds: Dict[str, Dict[str, int]] = {}

    # Loop characters
    for character in CHARACTER_NAMES:
        for kind in ("Stickers", "Stamps"):
            group = f"{character}: Base {kind}"
            total = len(item_name_groups.get(group, set()))

            # Get thresholds for each stage, per character
            group_thresholds: Dict[str, int] = {}
            group_thresholds.update(generate_stage_thresholds(STAGE_PERCENTAGES[(character, "Base")], total))
            
            # Add stage thresholds for each crown
            for crown in CROWN_NAMES:
                crown_percentages = STAGE_PERCENTAGES[(character, crown)]
                stage_names = [ f"{crown.lower()}_stage_{n}" for n in range(1, 6) ]
                group_thresholds.update({
                    name: round(total * pct) for name, pct in zip(stage_names, crown_percentages)
                })

            thresholds[group] = group_thresholds

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