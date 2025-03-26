import logging
from enum import Enum
from typing import Dict, List, NamedTuple
from BaseClasses import Item, ItemClassification, MultiWorld
from .Locations import goal_table

class ItemType(Enum):
    Mainland = 0
    DarkForest = 1
    Island = 2
    Junk = 3
    Trap = 4

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

#region Mainland Items

    # Booster Packs
    ItemData("Humble Beginnings Booster Pack",      1,    ItemClassification.progression,                                ItemType.Mainland),
    ItemData("Seeking Wisdom Booster Pack",         1,    ItemClassification.progression,                                ItemType.Mainland),
    ItemData("Reap & Sow Booster Pack",             1,    ItemClassification.progression,                                ItemType.Mainland),
    ItemData("Curious Cuisine Booster Pack",        1,    ItemClassification.progression,                                ItemType.Mainland),
    ItemData("Logic and Reason Booster Pack",       1,    ItemClassification.progression,                                ItemType.Mainland),
    ItemData("The Armory Booster Pack",             1,    ItemClassification.progression,                                ItemType.Mainland),
    ItemData("Explorers Booster Pack",              1,    ItemClassification.progression,                                ItemType.Mainland),
    ItemData("Order and Structure Booster Pack",    1,    ItemClassification.progression,                                ItemType.Mainland),

    # Ideas
    ItemData("Idea: Animal Pen",                    1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Axe",                           1,    ItemClassification.useful,                                      ItemType.Mainland),
    ItemData("Idea: Bone Spear",                    1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Boomerang",                     1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Breeding Pen",                  1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Brick",                         1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Brickyard",                     1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Butchery",                      1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Campfire",                      1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Chainmail Armor",               1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Charcoal",                      1,    ItemClassification.useful,                                      ItemType.Mainland),
    ItemData("Idea: Chicken",                       1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Club",                          1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Coin Chest",                    1,    ItemClassification.useful,                                      ItemType.Mainland),
    ItemData("Idea: Cooked Meat",                   1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Crane",                         1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Dustbin",                       1,    ItemClassification.filler,                                      ItemType.Mainland), 
    ItemData("Idea: Farm",                          1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Frittata",                      1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Fruit Salad",                   1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Garden",                        1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Growth",                        1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Hammer",                        1,    ItemClassification.useful,                                      ItemType.Mainland),
    ItemData("Idea: Hotpot",                        1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: House",                         1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Iron Bar",                      1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Iron Mine",                     1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Iron Shield",                   1,    ItemClassification.useful,                                      ItemType.Mainland),
    ItemData("Idea: Lumber Camp",                   1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Magic Blade",                   1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Magic Glue",                    1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Magic Ring",                    1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Magic Staff",                   1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Magic Tome",                    1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Magic Wand",                    1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Market",                        1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Mess Hall",                     1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Milkshake",                     1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Omelette",                      1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Offspring",                     1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Pickaxe",                       1,    ItemClassification.useful,                                      ItemType.Mainland),
    ItemData("Idea: Plank",                         1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Quarry",                        1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Resource Chest",                1,    ItemClassification.useful,                                      ItemType.Mainland),
    ItemData("Idea: Sawmill",                       1,    ItemClassification.useful,                                      ItemType.Mainland),
    ItemData("Idea: Shed",                          1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Slingshot",                     1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Smelter",                       1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Smithy",                        1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Spear",                         1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Spiked Plank",                  1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Stew",                          1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Stick",                         1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Stove",                         1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Sword",                         1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Temple",                        1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: Throwing Stars",                1,    ItemClassification.progression,                                 ItemType.Mainland),
    ItemData("Idea: University",                    1,    ItemClassification.filler,                                      ItemType.Mainland),
    ItemData("Idea: Warehouse",                     1,    ItemClassification.useful,                                      ItemType.Mainland),
    ItemData("Idea: Wooden Shield",                 1,    ItemClassification.useful,                                      ItemType.Mainland),

#endregion

#region The Dark Forest Items

    ItemData("Idea: Stable Portal",                 1,    ItemClassification.progression,                                ItemType.DarkForest),

#endregion

#region The Island Items

    # Coming soon...

#endregion

#region Junk Items

    # Junk Items
    ItemData("Apple Tree",                          1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Berry x3",                            1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Berry Bush",                          1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Coin",                                1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Coin x5",                             1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Coin x10",                            1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Egg x3",                              1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Flint x3",                            1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Iron Deposit",                        1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Iron Ore x3",                         1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Milk x3",                             1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Rock",                                1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Stick x3",                            1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Stone x3",                            1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Tree",                                1,    ItemClassification.filler,                                      ItemType.Junk),
    ItemData("Wood x3",                             1,    ItemClassification.filler,                                      ItemType.Junk),

#endregion

#region Trap Items

    # Trap Items
    ItemData("Get Gooped!",                         1,    ItemClassification.trap,                                          ItemType.Trap),
    ItemData("Rabbits!",                            1,    ItemClassification.trap,                                          ItemType.Trap),
    ItemData("Rats!",                               1,    ItemClassification.trap,                                          ItemType.Trap),
    ItemData("Small Slimes!",                       1,    ItemClassification.trap,                                          ItemType.Trap),
    ItemData("Snakes!",                             1,    ItemClassification.trap,                                          ItemType.Trap),

    # More trap items coming soon...

#endregion
]

# Item group mapping table
group_table: Dict[str, set[str]] = {
    "All Ideas": set(item.name for item in item_table if item.name.startswith("Idea:")),
    "All Mainland Ideas": set(item.name for item in item_table if item.type == ItemType.Mainland and item.name.startswith("Idea:")),
    "All Mainland Booster Packs": set(item.name for item in item_table if item.type == ItemType.Mainland and item.name.endswith("Booster Pack")),
    
    # Coming soon...
    "All Island Ideas": set(item.name for item in item_table if item.type == ItemType.Island and item.name.startswith("Idea:")),
    "All Island Booster Packs": set(item.name for item in item_table if item.type == ItemType.Island and item.name.endswith("Booster Pack")),
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

    # Add items to pool (include trap items if enabled)
    pool = []
    for item in [
        item for item in item_table if 
        (options.traps.value or item.type != ItemType.Trap) and # Include trap items if enabled in options
        (options.dark_forest.value or item.type != ItemType.DarkForest) # Include Dark Forest items if enabled in options
    ]:
        for _ in range(item.count):
            # Generate item object
            item_obj = StacklandsItem(name_to_id[item.name], item, player)

            # If item is not in starting inventory, add to pool
            if item_obj not in exclude:
                pool.append(item_obj)

    # Add all items to pool
    world.itempool += pool

    # Calculate how many additional junk items are required
    junk: int = len(world.get_unfilled_locations(player)) - len(pool)
    
    # If junk needed, randomly select junk items to fill gaps
    if junk > 0:
        logging.info(f"Junk items to add: {junk}")
        junk_items = [junk_item for junk_item in item_table if junk_item.type == ItemType.Junk]

        for _ in range(junk):
            junk_item = world.random.choice(junk_items)
            world.itempool.append(StacklandsItem(name_to_id[junk_item.name], junk_item, player))