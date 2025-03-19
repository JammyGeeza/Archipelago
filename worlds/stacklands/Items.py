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
    ItemData("Humble Beginnings Booster Pack",      ItemClassification.progression,     ItemType.Default),
    ItemData("Seeking Wisdom Booster Pack",         ItemClassification.progression,     ItemType.Default),
    ItemData("Reap & Sow Booster Pack",             ItemClassification.progression,     ItemType.Default),
    ItemData("Curious Cuisine Booster Pack",        ItemClassification.progression,     ItemType.Default),
    ItemData("Logic and Reason Booster Pack",       ItemClassification.progression,     ItemType.Default),
    ItemData("The Armory Booster Pack",             ItemClassification.progression,     ItemType.Default),
    ItemData("Explorers Booster Pack",              ItemClassification.progression,     ItemType.Default),
    ItemData("Order and Structure Booster Pack",    ItemClassification.progression,     ItemType.Default),
    
    # Ideas
    ItemData("Idea: Animal Pen",                    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Axe",                           ItemClassification.useful,          ItemType.Default), # Getting resources faster is useful
    ItemData("Idea: Bone Spear",                    ItemClassification.useful,          ItemType.Default), # Useful for fighting Demon
    ItemData("Idea: Boomerang",                     ItemClassification.useful,          ItemType.Default), # Useful for fighting Demon
    ItemData("Idea: Breeding Pen",                  ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Brick",                         ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Brickyard",                     ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Butchery",                      ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Campfire",                      ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Chainmail Armor",               ItemClassification.useful,          ItemType.Default), # Useful for fighting Demon
    ItemData("Idea: Charcoal",                      ItemClassification.useful,          ItemType.Default), # Useful for removing poison and making Magic Glue
    ItemData("Idea: Chicken",                       ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Club",                          ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Coin Chest",                    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Cooked Meat",                   ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Crane",                         ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Dustbin",                       ItemClassification.filler,          ItemType.Default), 
    ItemData("Idea: Farm",                          ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Frittata",                      ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Fruit Salad",                   ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Garden",                        ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Growth",                        ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Hammer",                        ItemClassification.useful,          ItemType.Default), # Building faster is useful
    ItemData("Idea: Hotpot",                        ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: House",                         ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Iron Bar",                      ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Iron Mine",                     ItemClassification.progression,     ItemType.Default), # Getting resources faster is useful
    ItemData("Idea: Iron Shield",                   ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Lumber Camp",                   ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Magic Blade",                   ItemClassification.useful,          ItemType.Default), # Useful for fighting Demon
    ItemData("Idea: Magic Glue",                    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Magic Ring",                    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Magic Staff",                   ItemClassification.useful,          ItemType.Default), # Useful for fighting Demon / 'Train a Wizard' quest, but can create Magic Wand instead
    ItemData("Idea: Magic Tome",                    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Magic Wand",                    ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Market",                        ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Mess Hall",                     ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Milkshake",                     ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Omelette",                      ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Offspring",                     ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Pickaxe",                       ItemClassification.useful,          ItemType.Default), # Getting resources faster is useful
    ItemData("Idea: Plank",                         ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Quarry",                        ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Resource Chest",                ItemClassification.useful,          ItemType.Default), # Storage is useful
    ItemData("Idea: Sawmill",                       ItemClassification.progression,     ItemType.Default), # Getting resources faster is useful
    ItemData("Idea: Shed",                          ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Slingshot",                     ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Smelter",                       ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Smithy",                        ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Spear",                         ItemClassification.progression,     ItemType.Default), # Useful for completing 'Train Militia' or 'Combat Level 20' but there are other options
    ItemData("Idea: Spiked Plank",                  ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Stable Portal",                 ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Stew",                          ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Stick",                         ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Stove",                         ItemClassification.progression,     ItemType.Default), # Useful for keeping enough food, but not required
    ItemData("Idea: Sword",                         ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Temple",                        ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: Throwing Stars",                ItemClassification.progression,     ItemType.Default),
    ItemData("Idea: University",                    ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Warehouse",                     ItemClassification.useful,          ItemType.Default), # Higher card limit is useful
    ItemData("Idea: Wizard Robe",                   ItemClassification.filler,          ItemType.Default),
    ItemData("Idea: Wooden Shield",                 ItemClassification.progression,     ItemType.Default),

    # Junk Items
    ItemData("Apple Tree x3",                       ItemClassification.filler,          ItemType.Junk),
    ItemData("Berry x5",                            ItemClassification.filler,          ItemType.Junk),
    ItemData("Berry Bush x3",                       ItemClassification.filler,          ItemType.Junk),
    ItemData("Coin x5",                             ItemClassification.filler,          ItemType.Junk),
    ItemData("Coin x10",                            ItemClassification.filler,          ItemType.Junk),
    ItemData("Coin x25",                            ItemClassification.filler,          ItemType.Junk),
    ItemData("Egg x5",                              ItemClassification.filler,          ItemType.Junk),
    ItemData("Flint x5",                            ItemClassification.filler,          ItemType.Junk),
    ItemData("Iron Deposit x3",                     ItemClassification.filler,          ItemType.Junk),
    ItemData("Iron Ore x5",                         ItemClassification.filler,          ItemType.Junk),
    ItemData("Milk x5",                             ItemClassification.filler,          ItemType.Junk),
    ItemData("Rock x3",                             ItemClassification.filler,          ItemType.Junk),
    ItemData("Stick x5",                            ItemClassification.filler,          ItemType.Junk),
    ItemData("Stone x5",                            ItemClassification.filler,          ItemType.Junk),
    ItemData("Tree x3",                             ItemClassification.filler,          ItemType.Junk),
    ItemData("Wood x5",                             ItemClassification.filler,          ItemType.Junk),

    # Trap Items
    ItemData("Get Gooped!",                         ItemClassification.trap,            ItemType.Trap),
    ItemData("Get Pooped!",                         ItemClassification.trap,            ItemType.Trap),

    # More trap items coming soon...
]

# Item group mapping table
group_table: Dict[str, set[str]] = {
    "All Ideas": set(item.name for item in item_table if item.name.startswith("Idea:")),
    "All Booster Packs": set(item.name for item in item_table if item.name.endswith("Booster Pack")),
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