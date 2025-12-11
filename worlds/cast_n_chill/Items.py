from BaseClasses import Item, ItemClassification, MultiWorld
from dataclasses import dataclass
import json, logging, os
from typing import Dict, List, NamedTuple

class JsonItem:
    """"""
    def __init__(self, item):
        self.name: str = item["name"]
        self.region: str = item["region"]
        self.classification: ItemClassification = item["classification"]

@dataclass
class CastNChillItem:
    """"""
    # id: int
    name: str
    region: str
    classification: ItemClassification


# Read items data from JSON
with open(os.path.join(os.path.dirname(__file__), 'data\items.json'), 'r') as file:
    __item_json_data = json.loads(file.read())

# Parse as items
item_table: List[CastNChillItem] = [CastNChillItem(**data) for data in __item_json_data]

logging.info(f"There are {len(item_table)} items in the item table")

# Create item lookup
__base_id: int = 78000
item_name_to_id_lookup: Dict[str, int] = {}

# Get items from JSON file
for item in item_table:
    item.id = __base_id
    item_name_to_id_lookup[item.name] = item.id
    __base_id += 1


