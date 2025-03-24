import logging
from typing import List, NamedTuple
from BaseClasses import Entrance, Item, ItemClassification, LocationProgressType, MultiWorld, Region
from .Locations import CheckType, LocationData, StacklandsLocation, goal_table, location_table, name_to_id as location_lookup

class RegionData(NamedTuple):
    name: str
    locations: List[LocationData]
    exits: List[str]

# Regions table
region_table: List[RegionData] = [
    RegionData("Menu",              [loc for loc in location_table if loc.region == "Menu"],                [ "Start" ]),
    RegionData("Mainland",          [loc for loc in location_table if loc.region == "Mainland"],            [ "Portal", "Rowboat" ]),
    RegionData("The Dark Forest",   [loc for loc in location_table if loc.region == "The Dark Forest"],     [ ]),
    RegionData("The Island",        [loc for loc in location_table if loc.region == "The Island"],          [ ]),
]

# Create a region
def create_region(world: MultiWorld, player: int, region: RegionData) -> Region:
    
    # Create region object
    region_obj = Region(region.name, player, world)

    # Get relevant options
    options = world.worlds[player].options

    # Cycle through all valid location checks
    for loc in [
        loc for loc in region.locations if 
        (options.dark_forest.value or loc.region != "The Dark Forest") and # Include Dark Forest checks if enabled in options
        (options.mobsanity.value or loc.check_type != CheckType.Mobsanity) and # Include Mobsanity checks if enabled in options
        (options.pausing.value or loc.name != "Pause using the play icon in the top right corner") and # Include Pausing check if enabled in options
        ((options.goal.value == 0 and loc.name != "Kill the Demon") or # Exclude 'Kill the Demon' if set as goal as this will be an Event instead
        (options.goal.value == 1 and loc.name != "Fight the Wicked Witch")) # Exclude 'Fight the Wicked Witch' if set as goal, as it will be an Event instead
    ]:

        # Add location check to region
        loc_obj = StacklandsLocation(player, loc.name, location_lookup[loc.name], region_obj)
        loc_obj.progress_type = loc.progress_type
        region_obj.locations.append(loc_obj)

    # Add exits to region, if provided
    if region.exits:
        for exit in region.exits:
            region_obj.exits.append(Entrance(player, exit, region_obj))

    # Get the goal data (if it exists in this region)
    goal = goal_table[options.goal.value] if goal_table[options.goal.value].region == region.name else None

    # Add goal and victory item to region, if goal is within this region
    if goal:
        goal_obj = StacklandsLocation(player, goal.name, None, region_obj)
        goal_obj.place_locked_item(Item("Victory", ItemClassification.progression, None, player))
        region_obj.locations.append(goal_obj)

    return region_obj

# Create all regions
def create_all_regions(world: MultiWorld, player: int):

    # Create regions
    for region in region_table:
        world.regions.append(create_region(world, player, region))

    # Connect exits to regions
    world.get_entrance("Start", player).connect(world.get_region("Mainland", player))
    world.get_entrance("Portal", player).connect(world.get_region("The Dark Forest", player))
    world.get_entrance("Rowboat", player).connect(world.get_region("The Island", player))