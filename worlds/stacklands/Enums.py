from enum import IntEnum, IntFlag

#region Enums

class CheckType(IntEnum):
    Check     = 0
    Goal      = 1
    Event     = 2

class ExpansionType(IntEnum):
    Vanilla         = 0
    Expansion_Items = 1

class ItemType(IntEnum):
    Booster   = 0
    Idea      = 1
    Resource  = 2
    Trap      = 3
    Structure = 4
    Buff      = 5

class MoonlengthType(IntEnum):
    Short     = 0
    Normal    = 1
    Long      = 2

class MoonPhase(IntEnum):
    Moon_0  = 0
    Moon_2  = 1
    Moon_6  = 2
    Moon_12 = 3
    Moon_18 = 4
    Moon_24 = 5
    Moon_30 = 6
    Moon_36 = 7

class RedStructureSpawnType(IntEnum):
    Vanilla = 0
    TopLeft = 1
    TopRight = 2
    BottomLeft = 3
    BottomRight = 4
    Middle = 5

class ProgressionPhase(IntEnum):
    General     = 0
    PhaseOne    = 1
    PhaseTwo    = 2
    PhaseThree  = 3
    PhaseFour   = 4

class SpendsanityType(IntEnum):
    Off         = 0
    Fixed       = 1
    Incremental = 2

#endregion

#region Flags

class CheckFlags(IntFlag):
    NA        = 0       
    Goal      = 1 << 0
    Pausing   = 1 << 1
    Mobsanity = 1 << 2

class GoalFlags(IntFlag):
    NONE        = 0
    AllBosses   = 1 << 0
    RandomBoss  = 1 << 1
    AllQuests   = 1 << 2

class ItemFlags(IntFlag):
    NA        = 0
    Booster   = 1 << 0
    Idea      = 1 << 1
    Resource  = 1 << 2
    Mob       = 1 << 3
    Expansion = 1 << 4

class OptionFlags(IntFlag):
    NONE            = 0
    Pausing         = 1 << 0
    Traps           = 1 << 1
    Equipmentsanity = 1 << 2
    Foodsanity      = 1 << 3
    Locationsanity  = 1 << 4
    Mobsanity       = 1 << 5
    Structuresanity = 1 << 6
    Expansion       = 1 << 7

class RegionFlags(IntFlag):
    NA        = 0
    Mainland  = 1 << 0
    Forest    = 1 << 1
    Island    = 1 << 2

    Mainland_and_Forest = Mainland | Forest
    Mainland_and_Island = Mainland | Island
    Island_and_Forest   = Forest   | Island
    All                 = Mainland | Forest | Island

#endregion