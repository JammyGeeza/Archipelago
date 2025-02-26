from dataclasses import dataclass
from Options import Choice, DeathLink, PerGameCommonOptions, Range, Toggle

class BasicPackOnStart(Toggle):
    """
    Whether or not to start the run with the Humble Beginnings booster pack already unlocked to prevent starving 
    at the end of Moon 2 due from starvation from not being able to buy a booster pack.
    """
    display_name = "Start with Humble Beginnings Booster Pack"

# To be implemented in future...
# class DeathLinkOffset(Range):
#     """How many villager deaths will trigger a DeathLink."""
#     display_name = "DeathLink Offset"
#     range_start = 1
#     range_end = 10
#     default = 1
    
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

# To be implemented in future...
# class VillagerHP(Range):
#     """How much base HP Villagers will have (before equipment bonuses)"""
#     display_name = "Villager HP"
#     range_start = 5
#     range_end = 30
#     default = 15

@dataclass
class StacklandsOptions(PerGameCommonOptions):
    basic_pack: BasicPackOnStart
    death_link: DeathLink
    # death_link_offset: DeathLinkOffset
    goal: Goal
    pause_enabled: PauseEnabled
    # villager_hp: VillagerHP
    