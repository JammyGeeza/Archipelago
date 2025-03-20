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

    logging.info(f"{region.name} locations: {str(len(region.locations))}")

    # Cycle through all location checks (skipping Dark Forest if not enables)
    for loc in region.locations:

        # Skip mobsanity check(s) if not enabled
        if loc.check_type == CheckType.Mobsanity and not options.mobsanity_enabled.value:
            continue

        # Skip pausing check(s) if not enabled
        if loc.check_type == CheckType.Pausing and not options.pausing_enabled.value:
            continue

        # Skip this check if the goal is set to 'Kill the Demon', as it will be an event instead.
        if loc.name == "Kill the Demon" and options.goal.value == 0:
            continue

        # Add location check to region (set dark forest progress types to excluded if set to skippable in options)
        loc_obj = StacklandsLocation(player, loc.name, location_lookup[loc.name], region_obj)
        loc_obj.progress_type = LocationProgressType.EXCLUDED if options.dark_forest_skippable.value and region.name == "The Dark Forest" else loc.progress_type
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