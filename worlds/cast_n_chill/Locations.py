from BaseClasses import Item, ItemClassification, MultiWorld
from dataclasses import dataclass
import json, logging, os
from typing import Dict, List, NamedTuple

@dataclass
class CastNChillLocation:
    """"""
    # id: int
    name: str
    region: str
    requires: List[str]


# Read items data from JSON
with open(os.path.join(os.path.dirname(__file__), 'data\locations.json'), 'r') as file:
    __location_json_data = json.loads(file.read())

# Parse as location objects
location_table: List[CastNChillLocation] = [CastNChillLocation(**data) for data in __location_json_data]

logging.info(f"There are {len(location_table)} locations in the location table")

# Create item lookup
__base_id: int = 79000
location_name_to_id_lookup: Dict[str, int] = {}

# Get items from JSON file
for location in location_table:
    location.id = __base_id
    location_name_to_id_lookup[location.name] = location.id
    __base_id += 1


