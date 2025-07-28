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
    ItemData("Idea: Shed"                           , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Slingshot"                      , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Smelter"                        , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Smithy"                         , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Spear"                          , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Stick"                          , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Sword"                          , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Temple"                         , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),
    ItemData("Idea: Throwing Stars"                 , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),

    # Useful
    ItemData("Idea: Animal Pen"                     , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Axe"                            , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Chainmail Armor"                , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Charcoal"                       , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Chicken"                        , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Coin Chest"                     , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Hammer"                         , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Garden"                         , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Iron Shield"                    , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Pickaxe"                        , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Resource Chest"                 , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Sawmill"                        , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Stove"                          , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),
    ItemData("Idea: Wooden Shield"                  , RegionFlags.Mainland   , ItemType.Idea        , OptionFlags.NA        , ItemClassification.useful     ),

#endregion

#region The Dark Forest Items

    ItemData("Idea: Stable Portal"                  , RegionFlags.Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.progression),

#endregion

#region The Island Items

    # Coming soon...

#endregion

#region YAML-Configured Filler Items

    # Board Expansion Ideas
    ItemData("Idea: Warehouse"                      , RegionFlags.Mainland_and_Forest     , ItemType.Idea       , OptionFlags.Expansion  , ItemClassification.useful     ),

    # Board Expansion Items
    ItemData("Board Expansion"                      , RegionFlags.Mainland   , ItemType.Structure  , OptionFlags.Expansion  , ItemClassification.progression),

#endregion

#region Junk Items

    # Filler Ideas
    ItemData("Idea: Bone Spear"                     , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Boomerang"                      , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Breeding Pen"                   , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Butchery"                       , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Club"                           , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Crane"                          , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Dustbin"                        , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ), 
    ItemData("Idea: Fruit Salad"                    , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Hotpot"                         , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Magic Blade"                    , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Magic Glue"                     , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Magic Ring"                     , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Magic Staff"                    , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Magic Tome"                     , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Mess Hall"                      , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Milkshake"                      , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Spiked Plank"                   , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: Stew"                           , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),
    ItemData("Idea: University"                     , RegionFlags.Mainland_and_Forest     , ItemType.Idea        , OptionFlags.NA        , ItemClassification.filler     ),

    # Filler Resources
    ItemData("Resource Booster Pack"                , RegionFlags.Mainland_and_Forest     , ItemType.Booster     , OptionFlags.NA        , ItemClassification.filler     ),

#endregion

#region Trap Items

    ItemData("Feed Villagers Trap"                  , RegionFlags.Mainland_and_Forest        , ItemType.Trap        , OptionFlags.Traps  , ItemClassification.trap       ),
    # ItemData("Flip Trap"                            , RegionFlags.Mainland_and_Forest        , ItemType.Trap        , OptionFlags.Traps  , ItemClassification.trap       ),
    ItemData("Mob Trap"                             , RegionFlags.Mainland_and_Forest        , ItemType.Trap        , OptionFlags.Traps  , ItemClassification.trap       ),
    ItemData("Sell Cards Trap"                      , RegionFlags.Mainland_and_Forest        , ItemType.Trap        , OptionFlags.Traps  , ItemClassification.trap       ),
    ItemData("Strange Portal Trap"                  , RegionFlags.Mainland_and_Forest        , ItemType.Trap        , OptionFlags.Traps  , ItemClassification.trap       ),

#endregion
]

# Item group mapping table
group_table: Dict[str, set[str]] = {

    "All Ideas": set(item.name for item in item_table if item.item_type is ItemType.Idea),

    # Mainland
    "All Mainland Ideas": set(item.name for item in item_table if item.region_flags is RegionFlags.Mainland and item.item_type is ItemType.Idea),
    "All Mainland Booster Packs": set(item.name for item in item_table if item.region_flags is RegionFlags.Mainland and item.item_type is ItemType.Booster),

    # Dark Forest
    "All Dark Forest Ideas": set(item.name for item in item_table if item.region_flags is RegionFlags.Forest and item.item_type is ItemType.Idea),
    
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
    if options.quest_checks.value & RegionFlags.Mainland:

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
    if options.quest_checks.value & RegionFlags.Forest:

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
    mainland_selected: bool = bool(options.quest_checks.value & RegionFlags.Mainland)
    forest_selected: bool = bool(options.quest_checks.value & RegionFlags.Forest)

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
            item.option_flags & OptionFlags.Expansion                               # Item is for the 'Board Expansion Mode' option
            and item.item_type is ItemType.Structure                                # AND Item is type 'Structure'
            and (                                                                   # AND
                (mainland_selected and item.region_flags & RegionFlags.Mainland)    # Item is for Mainland and that board is selected
                or (forest_selected and item.region_flags & RegionFlags.Forest)     # OR Item is for The Dark Forest and that board is selected
            )
        ]:
            # Add amount configured in yaml
            for _ in range(options.board_expansion_count.value):
                expansion_items.append(expansion_item)

    # Add each expansion item to the expansion pool
    for expansion_data in expansion_items:

        logging.info(f"Creating expansion item '{expansion_data.name}'...")

        expansion_item: StacklandsItem = StacklandsItem(name_to_id[expansion_data.name], expansion_data, player)
        expansion_pool.append(expansion_item)

    logging.info(f"Adding {len(expansion_pool)} expansion items to the item pool")

    # Add items to world item pool
    world.itempool += expansion_pool

def create_trap_items(world: MultiWorld, player: int, options: StacklandsOptions):

    # Prepare trap pool
    trap_pool: List[Item] = []

    # If traps are enabled and the weighting is greater than 0%
    if options.trap_fill.value > 0:

        logging.info("----- Creating Trap Items -----")

        # Calculate how many item slots need filling for this player
        unfilled_count: int = len(world.get_unfilled_locations(player)) - len([item for item in world.itempool if item.player == player])

        # Check if there are available item slots
        if unfilled_count > 0:

            logging.info(f"There are {unfilled_count} item slots to be filled")

            # Calculate how many trap items to create
            trap_count: int = round(unfilled_count * options.trap_fill.value / 100)

            # Check that calculated trap count is one or more
            if trap_count > 0:

                logging.info(f"Adding {trap_count} trap items to the item pool (trap fill {options.trap_fill.value}%)...")

                # Select traps using trap weights
                trap_selection = world.random.choices(
                    population=list(world.trap_weights.keys()),
                    weights=list(world.trap_weights.values()),
                    k=trap_count
                )

                # Add trap items to the pool
                for trap_item in trap_selection:
                    logging.info(f"Creating '{trap_item}' trap item...")

                    trap_data: ItemData = next(item for item in item_table if item.name == trap_item)
                    trap: StacklandsItem = StacklandsItem(name_to_id[trap_data.name], trap_data, player)
                    trap_pool.append(trap)

                logging.info(f"Added {len(trap_pool)} trap items to the item pool")

            else:
                logging.info("Trap count not high enough due to item slot availability and trap weighting - skipping...")

        else:
            logging.info("No unfilled item slots available for trap items - skipping...")

    else:
        logging.info("Trap fill set to 0%, skipping trap items...")

    # Add trap items to item pool
    world.itempool += trap_pool

def create_filler_items(world: MultiWorld, player: int, options: StacklandsOptions):

    # Prepare item pool
    filler_pool: List[Item] = []

    logging.info("----- Creating Filler Items -----")
    logging.info(f"Unfilled locations: {len(world.get_unfilled_locations(player))}")

    # If there are un-filled slots for this player...
    if (unfilled_count:= len(world.get_unfilled_locations(player)) - len([item for item in world.itempool if item.player == player])) > 0:

        logging.info(f"There are {unfilled_count} un-filled item slots")

        # Calculate selected boards
        mainland_selected: bool = bool(options.quest_checks.value & RegionFlags.Mainland)
        forest_selected: bool = bool(options.quest_checks.value & RegionFlags.Forest)

        # Get filler ideas
        filler_ideas: List[ItemData] = [
            item for item in item_table if
            item.classification_flags is ItemClassification.filler                  # Item is classified as 'filler'
            and item.item_type is ItemType.Idea                                     # AND Item is an 'Idea'
            and item.option_flags is OptionFlags.NA                                 # AND Item is not affected by options
            and {                                                                   # AND
                (mainland_selected and item.region_flags & RegionFlags.Mainland)    # Item is for Mainland and that board is selected
                or (forest_selected and item.region_flags & RegionFlags.Forest)     # OR Item is for The Dark Forest and that board is selected
            }
        ]

        # Randomly select how many ideas and boosters to add to the filler pool
        idea_count: int = world.random.randint(0, unfilled_count if unfilled_count < len(filler_ideas) else len(filler_ideas))

        # Select that many filler ideas (without duplicates)
        for idea_data in world.random.sample(filler_ideas, k=idea_count):

            logging.info(f"Creating filler item '{idea_data.name}'...")

            idea: StacklandsItem = StacklandsItem(name_to_id[idea_data.name], idea_data, player)
            filler_pool.append(idea)

        # Fill remaining spots with filler booster
        if idea_count < unfilled_count:

            # Get resource booster item
            filler_booster_data: ItemData = next((item for item in item_table if item.classification_flags is ItemClassification.filler and item.item_type is ItemType.Booster))

            # Add filler boosters
            for _ in range(unfilled_count - idea_count):

                logging.info(f"Creating filler item '{filler_booster_data.name}'...")

                filler_booster: StacklandsItem = StacklandsItem(name_to_id[filler_booster_data.name], filler_booster_data, player)
                filler_pool.append(filler_booster)

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