from BaseClasses import Item, ItemClassification, MultiWorld
from dataclasses import dataclass
import json, logging, os
from typing import Dict, List, NamedTuple, Optional
from worlds.AutoWorld import World

@dataclass
class CursedWordsLocation:
    """Data class for Cursed World locations from JSON configuration"""
    id: int = None

    def __init__(self, json_data: Dict[any, any]):
        self.access_rule: Optional[Dict[str, any]] = json_data.get("access_rule", {})
        self.name: str = json_data.get("name")
        self.region: str = json_data.get("region")
        self.tags: List[str] = json_data.get("tags", [])

    def is_for_region(self, region: str) -> bool:
        """Check if this location is for a specified region."""
        return self.region == region

    def has_tags(self, tags: List[str]) -> bool:
        """Check if all of this location's tags are present in a tags list"""
        return set(self.tags).issubset(set(tags))

# Read items data from JSON
with open(os.path.join(os.path.dirname(__file__), 'data\\locations.json'), 'r') as file:
    _locations_data = json.loads(file.read())

# Parse as location objects
location_table: List[CursedWordsLocation] = [ CursedWordsLocation(data) for data in _locations_data ]

logging.info(f"Found {len(location_table)} items from locations.json configuration")

# Create item lookup
_base_id: int = 322000
_cur_id: int = _base_id
location_name_to_id_lookup: Dict[str, int] = {}

# Get items from JSON file
for location in location_table:
    location.id = _cur_id
    location_name_to_id_lookup[location.name] = location.id
    _cur_id += 1