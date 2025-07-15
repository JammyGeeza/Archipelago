from enum import IntFlag

class CheckFlags(IntFlag):
    NA        = 0b0000
    Goal      = 0b0001
    Pausing   = 0b0010
    Mobsanity = 0b0100

class GoalFlags(IntFlag):
    Demon     = 0b0001
    Witch     = 0b0010
    All       = 0b0011

class ItemFlags(IntFlag):
    NA        = 0b0000
    Booster   = 0b0001
    Idea      = 0b0010
    Resource  = 0b0100
    Mob       = 0b1000

class RegionFlags(IntFlag):
    NA        = 0b0000
    Mainland  = 0b0001
    Forest    = 0b0010
    Island    = 0b0100
    All       = 0b0111