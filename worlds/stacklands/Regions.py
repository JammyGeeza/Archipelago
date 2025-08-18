import logging
from .Enums import CheckType, ExpansionType, GoalFlags, OptionFlags, RegionFlags, SpendsanityType
from typing import List, NamedTuple
from BaseClasses import Entrance, Item, ItemClassification, LocationProgressType, MultiWorld, Region
from .Options import StacklandsOptions
from .Locations import LocationData, StacklandsLocation, location_table, name_to_id as location_lookup

class RegionData(NamedTuple):
    name: str
    locations: List[LocationData]
    exits: List[str]

def create_region(world: MultiWorld, player: int, region_data: RegionData) -> Region:
    """Create a region in the multiworld from the region data"""

    # Create region object
    region: Region = Region(region_data.name, player, world)

    # Get all locations that are not goals
    for location_data in [ loc for loc in region_data.locations if loc.check_type is CheckType.Check ]:

        logging.info(f"Creating check: {location_data.name}")

        # Create and add location to region
        location: StacklandsLocation = StacklandsLocation(player, location_data, location_lookup[location_data.name], region)
        region.locations.append(location)

    # Get all locations that are goals
    for goal_data in [ loc for loc in region_data.locations if loc.check_type is CheckType.Goal ]:

        logging.info(f"Setting goal event for '{goal_data.name}'...")

        # Create and add goal to region
        goal: StacklandsLocation = StacklandsLocation(player, goal_data, None, region)
        goal.place_locked_item(Item("Victory", ItemClassification.progression, None, player))
        region.locations.append(goal)

    # Add exits to region
    for exit in region_data.exits:
        region.exits.append(Entrance(player, exit, region))

    # Add region to world
    world.regions.append(region)

    logging.info(f"Added {len(region.locations)} checks to the check pool!")

    return region

def create_all_regions(world: MultiWorld, player: int):
    """Create all regions for this apworld"""
    
    # Get YAML Options
    options: StacklandsOptions = world.worlds[player].options

    # expansion_items_selected: bool = options.board_expansion_mode.value is ExpansionType.Items
    mobsanity_selected: bool = options.mobsanity.value
    packsanity_selected: bool = options.packsanity.value
    pausing_selected: bool = options.pausing.value
    spendsanity_selected: bool = bool(options.spendsanity.value != SpendsanityType.Off)

    logging.info(f"Spendsanity value: {options.spendsanity.value}")
    logging.info(f"Spendsanity selected: {spendsanity_selected}")

    # Get all applicable locations for this run, given the YAML options
    location_pool: List[LocationData] = [
        loc for loc in location_table 
        if loc.region_flags & options.goal.value                                        # Location contains a flag for selected boards
        and (                                                                           # AND
            loc.option_flags is OptionFlags.NONE                                        # Is not affected by YAML options
            # or (expansion_items_selected and loc.option_flags & OptionFlags.Expansion)
            or (mobsanity_selected and loc.option_flags is OptionFlags.Mobsanity)        # OR Mobsanity is selected and has Mobsanity flag
            or (packsanity_selected and loc.option_flags is OptionFlags.Packsanity)      # OR Packsanity is selected and has packsanity flag
            or (pausing_selected and loc.option_flags is OptionFlags.Pausing)            # OR Pausing is selected and has pausing flag
            # or (spendsanity_selected and loc.option_flags is OptionFlags.Spendsanity)    # OR Spendsanity is selected and has Spendsanity flag
        )
    ]
    
    # If Spendsanity is enabled, add configured amount of spendsanity checks to the pool
    if spendsanity_selected:
        for location in [ loc for loc in location_table if loc.region_flags & options.goal.value and loc.option_flags is OptionFlags.Spendsanity ]:
            for x in range(1, options.spendsanity_count.value + 1):
                location_pool.append(LocationData(location.name.format(count=x), location.region_flags, location.check_type, location.option_flags, location.progress_type))

    # Create regions
    menu_region: Region = create_menu_region(world, player)
    mainland_region: Region = create_mainland_region(world, player, location_pool)
    forest_region: Region = create_forest_region(world, player, location_pool)
    island_region: Region = create_island_region(world, player, location_pool)

    # Menu exit(s)
    world.get_entrance("Start", player).connect(mainland_region)

    # Mainland exit(s)
    world.get_entrance("Portal from Mainland to Dark Forest", player).connect(forest_region)
    world.get_entrance("Rowboat from Mainland to The Island", player).connect(island_region)

    # The Island exit(s)
    world.get_entrance("Portal from The Island to Dark Forest", player).connect(forest_region)
    world.get_entrance("Rowboat from The Island to Mainland", player).connect(mainland_region)

    # Mainland Events
    # mainland_region.add_event("Kill the Demon", "Demon")
    # mainland_region.add_event("Milestone: Offspring", "Offspring")
    # mainland_region.add_event("Milestone: Sustainable Village", "Sustainable Village")
    # mainland_region.add_event("Milestone: Iron Bars", "Iron Bars")
    # mainland_region.add_event("Milestone: Basic Equipment", "Basic Equipment")
    # mainland_region.add_event("Milestone: Advanced Equipment", "Advanced Equipment")
    # # mainland_region.add_event("Create Iron Bars", "5x Iron Bars")
    # mainland_region.add_event("Milestone: Summon Mainland Boss", "Demon")

    # Create Mainland / Forest Shared region
    # mainland_forest_shared_region: Region = create_mainland_forest_shared_region(world, player, location_pool)
    # world.get_entrance("Mainland to Shared: Mainland & Dark Forest", player).connect(mainland_forest_shared_region)
    # world.get_entrance("Dark Forest to Shared: Mainland & Dark Forest", player).connect(mainland_forest_shared_region)

    # # Create Mainland / Island Shared region
    # mainland_island_shared_region: Region = create_mainland_island_shared_region(world, player, location_pool)
    # world.get_entrance("Mainland to Shared: Mainland & The Island", player).connect(mainland_island_shared_region)
    # world.get_entrance("The Island to Shared: Mainland & The Island", player).connect(mainland_island_shared_region)

    # # If mainland board is included, create region
    # if options.goal.value & RegionFlags.Mainland:
        

    # # If dark forest board is included, create region
    # if options.goal.value & RegionFlags.Forest:
        

    # # If island board is included, create region
    # if options.goal.value & RegionFlags.Island:
        

    # Create regions
    # menu_region: Region = create_menu_region(world, player, options)
    # mainland_region: Region = create_mainland_region(world, player, options)
    # forest_region: Region = create_forest_region(world, player, options)

    # Connect region entrances and exits
    
    
    # world.get_entrance("Rowboat", player).connect(world.get_region("The Island", player))

def create_menu_region(world: MultiWorld, player: int) -> Region:
    """Create the default 'Menu' region"""
    
    logging.info("----- Creating 'Menu' Region -----")

    # Compile region data
    menu_region: RegionData = RegionData("Menu", [], ["Start"])

    # Create region
    return create_region(world, player, menu_region)

def create_mainland_region(world: MultiWorld, player: int, locations: List[LocationData]) -> Region:
    """Create the 'Mainland' region"""

    logging.info("----- Creating 'Mainland' Region -----")

    # Pop all mainland checks from the locations pool
    check_pool: List[LocationData] = [
        locations.pop(index)
        for index in reversed(range(len(locations)))
        if locations[index].region_flags & RegionFlags.Mainland
    ]

    logging.info(f"Found {len(check_pool)} checks for region")

    # Compile region data
    region_data: RegionData = RegionData("Mainland", check_pool, [ 
        # "Mainland to Shared: Mainland & Dark Forest",
        # "Mainland to Shared: Mainland & The Island", 
        "Portal from Mainland to Dark Forest",
        "Rowboat from Mainland to The Island"
    ])

    # Create region
    return create_region(world, player, region_data)

def create_forest_region(world: MultiWorld, player: int, locations: List[LocationData]) -> Region:
    """Create the 'Dark Forest' region"""

    logging.info("----- Creating 'The Dark Forest' Region -----")

    # Pop all mainland checks from the locations pool
    check_pool: List[LocationData] = [
        locations.pop(index)
        for index in reversed(range(len(locations)))
        if locations[index].region_flags & RegionFlags.Forest
    ]

    logging.info(f"Found {len(check_pool)} checks for region")

    # Compile region data
    region_data: RegionData = RegionData("The Dark Forest", check_pool, [
        # "Dark Forest to Shared: Mainland & Dark Forest",
        # "Leave Dark Forest to Mainland",
        # "Leave Dark Forest to The Island"
    ])

    # Create region
    return create_region(world, player, region_data)

def create_island_region(world: MultiWorld, player: int, locations: List[LocationData]) -> Region:
    """Create the 'The Island' region"""

    logging.info("----- Creating 'The Island' Region -----")

    # Pop all mainland checks from the locations pool
    check_pool: List[LocationData] = [
        locations.pop(index)
        for index in reversed(range(len(locations)))
        if locations[index].region_flags & RegionFlags.Island
    ]

    logging.info(f"Found {len(check_pool)} checks for region")

    # Compile region data
    region_data: RegionData = RegionData("The Island", check_pool, [
        "Portal from The Island to Dark Forest",
        "Rowboat from The Island to Mainland",
        # "The Island to Shared: Mainland & The Island"
    ])

    # Create region
    return create_region(world, player, region_data)

# def create_mainland_forest_shared_region(world: MultiWorld, player: int, locations: List[LocationData]) -> Region:
#     """Create the 'Shared: Mainland & Forest' region"""

#     logging.info("----- Creating 'Shared: Mainland & Forest' Region -----")

#     # Pop all mainland checks from the locations pool
#     check_pool: List[LocationData] = [
#         locations.pop(index)
#         for index in reversed(range(len(locations)))
#         if locations[index].region_flags == RegionFlags.Mainland_and_Forest
#     ]

#     logging.info(f"Found {len(check_pool)} checks for region")

#     # Compile region data
#     region_data: RegionData = RegionData("Shared: Mainland & Dark Forest", check_pool, [ ])

#     # Create region
#     return create_region(world, player, region_data)

# def create_mainland_island_shared_region(world: MultiWorld, player: int, locations: List[LocationData]) -> Region:
#     """Create the 'Shared: Mainland & Island' region"""

#     logging.info("----- Creating 'Shared: Mainland & Island' Region -----")

#     # Pop all mainland checks from the locations pool
#     check_pool: List[LocationData] = [
#         locations.pop(index)
#         for index in reversed(range(len(locations)))
#         if locations[index].region_flags == RegionFlags.Mainland_and_Island
#     ]

#     logging.info(f"Found {len(check_pool)} checks for region")

#     # Compile region data
#     region_data: RegionData = RegionData("Shared: Mainland & The Island", check_pool, [ ])

#     # Create region
#     return create_region(world, player, region_data)