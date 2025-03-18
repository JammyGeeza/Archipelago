from dataclasses import dataclass
from Options import Choice, DeathLink, PerGameCommonOptions, Toggle
    
# More options to be implemented in future...

class Goal(Choice):
    """
    Select the end-goal for your run.
    """
    display_name = "Goal"
    option_kill_the_demon = 0
    option_kill_the_demon_lord = 1
    default = 0

class IncludeTraps(Toggle):
    """
    Include trap items in the item pool.
    """
    display_name = "Include Traps"
    default = 0

class Mobsanity(Toggle):
    """
    Add checks to defeat every type of enemy.
    """
    display_name = "Mobsanity"
    default = 0

class PauseEnabled(Toggle):
    """
    Enable / Disable in-game pausing.
    If disabled, time will only be paused by cutscenes and end-of-moon routines.
    """
    display_name = "Enable Pausing"
    default = 1

@dataclass
class StacklandsOptions(PerGameCommonOptions):
    death_link: DeathLink
    mobsanity: Mobsanity
    goal: Goal
    include_traps: IncludeTraps
    pause_enabled: PauseEnabled