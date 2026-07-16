from BaseClasses import Entrance, EntranceType, Location, MultiWorld, Region
from dataclasses import dataclass
import json, logging, os
from .Locations import location_table, location_name_to_id_lookup, CursedWordsLocation
import pkgutil
from typing import Dict, List
from worlds.AutoWorld import World

@dataclass
class CursedWordsExit:
    """Data class for Cursed World exits from JSON configuration"""
    def __init__(self, json_data: Dict[any, any]):
        self.access_rule: Dict[str, any] = json_data.get("access_rule", None)
        self.character_tags: str = json_data.get("character_tags", [])
        self.destination: str = json_data["destination"]
        self.include_for: List[str] = json_data.get("include_for", [])
        self.name: str = json_data.get("name")
        self.option_tags: str = json_data.get("option_tags", [])
        self.type: EntranceType = EntranceType(json_data.get("type", 2))

    def is_included(self, inclusions: List[str]) -> bool:
        """Check this exit against the world inclusions list to see if it should be included."""
        return not self.include_for or set(self.include_for).issubset(set(inclusions))
    
    def has_character_tags(self, tags: List[str]) -> bool:
        """Check if this exit's character tags contains at least one tag from a list."""
        return not self.character_tags or bool(set(self.character_tags) & set(tags))
    
    def has_option_tags(self, tags: List[str]) -> bool:
        """Check if this exit's option tags contains at least one tag from a list."""
        return not self.option_tags or bool(set(self.option_tags) & set(tags))

@dataclass
class CursedWordsRegion:
    """Data class for Cursed World regions from JSON configuration"""
    def __init__(self, json_data: Dict[any, any]):
        self.character_tags: List[str] = json_data.get("character_tags", [])
        self.count: int = json_data.get("count", 1)
        self.count_start: int = json_data.get("count_start", 1)
        self.count_step: int = json_data.get("count_step", 1)
        self.exits: List[CursedWordsExit] = [ CursedWordsExit(entrance) for entrance in json_data.get("exits", []) ]
        self.name: str = json_data["name"]
        self.option_tags: List[str] = json_data.get("option_tags", [])
        # self.starting_inventory: List[str] = json_data.get("starting_inventory", [])

    def has_character_tags(self, tags: List[str]) -> bool:
        """Check if this region's character tags contains at least one tag from a list."""
        return not self.character_tags or bool(set(self.character_tags) & set(tags))
    
    def has_option_tags(self, tags: List[str]) -> bool:
        """Check if this region's option tags contains at least one tag from a list."""
        return not self.option_tags or bool(set(self.option_tags) & set(tags))

# Read regions data from JSON
_file_data = pkgutil.get_data(__name__, 'data/regions.json')
_regions_data = json.loads(_file_data)

# Parse as region objects
region_table: List[CursedWordsRegion] = [ CursedWordsRegion(data) for data in _regions_data ]

# logging.info(f"Found {len(location_table)} regions from regions.json configuration")

def generate_regions(world: World):
    """Create all applicable regions for this multiworld."""

    # Get all regions with matching tags from configuration options
    enabled_regions: List[CursedWordsRegion] = [
        region for region in region_table
        if region.has_character_tags(world.character_tags)
        and region.has_option_tags(world.option_tags)
    ]

    # logging.info(f"Found {len(enabled_regions)} enabled regions based on configuration options")

    # First pass to create regions from region data models
    for region_model in enabled_regions:

        # Create regions
        for i in range(region_model.count_start, region_model.count_start + region_model.count * region_model.count_step, region_model.count_step):

            region: Region = Region(region_model.name.format(count=i), world.player, world.multiworld)

            # logging.info(f"  -> Creating region: {region.name}")

            # Get enabled locations for region with matching tags from configuration options
            enabled_locations: List[CursedWordsLocation] = [
                location for location in location_table
                if location.is_for_region(region.name)
                and location.has_character_tags(world.character_tags)
                and location.has_option_tags(world.option_tags)
            ]

            # logging.info(f"  -> Found {len(enabled_locations)} enabled locations for region")

            # Create locations and add to region
            for location_model in enabled_locations:
                
                # --- Intercept locations with specific counts defined ---

                # If 'Shopsanity' is enabled, update the amount of shopsanity checks to include
                if world.options.shopsanity.value and location_model.name.startswith("Shop: Buy Shopsanity Item "):
                    location_model.count = world.options.shopsanity_limit.value

                # --- End of Intercept ---

                for j in range(location_model.count_start, location_model.count_start + location_model.count * location_model.count_step, location_model.count_step):
                    loc_name: str = location_model.name.format(count=j)
                    loc_id: int = world.location_name_to_id[loc_name]

                    # logging.info(f"    -> Creating location: {loc_name} with ID {loc_id}...")

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

        for i in range(region_data.count_start, region_data.count_start + region_data.count * region_data.count_step, region_data.count_step):

            # Get region from multiworld
            region: Region = world.multiworld.get_region(region_data.name.format(count=i), world.player)

            for exit_model in [
                exit for exit in region_data.exits
                if exit.has_character_tags(world.character_tags)
                and exit.has_option_tags(world.option_tags)
            ]:

                # logging.info(f"    -> Creating exit: {exit_model.name}")
                
                exit: Entrance = Entrance(world.player, exit_model.name, region, randomization_type=exit_model.type)

                # Create access rule, if one exists
                if exit_model.access_rule:
                    world.set_rule(exit, world.rule_from_dict(exit_model.access_rule))

                # Connect exit to destination region
                destination_region: Region = world.multiworld.get_region(exit_model.destination, world.player)
                exit.connect(destination_region)

                # Append exit to region
                region.exits.append(exit)