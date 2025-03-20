import logging
from enum import Enum
from typing import Dict, List, NamedTuple
from BaseClasses import Item, ItemClassification, MultiWorld
from .Locations import goal_table

class ItemType(Enum):
    Default = 0
    Junk = 1
    Trap = 2

class ItemData(NamedTuple):
    name: str
    count: int
    classification: ItemClassification
    type: ItemType

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

    # Booster Packs
    ItemData("Humble Beginnings Booster Pack",      1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Seeking Wisdom Booster Pack",         1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Reap & Sow Booster Pack",             1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Curious Cuisine Booster Pack",        1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Logic and Reason Booster Pack",       1,    ItemClassification.progression,     ItemType.Default),
    ItemData("The Armory Booster Pack",             1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Explorers Booster Pack",              1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Order and Structure Booster Pack",    1,    ItemClassification.progression,     ItemType.Default),

    # Ideas
    ItemData("Idea: Animal Pen",                    1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Axe",                           1,    ItemClassification.useful,          ItemType.Default), # Getting resources faster is useful
    ItemData("Idea: Bone Spear",                    1,    ItemClassification.useful,          ItemType.Default), # Useful for fighting Demon
    ItemData("Idea: Boomerang",                     1,    ItemClassification.useful,          ItemType.Default), # Useful for fighting Demon
    ItemData("Idea: Breeding Pen",                  1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Brick",                         1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Brickyard",                     1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Butchery",                      1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Campfire",                      1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Chainmail Armor",               1,    ItemClassification.useful,          ItemType.Default), # Useful for fighting Demon
    ItemData("Idea: Charcoal",                      1,    ItemClassification.useful,          ItemType.Default), # <- Useful for removing poison and making Magic Glue
    ItemData("Idea: Chicken",                       1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Club",                          1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Coin Chest",                    1,    ItemClassification.useful,          ItemType.Default),
    ItemData("Idea: Cooked Meat",                   1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Crane",                         1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Dustbin",                       1,    ItemClassification.filler,          ItemType.Default), 
    ItemData("Idea: Farm",                          1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Frittata",                      1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Fruit Salad",                   1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Garden",                        1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Growth",                        1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Hammer",                        1,    ItemClassification.useful,          ItemType.Default), # <- Useful for building faster
    ItemData("Idea: Hotpot",                        1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: House",                         1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Iron Bar",                      1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Iron Mine",                     1,    ItemClassification.progression,     ItemType.Default), # Getting resources faster is useful
    ItemData("Idea: Iron Shield",                   1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Lumber Camp",                   1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Magic Blade",                   1,    ItemClassification.useful,          ItemType.Default), # Useful for higher combat stats
    ItemData("Idea: Magic Glue",                    1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Magic Ring",                    1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Magic Staff",                   1,    ItemClassification.useful,          ItemType.Default), # <- Useful for higher combat stats
    ItemData("Idea: Magic Tome",                    1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Magic Wand",                    1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Market",                        1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Mess Hall",                     1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Milkshake",                     1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Omelette",                      1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Offspring",                     1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Pickaxe",                       1,    ItemClassification.useful,          ItemType.Default), # Getting resources faster is useful
    ItemData("Idea: Plank",                         1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Quarry",                        1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Resource Chest",                1,    ItemClassification.useful,          ItemType.Default), # <- Storage is useful
    ItemData("Idea: Sawmill",                       1,    ItemClassification.progression,     ItemType.Default), # Getting resources faster is useful
    ItemData("Idea: Shed",                          1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Slingshot",                     1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Smelter",                       1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Smithy",                        1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Spear",                         1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Spiked Plank",                  1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Stable Portal",                 1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Stew",                          1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Stick",                         1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Stove",                         1,    ItemClassification.progression,     ItemType.Default), # Useful for keeping enough food, but not required
    ItemData("Idea: Sword",                         1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Temple",                        1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Throwing Stars",                1,    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: University",                    1,    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Warehouse",                     1,    ItemClassification.useful,          ItemType.Default), # <- Higher card capacity is useful
    ItemData("Idea: Wizard Robe",                   1,    ItemClassification.filler,          ItemType.Default), # <- Can't be made on Mainland
    ItemData("Idea: Wooden Shield",                 1,    ItemClassification.progression,     ItemType.Default),

    # Junk Items
    ItemData("Apple Tree x3",                       1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Berry x5",                            1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Berry Bush x3",                       1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Coin x5",                             1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Coin x10",                            1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Coin x25",                            1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Egg x5",                              1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Flint x5",                            1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Iron Deposit x3",                     1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Iron Ore x5",                         1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Milk x5",                             1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Rock x3",                             1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Stick x5",                            1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Stone x5",                            1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Tree x3",                             1,    ItemClassification.filler,          ItemType.Junk),
    ItemData("Wood x5",                             1,    ItemClassification.filler,          ItemType.Junk),

    # Trap Items
    ItemData("Get Gooped!",                         1,    ItemClassification.trap,            ItemType.Trap),
    ItemData("Get Pooped!",                         1,    ItemClassification.trap,            ItemType.Trap),

    # More trap items coming soon...
]

# Item group mapping table
group_table: Dict[str, set[str]] = {
    "All Ideas": set(item.name for item in item_table if item.name.startswith("Idea:")),
    "All Booster Packs": set(item.name for item in item_table if item.name.endswith("Booster Pack")),
    "Basic Equipment": set(["Idea: Club", "Idea: Magic Wand", "Idea: Spear", "Idea: Slingshot", "Idea: Wooden Shield"]),
    "Advanced Equipment": set(["Idea: Iron Shield", "Idea: Sword", "Idea: Throwing Stars"])
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

    # Add items to pool (ignore junk items and include trap items if enabled)
    pool = []
    for item in [item for item in item_table if item.type != ItemType.Junk and (options.traps_enabled.value or item.type != ItemType.Trap)]:
        for _ in range(item.count):
            # Generate item object
            item_obj = StacklandsItem(name_to_id[item.name], item, player)

            # If item is not in starting inventory, add to pool
            if item_obj not in exclude:
                pool.append(item_obj)

    # Add all items to pool
    world.itempool += pool

    # Calculate how many junk items are required
    junk: int = len(world.get_unfilled_locations(player)) - len(pool)
    logging.info(f"Junk to add: {junk}")
    
    # If junk needed, randomly select junk items to fill gaps
    if junk > 0:
        junk_items = [junk_item for junk_item in item_table if junk_item.type == ItemType.Junk]

        for _ in range(junk):
            junk_item = world.random.choice(junk_items)
            world.itempool.append(StacklandsItem(name_to_id[junk_item.name], junk_item, player))