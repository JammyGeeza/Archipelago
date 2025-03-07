from dataclasses import dataclass
from Options import Choice, DeathLink, PerGameCommonOptions, StartInventory, Toggle
    
# More options to be implemented in future...
class Goal(Choice):
    """
    What should the end-goal for your run be?
    """
    display_name = "Goal"
    option_kill_the_demon = 0
    option_kill_the_demon_lord = 1
    default = 0

class PauseEnabled(Toggle):
    """
    Should you be able to pause time manually?
    If disabled, time will only be paused by cutscenes and end-of-moon routines.
    """
    display_name = "Pausing Enabled"

@dataclass
class StacklandsOptions(PerGameCommonOptions):
    death_link: DeathLink
    goal: Goal
    pause_enabled: PauseEnabled    