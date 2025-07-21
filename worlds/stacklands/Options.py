from dataclasses import dataclass
from .Enums import ExpansionType, GoalFlags, RegionFlags
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

class Traps(Toggle):
    """
    Include trap items as filler items in the item pool.

    NOTE:
    If 'false', the 'trap_weighting' option is not required and will be ignored.
    """
    display_name = "Trap Items"
    default = 0

class TrapFill(Range):
    """
    The percentage of filler items to be traps.

    NOTE:
    Only used if the 'traps' option is 'true', otherwise ignored.
    """
    display_name = "Trap Fill Percentage"
    range_start = 1
    range_end = 100
    default = 25

class TrapWeightFeedVillagers(Range):
    """
    The weighting of Feed Villagers Trap in the trap pool.
    Feed Villager Trap will force all villagers on the current board to be fed - villagers not fed will die.
    """
    display_name = "Feed Villagers Trap Weighting"
    range_start = 0
    range_end = 100
    default = 50

# class TrapWeightFlip(Range):
#     """
#     The weighting of Flip Traps in the trap pool.
#     Flip Traps will flip a random card to be face-down.
#     """
#     display_name = "Flip Trap Weighting"
#     range_start = 0
#     range_end = 100
#     default = 25

class TrapWeightMob(Range):
    """
    The weighting of Mob Traps in the trap pool.
    Mob Traps will spawn a random enemy to the current board.

    NOTE:
    Killing mob traps does not count towards Mobsanity checks.
    """
    display_name = "Mob Trap Weighting"
    range_start = 0
    range_end = 100
    default = 50

class TrapWeightSellCards(Range):
    """
    The weighting of Sell Cards Trap in the trap pool.
    Sell Cards Trap forces you to sell up to 5 cards on the current board.
    """
    display_name = "Sell Cards Trap Weighting"
    range_start = 0
    range_end = 100
    default = 50

class TrapWeightStructure(Range):
    """
    The weighting of Structure Trap items in the trap pool.
    Structure Traps will spawn a Strange Portal to the Mainland board or Pirate Boat to the Island board.

    NOTE:
    You will not be able to use Strange Portals spawned from Structure Traps to travel to The Dark Forest.
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
    goal: Goal
    pausing: Pausing
    mobsanity: Mobsanity
    traps: Traps
    trap_fill: TrapFill
    feed_villagers_trap_weight: TrapWeightFeedVillagers
    # flip_trap_weight: TrapWeightFlip
    mob_trap_weight: TrapWeightMob
    sell_cards_trap_weight: TrapWeightSellCards
    structure_trap_weight: TrapWeightStructure