from dataclasses import dataclass
from .Enums import GoalFlags, RegionFlags
from Options import Choice, DeathLink, PerGameCommonOptions, Toggle

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

class Goal(Choice):
    """
    Select the goal for your run.

    kill_demon          -> Complete the 'Kill the Demon' quest (Mainland)
    kill_wicked_witch   -> Complete the 'Fight the Wicked Witch' quest (The Dark Forest)
    both                -> Complete both the 'Kill the Demon' and 'Fight the Wicked Witch' quests
    
    NOTE: It is possible to select a goal for a board you have not selected in the 'boards' option - this will still work, but there will be no other location checks for that board in the check pool.
          For example, selecting 'mainland_only' in 'boards' and selecting a goal of 'kill_wicked_witch' will work, but The Dark Forest will not contain any checks.
    """
    display_name = "Goal"
    option_kill_demon = GoalFlags.Demon
    option_kill_wicked_witch = GoalFlags.Witch
    # option_both = GoalFlags.All
    default = GoalFlags.Demon

class Mobsanity(Toggle):
    """
    Add checks for killing one of each enemy type to the check pool.
    NOTE: Will only include checks for enemies that are reachable within the boards you have selected in the 'boards' option.
    """
    display_name = "Enable Mobsanity"
    default = 0

class Pausing(Toggle):
    """
    The player keeps the ability to be able to pause time.
    NOTE: If disabled, time can only be paused by cutscenes and end-of-moon routines.
    """
    display_name = "Enable Pausing"
    default = 1

class Traps(Toggle):
    """
    Add trap items to the item pool.
    """
    display_name = "Trap Items"
    default = 0

@dataclass
class StacklandsOptions(PerGameCommonOptions):
    boards: Boards
    death_link: DeathLink
    goal: Goal
    pausing: Pausing
    mobsanity: Mobsanity
    traps: Traps