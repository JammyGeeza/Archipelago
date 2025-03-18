import logging
from typing import Dict, List, NamedTuple, Optional
from BaseClasses import Entrance, MultiWorld, Region
from .Locations import CheckType, LocationData, StacklandsLocation, goal_table, location_table, name_to_id as location_lookup

class RegionData(NamedTuple):
    locations: List[LocationData]
    exits: List[str]

# Regions table
region_table: Dict[str, RegionData] = {
    "Menu"      : RegionData([loc for loc in location_table if loc.region == "Menu"]        , [ "Start" ]),
    "Mainland"  : RegionData([loc for loc in location_table if loc.region == "Mainland"]    , [ "Rowboat"]),
    "Island"    : RegionData([loc for loc in location_table if loc.region == "Island"]      , [])
}

# Create a region
def create_region(world: MultiWorld, player: int, name: str) -> Region:
    
    # Create region object
    region = Region(name, player, world)
    region_data = region_table[name]

    # Get relevant options
    goal = world.worlds[player].options.goal.value
    mobsanity = world.worlds[player].options.mobsanity.value
    pause_enabled = world.worlds[player].options.pause_enabled.value

    # Get the goal data (if it exists in this region)
    goal_data = goal_table[goal] if goal_table[goal].region == name else None

    # Cycle through all location checks
    if region_data.locations:
        for loc in region_data.locations:

            # Skip mobsanity checks if not enabled
            if loc.check_type == CheckType.Mobsanity and mobsanity == False:
                continue

            # Skip this check if pausing is not enabled, as it becomes unachievable
            if not pause_enabled and loc.name == "Pause using the play icon in the top right corner":
                continue

            # Skip this check if the goal is set to 'Kill the Demon'
            if goal == 0 and loc.name == "Kill the Demon":
                continue

            # Add location check to region
            loc_obj = StacklandsLocation(player, loc, location_lookup[loc.name], region)
            region.locations.append(loc_obj)

    # Add exits to region, if provided
    if region_data.exits:
        for exit in region_data.exits:
            region.exits.append(Entrance(player, exit, region))

    # Add goal to region, if provided
    if goal_data:
        goal_obj = StacklandsLocation(player, goal_data, None, region)
        region.locations.append(goal_obj)   

    return region

# Create all regions
def create_all_regions(world: MultiWorld, player: int):

    # Get the goal from options
    goal = world.worlds[player].options.goal.value
    goal_evt = goal_table[goal]

    # Create regions
    world.regions += [
        create_region(world, player, "Menu"),
        create_region(world, player, "Mainland"),
        create_region(world, player, "Island")
    ]

    # Connect exits to regions
    world.get_entrance("Start", player).connect(world.get_region("Mainland", player))
    world.get_entrance("Rowboat", player).connect(world.get_region("Island", player))