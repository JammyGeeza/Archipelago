import logging
from typing import Dict, List, NamedTuple, Optional
from BaseClasses import CollectionState, Entrance, MultiWorld, Region
from .Locations import LocationData, StacklandsLocation, goal_table, location_table, name_to_id as location_lookup

class RegionData(NamedTuple):
    locations: List[LocationData]
    exits: List[str]

# Regions table
region_table: Dict[str, RegionData] = {
    "Menu"              : RegionData([loc for loc in location_table if loc.region == "Menu"]            , [ "Start" ]),
    "Mainland"          : RegionData([loc for loc in location_table if loc.region == "Mainland"]        , [ "Portal", "Rowboat" ]),
    "The Dark Forest"   : RegionData([loc for loc in location_table if loc.region == "The Dark Forest"] , {}),
    "Island"            : RegionData([loc for loc in location_table if loc.region == "Island"]          , {})
}

# Exits-to-Regions table
exit_table: Dict[str, str] = {
    "Start"     : "Mainland",
    "Portal"    : "The Dark Forest",
    "Rowboat"   : "Island"
}

# Create a region
def create_region(world: MultiWorld, player: int, name: str) -> Region:
    
    # Create region object
    region = Region(name, player, world)
    region_data = region_table[name]

    # Get relevant options
    pause_enabled = world.worlds[player].options.pause_enabled.value
    goal = world.worlds[player].options.goal.value
    dark_forest = world.worlds[player].options.include_forest.value

    # Get the goal data (if it exists in this region)
    goal_data = goal_table[goal] if goal_table[goal].region == name else None

    # If this region is the dark forest but it is disabled, skip locations / goals
    if name == "The Dark Forest" and dark_forest == False:
        return region

    # Cycle through all location checks
    if region_data.locations:
        for loc in region_data.locations:

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
    for exit in region_data.exits:
        region.exits.append(Entrance(player, exit, region))

    # Add goal to region, if provided
    if goal_data:
        goal_obj = StacklandsLocation(player, goal_data, None, region)
        region.locations.append(goal_obj)   

    return region

# Create all regions
def create_all_regions(world: MultiWorld, player: int):

    # Add all regions to world
    for region in region_table.keys():
        world.regions.append(create_region(world, player, region))

    # Connect exits to regions
    for ext, reg in exit_table.items():
        world.get_entrance(ext, player).connect(world.get_region(reg, player))