from typing import List, TypedDict
from BaseClasses import Entrance, MultiWorld, Region
from .Locations import StacklandsLocation, locations_table, lookup_name_to_id as locations_lookup_name_to_id
from .Options import StacklandsOptions

class RegionData(TypedDict):
    name: str
    exits: List[str]

# Regions
regions_table: List[RegionData] = [
    { "name": "Mainland", "exits": [ "Island" ] },
    { "name": "Island", "exits": None }
]
    
# Create a region
def create_region(name: str, world: MultiWorld, player: int, options: StacklandsOptions, locations: List[str]=None, exits: List[str]=None):
    region = Region(name, player, world)
    
    if locations:
        # Add locations to region
        for location in locations:
            
            # If goal is 'Kill the Demon', skip the 'Kill the Demon Lord' location
            if options.goal.value == 0 and location == "Kill the Demon Lord":
                continue

            # If pausing is disabled in options, skip pause location
            if options.pause_enabled.value == False and location == "Pause using the play icon in the top right corner":
                continue

            loc_id = locations_lookup_name_to_id[location]
            loc_obj = StacklandsLocation(player, location, loc_id, region)
            region.locations.append(loc_obj)
            
    if exits:
        for ext in exits:
            region.exits.append(Entrance(player, getConnectionName(name, ext), region))
            
    return region

# Create all regions
def create_all_regions(world: MultiWorld, player: int, options: StacklandsOptions):
    # Cycle through regions in json
    for region in regions_table:
        reg_obj = create_region(region["name"], world, player, options, [location["name"] for location in locations_table if location["region"] == region["name"]], region["exits"])
        world.regions += [ reg_obj ]
    
    # Create default region
    menu = create_region("Menu", world, player, options, None, [ "Mainland" ])
    world.regions += [ menu ]
    
    # Connect default region to main
    menuConn = world.get_entrance("MenuToMainland", player)
    menuConn.connect(world.get_region("Mainland", player))
    
    # Link regions together
    for region in regions_table:
        if region["exits"]:
            for linkedRegion in region["exits"]:
                connection = world.get_entrance(getConnectionName(region["name"], linkedRegion), player)
                connection.connect(world.get_region(linkedRegion, player))

# Get connection name between entrance and exit
def getConnectionName(ent: str, ext: str):
    return ent + "To" + ext
        