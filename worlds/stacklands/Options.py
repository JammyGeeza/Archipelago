from dataclasses import dataclass
from .Enums import ExpansionType, GoalFlags, MoonlengthType, RegionFlags
from Options import Choice, DeathLink, PerGameCommonOptions, Range, Toggle

class Goal(Choice):
    """
    Select which bosses to kill for the goal of your run.

    kill_demon          -> Complete the 'Kill the Demon' quest (Mainland)
    kill_wicked_witch   -> Complete the 'Fight the Wicked Witch' quest (The Dark Forest)
    all_bosses          -> Complete both 'Kill the Demon' (Mainland) and 'Fight the Wicked Witch' (The Dark Forest)

    NOTE:
    Selecting a goal for a board you have NOT selected in the <Board Checks> option will still work, but will not
    automatically include all quest checks for that board.

    EXAMPLE:
    If <Boards> option is set to 'mainland_only' and your <Goal> option is set to 'kill_wicked_witch', it will allow you
    to complete the goal in The Dark Forest but no other Dark Forest quests will be included as checks.
    """
    display_name = "Goal"
    option_kill_demon = GoalFlags.Demon
    option_kill_wicked_witch = GoalFlags.Witch
    option_all_bosses = GoalFlags.All
    default = option_all_bosses

class QuestChecks(Choice):
    """
    Select which quests to include as checks.

    mainland_only               -> Include all Mainland quests as checks.
    mainland_and_dark_forest    -> Include all Mainland and The Dark Forest quests as checks.
    """
    display_name = "Quest Checks"
    option_mainland_only = RegionFlags.Mainland
    option_mainland_and_dark_forest = RegionFlags.Mainland_and_Forest
    default = option_mainland_and_dark_forest

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
    quest_checks: QuestChecks
    board_expansion_mode: BoardExpansionMode
    board_expansion_amount: BoardExpansionAmount
    board_expansion_count: BoardExpansionCount
    death_link: DeathLink
    moon_length: MoonLength
    pausing: Pausing
    mobsanity: Mobsanity
    trap_fill: TrapFill
    feed_villagers_trap_weight: FeedVillagersTrapWeight
    # flip_trap_weight: TrapWeightFlip
    mob_trap_weight: MobTrapWeight
    sell_cards_trap_weight: SellCardsTrapWeight
    sell_cards_trap_amount: SellCardsTrapAmount
    strange_portal_trap_weight: StrangePortalTrapWeight