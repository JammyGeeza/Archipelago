import logging
from .Enums import CheckType, ExpansionType, GoalFlags, MoonPhase, OptionFlags, ProgressionPhase, RegionFlags, SpendsanityType
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

    logging.info(f"Creating region: '{region_data.name}'...")

    # Create region object
    region: Region = Region(region_data.name, player, world)

    # Get all locations that are not goals
    for location_data in [ loc for loc in region_data.locations if loc.check_type is CheckType.Check ]:

        # Create and add location to region
        location: StacklandsLocation = StacklandsLocation(player, location_data, location_lookup[location_data.name], region)
        region.locations.append(location)

    # Get all locations that are goals
    for goal_data in [ loc for loc in region_data.locations if loc.check_type is CheckType.Goal ]:

        # Create and add goal to region
        goal: StacklandsLocation = StacklandsLocation(player, goal_data, None, region)
        goal.place_locked_item(Item("Victory", ItemClassification.progression, None, player))
        region.locations.append(goal)

    # Add exits to region
    for exit in region_data.exits:
        region.exits.append(Entrance(player, exit, region))

    # Add region to world
    world.regions.append(region)

    # logging.info(f"Added {len(region.locations)} checks to the check pool!")

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
    setup_mainland(world, player, location_pool)
    setup_dark_forest(world, player, location_pool)
    setup_island(world, player, location_pool)

    # Menu exit(s)
    world.get_entrance("Start", player).connect(world.get_region("Mainland", player))

    # Mainland exit(s)
    world.get_entrance("Portal", player).connect(world.get_region("The Dark Forest", player))
    world.get_entrance("Rowboat", player).connect(world.get_region("The Island", player))

def create_menu_region(world: MultiWorld, player: int) -> Region:
    """Create the default 'Menu' regions"""
    
    logging.info("----- Creating 'Menu' Region -----")

    # Compile region data
    menu_region: RegionData = RegionData("Menu", [], ["Start"])

    # Create region
    return create_region(world, player, menu_region)

def setup_mainland(world: MultiWorld, player: int, locations: List[LocationData]) -> Region:
    """Create the 'Mainland' regions"""

    name: str = "Mainland"

    logging.info(f"----- Setting up '{name}' -----")

    # Pop all mainland checks from the locations pool
    check_pool: List[LocationData] = [
        locations.pop(index)
        for index in reversed(range(len(locations)))
        if locations[index].region_flags & RegionFlags.Mainland
    ]

    total_checks: int = len(check_pool)

    logging.info(f"Found {total_checks} checks for {name}")

    # Mainland Region (for all 'General' checks)
    mainland_region: Region = create_region(world, player, RegionData(f"{name}", [
        check_pool.pop(index) 
        for index in reversed(range(len(check_pool))) 
        if check_pool[index].prog_phase == ProgressionPhase.General
    ],
    [ 
        f"Forward to {name}: Progression Phase One",
        "Portal",
        "Rowboat"
    ]))

    # Mainland: Progression Phase One (Food & Villagers)
    mainland_phase_one_region: Region = create_region(world, player, RegionData(f"{name}: Progression Phase One", [
        check_pool.pop(index)
        for index in reversed(range(len(check_pool)))
        if check_pool[index].prog_phase == ProgressionPhase.PhaseOne
    ],
    [
        f"Forward to {name}: Progression Phase Two",
    ]))

    # Mainland: Progression Phase Two (Basic Resources & Equipment)
    mainland_phase_two_region: Region = create_region(world, player, RegionData(f"{name}: Progression Phase Two", [
        check_pool.pop(index)
        for index in reversed(range(len(check_pool)))
        if check_pool[index].prog_phase == ProgressionPhase.PhaseTwo
    ],
    [
        f"Forward to {name}: Progression Phase Three",
    ]))

    # Mainland: Progression Phase Three (Advanced Resources & Equipment)
    mainland_phase_three_region: Region = create_region(world, player, RegionData(f"{name}: Progression Phase Three", [
        check_pool.pop(index)
        for index in reversed(range(len(check_pool)))
        if check_pool[index].prog_phase == ProgressionPhase.PhaseThree
    ],
    [
        f"Forward to {name}: Progression Phase Four",
    ]))

    # Mainland: Progression Phase Four (Boss Battle)
    mainland_phase_four_region: Region = create_region(world, player, RegionData(f"{name}: Progression Phase Four", [
        check_pool.pop(index)
        for index in reversed(range(len(check_pool)))
        if check_pool[index].prog_phase == ProgressionPhase.PhaseFour
    ],[]))


    logging.info(f"Added {total_checks - len(check_pool)}/{total_checks} checks to the check pool")

    # Connect entrances and exits
    world.get_entrance(f"Forward to {name}: Progression Phase One", player).connect(mainland_phase_one_region)
    world.get_entrance(f"Forward to {name}: Progression Phase Two", player).connect(mainland_phase_two_region)
    world.get_entrance(f"Forward to {name}: Progression Phase Three", player).connect(mainland_phase_three_region)
    world.get_entrance(f"Forward to {name}: Progression Phase Four", player).connect(mainland_phase_four_region)

    # Add event(s)
    mainland_region.add_event(f"Defeat {name} Boss", "Demon")


def setup_dark_forest(world: MultiWorld, player: int, locations: List[LocationData]) -> Region:
    """Create the 'The Dark Forest' regions"""

    name: str = "The Dark Forest"

    logging.info(f"----- Setting up '{name}' -----")

    # Pop all mainland checks from the locations pool
    check_pool: List[LocationData] = [
        locations.pop(index)
        for index in reversed(range(len(locations)))
        if locations[index].region_flags & RegionFlags.Forest
    ]

    total_checks: int = len(check_pool)

    logging.info(f"Found {total_checks} checks for {name}")

    # Dark Forest Region (for all 'General' checks)
    dark_forest_region: Region = create_region(world, player, RegionData(f"{name}", [
        check_pool.pop(index) 
        for index in reversed(range(len(check_pool))) 
        if check_pool[index].prog_phase == ProgressionPhase.General
    ],
    [ 
        f"Forward to {name}: Progression Phase One",
    ]))

    # Dark Forest: Progression Phase One (Basic Weapons)
    dark_forest_phase_one_region: Region = create_region(world, player, RegionData(f"{name}: Progression Phase One", [
        check_pool.pop(index)
        for index in reversed(range(len(check_pool)))
        if check_pool[index].prog_phase == ProgressionPhase.PhaseOne
    ],
    [
        f"Forward to {name}: Progression Phase Two",
    ]))

    # Mainland: Progression Phase Two (Advanced Weapons)
    dark_forest_phase_two_region: Region = create_region(world, player, RegionData(f"{name}: Progression Phase Two", [
        check_pool.pop(index)
        for index in reversed(range(len(check_pool)))
        if check_pool[index].prog_phase == ProgressionPhase.PhaseTwo
    ],[]))

    logging.info(f"Added {total_checks - len(check_pool)}/{total_checks} checks to the check pool")

    # Connect entrances and exits
    world.get_entrance(f"Forward to {name}: Progression Phase One", player).connect(dark_forest_phase_one_region)
    world.get_entrance(f"Forward to {name}: Progression Phase Two", player).connect(dark_forest_phase_two_region)

    # Add event(s)
    dark_forest_region.add_event(f"Defeat {name} Boss", "Wicked Witch")


def setup_island(world: MultiWorld, player: int, locations: List[LocationData]) -> Region:
    """Create the 'The Island' regions"""

    name: str = "The Island"

    logging.info(f"----- Setting up '{name}' -----")

    # Pop all mainland checks from the locations pool
    check_pool: List[LocationData] = [
        locations.pop(index)
        for index in reversed(range(len(locations)))
        if locations[index].region_flags & RegionFlags.Island
    ]

    total_checks: int = len(check_pool)

    logging.info(f"Found {total_checks} checks for {name}")

    # The Island Region (for all 'General' checks)
    island_region: Region = create_region(world, player, RegionData(f"{name}", [
        check_pool.pop(index) 
        for index in reversed(range(len(check_pool))) 
        if check_pool[index].prog_phase == ProgressionPhase.General
    ],
    [ 
        f"Forward to {name}: Progression Phase One"
    ]))

    # The Island: Progression Phase One (Basic Weapons)
    island_phase_one_region: Region = create_region(world, player, RegionData(f"{name}: Progression Phase One", [
        check_pool.pop(index)
        for index in reversed(range(len(check_pool)))
        if check_pool[index].prog_phase == ProgressionPhase.PhaseOne
    ],
    [
        f"Forward to {name}: Progression Phase Two"
    ]))

    # The Island: Progression Phase Two (Advanced Weapons)
    island_phase_two_region: Region = create_region(world, player, RegionData(f"{name}: Progression Phase Two", [
        check_pool.pop(index)
        for index in reversed(range(len(check_pool)))
        if check_pool[index].prog_phase == ProgressionPhase.PhaseTwo
    ],[
        f"Forward to {name}: Progression Phase Three"
    ]))

    # The Island: Progression Phase Two (Advanced Weapons)
    island_phase_three_region: Region = create_region(world, player, RegionData(f"{name}: Progression Phase Three", [
        check_pool.pop(index)
        for index in reversed(range(len(check_pool)))
        if check_pool[index].prog_phase == ProgressionPhase.PhaseThree
    ],[]))

    logging.info(f"Added {total_checks - len(check_pool)}/{total_checks} checks to the check pool")

    # Connect entrances and exits
    world.get_entrance(f"Forward to {name}: Progression Phase One", player).connect(island_phase_one_region)
    world.get_entrance(f"Forward to {name}: Progression Phase Two", player).connect(island_phase_two_region)
    world.get_entrance(f"Forward to {name}: Progression Phase Three", player).connect(island_phase_three_region)

    # Add event(s)
    island_region.add_event(f"Defeat {name} Boss", "Demon Lord")