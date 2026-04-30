from BaseClasses import CollectionState, Item, ItemClassification, Location, MultiWorld, Region
import logging
from rule_builder.rules import CanReachLocation, Has, HasAll
from typing import Any, Dict, List
from worlds.AutoWorld import World
from worlds.generic.Rules import set_rule

def generate_goal(world: World):
    """Set the goal condition"""

    # Add events for each character's run completion
    for goal_character in world.options.goal.value:
        region: Region = world.multiworld.get_region(f"{goal_character} - Stage 5", world.player)

        logging.info(f"Creating goal location for region {region.name}")
        
        event: Location = Location(world.player, goal_character, None, region)
        event.place_locked_item(Item("Victory", ItemClassification.progression, None, world.player))
        
        # Add goal event to character's final stage
        region.locations.append(event)

    # Set rule to require victory event item
    world.set_completion_rule(Has("Victory", len(world.options.goal.value)))