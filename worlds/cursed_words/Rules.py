from BaseClasses import CollectionState, Item, ItemClassification, Location, MultiWorld, Region
import logging
from rule_builder.rules import CanReachLocation, Has
from typing import Any, Dict, List
from worlds.AutoWorld import World
from worlds.generic.Rules import set_rule

def generate_goal(world: World):
    """Set the goal condition"""

    # Get menu region
    menu_region: Region = world.multiworld.get_region("Menu", world.player)

    # Create goal event
    goal_location: Location = Location(world.player, "Goal Complete", None, menu_region)
    goal_location.place_locked_item(Item("Victory", ItemClassification.progression, None, world.player))

    # Require reaching all goal final levels
    for goal_character in world.options.goal.value:
        world.set_rule(goal_location, CanReachLocation(f"{goal_character} - 5-5 Complete"))
    
    # Add goal event to menu region
    menu_region.locations.append(goal_location)

    # Set rule to require victory event item
    world.set_completion_rule(Has("Victory"))