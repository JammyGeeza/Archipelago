from dataclasses import dataclass
from .Enums import ExpansionType, GoalFlags, MoonlengthType, RegionFlags
from Options import Choice, DeathLink, PerGameCommonOptions, Range, Toggle

class Boards(Choice):
    """
    Select which boards to include in the run - all quests from each selected board will be added as checks to the check pool.

    mainland_only               -> Include only Mainland
    mainland_and_dark_forest    -> Include both Mainland and The Dark Forest

    """
    # mainland_and_island         -> Include both Mainland and The Island
    # all                         -> Include Mainland, The Dark Forest and The Island
    # """
    display_name = "Included Boards"
    option_mainland_only = RegionFlags.Mainland
    option_mainland_and_dark_forest = RegionFlags.Mainland | RegionFlags.Forest
    # option_mainland_and_island = RegionFlags.Mainland | RegionFlags.Island
    # option_all = RegionFlags.All
    default = RegionFlags.Mainland | RegionFlags.Forest

class BoardExpansionMode(Choice):
    """
    Select how board expansion works in the run.

    ideas  -> Adds 'Idea: Shed' and 'Idea: Warehouse' to the item pool - build them yourself to expand the board as you like.
    items  -> Adds 7x 'Board Expansion: Shed' and 4x 'Board Expansion: Warehouse' items to the item pool - each spawns a Shed or Warehouse.

    """
    display_name = "Board Expansion Mode"
    option_ideas = ExpansionType.Ideas
    option_items = ExpansionType.Items
    default = ExpansionType.Items

class MoonLength(Choice):
    """
    Set the length of each moon for the run - this will disable and override the 'Moon Length' option in the 'Start New Run' menu.
    """
    display_name = "Moon Length"
    option_short = MoonlengthType.Short
    option_normal = MoonlengthType.Normal
    option_long = MoonlengthType.Long
    default = MoonlengthType.Normal


class Goal(Choice):
    """
    Select the goal for your run.

    kill_demon          -> Complete the 'Kill the Demon' quest (Mainland)
    kill_wicked_witch   -> Complete the 'Fight the Wicked Witch' quest (The Dark Forest)

    NOTE: 
    Selecting a goal for a board you have NOT selected in the 'boards' option will still work, but will not
    automatically include all quest checks for that board.

    EXAMPLE:
    Selecting 'mainland_only' in the 'boards' option and 'kill_wicked_witch' in the 'goal' option will allow you
    to complete the goal in The Dark Forest, but no other Dark Forest quests will be included as checks.
    """
    display_name = "Goal"
    option_kill_demon = GoalFlags.Demon
    option_kill_wicked_witch = GoalFlags.Witch
    # option_both = GoalFlags.All
    default = GoalFlags.Demon

class Mobsanity(Toggle):
    """
    Add checks for killing one of each enemy type to the check pool.
    Only includes checks for enemies that are reachable within the boards you have selected in the 'boards' option.
    """
    display_name = "Enable Mobsanity"
    default = 0

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

    Range from 0 to 100
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

    Range from 0 to 100
    """
    display_name = "Feed Villagers Trap Weighting"
    range_start = 0
    range_end = 100
    default = 50

class MobTrapWeight(Range):
    """
    The weighting of Mob Traps in the trap pool.
    The higher this number relative to the other trap weightings, the more often it is likely to appear.
    
    Mob Traps will spawn a random enemy to the current board - killing mob traps will not count towards Mobsanity checks.

    If <Trap Fill> is 0 then this setting will be ignored.

    Range from 0 to 100
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

    Range from 0 to 100
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

    Range from 1 to 25
    
    If <Trap Fill> is 0 or <Sell Cards Trap Weight> is 0 then this setting will be ignored.
    """
    display_name = "Sell Cards Trap Amount"
    range_start = 1
    range_end = 25
    default = 3

class StructureTrapWeight(Range):
    """
    The weighting of Structure Trap items in the trap pool.
    The higher this number relative to the other trap weightings, the more often it is likely to appear.

    Structure Traps will spawn a Strange Portal to the Mainland board or Pirate Boat to the Island board.
    You will not be able to use Strange Portals spawned from Structure Traps to travel to The Dark Forest.
    
    If <Trap Fill> is 0 then this setting will be ignored.
    """
    display_name = "Structure Trap Weighting"
    range_start = 0
    range_end = 100
    default = 50

@dataclass
class StacklandsOptions(PerGameCommonOptions):
    boards: Boards
    board_expansion_mode: BoardExpansionMode
    death_link: DeathLink
    moon_length: MoonLength
    goal: Goal
    pausing: Pausing
    mobsanity: Mobsanity
    trap_fill: TrapFill
    feed_villagers_trap_weight: FeedVillagersTrapWeight
    # flip_trap_weight: TrapWeightFlip
    mob_trap_weight: MobTrapWeight
    sell_cards_trap_weight: SellCardsTrapWeight
    sell_cards_trap_amount: SellCardsTrapAmount
    structure_trap_weight: StructureTrapWeight