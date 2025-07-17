import logging
from .Enums import ExpansionType, ItemType, ItemType, OptionFlags, RegionFlags
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
    item_type: ItemType
    option_flags: OptionFlags
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
    ItemData("Humble Beginnings Booster Pack"       , RegionFlags.Mainland   , ItemType.Booster     , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Seeking Wisdom Booster Pack"          , RegionFlags.Mainland   , ItemType.Booster     , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Reap & Sow Booster Pack"              , RegionFlags.Mainland   , ItemType.Booster     , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Curious Cuisine Booster Pack"         , RegionFlags.Mainland   , ItemType.Booster     , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Logic and Reason Booster Pack"        , RegionFlags.Mainland   , ItemType.Booster     , OptionFlags.NA        , ItemClassification.progression),
    ItemData("The Armory Booster Pack"              , RegionFlags.Mainland   , ItemType.Booster     , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Explorers Booster Pack"               , RegionFlags.Mainland   , ItemType.Booster     , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Order and Structure Booster Pack"     , RegionFlags.Mainland   , ItemType.Booster     , OptionFlags.NA        , ItemClassification.progression),

    # Progression
    ItemData("Idea: Brick"                          , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Brickyard"                      , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Campfire"                       , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Cooked Meat"                    , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Farm"                           , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Frittata"                       , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Growth"                         , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: House"                          , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Iron Bar"                       , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Iron Mine"                      , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Lumber Camp"                    , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Magic Wand"                     , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Market"                         , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Omelette"                       , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Offspring"                      , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Plank"                          , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Quarry"                         , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    # ItemData("Idea: Shed"                           , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA      , ItemClassification.progression),
    ItemData("Idea: Slingshot"                      , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Smelter"                        , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Smithy"                         , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Spear"                          , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Stick"                          , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Sword"                          , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Temple"                         , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Throwing Stars"                 , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),

    # Useful
    ItemData("Idea: Axe"                            , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Charcoal"                       , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Coin Chest"                     , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Hammer"                         , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Iron Shield"                    , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Pickaxe"                        , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Resource Chest"                 , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Sawmill"                        , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    # ItemData("Idea: Warehouse"                      , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA      , ItemClassification.useful     ),
    ItemData("Idea: Wooden Shield"                  , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),

    # Filler
    ItemData("Idea: Animal Pen"                     , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Bone Spear"                     , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Boomerang"                      , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Breeding Pen"                   , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Butchery"                       , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Chainmail Armor"                , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Chicken"                        , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Club"                           , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Crane"                          , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Dustbin"                        , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ), 
    ItemData("Idea: Fruit Salad"                    , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Garden"                         , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Hotpot"                         , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Magic Blade"                    , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Magic Glue"                     , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Magic Ring"                     , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Magic Staff"                    , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Magic Tome"                     , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Mess Hall"                      , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Milkshake"                      , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Spiked Plank"                   , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Stew"                           , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Stove"                          , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: University"                     , RegionFlags.Shared     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),

#endregion

#region The Dark Forest Items

    ItemData("Idea: Stable Portal"                  , RegionFlags.Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),

#endregion

#region The Island Items

    # Coming soon...

#endregion

#region YAML-Configured Filler Items

    # Board Expansion Ideas
    ItemData("Idea: Shed"                           , RegionFlags.Shared     , ItemType.Idea       , OptionFlags.Expansion  , ItemClassification.progression),
    ItemData("Idea: Warehouse"                      , RegionFlags.Shared     , ItemType.Idea       , OptionFlags.Expansion  , ItemClassification.useful     ),

    # Board Expansion Items 
    ItemData("Board Size Increase"                  , RegionFlags.Mainland   , ItemType.Buff       , OptionFlags.Expansion  , ItemClassification.progression),
    ItemData("Card Limit Increase"                  , RegionFlags.Mainland   , ItemType.Buff       , OptionFlags.Expansion  , ItemClassification.progression),

#endregion

#region Junk Items

    ItemData("Apple Tree"                           , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Berry x3"                             , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Berry Bush"                           , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Coin"                                 , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Coin x5"                              , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Coin x10"                             , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Egg x3"                               , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Flint x3"                             , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Iron Deposit"                         , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Iron Ore x3"                          , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Milk x3"                              , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Rock"                                 , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Stick x3"                             , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Stone x3"                             , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Tree"                                 , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),
    ItemData("Wood x3"                              , RegionFlags.Shared        , ItemType.Resource    , OptionFlags.NA     , ItemClassification.filler     ),

#endregion

#region Trap Items

    ItemData("Chickens"                             , RegionFlags.Shared        , ItemType.Mob         , OptionFlags.Traps  , ItemClassification.trap       ),
    ItemData("Goop"                                 , RegionFlags.Shared        , ItemType.Mob         , OptionFlags.Traps  , ItemClassification.trap       ),
    ItemData("Rabbits"                              , RegionFlags.Shared        , ItemType.Mob         , OptionFlags.Traps  , ItemClassification.trap       ),
    ItemData("Rat"                                  , RegionFlags.Shared        , ItemType.Mob         , OptionFlags.Traps  , ItemClassification.trap       ),
    ItemData("Slime"                                , RegionFlags.Shared        , ItemType.Mob         , OptionFlags.Traps  , ItemClassification.trap       ),
    ItemData("Snake"                                , RegionFlags.Shared        , ItemType.Mob         , OptionFlags.Traps  , ItemClassification.trap       ),

    # More trap items coming soon...

#endregion
]

# Item group mapping table
group_table: Dict[str, set[str]] = {

    "All Ideas": set(item.name for item in item_table if item.item_type is ItemType.Idea),

    # Mainland
    "All Mainland Ideas": set(item.name for item in item_table if item.region_flags & RegionFlags.Mainland and item.item_type is ItemType.Idea),
    "All Mainland Booster Packs": set(item.name for item in item_table if item.region_flags & RegionFlags.Mainland and item.item_type is ItemType.Booster),

    # Dark Forest
    "All Dark Forest Ideas": set(item.name for item in item_table if item.region_flags & RegionFlags.Forest and item.item_type is ItemType.Idea),
    
    # The Island
    # "All Island Ideas": set(item.name for item in item_table if item.region_flags == RegionFlags.Island and item.item_type is ItemType.Idea),
    # "All Island Booster Packs": set(item.name for item in item_table if item.region_flags == RegionFlags.Island and item.item_type is ItemType.Booster),
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

        # Add progression and useful items (not affected by options) for region to the pool
        for item_data in [ 
            item for item in region_items if 
            item.classification_flags & (ItemClassification.progression | ItemClassification.useful)
             and item.option_flags is OptionFlags.NA
        ]:

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

        # Add progression and useful items (not affected by options) for region to the pool
        for item_data in [ 
            item for item in region_items if 
            item.classification_flags & (ItemClassification.progression | ItemClassification.useful)  and
            item.option_flags is OptionFlags.NA
        ]:

            # Generate AP item
            item: StacklandsItem = StacklandsItem(name_to_id[item_data.name], item_data, player)

            # If item is not in the starting inventory, add it to the prospective item pool
            if item not in excluded_items:
                item_pool.append(item)

    logging.info(f"Adding {len(item_pool)} items to the item pool")

    # Add items to world item pool
    world.itempool += item_pool

def create_expansion_items(world: MultiWorld, player: int, options: StacklandsOptions):

    expansion_pool: List[Item] = []

    logging.info("----- Creating Board Expansion Items -----")

    expansion_items: List[ItemData] = []

    # Calculate selected boards
    mainland_selected: bool = bool(options.boards.value & RegionFlags.Mainland)
    forest_selected: bool = bool(options.boards.value & RegionFlags.Forest)

    # If 'Ideas' mode selected
    if options.board_expansion_mode.value is ExpansionType.Ideas:

        logging.info(f"Creating expansion items as ideas...")

        # Get expansion ideas
        expansion_items = [ 
            item for item in item_table if
            item.option_flags & OptionFlags.Expansion                               # Item is for the 'Expansion Mode' option
            and item.item_type is ItemType.Idea                                     # AND Item is type 'Idea'        
            and (                                                                   # AND
                (mainland_selected and item.region_flags & RegionFlags.Mainland)    # Item is for Mainland and that board is selected
                or (forest_selected and item.region_flags & RegionFlags.Forest)     # Item is for The Dark Forest and that board is selected
            )
        ]

    # If 'Items' mode selected
    elif options.board_expansion_mode.value is ExpansionType.Items:

        logging.info(f"Creating expansion items as items...")

        # Get expansion items
        for expansion_item in [ 
            item for item in item_table if 
            item.option_flags & OptionFlags.Expansion                               # Item is for the 'Expansion Mode' option
            and item.item_type is ItemType.Buff                                     # AND Item is type 'Buff'
            and (                                                                   # AND
                (mainland_selected and item.region_flags & RegionFlags.Mainland)    # Item is for Mainland and that board is selected
                or (forest_selected and item.region_flags & RegionFlags.Forest)     # OR Item is for The Dark Forest and that board is selected
            ) 
        ]:

            # Add each item 6 times
            for _ in range(6):
                expansion_items.append(expansion_item)

    # Add each expansion item to the expansion pool
    for expansion_data in expansion_items:

        logging.info(f"Creating expansion item '{expansion_data.name}'...")

        expansion_item: StacklandsItem = StacklandsItem(name_to_id[expansion_data.name], expansion_data, player)
        expansion_pool.append(expansion_item)

    logging.info(f"Adding {len(expansion_pool)} items to the item pool")

    # Add items to world item pool
    world.itempool += expansion_pool

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
                    item.option_flags & OptionFlags.Traps                                   # Item is for 'Traps' option 
                    and item.classification_flags & ItemClassification.trap                 # AND Item is classified as a trap
                    and (                                                                   # AND
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
            item.classification_flags is ItemClassification.filler                  # Item is classified as filler
            and item.option_flags is OptionFlags.NA                                 # AND Item is not affected by any options
            and (                                                                   # AND
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

    # Add expansion items
    create_expansion_items(world, player, options)

    # Add trap items
    create_trap_items(world, player, options)

    # Add filler items
    create_filler_items(world, player, options)

    logging.info(f"Total items: {len(world.itempool)}")
    logging.info(f"Total locations: {len(world.get_unfilled_locations())}")