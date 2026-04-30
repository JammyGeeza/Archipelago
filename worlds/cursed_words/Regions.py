from BaseClasses import Entrance, EntranceType, Location, MultiWorld, Region
from dataclasses import dataclass
import json, logging, os
from .Locations import location_table, location_name_to_id_lookup, CursedWordsLocation
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
        self.tags: str = json_data.get("tags", [])
        self.type: EntranceType = EntranceType(json_data.get("type", 2))

    def is_included(self, inclusions: List[str]) -> bool:
        """Check this exit against the world inclusions list to see if it should be included."""
        return not self.include_for or set(self.include_for).issubset(set(inclusions))
    
    def has_tags(self, tags: List[str]) -> bool:
        """Check if all of this exit's tags are present in a tags list"""
        return set(self.tags).issubset(set(tags))

@dataclass
class CursedWordsRegion:
    """Data class for Cursed World regions from JSON configuration"""
    def __init__(self, json_data: Dict[any, any]):
        self.name: str = json_data["name"]
        self.exits: List[CursedWordsExit] = [ CursedWordsExit(entrance) for entrance in json_data.get("exits", []) ]
        self.tags: List[str] = json_data.get("tags", [])
        # self.starting_inventory: List[str] = json_data.get("starting_inventory", [])

    def has_tags(self, tags: List[str]) -> bool:
        """Check if all of this region's tags are present in a tags list"""
        return set(self.tags).issubset(set(tags))

# Read regions data from JSON
with open(os.path.join(os.path.dirname(__file__), 'data\\regions.json'), 'r') as file:
    _regions_data = json.loads(file.read())

# Parse as region objects
region_table: List[CursedWordsRegion] = [ CursedWordsRegion(data) for data in _regions_data ]

logging.info(f"Found {len(location_table)} regions from regions.json configuration")

def generate_regions(world: World):
    """Create all applicable regions for this multiworld."""

    # Get all regions with matching tags from configuration options
    enabled_regions: List[CursedWordsRegion] = [
        region for region in region_table
        if region.has_tags(world.tags)
    ]

    logging.info(f"Found {len(enabled_regions)} enabled regions based on configuration options")

    # First pass to create regions from region data models
    for region_model in enabled_regions:
        logging.info(f"  -> Creating region: {region_model.name}...")

        # Create region
        region: Region = Region(region_model.name, world.player, world.multiworld)

        # Get enabled locations for region with matching tags from configuration options
        enabled_locations: List[CursedWordsLocation] = [
            location for location in location_table
            if location.is_for_region(region.name) and location.has_tags(world.tags)
        ]

        # logging.info(f"  -> Found {len(enabled_locations)} enabled locations for region")

        # Create locations and add to region
        for location_model in enabled_locations:

            for i in range(location_model.count):
                loc_name: str = location_model.name.format(count=i+1)
                loc_id: int = world.location_name_to_id[loc_name]

                logging.info(f"    -> Creating location: {loc_name} with ID {loc_id}...")

                # Create location
                location: Location = Location(world.player, loc_name, loc_id, region)
                if location_model.access_rule:
                    world.set_rule(location, world.rule_from_dict(location_model.access_rule))

                # Append to region
                region.locations.append(location)

        # Append region to multiworld
        world.multiworld.regions.append(region)

    # Second pass to create and connect exits (regions have to exist in the multiworld first)
    for region_data in enabled_regions:
        # Get region from multiworld
        region: Region = world.multiworld.get_region(region_data.name, world.player)

        for exit_model in [ exit for exit in region_data.exits if exit.has_tags(world.tags)]:

            logging.info(f"    -> Creating exit: {exit_model.name}")
            exit: Entrance = Entrance(world.player, exit_model.name, region, randomization_type=exit_model.type)

            # Create access rule, if one exists
            if exit_model.access_rule:
                world.set_rule(exit, world.rule_from_dict(exit_model.access_rule))

            # Connect exit to destination region
            destination_region: Region = world.multiworld.get_region(exit_model.destination, world.player)
            exit.connect(destination_region)

            # Append exit to region
            region.exits.append(exit)