from BaseClasses import Item, ItemClassification, MultiWorld
from dataclasses import dataclass
import json, logging, os
import pkgutil
from typing import Dict, List, NamedTuple, Optional
from worlds.AutoWorld import World

@dataclass
class CursedWordsLocation:
    """Data class for Cursed World locations from JSON configuration"""
    id: int = None

    def __init__(self, json_data: Dict[any, any]):
        self.access_rule: Optional[Dict[str, any]] = json_data.get("access_rule", {})
        self.character_tags: List[str] = json_data.get("character_tags", [])
        self.count: int = json_data.get("count", 1)
        self.count_start: int = json_data.get("count_start", 1)
        self.count_step: int = json_data.get("count_step", 1)
        self.name: str = json_data.get("name")
        self.option_tags: List[str] = json_data.get("option_tags", [])
        self.region: str = json_data.get("region")

    def is_for_region(self, region: str) -> bool:
        """Check if this location is for a specified region."""
        return self.region == region

    def has_character_tags(self, tags: List[str]) -> bool:
        """Check if this region's character tags contains at least one tag from a list."""
        return not self.character_tags or bool(set(self.character_tags) & set(tags))
    
    def has_option_tags(self, tags: List[str]) -> bool:
        """Check if this region's option tags contains at least one tag from a list."""
        return not self.option_tags or bool(set(self.option_tags) & set(tags))

# Read items data from JSON
_file_data = pkgutil.get_data(__name__, 'data/locations.json')
_locations_data = json.loads(_file_data)

# Parse as location objects
location_table: List[CursedWordsLocation] = [ CursedWordsLocation(data) for data in _locations_data ]

# logging.info(f"Found {len(location_table)} items from locations.json configuration")

# Create item lookup
_base_loc_id: int = 322000
_cur_loc_id: int = _base_loc_id
location_name_to_id_lookup: Dict[str, int] = {}

# Get locations from JSON file
for location in location_table:

    for i in range(location.count_start, location.count_start + location.count * location.count_step, location.count_step):
        loc_name: str = location.name.format(count=i)
        loc_id: str = _cur_loc_id

        # logging.info(f"Adding location lookup '{loc_name}': {loc_id}")
        
        location_name_to_id_lookup[loc_name] = loc_id
        _cur_loc_id += 1