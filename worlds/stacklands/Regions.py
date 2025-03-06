import logging
from typing import List
from BaseClasses import Entrance, MultiWorld, Region
from .Locations import StacklandsLocation, location_table
from .Options import StacklandsOptions

# Create a region
def create_region(world: MultiWorld, player: int, name: str, locations: List[str]=None, exits: List[str]=None) -> Region:
    region = Region(name, player, world)

    if locations:
        for location in locations:
            loc_id = location_table[location].code
            loc_obj = StacklandsLocation(player, location, loc_id, region)
            region.locations.append(loc_obj)

    if exits:
        for exit in exits:
            region.exits.append(Entrance(player, exit, region))

    return region

# Create all regions
def create_all_regions(world: MultiWorld, player: int):

    world.regions += [
        create_region(world, player, "Menu", None, [ "Start" ]),
        create_region(world, player, "Mainland", [name for name, loc in location_table.items() if loc.region == "Mainland"])
    ]

    # Connect menu region to entrance of mainland
    world.get_entrance("Start", player).connect(world.get_region("Mainland", player))
        