from dataclasses import dataclass
from Options import Choice, DeathLink, PerGameCommonOptions, Toggle

class DarkForest(Toggle):
    """
    Add checks for The Dark Forest to the check pool.
    """
    display_name = "The Dark Forest"
    default = 1

class Goal(Choice):
    """
    Select the end-goal for your run.
    (Currently only supports 'Kill the Demon' and 'Kill the Wicked Witch' - more goals coming soon...)
    """
    display_name = "Goal"
    option_kill_the_demon = 0
    option_kill_the_wicked_witch = 1
    default = 0

class Mobsanity(Toggle):
    """
    Add checks for killing one of each enemy type to the check pool.
    """
    display_name = "Mobsanity"
    default = 0

class Pausing(Toggle):
    """
    Player is able to pause time.
    If disabled, time will only be paused by cutscenes and end-of-moon routines.
    """
    display_name = "Pausing"
    default = 1

class Traps(Toggle):
    """
    Add trap items to the item pool. 
    (Currently only one trap item, more coming soon...)
    """
    display_name = "Trap Items"
    default = 0

@dataclass
class StacklandsOptions(PerGameCommonOptions):
    dark_forest: DarkForest
    death_link: DeathLink
    goal: Goal
    pausing: Pausing
    mobsanity: Mobsanity
    traps: Traps