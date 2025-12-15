from dataclasses import dataclass
from BaseClasses import Options
from Options import Choice, OptionList, ItemDict, PerGameCommonOptions
from .Enums import GoalType

class Goal(Choice):
    """
    Select the goal for your session.

    Catch All Fish -> Catch at least one of every fish from each <Spot>.

    More goals coming soon...
    """
    display_name = "Goal"
    option_catch_all_fish = GoalType.CatchAllFish.value
    option_catch_all_legendaries = GoalType.CatchAllLegendaries.value
    default = option_catch_all_legendaries

class Spots(OptionList):
    """
    The spots to include in your session.
    Currently only supports The Fork and Beaver Dam - more spots will be added as development continues...
    """

    display_name = "Spots"
    valid_keys_casefold = False
    valid_keys = [
        "All",
        "The Fork",
        "Beaver Dam"
    ]
    default = [
        "The Fork",
        "Beaver Dam"
    ]

class FillerItemWeights(ItemDict):
    """
    The weightings for filler item frequency in the item pool.
    The higher the number for each item (relative to the other items), the more times it is likely to appear in the pool.

    EXAMPLE: { "Gold": 5, "Nothing": 15 }
    The 'Nothing' item is likely to appear 3x as often as the 'Gold' item.
    """

    display_name = "Filler Item Weights"
    valid_keys_casefold = False
    valid_keys = [
         "Gold",
         "Nothing"
    ]
    default = {
        "Gold": 50,
        "Nothing": 50
    }

@dataclass
class CastNChillOptions(PerGameCommonOptions):
    """"""
    # Goal settings
    goal: Goal
    spots: Spots

    # Item Weights
    filler_weights: FillerItemWeights