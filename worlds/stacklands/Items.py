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
    ItemData("Humble Beginnings Booster Pack"       , RegionFlags.Mainland              , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Seeking Wisdom Booster Pack"          , RegionFlags.Mainland              , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Reap & Sow Booster Pack"              , RegionFlags.Mainland              , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Curious Cuisine Booster Pack"         , RegionFlags.Mainland              , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Logic and Reason Booster Pack"        , RegionFlags.Mainland              , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("The Armory Booster Pack"              , RegionFlags.Mainland              , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression), 
    ItemData("Explorers Booster Pack"               , RegionFlags.Mainland              , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression), 
    ItemData("Order and Structure Booster Pack"     , RegionFlags.Mainland              , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early

    # Progression Ideas
    ItemData("Idea: Brick"                          , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Brickyard"                      , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Campfire"                       , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Club"                           , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Coin Chest"                     , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Cooked Meat"                    , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Farm"                           , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Frittata"                       , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Growth"                         , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: House"                          , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Iron Bar"                       , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Iron Shield"                    , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Lumber Camp"                    , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Magic Wand"                     , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Market"                         , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Offspring"                      , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Omelette"                       , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Plank"                          , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Quarry"                         , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Shed"                           , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Slingshot"                      , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Smelter"                        , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Smithy"                         , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Spear"                          , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Spiked Plank"                   , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Stick"                          , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Stove"                          , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Sword"                          , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Temple"                         , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Throwing Stars"                 , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Warehouse"                      , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Wooden Shield"                  , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),

    # Useful Ideas
    ItemData("Idea: Axe"                            , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.useful),
    ItemData("Idea: Chicken"                        , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.useful),
    ItemData("Idea: Hammer"                         , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.useful),
    ItemData("Idea: Pickaxe"                        , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.useful),

    # Equipmentsanity Ideas (that are not required for progression elsewhere)
    # Item classifications are changed to 'progression' if equipmentsanity is enabled
    ItemData("Idea: Bone Spear"                     , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.filler),
    ItemData("Idea: Boomerang"                      , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.filler),
    ItemData("Idea: Chainmail Armor"                , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.useful),
    ItemData("Idea: Magic Blade"                    , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.filler),
    ItemData("Idea: Magic Ring"                     , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.filler),
    ItemData("Idea: Magic Staff"                    , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.filler),
    ItemData("Idea: Magic Tome"                     , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.filler),

    # Foodsanity Ideas (that are not required for progression elsewhere)
    # Item classifications are changed to 'progression' if foodsanity is enabled
    ItemData("Idea: Fruit Salad"                    , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Foodsanity        , ItemClassification.filler),
    ItemData("Idea: Milkshake"                      , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Foodsanity        , ItemClassification.filler),
    ItemData("Idea: Stew"                           , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Foodsanity        , ItemClassification.filler),

    # Structuresanity Ideas (that are not required for progression elsewhere)
    # Item classifications are changed to 'progression' if structuresanity is enabled
    ItemData("Idea: Animal Pen"                     , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.useful),
    ItemData("Idea: Breeding Pen"                   , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler),
    ItemData("Idea: Butchery"                       , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler),
    ItemData("Idea: Crane"                          , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler),
    ItemData("Idea: Dustbin"                        , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler), 
    ItemData("Idea: Garden"                         , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler),
    ItemData("Idea: Hotpot"                         , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler),
    ItemData("Idea: Iron Mine"                      , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.useful),
    ItemData("Idea: Resource Chest"                 , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.useful),
    ItemData("Idea: Sawmill"                        , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.useful),
    ItemData("Idea: University"                     , RegionFlags.Mainland              , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler),

#endregion

#region The Dark Forest Items

    ItemData("Idea: Stable Portal"                  , RegionFlags.Forest                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),

#endregion

#region The Island Items

    # Booster Packs
    ItemData("On the Shore Booster Pack"            , RegionFlags.Island                , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Island of Ideas Booster Pack"         , RegionFlags.Island                , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Grilling and Brewing Booster Pack"    , RegionFlags.Island                , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Island Insights Booster Pack"         , RegionFlags.Island                , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Advanced Archipelago Booster Pack"    , RegionFlags.Island                , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Enclave Explorers Booster Pack"       , RegionFlags.Island                , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.progression),
    
    # Progression Ideas
    ItemData("Idea: Bow"                            , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Bottle of Rum"                  , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Bottle of Water"                , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Broken Bottle"                  , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Cathedral"                      , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Ceviche"                        , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Charcoal"                       , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Coin"                           , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Composter"                      , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Distillery"                     , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Empty Bottle"                   , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Fabric"                         , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Fish Trap"                      , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Forest Amulet"                  , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Glass"                          , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Gold Bar"                       , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Golden Chestplate"              , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Greenhouse"                     , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Lighthouse"                     , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Mess Hall"                      , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Rope"                           , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Rowboat"                        , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Sacred Key"                     , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Sail"                           , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Sandstone"                      , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Seafood Stew"                   , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Shell Chest"                    , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),
    ItemData("Idea: Sloop"                          , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression_skip_balancing), # <- Try not to release this too early
    ItemData("Idea: Sushi"                          , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.progression),

    # Useful Ideas
    ItemData("Idea: Fishing Rod"                    , RegionFlags.Island                , ItemType.Idea         , OptionFlags.NONE              , ItemClassification.useful),

    # Equipmentsanity Ideas (that are not required for progression elsewhere)
    # Item classifications are changed to 'progression' if equipmentsanity is enabled
    ItemData("Idea: Blunderbuss"                    , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.filler),
    ItemData("Idea: Bone Staff"                     , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.filler),
    ItemData("Idea: Crossbow"                       , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.useful),
    ItemData("Idea: Mountain Amulet"                , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.useful),
    ItemData("Idea: Wizard Robe"                    , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Equipmentsanity   , ItemClassification.filler),

    # Foodsanity Ideas (that are not required for progression elsewhere)
    # Item classifications are changed to 'progression' if foodsanity is enabled
    ItemData("Idea: Tamago Sushi"                   , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Foodsanity        , ItemClassification.filler),

    # Structuresanity Ideas (that are not required for progression elsewhere)
    # Item classifications are changed to 'progression' if structuresanity is enabled
    ItemData("Idea: Aquarium"                       , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler),
    ItemData("Idea: Frigate"                        , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.useful),
    ItemData("Idea: Gold Mine"                      , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.useful),
    ItemData("Idea: Magic Glue"                     , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler),
    ItemData("Idea: Resource Magnet"                , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler),
    ItemData("Idea: Sand Quarry"                    , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.useful),
    ItemData("Idea: Wishing Well"                   , RegionFlags.Island                , ItemType.Idea         , OptionFlags.Structuresanity   , ItemClassification.filler),

#endregion

#region YAML-Configured Filler Items

    # Board Expansion Items
    ItemData("Mainland Board Expansion"             , RegionFlags.Mainland              , ItemType.Structure    , OptionFlags.Expansion         , ItemClassification.progression),
    ItemData("Island Board Expansion"               , RegionFlags.Island                , ItemType.Structure    , OptionFlags.Expansion         , ItemClassification.progression),

#endregion

#region Junk Items

    # Filler Resource Boosters
    ItemData("Mainland Resource Booster Pack"       , RegionFlags.Mainland              , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.filler),
    ItemData("Island Resource Booster Pack"         , RegionFlags.Island                , ItemType.Booster      , OptionFlags.NONE              , ItemClassification.filler),

#endregion

#region Trap Items

    ItemData("Feed Villagers Trap"                  , RegionFlags.Mainland_and_Forest   , ItemType.Trap         , OptionFlags.Traps             , ItemClassification.trap),
    ItemData("Mob Trap"                             , RegionFlags.Mainland_and_Forest   , ItemType.Trap         , OptionFlags.Traps             , ItemClassification.trap),
    ItemData("Sell Cards Trap"                      , RegionFlags.Mainland_and_Forest   , ItemType.Trap         , OptionFlags.Traps             , ItemClassification.trap),
    ItemData("Strange Portal Trap"                  , RegionFlags.Mainland_and_Forest   , ItemType.Trap         , OptionFlags.Traps             , ItemClassification.trap),

#endregion
]

# Item group mapping table
group_table: Dict[str, set[str]] = {

    # All
    "All Booster Packs": set(item.name for item in item_table if item.item_type is ItemType.Booster),
    "All Ideas": set(item.name for item in item_table if item.item_type is ItemType.Idea),

    # Mainland
    "All Mainland Booster Packs": set(item.name for item in item_table if item.region_flags is RegionFlags.Mainland and item.item_type is ItemType.Booster),
    "All Mainland Ideas": set(item.name for item in item_table if item.region_flags is RegionFlags.Mainland and item.item_type is ItemType.Idea),

    # Dark Forest
    "All Dark Forest Ideas": set(item.name for item in item_table if item.region_flags is RegionFlags.Forest and item.item_type is ItemType.Idea),
    
    # The Island
    "All Island Booster Packs": set(item.name for item in item_table if item.region_flags == RegionFlags.Island and item.item_type is ItemType.Booster),
    "All Island Ideas": set(item.name for item in item_table if item.region_flags == RegionFlags.Island and item.item_type is ItemType.Idea),
}

base_id: int = 91000
current_id: int = base_id

name_to_id = {}

# Create name-to-id lookup
for item in item_table:
    name_to_id[item.name] = current_id
    current_id += 1

def create_progression_items(world: MultiWorld, player: int, items: List[ItemData]):

    # Get items from starting inventory
    excluded_items: List[Item] = world.precollected_items[player]

    # Pop all relevant progression / useful items
    progression_items: List[ItemData] = [
        items.pop(index)
        for index in reversed(range(len(items)))
        if (item:= items[index]) 
        and item.option_flags is OptionFlags.NONE
        and item.classification_flags & (ItemClassification.progression | ItemClassification.useful)
    ]

    # Prepare item pool
    item_pool: List[Item] = []

    # Add each item
    for item_data in progression_items:
        
        # Generate AP item
        item: StacklandsItem = StacklandsItem(name_to_id[item_data.name], item_data, player)

        # If item is not in the starting inventory, add it to the prospective item pool
        if item not in excluded_items:
            item_pool.append(item)

    # Add items to world item pool
    world.itempool += item_pool

def create_expansion_items(world: MultiWorld, player: int, items: List[ItemData], options: StacklandsOptions):

    # Ignore if expansion items not selected
    if not (options.board_expansion_mode & ExpansionType.Expansion_Items):
        return

    # Pop all relevant board expansion items
    expansion_items: List[ItemData] = [
        items.pop(index)
        for index in reversed(range(len(items)))
        if (item:= items[index]) 
        and item.option_flags is OptionFlags.Expansion
        and item.classification_flags & (ItemClassification.progression | ItemClassification.useful)
    ]

    # Prepare item pool 
    item_pool: List[Item] = []

    # Add items
    for item_data in expansion_items:

        # Add X amount of structures to the item pool
        if item_data.item_type is ItemType.Structure:
            for _ in range(options.board_expansion_count.value):
                expansion_item: StacklandsItem = StacklandsItem(name_to_id[item_data.name], item_data, player)
                item_pool.append(expansion_item)

    # Add items to world item pool
    world.itempool += item_pool

def create_sanity_items(world: MultiWorld, player: int, items: List[ItemData], options: StacklandsOptions):
    
    # Get items from starting inventory
    excluded_items: List[Item] = world.precollected_items[player]

    # Pop all relevant sanity items
    sanity_items: List[ItemData] = [
        items.pop(index)
        for index in reversed(range(len(items)))
        if (item:= items[index])
        and item.option_flags & (OptionFlags.Equipmentsanity | OptionFlags.Foodsanity | OptionFlags.Structuresanity)
    ]

    logging.info(f"Found {len(sanity_items)} sanity items")

    # Prepare item pool
    item_pool: List[Item] = []

    # Add each item
    for item_data in sanity_items:

        # Generate AP item
        item: StacklandsItem = StacklandsItem(name_to_id[item_data.name], item_data, player)

        # If item is not in the starting inventory, add it to the prospective item pool
        if item not in excluded_items:

            # Adjust item classification to 'progression' for enabled sanity items
            if (
                (options.equipmentsanity.value and bool(item_data.option_flags & OptionFlags.Equipmentsanity))
                or (options.foodsanity.value and bool(item_data.option_flags & OptionFlags.Foodsanity))
                or (options.structuresanity.value and bool(item_data.option_flags & OptionFlags.Structuresanity))
            ):
                item.classification = ItemClassification.progression

            item_pool.append(item)

    # Add items to world item pool
    world.itempool += item_pool

def create_trap_items(world: MultiWorld, player: int, options: StacklandsOptions):

    # Prepare trap pool
    item_pool: List[Item] = []

    # Check if there are available item slots
    if (unfilled_count:= len(world.get_unfilled_locations(player)) - len([item for item in world.itempool if item.player == player])) > 0:

        # Calculate how many trap items to create
        trap_count: int = round(unfilled_count * options.trap_fill.value / 100)

        # Check that calculated trap count is one or more
        if trap_count >= 1:

            # Select traps using trap weights
            trap_selection = world.random.choices(
                population=list(world.trap_weights.keys()),
                weights=list(world.trap_weights.values()),
                k=trap_count
            )

            # Add trap items to the pool
            for trap_item in trap_selection:
                trap_data: ItemData = next(item for item in item_table if item.name == trap_item)
                trap: StacklandsItem = StacklandsItem(name_to_id[trap_data.name], trap_data, player)
                item_pool.append(trap)

        else:
            logging.info("Trap count not high enough due to unfilled slot availability and trap weighting - skipping...")
    else:
        logging.info("No unfilled item slots available for trap items - skipping...")

    # Add trap items to item pool
    world.itempool += item_pool

def create_filler_items(world: MultiWorld, player: int, items: List[ItemData], options: StacklandsOptions):

    # Prepare item pool
    item_pool: List[Item] = []

    # Get items from starting inventory
    excluded_items: List[Item] = world.precollected_items[player]

    # If there are un-filled slots...
    if (unfilled_count:= len(world.get_unfilled_locations(player)) - len([item for item in world.itempool if item.player == player])) > 0:

        # Get filler ideas
        filler_ideas: List[ItemData] = [
            item for item in items if
            item.classification_flags is ItemClassification.filler  # Item is classified as 'filler'
            and item.item_type is ItemType.Idea                     # AND Item is an 'Idea'
        ]

        # Get amount of filler ideas to add (amount of slots remaining or amount of filler ideas, whichever is lower)
        idea_fill_count: int = min(len(filler_ideas), unfilled_count)

        # Randomly select filler ideas (no duplicates) - select all if there's space or fill remaining unfilled count, whichever is lower
        for idea_data in world.random.sample(filler_ideas, k=idea_fill_count):
            idea_item: StacklandsItem = StacklandsItem(name_to_id[idea_data.name], idea_data, player)

            # If item is not in the starting inventory, add it to the prospective item pool
            if idea_item not in excluded_items:
                item_pool.append(idea_item)
        
        # Re-count unfilled slots
        unfilled_count -= len(item_pool)

        # Fill remaining spots with filler booster
        if unfilled_count > 0:

            # Select filler boosters using weights
            booster_selection = world.random.choices(
                population=list(world.filler_booster_weights.keys()),
                weights=list(world.filler_booster_weights.values()),
                k=unfilled_count
            )

            # Add filler boosters to the pool
            for booster_item in booster_selection:
                booster_data: ItemData = next(item for item in item_table if item.name == booster_item)
                booster: StacklandsItem = StacklandsItem(name_to_id[booster_data.name], booster_data, player)
                item_pool.append(booster)

    else:
        logging.info(f"No free slots for filler items - skipping...")

    # Add filler items to the item pool
    world.itempool += item_pool

def create_all_items(world: MultiWorld, player: int) -> None:

    # Get YAML options
    options = world.worlds[player].options

    # Calculate if any traps are required
    traps_selected: bool = options.trap_fill.value > 0 and any(weight > 0 for weight in [
        options.feed_villagers_trap_weight.value,
        options.mob_trap_weight.value,
        options.sell_cards_trap_weight,
        options.strange_portal_trap_weight
    ]) 

    # Select items for selected boards
    item_pool: List[ItemData] = [
        item for item in item_table
        if item.region_flags & options.boards.value     # Item contains a flag for selected boards
    ]

    # Add all progression / useful items
    create_progression_items(world, player, item_pool)

    # Add expansion items
    create_expansion_items(world, player, item_pool, options)

    # Add sanity items
    create_sanity_items(world, player, item_pool, options)

    # Add trap items if enabled
    if traps_selected:
        create_trap_items(world, player, options)

    # Add filler items
    create_filler_items(world, player, item_pool, options)