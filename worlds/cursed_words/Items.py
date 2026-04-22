from BaseClasses import Item, ItemClassification, MultiWorld, Optional
from dataclasses import dataclass
import json, logging, os
from typing import Dict, List, NamedTuple
from worlds.AutoWorld import World

@dataclass
class CursedWordsItem:
    """Data class for Cursed World items from JSON configuration"""
    id: int = None

    def __init__(self, json_data: dict):
        self.name: str = json_data.get("name")
        self.classification: ItemClassification = ItemClassification(json_data.get("classification", ItemClassification.filler.value))
        self.region: str = json_data.get("region")
        self.tags: List[str] = json_data.get("tags", [])

    def has_tags(self, tags: List[str]) -> bool:
        """Check if all of this item's tags are present in a tags list"""
        return set(self.tags).issubset(set(tags))

    def is_classification(self, classification: ItemClassification) -> bool:
        """Check if this item has a matching classification flag"""
        return self.classification & classification if classification != ItemClassification.filler else self.classification == classification

# Read items data from JSON config
with open(os.path.join(os.path.dirname(__file__), 'data\\items.json'), 'r') as file:
    _items_data = json.loads(file.read())

# Parse as items
item_table: List[CursedWordsItem] = [ CursedWordsItem(item) for item in _items_data ]

logging.info(f"Found {len(item_table)} items from items.json configuration")

# Create item name-to-id lookup
_base_id: int = 323000
_cur_id: int = _base_id
item_name_to_id_lookup: Dict[str, int] = {}

for item in item_table:
    item.id = _cur_id
    item_name_to_id_lookup[item.name] = item.id
    _cur_id += 1


def generate_items(world: World):
    """Get all items applicable for the multiworld generation"""

    logging.info(f"Generating items for multiworld...")

    # Get all progression/useful items with matching tags from configuration options
    enabled_items: List[CursedWordsItem] = [
        item for item in item_table
        if item.has_tags(world.tags) and item.is_classification(ItemClassification.progression | ItemClassification.useful)
    ]

    logging.info(f"Found {len(enabled_items)} enabled progression/useful items for the multiworld")

    # Create items
    for item_data in enabled_items:
        logging.info(f"Creating item: {item_data.name}...")

        # Add to item pool
        item: Item = Item(item_data.name, item_data.classification, item_data.id, world.player)
        world.multiworld.itempool.append(item)

    # Check if all locations would be filled
    unfilled_location_count: int = len(world.multiworld.get_unfilled_locations(world.player))
    required_filler_count: int = unfilled_location_count - len(world.multiworld.itempool)

    # Append filler items if required
    if required_filler_count > 0:
        logging.info(f"Found {required_filler_count} empty spaces for filler items")
        world.multiworld.itempool += generate_filler_items(world, required_filler_count)

def generate_filler_items(world: World, amount: int) -> List[Item]:
    """Randomly select {amount} filler items."""

    logging.info(f"Generating {amount} filler item(s)...")

    # Get applicable filler items
    enabled_filler_items = [
        itm for itm in item_table 
        if item.has_tags(world.tags) and itm.is_classification(ItemClassification.filler)
    ]

    # Randomly select from filler items
    selected_filler = world.random.choices(
        enabled_filler_items,
        k=amount
    )

    return [ Item(itm.name, itm.classification, itm.id, world.player) for itm in selected_filler ]