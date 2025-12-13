from BaseClasses import Entrance, EntranceType, Location, MultiWorld, Region
from dataclasses import dataclass
import json, logging, os
from .Locations import location_table, CastNChillLocation
from .Options import CastNChillOptions
from .Rules import compile_access_rules
from typing import Dict, List

@dataclass
class CastNChillExit:
    """Data class for JSON region exit data"""
    def __init__(self, json_data):
        self.name: str = json_data["name"]
        self.destination: str = json_data["destination"]
        self.access_rules: Dict[str, any] = json_data.get("access_rules", None)
        self.type: EntranceType = EntranceType(json_data.get("type", 2))

@dataclass
class CastNChillRegion:
    """Data class for JSON region data"""
    def __init__(self, json_data):
        self.name: str = json_data["name"]
        self.exits: List[CastNChillExit] = [ CastNChillExit(data) for data in json_data.get("exits", []) ]
        self.requires: List[str] = json_data.get("requires", [])

# Read regions data from JSON
with open(os.path.join(os.path.dirname(__file__), 'data\\regions.json'), 'r') as file:
    __region_json_data = json.loads(file.read())

# Parse as region objects
region_table: List[CastNChillRegion] = [ CastNChillRegion(data) for data in __region_json_data ]

logging.info(f"There are {len(region_table)} regions in the regions table.")

def set_regions(multiworld: MultiWorld, player: int):
    """Create and retrieve all applicable regions for the configured multiworld."""

    # Get selected spots from options
    options: CastNChillOptions = multiworld.worlds[player].options
    spots: List[str] = options.spots.value

    # Get all region data models for selected 'Spots' configuration options
    applicable_region_models: List[CastNChillRegion] = [ region for region in region_table if region.name in [ "Menu" ] or any(spot in region.name for spot in spots)]
    applicable_exit_models: List[CastNChillExit] = []

    logging.info(f"Creating {len(applicable_region_models)} eligible region(s) based on configuration options ...")

    for region_model in applicable_region_models:
        logging.info(f"Creating region '{region_model.name}' ...")
        region: Region = Region(region_model.name, player, multiworld)

        # Get all exit data models in region that connect to selected 'Spots' configuration options
        exit_models: List[CastNChillExit] = [ exit for exit in region_model.exits if exit.destination in [ region.name for region in applicable_region_models ] ]
        logging.info(f"-> Creating {len(exit_models)} eligible exit(s) based on configuration options ...")

        for exit_model in exit_models:
            logging.info(f"--> Creating exit '{exit_model.name}' ...")
            exit: Entrance = Entrance(player, exit_model.name, region, randomization_type=exit_model.type)
            exit.access_rule(compile_access_rules(exit_model.access_rules, player))

            # Append exit to region
            region.exits.append(exit)

        # Add exit models to applicable exits
        applicable_exit_models += exit_models

        # Get applicable location data models for region
        location_models: List[CastNChillLocation] = [ location for location in location_table if region.name == " / ".join(location.regions) ]
        logging.info(f"-> Creating {len(location_models)} eligible location(s) based on configuration options ...")

        for location_model in location_models:
            logging.info(f"--> Creating location '{location_model.name}' ...")
            location: Location = Location(player, location_model.name, location_model.id, region)
            location.access_rule(compile_access_rules(location_model.access_rules, player))

            # Append location to region
            region.locations.append(location)

        # Append region
        multiworld.regions.append(region)

    logging.info(f"Connecting exits...")

    # Now that all regions have been created, connect applicable exits to their destination regions
    for exit_model in applicable_exit_models:
        exit: Entrance = multiworld.get_entrance(exit_model.name, player)
        connecting_region: Region = multiworld.get_region(exit_model.destination, player)

        logging.info(f"-> Connecting region {exit.parent_region.name}'s exit '{exit.name}' to {connecting_region.name} ...")

        # Connect exit to destination region
        exit.connect(connecting_region)