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
    """Data class for items from JSON data."""
    id: int = None

    def __init__(self, json_data):
        self.name: str = json_data["name"]
        self.spots: List[str] = json_data.get("spots", [])
        self.classification: ItemClassification = ItemClassification(json_data.get("classification", ItemClassification.filler.value))
        self.count: int = json_data.get("count", 1)

# Read items data from JSON
with open(os.path.join(os.path.dirname(__file__), 'data\\items.json'), 'r') as file:
    __item_json_data = json.loads(file.read())

# Parse as items
item_table: List[CastNChillItem] = [CastNChillItem(data) for data in __item_json_data]

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

    # Get filler items, if required
    item_count: int = len(items)
    location_count: int = len(multiworld.get_locations())

    # If not all locations filled, add filler items
    if item_count < location_count:
        amount_required: int = location_count - item_count
        items += get_filler_items(multiworld, player, amount_required)

    return items

def __get_progression_items(multiworld: MultiWorld, player: int) -> List[Item]:
    """Get all relevant progression items applicable to the configured multiworld generation."""

    options = multiworld.worlds[player].options
    items: List[Item] = []

    logging.info(f"Creating progression / useful items for the item pool...")

    # Add progression and useful items for each selected region to the pool
    for item_data in [ 
        item for item in item_table 
        if (
            len(item.spots) == 0 
            or set(item.spots) & set(options.spots.value)
        )
        and item.classification is not ItemClassification.filler 
        and bool(item.classification & (ItemClassification.progression | ItemClassification.useful))
    ]:
        for i in range(item_data.count):
            logging.info(f"-> Adding item '{item_data.name.format(count=i+1)}' ...")
            items.append(Item(item_data.name.format(count=i+1), item_data.classification, item_data.id, player))

    # Remove starting_inventory items

    logging.info(f"Added {len(items)} progression / useful items to the item pool!")

    return items

def get_filler_items(multiworld: MultiWorld, player: int, amount: int) -> List[Item]:
    """Get all relevant filler items applicable to the configured multiworld generation."""

    options = multiworld.worlds[player].options
    items: List[Item] = []

    # Select amount of filler items using weights
    for filler_item in multiworld.random.choices(
        population=list(options.filler_weights.value.keys()),
        weights=list(options.filler_weights.value.values()),
        k=amount
    ):
        logging.info(f"Adding filler item '{filler_item}' ...")
        item_data: CastNChillItem = next(item for item in item_table if item.name.casefold() == filler_item.casefold())
        items.append(Item(item_data.name, item_data.classification, item_data.id, player))

    logging.info(f"Added {len(items)} filler items to the item pool!")

    return items