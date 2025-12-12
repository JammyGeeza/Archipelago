from BaseClasses import Item, ItemClassification, MultiWorld
from dataclasses import dataclass
import json, logging, os
from .Options import CastNChillOptions
from typing import Dict, List, NamedTuple

class JsonItem:
    """"""
    def __init__(self, item):
        self.name: str = item["name"]
        self.region: str = item["region"]
        self.classification: ItemClassification = item["classification"]

@dataclass
class CastNChillItem:
    """Data class for items from JSON data."""
    id: int = None

    def __init__(self, json_data):
        self.name: str = json_data["name"]
        self.regions: List[str] = json_data["regions"]
        self.classification: ItemClassification = ItemClassification(json_data["classification"])
        self.count: int = json_data.get("count", 1)

# Read items data from JSON
with open(os.path.join(os.path.dirname(__file__), 'data\\items.json'), 'r') as file:
    __item_json_data = json.loads(file.read())

# Parse as items
item_table: List[CastNChillItem] = [CastNChillItem(data) for data in __item_json_data]

logging.info(f"There are {len(item_table)} items in the item table")

# Create item lookup
__base_id: int = 78000
item_name_to_id_lookup: Dict[str, int] = {}

# Get items from JSON file
for item in item_table:
    item.id = __base_id
    item_name_to_id_lookup[item.name] = item.id
    __base_id += 1


def get_items(multiworld: MultiWorld, player: int) -> List[Item]:
    """Get all items applicable for the multiworld generation."""

    items: List[Item] = []

    # Get all progression items
    items += __get_progression_items(multiworld, player)

    return items

def __get_progression_items(multiworld: MultiWorld, player: int) -> List[Item]:
    """Get all relevant progression items applicable to the configured multiworld generation."""

    options: CastNChillOptions = multiworld.worlds[player].options
    items: List[Item] = []

    logging.info(f"Creating progression / useful items for the item pool...")

    # Add progression and useful items for each selected region to the pool
    for spot in options.spots.value:
        for item in [
            item for item in item_table 
            if (len(item.regions) == 0 or spot in item.regions) and bool((ItemClassification.progression | ItemClassification.useful) & item.classification)
        ]:
            for i in range(item.count):
                items.append(Item(item.name.replace("{count}", str(i)), item.classification, item.id, player))

    logging.info(f"Created {len(items)} items across {len(options.spots.value)} regions for the item pool!")

    return items