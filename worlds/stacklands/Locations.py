from enum import Enum, IntFlag
from typing import Dict, List, NamedTuple
from BaseClasses import MultiWorld, Location, LocationProgressType, Region

class CheckFlags(IntFlag):
    None      = 0b0000
    Quest     = 0b0001
    Mobsanity = 0b0010

class RegionFlags(IntFlag):
    None      = 0b0000
    Mainland  = 0b0001
    Forest    = 0b0010
    Island    = 0b0100

class LocationData(NamedTuple):
    name: str
    region_flags: RegionFlags
    check_flags: CheckFlags
    progress_type: LocationProgressType

class StacklandsLocation(Location):
    game = "Stacklands"

# Locations table
location_table: List[LocationData] = [

#region Mainland Quests

    # 'Welcome' Category
    LocationData("Open the Booster Pack"                                , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.EXCLUDED), # <- Prevent opening quests from flooding early spheres
    LocationData("Drag the Villager on top of the Berry Bush"           , RegionFlags.Mainland                          , CheckFlags.Quest      , LocationProgressType.DEFAULT ),
    LocationData("Mine a Rock using a Villager"                         , RegionFlags.Mainland                          , CheckFlags.Quest      , LocationProgressType.EXCLUDED),  # <- Prevent opening quests from flooding early spheres
    LocationData("Sell a Card"                                          , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.EXCLUDED), # <- Prevent opening quests from flooding early spheres
    LocationData("Buy the Humble Beginnings Pack"                       , RegionFlags.Mainland                          , CheckFlags.Quest      , LocationProgressType.DEFAULT ), 
    LocationData("Harvest a Tree using a Villager"                      , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.DEFAULT ),
    LocationData("Make a Stick from Wood"                               , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.DEFAULT ),
    LocationData("Pause using the play icon in the top right corner"    , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.EXCLUDED), # <- Prevent opening quests from flooding early spheres
    LocationData("Grow a Berry Bush using Soil"                         , RegionFlags.Mainland                          , CheckFlags.Quest      , LocationProgressType.DEFAULT ),
    LocationData("Build a House"                                        , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.DEFAULT ),
    LocationData("Get a Second Villager"                                , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.DEFAULT ),
    LocationData("Create Offspring"                                     , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.DEFAULT ), # <- Required to help prevent stagnant game state, increase priority

    # 'The Grand Scheme' Category
    LocationData("Unlock all Packs"                                     , RegionFlags.Mainland                          , CheckFlags.Quest      , LocationProgressType.EXCLUDED), # <- Achieved only by receiving items from checks, reduce priority
    LocationData("Get 3 Villagers"                                      , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.DEFAULT ),
    LocationData("Find the Catacombs"                                   , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.DEFAULT ),
    LocationData("Find a mysterious artifact"                           , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.DEFAULT ), 
    LocationData("Build a Temple"                                       , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.DEFAULT ),
    LocationData("Bring the Goblet to the Temple"                       , RegionFlags.Mainland | RegionFlags.Island     , CheckFlags.Quest      , LocationProgressType.DEFAULT ),
    LocationData("Kill the Demon",                                      "Mainland",            CheckFlags.Quest,        LocationProgressType.EXCLUDED), # <- Don't force player to complete Demon if goal is Kill the Wicked Witch

    # 'Power & Skill' Category
    LocationData("Train Militia",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Kill a Rat",                                          "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Kill a Skeleton",                                     "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),

    # 'Strengthen Up' Category
    LocationData("Train an Archer",                                     "Mainland",            CheckFlags.Quest,        LocationProgressType.EXCLUDED), # <- Relies heavily on RNG, reduce priority
    LocationData("Make a Villager wear a Rabbit Hat",                   "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Build a Smithy",                                      "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Train a Wizard",                                      "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Equip an Archer with a Quiver",                       "Mainland",            CheckFlags.Quest,        LocationProgressType.EXCLUDED), # <- Relies heavily on RNG, reduce priority
    LocationData("Have a Villager with Combat Level 20",                "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Train a Ninja",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),

    # 'Potluck' Category
    LocationData("Start a Campfire",                                    "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Cook Raw Meat",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Cook an Omelette",                                    "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Cook a Frittata",                                     "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),

    # 'Discovery' Category
    LocationData("Explore a Forest",                                    "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Explore a Mountain",                                  "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Open a Treasure Chest",                               "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Find a Graveyard",                                    "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Get a Dog",                                           "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Train an Explorer",                                   "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Buy something from a Travelling Cart",                "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),

    # 'Ways and Means' Category
    LocationData("Have 5 Ideas",                                        "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Have 10 Ideas",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Have 10 Wood",                                        "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Have 10 Stone",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Get an Iron Bar",                                     "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Have 5 Food",                                         "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Have 10 Food",                                        "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Have 20 Food",                                        "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Have 50 Food",                                        "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Have 10 Coins",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Have 30 Coins",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Have 50 Coins",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),

    # 'Construction' Category
    LocationData("Have 3 Houses",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Build a Shed",                                        "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Build a Quarry",                                      "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Build a Lumber Camp",                                 "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Build a Farm",                                        "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Build a Brickyard",                                   "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Sell a Card at a Market",                             "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),

    # 'Longevity' Category
    LocationData("Reach Moon 6",                                        "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT), 
    LocationData("Reach Moon 12",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Reach Moon 24",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Reach Moon 36",                                       "Mainland",            CheckFlags.Quest,        LocationProgressType.EXCLUDED), # <- Long duration is not required, reduce priority

#endregion

#region The Dark Forest Quests

    LocationData("Find the Dark Forest",                                "The Dark Forest",     CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Complete the first wave",                             "The Dark Forest",     CheckFlags.Quest,        LocationProgressType.DEFAULT), 
    LocationData("Build a Stable Portal",                               "The Dark Forest",     CheckFlags.Quest,        LocationProgressType.DEFAULT),
    LocationData("Get to Wave 6",                                       "The Dark Forest",     CheckFlags.Quest,        LocationProgressType.DEFAULT), 
    LocationData("Fight the Wicked Witch",                              "The Dark Forest",     CheckFlags.Quest,        LocationProgressType.DEFAULT),

#endregion

#region Mobsanity Quests

    # Mobsanity
    LocationData("Kill a Bear",                                         "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Dark Elf",                                     "The Dark Forest",     CheckFlags.Mobsanity,      LocationProgressType.DEFAULT), # <- Found only in The Dark Forest waves
    LocationData("Kill an Elf",                                         "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill an Elf Archer",                                  "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill an Enchanted Shroom",                            "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill an Ent",                                         "The Dark Forest",     CheckFlags.Mobsanity,      LocationProgressType.DEFAULT), # <- Found only in The Dark Forest waves
    LocationData("Kill a Feral Cat",                                    "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Frog Man",                                     "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Ghost",                                        "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Giant Rat",                                    "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Giant Snail",                                  "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Goblin",                                       "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Goblin Archer",                                "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Goblin Shaman",                                "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Merman",                                       "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Mimic",                                        "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Mosquito",                                     "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill an Ogre",                                        "The Dark Forest",     CheckFlags.Mobsanity,      LocationProgressType.DEFAULT), # <- Found only in The Dark Forest waves
    LocationData("Kill an Orc Wizard",                                  "The Dark Forest",     CheckFlags.Mobsanity,      LocationProgressType.DEFAULT), # <- Found only in The Dark Forest waves
    LocationData("Kill a Slime",                                        "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Small Slime",                                  "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Snake",                                        "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Tiger",                                        "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Wolf",                                         "Mainland",            CheckFlags.Mobsanity,      LocationProgressType.DEFAULT),

#endregion
]

# Goal table ('Goal' option value mapped to goal name)
goal_table: Dict[int, LocationData] = {
    0   : LocationData("Kill the Demon",             "Mainland",           CheckFlags.Quest,    LocationProgressType.DEFAULT),
    1   : LocationData("Fight the Wicked Witch",     "The Dark Forest",    CheckFlags.Quest,    LocationProgressType.DEFAULT),
}

base_id: int = 92000
current_id: int = base_id

name_to_id = {}

# Create locations lookup
for location in location_table:
    name_to_id[location.name] = current_id
    current_id += 1