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
        self.region: str = json_data.get("region")
        self.classification: ItemClassification = ItemClassification(json_data.get("classification", ItemClassification.filler.value))
        self.include_for: List[str] = json_data.get("include_for", [])

    def is_included(self, inclusions: List[str]) -> bool:
        """Check this item against the world inclusions to see if it should be included."""
        return not self.include_for or bool(set(self.include_for) & set(inclusions))
    
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


def create_items(world: World) -> List[Item]:
    """Get all items applicable for the multiworld generation"""

    logging.info(f"Generating items for multiworld...")

    # Get all progression / useful items to be included
    items: List[Item] = [ 
        Item(itm.name, itm.classification, itm.id, world.player)
        for itm in item_table 
        if itm.is_included(world.inclusions)
        and itm.is_classification(ItemClassification.progression | ItemClassification.useful)
    ]

    logging.info(f"Found {len(items)} progression / useful items...")

    # Append progression items to item pool
    world.multiworld.itempool += items

    # Check if all locations are filled
    unfilled_location_count: int = len(world.multiworld.get_unfilled_locations(world.player))
    if unfilled_location_count > 0:
        logging.info(f"{unfilled_location_count} un-filled locations detected ...")
        world.multiworld.itempool += create_filler_items(world, unfilled_location_count)

def create_filler_items(world: World, amount: int) -> List[Item]:
    """Randomly select {amount} filler items."""

    logging.info(f"Generating {amount} filler items...")

    # Get applicable filler items
    filler_items = [
        itm for itm in item_table 
        if item.is_included(world.inclusions)
        and itm.is_classification(ItemClassification.filler)
    ]

    # Randomly select from filler items
    selected_filler = world.random.choices(
        filler_items,
        k=amount
    )

    return [ Item(itm.name, itm.classification, itm.id, world.player) for itm in selected_filler ]