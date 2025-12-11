from dataclasses import dataclass
from BaseClasses import Options
from Options import Choice, ItemSet, PerGameCommonOptions
from .Enums import GoalType

class Goal(Choice):
    """
    Select the goal for your session.

    Catch All Fish -> Catch at least one of every fish from each <Spot>.

    More goals coming soon...
    """
    display_name = "Goal"
    option_catch_all_fish = GoalType.CatchAllFish.value
    default = option_catch_all_fish

class Spots(ItemSet):
    """
    The spots to include in your session.
    Currently only supports The Fork - more spots will be added as development continues...
    """

    display_name = "Spots"
    default = [ "The Fork" ]

@dataclass
class CastNChillOptions(PerGameCommonOptions):
    """"""
    # Goal settings
    goal: Goal
    spots: Spots