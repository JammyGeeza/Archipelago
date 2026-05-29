from BaseClasses import CollectionState, Item, ItemClassification, Location, MultiWorld, Region
import logging
from rule_builder.rules import CanReachLocation, Has, HasAll
from typing import Any, Dict, List
from worlds.AutoWorld import World
from worlds.generic.Rules import set_rule

def generate_goal_events(world: World):
    """Create goal event locations and items for each goal character."""

    for goal_character in world.options.goal.value:

        region: Region = world.multiworld.get_region(f"{goal_character} - Stage 5", world.player)

        event: Location = Location(world.player, goal_character, None, region)
        event.place_locked_item(Item("Victory", ItemClassification.progression, None, world.player))

        region.locations.append(event)


def generate_goal(world: World):
    """Set the goal completion rule."""

    world.set_completion_rule(Has("Victory", len(world.options.goal.value)))