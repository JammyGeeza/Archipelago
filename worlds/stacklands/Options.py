from dataclasses import dataclass
from .Enums import ExpansionType, GoalFlags, MoonlengthType, RegionFlags
from Options import Choice, DeathLink, PerGameCommonOptions, Range, Toggle

class Goal(Choice):
    """
    Select which boards to complete (kill the boss) for the goal of your run.

    Mainland Only       -> Kill the Demon
    Mainland and Forest -> Kill the Demon and the Wicked Witch
    Mainland and Island -> Kill the Demon and the Demon Lord
    All                 -> Kill the Demon, Wicked Witch and Demon Lord

    For each board selected, all quests for that board will be added as Location Checks.
    """
    display_name = "Goal"
    option_mainland_only = RegionFlags.Mainland
    option_mainland_and_forest = RegionFlags.Mainland | RegionFlags.Forest
    option_mainland_and_island = RegionFlags.Mainland | RegionFlags.Island
    option_all = RegionFlags.All
    default = option_all

class Equipmentsanity(Toggle):
    """
    Add checks for crafting one of each Equipment card. (E.g. Club, Sword, Blunderbuss etc.)
    Will only add checks for Equipment that are reachable on the boards selected in the <Goal> option.
    
    This will add 16 checks to Mainland and 6 checks to The Island (if selected).
    """
    display_name = "Equipmentsanity"
    default = 0

class Foodsanity(Toggle):
    """
    Add checks for cooking one of each Food card. (E.g. Stew, Fruit Salad, Tamago Sushi etc.)
    Will only add checks for Foods that are reachable on the boards selected in the <Goal> option.

    This will add 3 checks to Mainland and 3 checks to The Island (if selected).
    """
    display_name = "Foodsanity"
    default = 0

class Locationsanity(Toggle):
    """
    Add checks for exploring one of each Location card. (E.g. Mountain, Old Village, Jungle etc.)
    Will only add checks for Locations that are reachable on the boards selected in the <Goal> option.

    This will add 4 checks to Mainland and 2 checks to The Island (if selected).
    """
    display_name = "Locationsanity"
    default = 0

class Mobsanity(Toggle):
    """
    Add checks for killing one of each Mob card. (E.g. Elf, Giant Snail, Tiger etc.)
    Will only add checks for Mobs that are reachable on the boards selected in the <Goal> option.

    This will add 18 checks to Mainland, 3 checks to The Dark Forest and 9 checks to The Island (if selected).
    """
    display_name = "Mobsanity"
    default = 0

class MobsanityBalancing(Toggle):
    """
    Greatly increases chance for all Packs / Strange Portals / Dark Forest Waves to spawn reachable Mobs that you have not yet killed.
    
    It is recommended to set this to 'true' to prevent relying on RNG to reach all Mobsanity checks.
    If set to 'false' you will be at the mercy of RNG to spawn all Mob types to reach all Mobsanity checks.

    This setting is ignored if the <Mobsanity> option is 'false'.
    """
    display_name = "Mobsanity Balancing"
    default = 1

class Structuresanity(Toggle):
    """
    Add checks for building one of each reachable Structure card. (E.g Garden, Market, Distillery etc.)
    Will only add checks for Structures that are reachable on the boards selected in the <Goal> option.

    This will add 10 checks to Mainland and 6 checks to The Island (if selected).
    """
    display_name = "Structuresanity"
    default = 0

# class Packsanity(Toggle):
#     """
#     Add checks for buying each booster pack to the check pool.
#     Includes checks for packs available in all boards selected in <Boards>.
#     """
#     display_name = "Packsanity"
#     default = 0

# class Spendsanity(Choice):
#     """
#     Adds a new 'Spendsanity' booster box to the pack line - 'buying' boosters from this box are checks.

#     off         -> Disabled
#     fixed       -> The cost starts at <Spendsanity Cost> and remains at this cost after each purchase.
#     incremental -> The cost starts at <Spendsanity Cost> and increases by the same amount after each purchase.
#     """
#     display_name = "Spendsanity"
#     option_off = 0
#     option_fixed = 1
#     option_incremental = 2
#     default = option_off

# class SpendsanityCost(Range):
#     """
#     The cost for a 'Spendsanity' purchase - the cost throughout will be affected by your choice in <Spendsanity>.
#     """
#     display_name = "Spendsanity Cost"
#     range_start = 1
#     range_end = 25
#     default = 10

# class SpendsanityCount(Range):
#     """
#     How many Spendsanity checks to add to the check pool.
#     """
#     display_name = "Spendsanity Count"
#     range_start = 1
#     range_end = 25
#     default = 10

class BoardExpansionMode(Choice):
    """
    Select how board expansion works in the run.

    ideas  -> Adds 'Idea: Shed' and 'Idea: Warehouse' to the item pool - build them yourself to expand the board as you like.
    items  -> Adds 'Board Expansion' items to the item pool and removes 'Idea: Warehouse'. Building 'Shed' will no longer expand your board, but can be used to complete the 'Build a Shed' check.
    """
    display_name = "Board Expansion Mode"
    option_ideas = ExpansionType.Ideas
    option_items = ExpansionType.Items
    default = ExpansionType.Items

class BoardExpansionAmount(Range):
    """
    How many additional cards a board expansion item will give.
    NOTE: Board size is increased as if building a Shed or Warehouse in vanilla and max board size remains capped at the largest vanilla size (without Lighthouses).
    
    If <Board Expansion Mode> option is 'ideas' then this setting will be ignored.
    """
    display_name = "Board Expansion Amount"
    range_start = 4
    range_end = 14
    default = 7

class BoardExpansionCount(Range):
    """
    How many 'Board Expansion' items are added to the item pool.
    
    If <Board Expansion Mode> option is 'ideas' then this setting will be ignored.
    """
    display_name = "Board Expansion Count"
    range_start = 4
    range_end = 10
    default = 6

class MoonLength(Choice):
    """
    Set the length of each moon for the run - this will disable and override the 'Moon Length' option in the 'Start New Run' menu.
    """
    display_name = "Moon Length"
    option_short = MoonlengthType.Short
    option_normal = MoonlengthType.Normal
    option_long = MoonlengthType.Long
    default = MoonlengthType.Normal

class Pausing(Toggle):
    """
    The player keeps the ability to be able to pause time.
    If disabled, time will only be paused by cutscenes and end-of-moon routines.
    """
    display_name = "Enable Pausing"
    default = 1

class TrapFill(Range):
    """
    The percentage of the filler item pool that should be populated with trap items.
    
    0   -> No trap items will be included in the filler item pool
    25  -> Approximately 25% of the filler item pool will be trap items
    50  -> Approximately 50% of the filler item pool will be trap items
    etc.
    """
    display_name = "Trap Fill Percentage"
    range_start = 0
    range_end = 100
    default = 25

class FeedVillagersTrapWeight(Range):
    """
    The weighting of Feed Villagers Trap in the trap pool.
    The higher this number relative to the other trap weightings, the more often it is likely to appear.

    Feed Villager Trap will force all villagers on the current board to be fed - villagers not fed will die.

    If <Trap Fill> is 0 then this setting will be ignored.
    """
    display_name = "Feed Villagers Trap Weighting"
    range_start = 0
    range_end = 100
    default = 50

class MobTrapWeight(Range):
    """
    The weighting of Mob Traps in the trap pool.
    The higher this number relative to the other trap weightings, the more often it is likely to appear.
    
    Mob Traps will spawn a random, basic enemy to the current board - killing mobs from Mob Traps will not count towards Mobsanity checks.

    If <Trap Fill> is 0 then this setting will be ignored.
    """
    display_name = "Mob Trap Weighting"
    range_start = 0
    range_end = 100
    default = 50

class SellCardsTrapWeight(Range):
    """
    The weighting of Sell Cards Trap in the trap pool
    The higher this number relative to the other trap weightings, the more often it is likely to appear.

    Sell Cards Trap forces you to immediately sell <Sell Cards Trap Amount> of cards from the current board.

    If <Trap Fill> is 0 then this setting will be ignored.
    """
    display_name = "Sell Cards Trap Weighting"
    range_start = 0
    range_end = 100
    default = 50

class SellCardsTrapAmount(Range):
    """
    How many cards a Sell Cards Trap will force you to sell.

    You will be forced to sell this amount of all sellable cards when you receive this trap. If you have fewer than
    this amount, you will instead be forced to sell all remaining sellable cards.

    If <Trap Fill> is 0 or <Sell Cards Trap Weight> is 0 then this setting will be ignored.
    """
    display_name = "Sell Cards Trap Amount"
    range_start = 1
    range_end = 10
    default = 3

class StrangePortalTrapWeight(Range):
    """
    The weighting of Strange Portal Trap items in the trap pool.
    The higher this number relative to the other trap weightings, the more often it is likely to appear.

    Strange Portal Traps will spawn a Strange Portal to the current board.
    Portals from these traps cannot be used to travel to The Dark Forest and killing enemies spawned from these Portals will not count towards Mobsanity checks.
    
    If <Trap Fill> is 0 then this setting will be ignored.
    """
    display_name = "Strange Portal Trap Weighting"
    range_start = 0
    range_end = 100
    default = 50

@dataclass
class StacklandsOptions(PerGameCommonOptions):
    goal: Goal

    # Sanities
    equipmentsanity: Equipmentsanity
    foodsanity: Foodsanity
    locationsanity: Locationsanity
    mobsanity: Mobsanity
    mobsanity_balancing: MobsanityBalancing
    structuresanity: Structuresanity
    # spendsanity: Spendsanity
    # spendsanity_cost: SpendsanityCost
    # spendsanity_count: SpendsanityCount

    # Run settings
    board_expansion_mode: BoardExpansionMode
    board_expansion_amount: BoardExpansionAmount
    board_expansion_count: BoardExpansionCount
    moon_length: MoonLength
    pausing: Pausing

    # Traps
    trap_fill: TrapFill
    feed_villagers_trap_weight: FeedVillagersTrapWeight
    mob_trap_weight: MobTrapWeight
    sell_cards_trap_weight: SellCardsTrapWeight
    sell_cards_trap_amount: SellCardsTrapAmount
    strange_portal_trap_weight: StrangePortalTrapWeight