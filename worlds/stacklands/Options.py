from dataclasses import dataclass
from .Enums import ExpansionType, GoalFlags, MoonlengthType, RegionFlags
from Options import Choice, DeathLink, PerGameCommonOptions, Range, Toggle

class Boards(Choice):
    """
    Select which boards to include in your run - will include all quests for each board as location checks.
    """
    display_name = "Boards"
    option_mainland_only = RegionFlags.Mainland
    option_mainland_and_forest = RegionFlags.Mainland | RegionFlags.Forest
    option_mainland_and_island = RegionFlags.Mainland | RegionFlags.Island
    option_all = RegionFlags.All
    default = option_all

class Goal(Choice):
    """
    Select the goal for your run.

    All Bosses -> Kill all bosses on each board selected in the <Boards> option.
    All Quests -> Complete all quests on each board selected in the <Boards> option.
    """
    display_name = "Goal"
    option_all_bosses = GoalFlags.Bosses
    option_all_quests = GoalFlags.Quests
    default = option_all_bosses

class Mobsanity(Toggle):
    """
    Add checks for killing one of each enemy type to the check pool.
    Includes checks for all enemies reachable in all boards selected in <Boards>.
    """
    display_name = "Mobsanity"
    default = 0

class Packsanity(Toggle):
    """
    Add checks for buying each booster pack to the check pool.
    Includes checks for packs available in all boards selected in <Boards>.
    """
    display_name = "Packsanity"
    default = 0

class Spendsanity(Choice):
    """
    Adds a new 'Spendsanity' booster box to the pack line - 'buying' boosters from this box are checks.

    off         -> Disabled
    fixed       -> The cost starts at <Spendsanity Cost> and remains at this cost after each purchase.
    incremental -> The cost starts at <Spendsanity Cost> and increases by the same amount after each purchase.
    """
    display_name = "Spendsanity"
    option_off = 0
    option_fixed = 1
    option_incremental = 2
    default = option_off

class SpendsanityCost(Range):
    """
    The cost for a 'Spendsanity' purchase - the cost throughout will be affected by your choice in <Spendsanity>.
    """
    display_name = "Spendsanity Cost"
    range_start = 1
    range_end = 25
    default = 10

class SpendsanityCount(Range):
    """
    How many Spendsanity checks to add to the check pool.
    """
    display_name = "Spendsanity Count"
    range_start = 1
    range_end = 25
    default = 10

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
    default = 8

class BoardExpansionCount(Range):
    """
    How many 'Board Expansion' items are added to the item pool.
    
    If <Board Expansion Mode> option is 'ideas' then this setting will be ignored.
    """
    display_name = "Board Expansion Count"
    range_start = 3
    range_end = 10
    default = 4

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
    boards: Boards
    goal: Goal
    mobsanity: Mobsanity
    packsanity: Packsanity
    spendsanity: Spendsanity
    spendsanity_cost: SpendsanityCost
    spendsanity_count: SpendsanityCount
    board_expansion_mode: BoardExpansionMode
    board_expansion_amount: BoardExpansionAmount
    board_expansion_count: BoardExpansionCount
    moon_length: MoonLength
    pausing: Pausing
    trap_fill: TrapFill
    feed_villagers_trap_weight: FeedVillagersTrapWeight
    mob_trap_weight: MobTrapWeight
    sell_cards_trap_weight: SellCardsTrapWeight
    sell_cards_trap_amount: SellCardsTrapAmount
    strange_portal_trap_weight: StrangePortalTrapWeight