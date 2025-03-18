import logging
from typing import Dict, List, NamedTuple
from BaseClasses import Item, ItemClassification, MultiWorld
from .Locations import goal_table

class ItemData(NamedTuple):
    name: str
    classification: ItemClassification

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
    ItemData("Humble Beginnings Booster Pack"      , ItemClassification.progression),
    ItemData("Seeking Wisdom Booster Pack"         , ItemClassification.progression),
    ItemData("Reap & Sow Booster Pack"             , ItemClassification.progression),
    ItemData("Curious Cuisine Booster Pack"        , ItemClassification.progression),
    ItemData("Logic and Reason Booster Pack"       , ItemClassification.progression),
    ItemData("The Armory Booster Pack"             , ItemClassification.progression),
    ItemData("Explorers Booster Pack"              , ItemClassification.progression),
    ItemData("Order and Structure Booster Pack"    , ItemClassification.progression),
    
    # Ideas
    ItemData("Idea: Animal Pen"                    , ItemClassification.filler),
    ItemData("Idea: Axe"                           , ItemClassification.useful), # Getting resources faster is useful
    ItemData("Idea: Bone Spear"                    , ItemClassification.useful), # Useful for fighting Demon
    ItemData("Idea: Boomerang"                     , ItemClassification.useful), # Useful for fighting Demon
    ItemData("Idea: Breeding Pen"                  , ItemClassification.filler),
    ItemData("Idea: Brick"                         , ItemClassification.progression),
    ItemData("Idea: Brickyard"                     , ItemClassification.progression),
    ItemData("Idea: Butchery"                      , ItemClassification.filler),
    ItemData("Idea: Campfire"                      , ItemClassification.progression),
    ItemData("Idea: Chainmail Armor"               , ItemClassification.useful), # Useful for fighting Demon
    ItemData("Idea: Charcoal"                      , ItemClassification.useful), # Useful for removing poison and making Magic Glue
    ItemData("Idea: Chicken"                       , ItemClassification.filler),
    ItemData("Idea: Club"                          , ItemClassification.progression),
    ItemData("Idea: Coin Chest"                    , ItemClassification.progression),
    ItemData("Idea: Cooked Meat"                   , ItemClassification.progression),
    ItemData("Idea: Crane"                         , ItemClassification.filler),
    ItemData("Idea: Dustbin"                       , ItemClassification.filler), 
    ItemData("Idea: Farm"                          , ItemClassification.progression),
    ItemData("Idea: Frittata"                      , ItemClassification.progression),
    ItemData("Idea: Fruit Salad"                   , ItemClassification.filler),
    ItemData("Idea: Garden"                        , ItemClassification.progression),
    ItemData("Idea: Growth"                        , ItemClassification.progression),
    ItemData("Idea: Hammer"                        , ItemClassification.useful), # Building faster is useful
    ItemData("Idea: Hotpot"                        , ItemClassification.filler),
    ItemData("Idea: House"                         , ItemClassification.progression),
    ItemData("Idea: Iron Bar"                      , ItemClassification.progression),
    ItemData("Idea: Iron Mine"                     , ItemClassification.progression), # Getting resources faster is useful
    ItemData("Idea: Iron Shield"                   , ItemClassification.progression),
    ItemData("Idea: Lumber Camp"                   , ItemClassification.progression),
    ItemData("Idea: Magic Blade"                   , ItemClassification.useful), # Useful for fighting Demon
    ItemData("Idea: Magic Glue"                    , ItemClassification.filler),
    ItemData("Idea: Magic Ring"                    , ItemClassification.filler),
    ItemData("Idea: Magic Staff"                   , ItemClassification.useful), # Useful for fighting Demon / 'Train a Wizard' quest, but can create Magic Wand instead
    ItemData("Idea: Magic Tome"                    , ItemClassification.filler),
    ItemData("Idea: Magic Wand"                    , ItemClassification.progression),
    ItemData("Idea: Market"                        , ItemClassification.progression),
    ItemData("Idea: Mess Hall"                     , ItemClassification.filler),
    ItemData("Idea: Milkshake"                     , ItemClassification.filler),
    ItemData("Idea: Omelette"                      , ItemClassification.progression),
    ItemData("Idea: Offspring"                     , ItemClassification.progression),
    ItemData("Idea: Pickaxe"                       , ItemClassification.useful), # Getting resources faster is useful
    ItemData("Idea: Plank"                         , ItemClassification.progression),
    ItemData("Idea: Quarry"                        , ItemClassification.progression),
    ItemData("Idea: Resource Chest"                , ItemClassification.useful), # Storage is useful
    ItemData("Idea: Sawmill"                       , ItemClassification.progression), # Getting resources faster is useful
    ItemData("Idea: Shed"                          , ItemClassification.progression),
    ItemData("Idea: Slingshot"                     , ItemClassification.progression),
    ItemData("Idea: Smelter"                       , ItemClassification.progression),
    ItemData("Idea: Smithy"                        , ItemClassification.progression),
    ItemData("Idea: Spear"                         , ItemClassification.progression), # Useful for completing 'Train Militia' or 'Combat Level 20' but there are other options
    ItemData("Idea: Spiked Plank"                  , ItemClassification.filler),
    ItemData("Idea: Stew"                          , ItemClassification.filler),
    ItemData("Idea: Stick"                         , ItemClassification.progression),
    ItemData("Idea: Stove"                         , ItemClassification.progression), # Useful for keeping enough food, but not required
    ItemData("Idea: Sword"                         , ItemClassification.progression),
    ItemData("Idea: Temple"                        , ItemClassification.progression),
    ItemData("Idea: Throwing Stars"                , ItemClassification.progression),
    ItemData("Idea: University"                    , ItemClassification.filler),
    ItemData("Idea: Warehouse"                     , ItemClassification.useful), # Higher card limit is useful
    ItemData("Idea: Wizard Robe"                   , ItemClassification.filler),
    ItemData("Idea: Wooden Shield"                 , ItemClassification.progression),
    
    # Resources / Junk
    ItemData("Apple Tree x3"                       , ItemClassification.filler),
    ItemData("Berry x5"                            , ItemClassification.filler),
    ItemData("Berry Bush x3"                       , ItemClassification.filler),
    ItemData("Coin x5"                             , ItemClassification.filler),
    ItemData("Coin x10"                            , ItemClassification.filler),
    ItemData("Coin x25"                            , ItemClassification.filler),
    ItemData("Egg x5"                              , ItemClassification.filler),
    ItemData("Flint x5"                            , ItemClassification.filler),
    ItemData("Iron Deposit x3"                     , ItemClassification.filler),
    ItemData("Iron Ore x5"                         , ItemClassification.filler),
    ItemData("Milk x5"                             , ItemClassification.filler),
    ItemData("Rock x3"                             , ItemClassification.filler),
    ItemData("Stick x5"                            , ItemClassification.filler),
    ItemData("Stone x5"                            , ItemClassification.filler),
    ItemData("Tree x3"                             , ItemClassification.filler),
    ItemData("Wood x5"                             , ItemClassification.filler),
    
    # Traps (to be implemented...)
    ItemData("Get Gooped!"                         , ItemClassification.trap),
    ItemData("Get Pooped!"                         , ItemClassification.trap),
    
    # Additional idea - spawn enemies onto the board?
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
    goal = world.worlds[player].options.goal.value
    include_traps = world.worlds[player].options.include_traps.value

    # Get list of items to exclude if in starting inventory
    exclude = [item for item in world.precollected_items[player]]

    # Gather items
    pool = []
    for item in item_table:
        # Create item object
        item_obj = StacklandsItem(name_to_id[item.name], item, player)

        # If item is not in starting inventory and not a trap item if traps are disabled
        if item_obj not in exclude and (include_traps == True or item.classification != ItemClassification.trap):
            pool.append(item_obj)

    # Add all valid items to pool
    world.itempool += pool

    # Add victory item to goal event
    goal_data = goal_table[goal]
    world.get_location(goal_data.name, player).place_locked_item(Item("Victory", ItemClassification.progression, None, player))