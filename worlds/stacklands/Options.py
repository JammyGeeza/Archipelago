from dataclasses import dataclass
from Options import Choice, DeathLink, PerGameCommonOptions, Toggle
    
# More options to be implemented in future...

class DarkForestSkippable(Toggle):
    """
    Checks in The Dark Forest will be guaranteed to only contain junk / filler items.
    """
    display_name = "The Dark Forest is Skippable"
    default = 0

class Goal(Choice):
    """
    Select the end-goal for your run.
    """
    display_name = "Goal"
    option_kill_the_demon = 0
    option_kill_the_demon_lord = 1
    default = 0

class MobsanityEnabled(Toggle):
    """
    Killing all enemy types are checks.
    """
    display_name = "Mobsanity"
    default = 0

class PausingEnabled(Toggle):
    """
    Enable / Disable in-game pausing.
    If disabled, time will only be paused by cutscenes and end-of-moon routines.
    """
    display_name = "Enable Pausing"
    default = 1

class TrapsEnabled(Toggle):
    """
    Add trap items to the item pool.
    """
    display_name = "Include Trap Items"
    default = 0

@dataclass
class StacklandsOptions(PerGameCommonOptions):
    dark_forest_skippable: DarkForestSkippable
    death_link: DeathLink
    goal: Goal
    pausing_enabled: PausingEnabled
    mobsanity_enabled: MobsanityEnabled
    traps_enabled: TrapsEnabled