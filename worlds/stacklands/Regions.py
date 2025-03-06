import logging
from typing import List
from BaseClasses import Entrance, MultiWorld, Region
from .Locations import LocationData, StacklandsLocation, location_table, name_to_id as location_lookup

# Create a region
def create_region(world: MultiWorld, player: int, name: str, locations: List[LocationData]=None, exits: List[str]=None) -> Region:
    
    # Get relevant options
    pause_enabled = world.worlds[player].options.pause_enabled.value
    goal = world.worlds[player].options.goal.value

    region = Region(name, player, world)

    if locations:
        for location in locations:

            # Skip this location if pausing is not enabled
            if not pause_enabled and location.name == "Pause using the play icon in the top right corner":
                continue
            
            # Skip this location if the goal is set to 'Kill the Demon'
            if goal == 0 and location.name == "Kill the Demon Lord":
                continue

            loc_obj = StacklandsLocation(player, location, location_lookup[location.name], region)
            region.locations.append(loc_obj)

    if exits:
        for exit in exits:
            region.exits.append(Entrance(player, exit, region))

    return region

# Create all regions
def create_all_regions(world: MultiWorld, player: int):

    world.regions += [
        create_region(world, player, "Menu", None, [ "Start" ]),
        create_region(world, player, "Mainland", [location for location in location_table if location.region == "Mainland"])
    ]

    # Connect menu region to entrance of mainland
    world.get_entrance("Start", player).connect(world.get_region("Mainland", player))
        