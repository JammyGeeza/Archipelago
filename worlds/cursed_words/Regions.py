from BaseClasses import Entrance, EntranceType, Location, MultiWorld, Region
from dataclasses import dataclass
import json, logging, os
from .Locations import location_table, CursedWordsLocation
# from .Options import CastNChillOptions
# from .Rules import compile_access_rules
from typing import Dict, List
from worlds.AutoWorld import World

@dataclass
class CursedWordsExit:
    """Data class for Cursed World exits from JSON configuration"""
    def __init__(self, json_data: Dict[any, any]):
        self.access_rule: Dict[str, any] = json_data.get("access_rule", None)
        self.destination: str = json_data["destination"]
        self.include_for: List[str] = json_data.get("include_for", [])
        self.name: str = json_data.get("name")
        self.type: EntranceType = EntranceType(json_data.get("type", 2))

    def is_included(self, inclusions: List[str]) -> bool:
        """Check this exit against the world inclusions list to see if it should be included."""
        return not self.include_for or bool(set(self.include_for) & set(inclusions))

@dataclass
class CursedWordsRegion:
    """Data class for Cursed World regions from JSON configuration"""
    def __init__(self, json_data: Dict[any, any]):
        self.name: str = json_data["name"]
        self.exits: List[CursedWordsExit] = [ CursedWordsExit(entrance) for entrance in json_data.get("exits", []) ]
        self.include_for: List[str] = json_data.get("include_for", [])
        # self.starting_inventory: List[str] = json_data.get("starting_inventory", [])

    def is_included(self, inclusions: List[str]) -> bool:
        """Check this region against the world inclusions list to see if it should be included."""
        return not self.include_for or bool(set(self.include_for) & set(inclusions))

# Read regions data from JSON
with open(os.path.join(os.path.dirname(__file__), 'data\\regions.json'), 'r') as file:
    _regions_data = json.loads(file.read())

# Parse as region objects
region_table: List[CursedWordsRegion] = [ CursedWordsRegion(data) for data in _regions_data ]

logging.info(f"Found {len(location_table)} regions from regions.json configuration")

def create_regions(world: World):
    """Create all applicable regions for this multiworld."""

    regions: List[Region] = []

    # Get regions to be included
    applicable_regions: List[CursedWordsRegion] = [
        region for region in region_table
        if region.is_included(world.inclusions)
    ]

    # Get exits to be included
    applicable_exits: List[CursedWordsExit] = []

    logging.info(f"Found {len(applicable_regions)} applicable regions for this multiworld")

    # Create regions from region data models
    for region_model in applicable_regions:
        logging.info(f"Creating region: {region_model.name}...")

        # Create region
        region: Region = Region(region_model.name, world.player, world.multiworld)

        # Get applicable exits
        applicable_exit_models: List[CursedWordsExit] = [
            exit for exit in region_model.exits
            if exit.is_included(world.inclusions)
        ]

        # Create exits for region
        for exit_model in applicable_exit_models:
            logging.info(f"\tCreating entrance: {exit_model.name}...")

            # Create exit
            exit: Entrance = Entrance(world.player, exit_model.name, region, randomization_type=exit_model.type)
            if exit_model.access_rule:
                world.set_rule(exit, world.rule_from_dict(exit_model.access_rule))

            # Append to region
            region.exits.append(exit)

        # Add to applicable exits
        applicable_exits += applicable_exit_models

        # Get applicable locations for this region
        applicable_locations: List[CursedWordsLocation] = [
            location for location in location_table
            if location.is_included(world.inclusions)
            and location.is_for_region(region.name)
        ]

        logging.info(f"Found {len(applicable_locations)} locations for region...")

        # Create locations and add to region
        for location_model in applicable_locations:
            logging.info(f"\t Creating location: {location_model.name}")

            # Create location
            location: Location = Location(world.player, location_model.name, location_model.id, region)
            if location_model.access_rule:
                world.set_rule(location, world.rule_from_dict(exit_model.access_rule))

            # Append to region
            region.locations.append(location)

        # Append region to list
        regions.append(region)

    # Append regions to multiworld
    world.multiworld.regions += regions

    # Connect all exits now that all regions are present
    for exit_model in applicable_exits:
        exit: Entrance = world.get_entrance(exit_model.name)
        region: Region = world.get_region(exit_model.destination)
        exit.connect(region)