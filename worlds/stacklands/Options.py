from dataclasses import dataclass
from Options import Choice, DeathLink, PerGameCommonOptions, StartInventory, Toggle
    
# More options to be implemented in future...
class Goal(Choice):
    """
    Select the end-goal for the run.
    'Kill Demon Lord' may currently be very difficult as The Island is not yet supported.
    """
    display_name = "Goal"
    option_kill_demon = 0
    option_kill_demon_lord = 1
    # More options to come...
    default = 0

class PauseEnabled(Toggle):
    """
    Whether or not to enable the ability to pause time manually.
    If disabled, time will only be paused by cutscenes.
    """
    display_name = "Pausing Enabled"

@dataclass
class StacklandsOptions(PerGameCommonOptions):
    death_link: DeathLink
    goal: Goal
    pause_enabled: PauseEnabled    