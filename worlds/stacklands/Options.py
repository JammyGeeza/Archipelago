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
    items  -> Ads 6x 'Board Size Increase' and 6x 'Card Limit Increase' to the item pool - each gives the size / card limit increase of one Warehouse.

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

class TrapWeighting(Range):
    """
    The percentage of filler items that should be traps - ranges from 1 to 100

    EXAMPLE:
    If 10 filler items are required to fill all remaining locations then... 
    10  -> 10% (1 / 10) of filler items will be traps.
    30  -> 30% (3 / 10) of filler items will be traps.
    50  -> 50% (5 / 10) of filler items will be traps.
    100 -> 100% (10 / 10) of filler items will be traps.

    NOTE:
    If the 'traps' option is 'false', this setting is not required and will be ignored.
    """
    display_name = "Trap Weighting"
    range_start = 1
    range_end = 100
    default = 25

@dataclass
class StacklandsOptions(PerGameCommonOptions):
    boards: Boards
    board_expansion_mode: BoardExpansionMode
    death_link: DeathLink
    goal: Goal
    pausing: Pausing
    mobsanity: Mobsanity
    traps: Traps
    trap_weighting: TrapWeighting