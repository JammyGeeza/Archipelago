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

def create_trap_items(world: MultiWorld, player: int, options: StacklandsOptions):

    # Prepare trap pool
    trap_pool: List[Item] = []

    # If traps are enabled and the weighting is greater than 0%
    if options.traps.value and options.trap_weighting.value > 0:

        logging.info("----- Creating Trap Items -----")

        # Calculate how many item slots need filling
        unfilled_count: int = len(world.get_unfilled_locations(player)) - len(world.itempool)

        # Check if there are available item slots
        if unfilled_count > 0:

            logging.info(f"There are {unfilled_count} item slots to be filled")

            # Calculate how many trap items to create
            trap_count: int = round(unfilled_count * options.trap_weighting.value / 100)

            # Check that calculated trap count is one or more
            if trap_count > 0:

                # Calculate selected boards
                mainland_selected: bool = bool(options.boards.value & RegionFlags.Mainland)
                forest_selected: bool = bool(options.boards.value & RegionFlags.Forest)

                # Get all filler and trap items
                trap_items: List[ItemData] = [ 
                    item for item in item_table if 
                    item.classification_flags & ItemClassification.trap                     # Item is a trap
                    and (
                        (mainland_selected and item.region_flags & RegionFlags.Mainland)    # Item is for Mainland and that board is selected
                        or (forest_selected and item.region_flags & RegionFlags.Forest)     # Item is for The Dark Forest and that board is selected
                    )
                ]

                logging.info(f"Attempting to add {trap_count} trap items to the item pool (trap weighting {options.trap_weighting.value}%)...")

                # Fill until trap count reached
                while trap_count > 0:

                    # Shuffle list    
                    world.random.shuffle(trap_items)

                    # Add trap items to trap pool
                    for trap_item in trap_items:

                        logging.info(f"Creating trap item '{trap_item.name}'...")

                        trap: StacklandsItem = StacklandsItem(name_to_id[trap_item.name], trap_item, player)
                        trap_pool.append(trap)
                        
                        # Decrement the trap count
                        trap_count -= 1

                        # If no more trap items required, break from for loop
                        if trap_count == 0:
                            break

                logging.info(f"Added {len(trap_pool)} trap items to the item pool")

            else:
                logging.info("Trap count not high enough due to item slot availability and trap weighting - skipping...")

        else:
            logging.info("No unfilled item slots available for trap items - skipping...")

    else:
        logging.info("Trap item options are disabled - skipping...")

    # Add trap items to item pool
    world.itempool += trap_pool

def create_filler_items(world: MultiWorld, player: int, options: StacklandsOptions):

    # Prepare item pool
    filler_pool: List[Item] = []

    logging.info("----- Creating Filler Items -----")

    # Calculate how many item slots need filling
    unfilled_count: int = len(world.get_unfilled_locations(player)) - len(world.itempool)

    # If filler items need creating
    if unfilled_count > 0:

        logging.info(f"There are {unfilled_count} item slots to be filled")

        # Calculate selected boards
        mainland_selected: bool = bool(options.boards.value & RegionFlags.Mainland)
        forest_selected: bool = bool(options.boards.value & RegionFlags.Forest)

        # Get all filler and trap items
        filler_items: List[ItemData] = [ 
            item for item in item_table if
            item.classification_flags is ItemClassification.filler                  # Item is a filler item
            and (
                (mainland_selected and item.region_flags & RegionFlags.Mainland)    # Item is for Mainland and that board is selected
                or (forest_selected and item.region_flags & RegionFlags.Forest)     # Item is for The Dark Forest and that board is selected
            )
        ]

        logging.info(f"Attempting to add {unfilled_count} filler items to the item pool...")

        # Continue to fill pool until filled
        while unfilled_count > 0:

            # If there are fewer junk items than available slots, shuffle the list to make the limited selection random
            if unfilled_count < len(filler_items):
                world.random.shuffle(filler_items)

            # Create and add junk items to the prospective pool
            for filler_item in filler_items:

                logging.info(f"Creating filler item '{filler_item.name}'...")

                junk: StacklandsItem = StacklandsItem(name_to_id[filler_item.name], filler_item, player)
                filler_pool.append(junk)
                
                # Decrement the unfilled count
                unfilled_count -= 1

                # If no more filler items required, break from for loop
                if unfilled_count == 0:
                    break

        logging.info(f"Added {len(filler_pool)} filler items to the item pool")

    else:
        logging.info(f"No free slots for filler items - skipping...")

    # Add filler items to the item pool
    world.itempool += filler_pool

# Create all items
def create_all_items(world: MultiWorld, player: int) -> None:

    # Get YAML options
    options = world.worlds[player].options

    # Add mainland progression / useful items
    create_mainland_items(world, player, options)

    # Add forest progression / useful items
    create_forest_items(world, player, options)

    # Add trap items
    create_trap_items(world, player, options)

    # Add remaining trap / filler items
    create_filler_items(world, player, options)

    logging.info(f"Total items: {len(world.itempool)}")
    logging.info(f"Total locations: {len(world.get_unfilled_locations())}")