from enum import IntEnum, IntFlag

#region Enums

class CheckType(IntEnum):
    Check     = 0
    Goal      = 1

class ExpansionType(IntEnum):
    Ideas     = 0
    Items     = 1

class ItemType(IntEnum):
    Booster   = 0
    Idea      = 1
    Resource  = 2
    Mob       = 3
    Structure = 4
    Buff      = 5

#endregion

#region Flags

class CheckFlags(IntFlag):
    NA        = 0       
    Goal      = 1 << 0
    Pausing   = 1 << 1
    Mobsanity = 1 << 2

class GoalFlags(IntFlag):
    Demon     = 1 << 0
    Witch     = 1 << 1
    All       = 1 << 2

class ItemFlags(IntFlag):
    NA        = 0
    Booster   = 1 << 0
    Idea      = 1 << 1
    Resource  = 1 << 2
    Mob       = 1 << 3
    Expansion = 1 << 4
    CardLimit = 1 << 5

class OptionFlags(IntFlag):
    NA        = 0
    Pausing   = 1 << 0
    Traps     = 1 << 1
    Mobsanity = 1 << 2
    Expansion = 1 << 3

class RegionFlags(IntFlag):
    NA        = 0
    Mainland  = 1 << 0
    Forest    = 1 << 1
    Island    = 1 << 2
    Shared    = Mainland | Forest

#endregion