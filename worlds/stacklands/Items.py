import logging
from .Enums import ItemFlags, RegionFlags
from .Options import StacklandsOptions
from enum import Enum
from typing import Dict, List, NamedTuple
from BaseClasses import Item, ItemClassification, MultiWorld, LocationProgressType
# from .Locations import goal_table

class ItemRegion(Enum):
    Any = 0
    Mainland = 1
    DarkForest = 2
    Island = 3

class ItemData(NamedTuple):
    name: str
    region_flags: RegionFlags
    item_flags: ItemFlags
    classification_flags: ItemClassification

class StacklandsItem(Item):
    game = "Stacklands"

    def __init__(self, code: int, item: ItemData, player: int = None):
        super(StacklandsItem, self).__init__(
            item.name,
            item.classification_flags,
            code,
            player
        )

# Item mapping
item_table: List[ItemData] = [

#region Mainland Items

    # Booster Packs
    ItemData("Humble Beginnings Booster Pack"       , RegionFlags.Mainland   , ItemFlags.Booster     , ItemClassification.progression),
    ItemData("Seeking Wisdom Booster Pack"          , RegionFlags.Mainland   , ItemFlags.Booster     , ItemClassification.progression),
    ItemData("Reap & Sow Booster Pack"              , RegionFlags.Mainland   , ItemFlags.Booster     , ItemClassification.progression),
    ItemData("Curious Cuisine Booster Pack"         , RegionFlags.Mainland   , ItemFlags.Booster     , ItemClassification.progression),
    ItemData("Logic and Reason Booster Pack"        , RegionFlags.Mainland   , ItemFlags.Booster     , ItemClassification.progression),
    ItemData("The Armory Booster Pack"              , RegionFlags.Mainland   , ItemFlags.Booster     , ItemClassification.progression),
    ItemData("Explorers Booster Pack"               , RegionFlags.Mainland   , ItemFlags.Booster     , ItemClassification.progression),
    ItemData("Order and Structure Booster Pack"     , RegionFlags.Mainland   , ItemFlags.Booster     , ItemClassification.progression),

    # Progression
    ItemData("Idea: Brick"                          , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Brickyard"                      , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Campfire"                       , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Cooked Meat"                    , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Farm"                           , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Frittata"                       , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Growth"                         , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: House"                          , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Iron Bar"                       , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Iron Mine"                      , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Lumber Camp"                    , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Magic Wand"                     , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Market"                         , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Omelette"                       , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Offspring"                      , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Plank"                          , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Quarry"                         , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Shed"                           , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Slingshot"                      , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Smelter"                        , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Smithy"                         , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Spear"                          , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Stick"                          , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Sword"                          , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Temple"                         , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),
    ItemData("Idea: Throwing Stars"                 , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.progression),

    # Useful
    ItemData("Idea: Axe"                            , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.useful     ),
    ItemData("Idea: Charcoal"                       , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.useful     ),
    ItemData("Idea: Coin Chest"                     , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.useful     ),
    ItemData("Idea: Hammer"                         , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.useful     ),
    ItemData("Idea: Iron Shield"                    , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.useful     ),
    ItemData("Idea: Pickaxe"                        , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.useful     ),
    ItemData("Idea: Resource Chest"                 , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.useful     ),
    ItemData("Idea: Sawmill"                        , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.useful     ),
    ItemData("Idea: Warehouse"                      , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.useful     ),
    ItemData("Idea: Wooden Shield"                  , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.useful     ),

    # Filler
    ItemData("Idea: Animal Pen"                     , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Bone Spear"                     , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Boomerang"                      , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Breeding Pen"                   , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Butchery"                       , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Chainmail Armor"                , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Chicken"                        , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Club"                           , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Crane"                          , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Dustbin"                        , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ), 
    ItemData("Idea: Fruit Salad"                    , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Garden"                         , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Hotpot"                         , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Magic Blade"                    , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Magic Glue"                     , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Magic Ring"                     , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Magic Staff"                    , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Magic Tome"                     , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Mess Hall"                      , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Milkshake"                      , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Spiked Plank"                   , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Stew"                           , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: Stove"                          , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Idea: University"                     , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),

#endregion

#region The Dark Forest Items

    ItemData("Idea: Stable Portal"                  , RegionFlags.Forest     , ItemFlags.Idea        , ItemClassification.progression),

#endregion

#region The Island Items

    # Coming soon...

#endregion

#region Junk Items

    ItemData("Apple Tree"                           , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Berry x3"                             , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Berry Bush"                           , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Coin"                                 , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Coin x5"                              , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Coin x10"                             , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Egg x3"                               , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Flint x3"                             , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Iron Deposit"                         , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Iron Ore x3"                          , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Milk x3"                              , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Rock"                                 , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Stick x3"                             , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Stone x3"                             , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Tree"                                 , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),
    ItemData("Wood x3"                              , RegionFlags.Mainland   , ItemFlags.Idea        , ItemClassification.filler     ),

#endregion

#region Trap Items

    ItemData("Chickens"                             , RegionFlags.Mainland   , ItemFlags.Mob         , ItemClassification.trap       ),
    ItemData("Goop"                                 , RegionFlags.Mainland   , ItemFlags.Mob         , ItemClassification.trap       ),
    ItemData("Rabbits"                              , RegionFlags.Mainland   , ItemFlags.Mob         , ItemClassification.trap       ),
    ItemData("Rat"                                  , RegionFlags.Mainland   , ItemFlags.Mob         , ItemClassification.trap       ),
    ItemData("Slime"                                , RegionFlags.Mainland   , ItemFlags.Mob         , ItemClassification.trap       ),
    ItemData("Snake"                                , RegionFlags.Mainland   , ItemFlags.Mob         , ItemClassification.trap       ),

    # More trap items coming soon...

#endregion
]

# Item group mapping table
group_table: Dict[str, set[str]] = {

    "All Ideas": set(item.name for item in item_table if item.item_flags == ItemFlags.Idea),

    # Mainland
    "All Mainland Ideas": set(item.name for item in item_table if item.region_flags == RegionFlags.Mainland and item.item_flags == ItemFlags.Idea),
    "All Mainland Booster Packs": set(item.name for item in item_table if item.region_flags == RegionFlags.Mainland and item.item_flags == ItemFlags.Booster),

    # Dark Forest
    "All Dark Forest Ideas": set(item.name for item in item_table if item.region_flags == RegionFlags.Forest and item.item_flags == ItemFlags.Idea),
    
    # The Island
    # "All Island Ideas": set(item.name for item in item_table if item.region_flags == RegionFlags.Island and item.item_flags == ItemFlags.Idea),
    # "All Island Booster Packs": set(item.name for item in item_table if item.region_flags == RegionFlags.Island and item.item_flags == ItemFlags.Booster),
}

base_id: int = 91000
current_id: int = base_id

name_to_id = {}

# Create name-to-id lookup
for item in item_table:
    name_to_id[item.name] = current_id
    current_id += 1

def create_mainland_items(world: MultiWorld, player: int, options: StacklandsOptions):

    # Prepare item pool
    item_pool: List[Item] = []

    logging.info("----- Creating 'Mainland' Items -----")

    # If mainland board is selected in YAML
    if options.boards.value & RegionFlags.Mainland:

        # Get items from starting inventory
        excluded_items: List[Item] = world.precollected_items[player]

        # Get all items for region
        region_items: List[ItemData] = [ item for item in item_table if item.region_flags is RegionFlags.Mainland ]

        # Add progression and useful items for region to the pool
        for item_data in [ item for item in region_items if item.classification_flags & (ItemClassification.progression | ItemClassification.useful) ]:

            # Generate AP item
            item: StacklandsItem = StacklandsItem(name_to_id[item_data.name], item_data, player)

            # If item is not in the starting inventory, add it to the prospective item pool
            if item not in excluded_items:
                item_pool.append(item)

    logging.info(f"Adding {len(item_pool)} items to the item pool")

    # Add items to world item pool
    world.itempool += item_pool

def create_forest_items(world: MultiWorld, player: int, options: StacklandsOptions):

    # Prepare item pool
    item_pool: List[Item] = []

    logging.info("----- Creating 'The Dark Forest' Items -----")

    # If The Dark Forest board is selected in YAML
    if options.boards.value & RegionFlags.Forest:

        # Get items from starting inventory
        excluded_items: List[Item] = world.precollected_items[player]

        # Get all items for region
        region_items: List[ItemData] = [ item for item in item_table if item.region_flags is RegionFlags.Forest ]

        # Add progression and useful items for region to the pool
        for item_data in [ item for item in region_items if item.classification_flags & (ItemClassification.progression | ItemClassification.useful) ]:

            # Generate AP item
            item: StacklandsItem = StacklandsItem(name_to_id[item_data.name], item_data, player)

            # If item is not in the starting inventory, add it to the prospective item pool
            if item not in excluded_items:
                item_pool.append(item)

    logging.info(f"Adding {len(item_pool)} items to the item pool")

    # Add items to world item pool
    world.itempool += item_pool

def create_filler_items(world: MultiWorld, player: int, options: StacklandsOptions):

    # Prepare item pool
    item_pool: List[Item] = []

    logging.info("----- Creating Trap / Filler Items -----")

    # Calculate how many filler items to create
    unfilled_count: int = len(world.get_unfilled_locations(player)) - len(world.itempool)

    # If filler items need creating
    if unfilled_count > 0:

        logging.info(f"There are currently {unfilled_count} un-filled locations")

        # Get all filler and trap items
        filler_items: List[ItemData] = [ item for item in item_table if item.classification_flags is ItemClassification.filler or item.classification_flags & ItemClassification.trap ]

        # Calculate selected boards
        mainland_selected: bool = bool(options.boards.value & RegionFlags.Mainland)
        forest_selected: bool = bool(options.boards.value & RegionFlags.Forest)

        # If trap items are enabled
        if options.traps.value:

            logging.info("Adding trap items to the item pool...")

            # Get trap items for selected boards
            trap_items: List[ItemData] = [
                item for item in filler_items if 
                item.classification_flags & ItemClassification.trap and                 # Item is a trap item
                (
                    (mainland_selected and item.region_flags & RegionFlags.Mainland)    # Item is for Mainland and that board is selected
                    or (forest_selected and item.region_flags & RegionFlags.Forest)     # Item is for The Dark Forest and that board is selected
                )
            ]

            # If there are fewer item slots than total trap items, shuffle them to make the limited selection random
            if (unfilled_count < len(trap_items)):
                world.random.shuffle(trap_items)

            # Create and add trap items to the prospective pool
            for trap_item in trap_items:

                logging.info(f"Creating trap item '{trap_item.name}...")

                trap: StacklandsItem = StacklandsItem(name_to_id[trap_item.name], trap_item, player)
                item_pool.append(trap)
                
                # Decrement the unfilled count
                unfilled_count -= 1

                # If no more filler items required, break from for loop
                if unfilled_count == 0:
                    break

        if unfilled_count > 0:

            logging.info(f"There are currently {unfilled_count} un-filled locations")

            junk_items: List[ItemData] = [
                item for item in filler_items if
                item.classification_flags is ItemClassification.filler and              # Item is a filler item
                (
                    (mainland_selected and item.region_flags & RegionFlags.Mainland)    # Item is for Mainland and that board is selected
                    or (forest_selected and item.region_flags & RegionFlags.Forest)     # Item is for The Dark Forest and that board is selected
                )
            ]

            logging.info("Adding junk items to the item pool...")

            # Continue to fill pool until filled
            while unfilled_count > 0:

                # If there are fewer junk items than available slots, shuffle the list to make the limited selection random
                if unfilled_count < len(junk_items):
                    world.random.shuffle(junk_items)

                # Create and add junk items to the prospective pool
                for junk_item in junk_items:

                    logging.info(f"Creating junk item '{junk_item.name}...")

                    junk: StacklandsItem = StacklandsItem(name_to_id[junk_item.name], junk_item, player)
                    item_pool.append(junk)
                    
                    # Decrement the unfilled count
                    unfilled_count -= 1

                    # If no more filler items required, break from for loop
                    if unfilled_count == 0:
                        break

    # Add filler items to the item pool
    world.itempool += item_pool

# Create all items
def create_all_items(world: MultiWorld, player: int) -> None:

    # Get YAML options
    options = world.worlds[player].options

    # Add mainland progression / useful items
    create_mainland_items(world, player, options)

    # Add forest progression / useful items
    create_forest_items(world, player, options)

    # Add remaining trap / filler items
    create_filler_items(world, player, options)

    logging.info(f"Total items: {len(world.itempool)}")
    logging.info(f"Total locations: {len(world.get_unfilled_locations())}")