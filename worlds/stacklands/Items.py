from BaseClasses import Item, ItemClassification, MultiWorld
from .Options import StacklandsOptions
from typing import Dict, List, Set, TypedDict

class StacklandsItem(Item):
    game = "Stacklands"
    

class ItemData(TypedDict):
    name: str
    classification: ItemClassification
    count: int

items_table: List[ItemData] = [
    
    ### Mainland Items ###

    # Booster Packs
    { "name": "Humble Beginnings Booster Pack", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Seeking Wisdom Booster Pack", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Reap & Sow Booster Pack", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Curious Cuisine Booster Pack", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Logic and Reason Booster Pack", "classification": ItemClassification.progression, "count": 1 },
    { "name": "The Armory Booster Pack", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Explorers Booster Pack", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Order and Structure Booster Pack", "classification": ItemClassification.progression, "count": 1 },
    
    # Ideas
    { "name": "Idea: Animal Pen", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Axe", "classification": ItemClassification.useful, "count": 1 }, # Getting resources faster is useful
    { "name": "Idea: Bone Spear", "classification": ItemClassification.useful, "count": 1 }, # Useful for fighting Demon
    { "name": "Idea: Boomerang", "classification": ItemClassification.useful, "count": 1 }, # Useful for fighting Demon
    { "name": "Idea: Breeding Pen", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Brick", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Brickyard", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Butchery", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Campfire", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Chainmail Armor", "classification": ItemClassification.useful, "count": 1 }, # Useful for fighting Demon
    { "name": "Idea: Chicken", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Club", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Coin Chest", "classification": ItemClassification.useful, "count": 1 }, # Storage is useful
    { "name": "Idea: Cooked Meat", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Crane", "classification": ItemClassification.useful, "count": 1 }, # Useful for automation
    { "name": "Idea: Dustbin", "classification": ItemClassification.filler, "count": 1 }, 
    { "name": "Idea: Farm", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Frittata", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Fruit Salad", "classification": ItemClassification.useful, "count": 1 }, # Food types are useful
    { "name": "Idea: Garden", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Growth", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Hammer", "classification": ItemClassification.useful, "count": 1 }, # Building faster is useful
    { "name": "Idea: Hotpot", "classification": ItemClassification.useful, "count": 1 }, # Useful for keeping enough food, but not required
    { "name": "Idea: House", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Iron Bar", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Iron Mine", "classification": ItemClassification.progression, "count": 1 }, # Getting resources faster is useful
    { "name": "Idea: Iron Shield", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Lumber Camp", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Magic Blade", "classification": ItemClassification.useful, "count": 1 }, # Useful for fighting Demon
    { "name": "Idea: Magic Glue", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Magic Ring", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Magic Staff", "classification": ItemClassification.useful, "count": 1 }, # Useful for fighting Demon / 'Train a Wizard' quest, but can create Magic Wand instead
    { "name": "Idea: Magic Tome", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Magic Wand", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Market", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Milkshake", "classification": ItemClassification.useful, "count": 1 }, # Food types are useful
    { "name": "Idea: Omelette", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Offspring", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Pickaxe", "classification": ItemClassification.useful, "count": 1 }, # Getting resources faster is useful
    { "name": "Idea: Plank", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Quarry", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Resource Chest", "classification": ItemClassification.useful, "count": 1 }, # Storage is useful
    { "name": "Idea: Resource Magnet", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Sawmill", "classification": ItemClassification.progression, "count": 1 }, # Getting resources faster is useful
    { "name": "Idea: Shed", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Slingshot", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Smelter", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Smithy", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Spear", "classification": ItemClassification.useful, "count": 1 }, # Useful for completing 'Train Militia' or 'Combat Level 20' but there are other options
    { "name": "Idea: Spiked Plank", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Stew", "classification": ItemClassification.useful, "count": 1 }, # Food types are useful
    { "name": "Idea: Stick", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Stove", "classification": ItemClassification.useful, "count": 1 }, # Useful for keeping enough food, but not required
    { "name": "Idea: Sword", "classification": ItemClassification.useful, "count": 1 }, # Useful for completing 'Train Militia' or 'Combat Level 20' but there are other options
    { "name": "Idea: Temple", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: Throwing Stars", "classification": ItemClassification.progression, "count": 1 },
    { "name": "Idea: University", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Warehouse", "classification": ItemClassification.useful, "count": 1 }, # Higher card limit is useful
    { "name": "Idea: Wizard Robe", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Idea: Wooden Shield", "classification": ItemClassification.useful, "count": 1 }, # Useful for 'Combat level 20' but are other things available
    
    # Equipment
    # { "name": "Club", "classification": ItemClassification.filler, "count": 1 },
    # { "name": "Magic Wand", "classification": ItemClassification.filler, "count": 1 },
    # { "name": "Spear", "classification": ItemClassification.filler, "count": 1 },
    # { "name": "Sword", "classification": ItemClassification.filler, "count": 1 },
    # { "name": "Wooden Shield", "classification": ItemClassification.filler, "count": 1 },
    
    # Resources
    { "name": "Berry x5", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Flint x5", "classification": ItemClassification.filler, "count": 1 },
    # { "name": "Iron Ore x5", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Poop x5", "classification": ItemClassification.filler, "count": 1 }, # Could add something like a 'Get Pooped' "trap" item that spawns a whole bunch of poop, toggle-able in options
    { "name": "Stone x5", "classification": ItemClassification.filler, "count": 1 },
    { "name": "Wood x5", "classification": ItemClassification.filler, "count": 1 }
    
    # Traps (to be implemented..)
    # - Spawn enemies onto the board?
    # - 'Get Pooped' item that spawns a bunch of poop?
]

item_group_table: Dict[str, Set[str]] = {
    "All Ideas": set(item["name"] for item in items_table if item["name"].startswith("Idea:")),
    "All Booster Packs": set(item["name"] for item in items_table if item["name"].endswith("Booster Pack")),
    "Basic Booster Packs": {"Humble Beginnings Booster Pack", "Seeking Wisdom Booster Pack", "Reap & Sow Booster Pack"}
}
    
# ID assignment
base_id: int = 92000
current_id: int = base_id

# Lookups
lookup_id_to_name = {}
lookup_name_to_id = {}   

# Create item lookups
for item in items_table:
    
    # Add to lookups
    lookup_id_to_name[current_id] = item["name"]
    lookup_name_to_id[item["name"]] = current_id
    
    # Increment ID
    current_id += 1

# Create an item as a StacklandsItem object
def create_item(player: int, item: ItemData) -> StacklandsItem:
    return StacklandsItem(item["name"], item["classification"], lookup_name_to_id[item["name"]], player=player)

# Add all items to the item pool
def create_all_items(world: MultiWorld, player: int, options: StacklandsOptions):
    for item in items_table:
        
        # Exclude Humble Beginnings if 'basic pack' option is true
        if options.basic_pack.value and item["name"] == "Humble Beginnings Booster Pack":
            continue

        for _ in range(item["count"]):
            world.itempool.append(create_item(player, item))