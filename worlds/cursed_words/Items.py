from BaseClasses import Item, ItemClassification
from dataclasses import dataclass
import json, logging
import pkgutil
from typing import Dict, List, Tuple
from worlds.AutoWorld import World
from .classes.Constants import CHARACTER_NAMES
from .Locations import location_table, CursedWordsLocation
from .Regions import region_table, CursedWordsRegion

@dataclass
class CursedWordsItem:
    """Data class for Cursed World items from JSON configuration"""
    id: int = None

    def __init__(self, json_data: dict):
        self.name: str = json_data.get("name")
        self.character_tags: List[str] = json_data.get("character_tags", [])
        self.classification: ItemClassification = ItemClassification(json_data.get("classification", ItemClassification.filler.value))
        self.count: int = json_data.get("count", 1)
        self.groups: List[str] = json_data.get("groups", [])
        self.metadata: Dict[str, any] = json_data.get("metadata", {})
        self.option_tags: List[str] = json_data.get("option_tags", [])
        self.region: str = json_data.get("region")

    def has_character_tags(self, tags: List[str]) -> bool:
        """Check if this item's character tags contains at least one tag from a list."""
        return not self.character_tags or bool(set(self.character_tags) & set(tags))
    
    def has_option_tags(self, tags: List[str]) -> bool:
        """Check if this item's option tags contains at least one tag from a list."""
        return not self.option_tags or bool(set(self.option_tags) & set(tags))

    def is_classification(self, classification: ItemClassification) -> bool:
        """Check if this item has a matching classification flag"""
        return self.classification & classification if classification != ItemClassification.filler else self.classification == classification

# Read items data from JSON config
_file_data = pkgutil.get_data(__name__, 'data/items.json')
_items_data = json.loads(_file_data)

# Parse as items
item_table: List[CursedWordsItem] = [ CursedWordsItem(item) for item in _items_data ]

# logging.info(f"Found {len(item_table)} items from items.json configuration")

# Create item name-to-id lookup
_base_item_id: int = 323000
_cur_item_id: int = _base_item_id
item_name_to_id_lookup: Dict[str, int] = {}
item_name_groups_lookup: Dict[str, set] = {}

for item in item_table:
    item.id = _cur_item_id
    item_name_to_id_lookup[item.name] = item.id

    # Add item to groups, if set
    for group in item.groups:
        item_name_groups_lookup.setdefault(group, set()).add(item.name)

    _cur_item_id += 1

CHARACTER_ITEM_NAMES = set(CHARACTER_NAMES)

# Create the base sticker/stamp item group threshold names for each character
for character in CHARACTER_NAMES:
    for kind in ("Stickers", "Stamps"):
        item_name_groups_lookup.setdefault(f"{character}: {kind} Synergy", set())

# Set the sticker/stamp threshold names
for item in item_table:
    for kind in ("Stickers", "Stamps"):
        
        # If not a sticker or stamp, skip it
        if kind not in item.groups:
            continue

        for character in item.character_tags:
            if not item.option_tags:
                item_name_groups_lookup.setdefault(f"{character}: {kind} Synergy", set()).add(item.name)

# 
item_name_to_groups_lookup: Dict[str, List[str]] = {}
for group_name, member_names in item_name_groups_lookup.items():
    for member_name in member_names:
        item_name_to_groups_lookup.setdefault(member_name, []).append(group_name)

def generate_items(world: World):
    """Get all items applicable for the multiworld generation"""

    # Get pre-collected items (characters / basic stickers and stamps)
    precollected_item_names = [
        item.name for item in world.multiworld.precollected_items[world.player]
    ]

    # Get all stickers and stamps from character synergies
    selected_synergy_items: set = {
        name
        for character in world.character_tags
        for kind in ("Stickers", "Stamps")
        for name in world.character_synergies[(character, kind)]
    }

    # Get all progression/useful items this seed could possibly need based on player YAML options
    eligible_items: List[CursedWordsItem] = [
        item for item in item_table
        if (item.has_character_tags(world.character_tags) or item.name in selected_synergy_items)
        and item.has_option_tags(world.option_tags)
        and item.is_classification(ItemClassification.progression | ItemClassification.useful)
        and item.name not in precollected_item_names
    ]

    # Clamp possible 'Progressive Crown' item count to the <Crowns> YAML value (per-player)
    resolved_counts: Dict[str, int] = {}
    for item_data in eligible_items:
        if item_data.name.endswith(": Progressive Crown"):
            resolved_counts[item_data.name] = world.options.crowns.value
    
    # Shuffle all eligible items
    world.random.shuffle(eligible_items)

    # Get applicable regions based on player YAML options
    enabled_regions = [
        region for region in region_table
        if region.has_character_tags(world.character_tags)
        and region.has_option_tags(world.option_tags)
    ]

    # Get applicable locations based on player YAML options
    enabled_locations = [
        location for location in location_table
        if location.has_character_tags(world.character_tags)
        and location.has_option_tags(world.option_tags)
    ]

    # Calculate required item counts based on thresholds from Rules.py
    required_counts = generate_required_group_counts(enabled_regions, enabled_locations, world.group_thresholds, world.character_tags, world.option_tags)

    # Sort items into:
    # Critical  -> Required to progress based on access rules and/or other factors
    # Optional  -> Not essential, can be dropped if item pool is full
    critical_items: List[CursedWordsItem] = []
    optional_items: List[CursedWordsItem] = []
    item_totals: Dict[str, int] = {group: 0 for group in required_counts}

    for item_data in eligible_items:
        # Protect 'critical' items such as Characters and Progressive Crowns
        item_is_protected: bool = (
            item_data.name in CHARACTER_ITEM_NAMES 
            or item_data.name.endswith(": Progressive Crown")
        )

        # Get amount of times to apply item per-player or revert to global count if not a counted item
        item_count = resolved_counts.get(item_data.name, item_data.count)

        # Check if this item's current count is below the required 'critical' threshold
        item_groups = world.item_name_to_groups_lookup.get(item_data.name, item_data.groups)
        below_threshold = any(
            item_totals.get(group, 0) < required_counts[group]
            for group in item_groups if group in required_counts
        )

        # If protected item or currently below threshold, treat item as 'critical', otherwise treat as optional
        if item_is_protected or below_threshold:
            critical_items.append(item_data)
            for group in item_groups:
                if group in item_totals:
                    item_totals[group] += item_count
        else:
            optional_items.append(item_data)

    # Calculate how many slots there are to fill
    unfilled_location_count = len(world.multiworld.get_unfilled_locations(world.player))
    critical_count = sum(resolved_counts.get(item_data.name, item_data.count) for item_data in critical_items)

    # Check if this will exceed the location count before creating
    if critical_count > unfilled_location_count:
        raise Exception(f"Required progression items count {critical_count} will exceed location count ({unfilled_location_count}) for player {world.player} - thresholds may be too aggressive or not enough locations to accommodate all items.")

    # Calculate any remaining un-filled locations
    remaining_slots = unfilled_location_count - critical_count
    selected_optional: List[CursedWordsItem] = []
    populated_slots = 0

    # Get and shuffle optional items that are both tagged and untagged for characters
    character_tagged_items = [item for item in optional_items if item.character_tags]
    world.random.shuffle(character_tagged_items)

    untagged_items = [item for item in optional_items if not item.character_tags]
    world.random.shuffle(untagged_items)

    # Select required amount of optional items - character-relevant first, untagged as fallback
    for item_data in character_tagged_items + untagged_items:
        if populated_slots + item_data.count > remaining_slots:
            continue
        
        selected_optional.append(item_data)
        populated_slots += item_data.count

    # Add 'critical' items to the pool
    for item_data in critical_items:
        item_count = resolved_counts.get(item_data.name, item_data.count)
        for _ in range(item_count):
            item = Item(item_data.name, item_data.classification, item_data.id, world.player)
            world.multiworld.itempool.append(item)

    # Add 'optional' items to the pool and swap them to 'useful'
    for item_data in selected_optional:
        for _ in range(item_data.count):
            item = Item(item_data.name, ItemClassification.useful, item_data.id, world.player)
            world.multiworld.itempool.append(item)

    # Check if any locations remain un-filled, if so, populate with filler
    remaining_slots = remaining_slots - populated_slots
    if remaining_slots > 0:
        
        # If traps required, generate them first and add to pool
        trap_count = round(remaining_slots * world.options.trap_percentage.value / 100) if world.options.trap_percentage.value > 0 else 0
        traps = generate_trap_items(world, trap_count)
        world.multiworld.itempool += traps

        # Fill remaining item slots with filler
        filler_count = remaining_slots - len(traps)
        world.multiworld.itempool += generate_filler_items(world, filler_count)

def generate_trap_items(world: World, amount: int) -> List[Item]:
    """Randomly select an {amount} of trap items."""

    # If invalid amount, return none
    if amount <= 0:
        return []

    # Get applicable trap items based on player YAML options
    enabled_trap_items = [
        item for item in item_table
        if item.has_character_tags(world.character_tags)
        and item.has_option_tags(world.option_tags)
        and item.is_classification(ItemClassification.trap)
    ]

    # If no enabled trap items, return none
    if len(enabled_trap_items) == 0:
        return []

    # Get trap item weighting from YAML options
    weights = [
        world.options.trap_weighting.value.get(item.name, 1)
        for item in enabled_trap_items
    ]

    # Randomly select from trap items
    selected_traps = world.random.choices(
        enabled_trap_items,
        weights=weights,
        k=amount
    )

    return [ Item(item.name, item.classification, item.id, world.player) for item in selected_traps ]


def generate_filler_items(world: World, amount: int) -> List[Item]:
    """Randomly select an {amount} of filler items."""

    # logging.info(f"Generating {amount} filler item(s)...")

    # If invalid number, return none
    if amount <= 0:
        return []

    # Get applicable filler items based on player YAML options
    enabled_filler_items = [
        item for item in item_table 
        if item.has_character_tags(world.character_tags)
        and item.has_option_tags(world.option_tags)
        and item.is_classification(ItemClassification.filler)
    ]

    # If no enabled filler items, return none
    if len(enabled_filler_items) == 0:
        return []

    # Get filler item weighting from YAML options
    weights = [
        world.options.filler_weighting.value.get(item.name, 1)
        for item in enabled_filler_items
    ]

    # Randomly select from filler items
    selected_filler = world.random.choices(
        enabled_filler_items,
        weights=weights,
        k=amount
    )

    return [ Item(item.name, item.classification, item.id, world.player) for item in selected_filler ]


def generate_required_group_counts(region_table: List[CursedWordsRegion], location_table: List[CursedWordsLocation], group_thresholds: Dict[str, Dict[str, int]], character_tags: List[str], option_tags: List[str]) -> Dict[str, int]:
    """Get the highest 'HasGroup' of each item group across all applicable locations and region exits"""

    required: Dict[str, int] = {}

    # Get the count value from the count field
    def resolve_count(count_field):

        # If the value is an integer, take it
        if isinstance(count_field, int):
            return count_field
        
        # If it's an object with a resolver, resolve the value from group thresholds.
        if isinstance(count_field, dict) and count_field.get("resolver") == "FromWorldAttr":
            path = count_field["name"].split(".")
            if path[0] == "group_thresholds":
                return group_thresholds.get(path[1], {}).get(path[2], 0)
            
        return 0

    def traverse(node):
        """Traverse a node's properties"""
        
        # If the node is an object, search for 'rule' key with a 'HasGroup' value
        if isinstance(node, dict):
            if node.get("rule") == "HasGroup":
                args = node.get("args", {})
                item_name_group = args.get("item_name_group")
                count = resolve_count(args.get("count", 0))
                
                if item_name_group:
                    required[item_name_group] = max(required.get(item_name_group, 0), count)
            
            # Continue to traverse each value
            for value in node.values():
                traverse(value)
        
        # If it's a list, traverse each object in the list
        elif isinstance(node, list):
            for item in node:
                traverse(item)

    # Traverse every applicable Region's access rules
    for region in region_table:
        for exit_model in region.exits:
            if not (exit_model.has_character_tags(character_tags) and exit_model.has_option_tags(option_tags)):
                continue
            if exit_model.access_rule:
                traverse(exit_model.access_rule)

    # Traverse every Location's access rules
    for location in location_table:
        if getattr(location, "access_rule", None):
            traverse(location.access_rule)

    return required