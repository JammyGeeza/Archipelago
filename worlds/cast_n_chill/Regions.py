from BaseClasses import Entrance, EntranceType, Location, MultiWorld, Region
from dataclasses import dataclass
import json, logging, os
from .Locations import location_table
from .Options import CastNChillOptions
from typing import List

@dataclass
class CastNChillExit:
    """Data class for JSON region exit data"""
    def __init__(self, json_data):
        self.name: str = json_data["name"]
        self.destination: str = json_data["destination"]

@dataclass
class CastNChillRegion:
    """Data class for JSON region data"""
    def __init__(self, json_data):
        self.name: str = json_data["name"]
        self.exits: List[CastNChillExit] = [ CastNChillExit(data) for data in json_data["exits"] ]

# Read regions data from JSON
with open(os.path.join(os.path.dirname(__file__), 'data\\regions.json'), 'r') as file:
    __region_json_data = json.loads(file.read())

# Parse as region objects
region_table: List[CastNChillRegion] = [ CastNChillRegion(data) for data in __region_json_data ]

logging.info(f"There are {len(region_table)} regions in the regions table.")

def get_regions(multiworld: MultiWorld, player: int) -> List[Region]:
    """Create and retrieve all applicable regions for the configured multiworld."""

    options: CastNChillOptions = multiworld.worlds[player].options
    regions: List[Region] = []

    # Create applicable region(s) for 'Spots' option
    for region_data in [ reg for reg in region_table if reg.name == "Menu" or reg.name in options.spots.value ]:
        region: Region = Region(region_data.name, player, multiworld)

        # Create and append exits
        for exit in region_data.exits:
            exit: Entrance = Entrance(player, exit.name, region, randomization_type=EntranceType.TWO_WAY)
            region.exits.append(exit)

        # Create and append all location(s) for region
        for location_data in [ loc for loc in location_table if loc.region == region.name ]:
            location: Location = Location(player, location_data.name, location_data.id, region)
            region.locations.append(location)

        logging.info(f"Added {len(region.locations)} locations to region '{region.name}'!")

        # Append region
        regions.append(region)

    # Connect exits to respective regions
    for region in regions:
        region_data: CastNChillRegion = next(reg for reg in region_table if reg.name == region.name)
        for exit in region.exits:
            exit_data: CastNChillExit = next(ex for ex in region_data.exits if ex.name == exit.name)
            connected_region: Region = next(region for region in regions if region.name == exit_data.destination)
            exit.connect(connected_region)

    return regions