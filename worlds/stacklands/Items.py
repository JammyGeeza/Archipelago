import logging
from enum import Enum
from typing import Dict, List, NamedTuple
from BaseClasses import Item, ItemClassification, MultiWorld
from .Locations import goal_table

class ItemRegion(Enum):
    Any = 0
    Mainland = 1
    DarkForest = 2
    Island = 3

class ItemData(NamedTuple):
    name: str
    classification: ItemClassification
    region: ItemRegion

class StacklandsItem(Item):
    game = "Stacklands"

    def __init__(self, code: int, item: ItemData, player: int = None):
        super(StacklandsItem, self).__init__(
            item.name,
            item.classification,
            code,
            player
        )

# Item mapping
item_table: List[ItemData] = [

#region Mainland Items

    # Booster Packs
    ItemData("Humble Beginnings Booster Pack",      ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Seeking Wisdom Booster Pack",         ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Reap & Sow Booster Pack",             ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Curious Cuisine Booster Pack",        ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Logic and Reason Booster Pack",       ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("The Armory Booster Pack",             ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Explorers Booster Pack",              ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Order and Structure Booster Pack",    ItemClassification.progression,                                ItemRegion.Mainland),

    # Ideas
    ItemData("Idea: Animal Pen",                    ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Axe",                           ItemClassification.useful,                                     ItemRegion.Mainland),
    ItemData("Idea: Bone Spear",                    ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Boomerang",                     ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Breeding Pen",                  ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Brick",                         ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Brickyard",                     ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Butchery",                      ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Campfire",                      ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Chainmail Armor",               ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Charcoal",                      ItemClassification.useful,                                     ItemRegion.Mainland),
    ItemData("Idea: Chicken",                       ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Club",                          ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Coin Chest",                    ItemClassification.useful,                                     ItemRegion.Mainland),
    ItemData("Idea: Cooked Meat",                   ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Crane",                         ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Dustbin",                       ItemClassification.filler,                                     ItemRegion.Mainland), 
    ItemData("Idea: Farm",                          ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Frittata",                      ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Fruit Salad",                   ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Garden",                        ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Growth",                        ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Hammer",                        ItemClassification.useful,                                     ItemRegion.Mainland),
    ItemData("Idea: Hotpot",                        ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: House",                         ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Iron Bar",                      ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Iron Mine",                     ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Iron Shield",                   ItemClassification.useful,                                     ItemRegion.Mainland),
    ItemData("Idea: Lumber Camp",                   ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Magic Blade",                   ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Magic Glue",                    ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Magic Ring",                    ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Magic Staff",                   ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Magic Tome",                    ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Magic Wand",                    ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Market",                        ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Mess Hall",                     ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Milkshake",                     ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Omelette",                      ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Offspring",                     ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Pickaxe",                       ItemClassification.useful,                                     ItemRegion.Mainland),
    ItemData("Idea: Plank",                         ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Quarry",                        ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Resource Chest",                ItemClassification.useful,                                     ItemRegion.Mainland),
    ItemData("Idea: Sawmill",                       ItemClassification.useful,                                     ItemRegion.Mainland),
    ItemData("Idea: Shed",                          ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Slingshot",                     ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Smelter",                       ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Smithy",                        ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Spear",                         ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Spiked Plank",                  ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Stew",                          ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Stick",                         ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Stove",                         ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Sword",                         ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Temple",                        ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: Throwing Stars",                ItemClassification.progression,                                ItemRegion.Mainland),
    ItemData("Idea: University",                    ItemClassification.filler,                                     ItemRegion.Mainland),
    ItemData("Idea: Warehouse",                     ItemClassification.useful,                                     ItemRegion.Mainland),
    ItemData("Idea: Wooden Shield",                 ItemClassification.useful,                                     ItemRegion.Mainland),

#endregion

#region The Dark Forest Items

    ItemData("Idea: Stable Portal",                 ItemClassification.progression,                                ItemRegion.DarkForest),

#endregion

#region The Island Items

    # Coming soon...

#endregion

#region Junk Items

    # Junk Items
    ItemData("Apple Tree",                          ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Berry x3",                            ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Berry Bush",                          ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Coin",                                ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Coin x5",                             ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Coin x10",                            ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Egg x3",                              ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Flint x3",                            ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Iron Deposit",                        ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Iron Ore x3",                         ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Milk x3",                             ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Rock",                                ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Stick x3",                            ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Stone x3",                            ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Tree",                                ItemClassification.filler,                                     ItemRegion.Any),
    ItemData("Wood x3",                             ItemClassification.filler,                                     ItemRegion.Any),

#endregion

#region Trap Items

    # Trap Items
    ItemData("Chickens",                            ItemClassification.trap,                                       ItemRegion.Any),
    ItemData("Goop",                                ItemClassification.trap,                                       ItemRegion.Any),
    ItemData("Rabbits",                             ItemClassification.trap,                                       ItemRegion.Any),
    ItemData("Rat",                                 ItemClassification.trap,                                       ItemRegion.Any),
    ItemData("Slime",                               ItemClassification.trap,                                       ItemRegion.Any),
    ItemData("Snake",                               ItemClassification.trap,                                       ItemRegion.Any),

    # More trap items coming soon...

#endregion
]

# Item group mapping table
group_table: Dict[str, set[str]] = {
    "All Ideas": set(item.name for item in item_table if item.name.startswith("Idea:")),
    "All Mainland Ideas": set(item.name for item in item_table if item.region == ItemRegion.Mainland and item.name.startswith("Idea:")),
    "All Mainland Booster Packs": set(item.name for item in item_table if item.region == ItemRegion.Mainland and item.name.endswith("Booster Pack")),
    
    # Coming soon...
    "All Island Ideas": set(item.name for item in item_table if item.region == ItemRegion.Island and item.name.startswith("Idea:")),
    "All Island Booster Packs": set(item.name for item in item_table if item.region == ItemRegion.Island and item.name.endswith("Booster Pack")),
}

base_id: int = 91000
current_id: int = base_id

name_to_id = {}

# Create name-to-id lookup
for item in item_table:
    name_to_id[item.name] = current_id
    current_id += 1

# Create all items
def create_all_items(world: MultiWorld, player: int) -> None:
    # Get goal
    options = world.worlds[player].options

    # Get list of items to exclude if in starting inventory
    exclude = [item for item in world.precollected_items[player]]

    logging.info(f"Adding progression items...")

    # Add items to pool (include trap items if enabled)
    pool = []
    for item in [
        item for item in item_table if
        item.region is ItemRegion.Mainland or # Item type is mainland
        (options.dark_forest.value and item.region is ItemRegion.DarkForest) or # or item type is Dark Forest and dark forest is enabled
        (options.traps.value and item.classification is ItemClassification.trap) # or item type is Trap and traps are enabled
    ]:
        # Generate item object
        item_obj = StacklandsItem(name_to_id[item.name], item, player)

        # If item is not in starting inventory, add to pool
        if item_obj not in exclude:
            pool.append(item_obj)

    # Add items to item pool
    world.itempool += pool

    # Calculate if we have fewer items than locations
    unfilled_count: int = len(world.get_unfilled_locations(player)) - len(pool)

    junk_pool = []

    # If we have fewer items than locations, top the rest up with junk filler items
    if unfilled_count > 0:

        logging.info(f"{unfilled_count} more Locations than Items. Adding filler items to pool...")

        # Get list of filler items that are not ideas
        junk_items = [item for item in item_table if item.classification is ItemClassification.filler and item.region is ItemRegion.Any]

        for _ in range(unfilled_count):
            junk_item = world.random.choice(junk_items)
            junk_pool.append(StacklandsItem(name_to_id[junk_item.name], junk_item, player))

    # Add junk items to item pool
    world.itempool += junk_pool