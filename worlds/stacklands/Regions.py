import logging
from .Enums import CheckType, ExpansionType, GoalFlags, OptionFlags, RegionFlags
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

    # Create regions
    menu_region: Region = create_menu_region(world, player, options)
    mainland_region: Region = create_mainland_region(world, player, options)
    forest_region: Region = create_forest_region(world, player, options)

    # Connect region entrances and exits
    world.get_entrance("Start", player).connect(mainland_region)
    world.get_entrance("Strange Portal", player).connect(forest_region)
    # world.get_entrance("Rowboat", player).connect(world.get_region("The Island", player))

def create_menu_region(world: MultiWorld, player: int, options: StacklandsOptions) -> Region:
    """Create the default 'Menu' region"""
    
    logging.info("----- Creating 'Menu' Region -----")

    # Compile region data
    menu_region: RegionData = RegionData("Menu", [], ["Start"])

    # Create region
    return create_region(world, player, menu_region)

def create_mainland_region(world: MultiWorld, player: int, options: StacklandsOptions) -> Region:
    """Create the 'Mainland' region"""

    logging.info("----- Creating 'Mainland' Region -----")

    # Prepare check pool
    check_pool: List[LocationData] = []

    # Get all checks for Mainland board
    mainland_checks: List[LocationData] = [ loc for loc in location_table if loc.region_flags is RegionFlags.Mainland ]

    # Check if mainland board is selected in YAML
    board_selected: bool = bool(options.quest_checks.value & RegionFlags.Mainland)
    goal_selected: bool = bool(options.goal.value & GoalFlags.Demon)

    # If mainland board has been selected
    if board_selected:

        # Add all quest checks (not affected by options) for Mainland to check pool
        check_pool += [ loc for loc in mainland_checks if loc.check_type is CheckType.Check and loc.option_flags is OptionFlags.NONE ]

        # If pausing is enabled, add all Pausing quest checks for Mainland to check pool 
        if options.pausing.value:
            check_pool += [ loc for loc in mainland_checks if loc.check_type is CheckType.Check and loc.option_flags & OptionFlags.Pausing ]

        # If mobsanity is enabled, add all mobsanity checks for Mainland to the check pool
        if options.mobsanity.value:
            check_pool += [ loc for loc in mainland_checks if loc.check_type is CheckType.Check and loc.option_flags & OptionFlags.Mobsanity ]

        # If packsanity is enabled, add all packsanity checks for Mainland to the check pool
        if options.packsanity.value:
            check_pool += [ loc for loc in mainland_checks if loc.check_type is CheckType.Check and loc.option_flags & OptionFlags.Packsanity ]

    # Get goal check, if exists
    if (goal_check:= next((loc for loc in mainland_checks if loc.check_type & CheckType.Goal), None)) is not None:

        # If the goal has been selected, add the goal to the check pool
        if goal_selected:
            check_pool += [ goal_check ]

        # If goal is not selected but board is selected, replace the goal check with a normal quest check
        # NOTE: Can't just update the location's check flag because it messes it up for all Fuzz.py generations
        elif not goal_selected and board_selected:
            check_pool += [ LocationData(goal_check.name, goal_check.region_flags, CheckType.Check, goal_check.option_flags, goal_check.progress_type) ]

    # Compile region data
    region_data: RegionData = RegionData("Mainland", check_pool, [ "Strange Portal" ])

    # Create region
    return create_region(world, player, region_data)

def create_forest_region(world: MultiWorld, player: int, options: StacklandsOptions) -> Region:
    """Create the 'Dark Forest' region"""

    logging.info("----- Creating 'The Dark Forest' Region -----")

    # Prepare check pool
    check_pool: List[LocationData] = []

    # Get all checks for The Dark Forest board
    forest_checks: List[LocationData] = [ loc for loc in location_table if loc.region_flags is RegionFlags.Forest ]

    # Check if Dark Forest board is selected in YAML
    board_selected: bool = bool(options.quest_checks.value & RegionFlags.Forest)
    goal_selected: bool = bool(options.goal.value & GoalFlags.Witch)

    # If dark forest board has been selected
    if board_selected:
        
        # Add all quest checks for Mainland to check pool
        check_pool += [ loc for loc in forest_checks if loc.check_type is CheckType.Check and loc.option_flags is OptionFlags.NONE ]

        # If mobsanity is enabled, add all mobsanity checks for Mainland to the check pool
        if options.mobsanity.value:
            check_pool += [ loc for loc in forest_checks if loc.check_type is CheckType.Check and loc.option_flags & OptionFlags.Mobsanity ]

    # Get goal check, if exists
    if (goal_check:= next((loc for loc in forest_checks if loc.check_type is CheckType.Goal), None)) is not None:

        # If the goal has been selected, add the goal to the check pool
        if goal_selected:
            check_pool += [ goal_check ]

        # If goal is not selected but board is selected, replace the goal check with a normal quest check
        # NOTE: Can't just update the location's check flag because it messes it up for all Fuzz.py generations
        elif not goal_selected and board_selected:
            check_pool += [ LocationData(goal_check.name, goal_check.region_flags, CheckType.Check, goal_check.option_flags, goal_check.progress_type) ]

    # Compile region data
    region_data: RegionData = RegionData("The Dark Forest", check_pool, [ ])

    # Create region
    return create_region(world, player, region_data)