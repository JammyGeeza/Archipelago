from enum import Enum
from typing import Dict, List, NamedTuple
from BaseClasses import MultiWorld, Location, LocationProgressType, Region

class CheckType(Enum):
    Default = 0
    Mobsanity = 1
    Custom = 2 # Coming soon...

class LocationData(NamedTuple):
    name: str
    region: str
    check_type: CheckType
    progress_type: LocationProgressType

class StacklandsLocation(Location):
    game = "Stacklands"

# Locations table
location_table: List[LocationData] = [

#region Mainland Quests

    # 'Welcome' Category
    LocationData("Open the Booster Pack",                               "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Prevent opening quests from flooding early spheres
    LocationData("Drag the Villager on top of the Berry Bush",          "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Mine a Rock using a Villager",                        "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Sell a Card",                                         "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Prevent opening quests from flooding early spheres
    LocationData("Buy the Humble Beginnings Pack",                      "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Prevent opening quests from flooding early spheres
    LocationData("Harvest a Tree using a Villager",                     "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Make a Stick from Wood",                              "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Pause using the play icon in the top right corner",   "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Prevent opening quests from flooding early spheres
    LocationData("Grow a Berry Bush using Soil",                        "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Build a House",                                       "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Get a Second Villager",                               "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Create Offspring",                                    "Mainland",            CheckType.Default,        LocationProgressType.PRIORITY),  # <- Required, increase priority

    # 'The Grand Scheme' Category
    LocationData("Unlock all Packs",                                    "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Achieved only by receiving items from checks, reduce priority
    LocationData("Get 3 Villagers",                                     "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Find the Catacombs",                                  "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Find a mysterious artifact",                          "Mainland",            CheckType.Default,        LocationProgressType.PRIORITY), # <- Required, increase priority
    LocationData("Build a Temple",                                      "Mainland",            CheckType.Default,        LocationProgressType.PRIORITY), # <- Required, increase priority
    LocationData("Bring the Goblet to the Temple",                      "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Achieved immediately between two quests above and one below, no need for important item here.
    LocationData("Kill the Demon",                                      "Mainland",            CheckType.Default,        LocationProgressType.PRIORITY),  # <- Required, increase priority (if not the Goal)

    # 'Power & Skill' Category
    LocationData("Train Militia",                                       "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Kill a Rat",                                          "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Kill a Skeleton",                                     "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),

    # 'Strengthen Up' Category
    LocationData("Train an Archer",                                     "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Relies heavily on RNG, reduce priority
    LocationData("Make a Villager wear a Rabbit Hat",                   "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Build a Smithy",                                      "Mainland",            CheckType.Default,        LocationProgressType.PRIORITY), # <- Required, increase priority
    LocationData("Train a Wizard",                                      "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Equip an Archer with a Quiver",                       "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Relies heavily on RNG, reduce priority
    LocationData("Have a Villager with Combat Level 20",                "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Train a Ninja",                                       "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),

    # 'Potluck' Category
    LocationData("Start a Campfire",                                    "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Cook Raw Meat",                                       "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Cook an Omelette",                                    "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Cook a Frittata",                                     "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),

    # 'Discovery' Category
    LocationData("Explore a Forest",                                    "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Explore a Mountain",                                  "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Open a Treasure Chest",                               "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Find a Graveyard",                                    "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Get a Dog",                                           "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Train an Explorer",                                   "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Buy something from a Travelling Cart",                "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Spawns Moon 19 or heavily RNG-based, reduce priority

    # 'Ways and Means' Category
    LocationData("Have 5 Ideas",                                        "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Achieved only by receiving ideas from checks, reduce priority
    LocationData("Have 10 Ideas",                                       "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- Achieved only by receiving ideas from checks, reduce priority
    LocationData("Have 10 Wood",                                        "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Have 10 Stone",                                       "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Get an Iron Bar",                                     "Mainland",            CheckType.Default,        LocationProgressType.PRIORITY), # <- Required, increase priority
    LocationData("Have 5 Food",                                         "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Have 10 Food",                                        "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Have 20 Food",                                        "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Have 50 Food",                                        "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Have 10 Coins",                                       "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Have 30 Coins",                                       "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Have 50 Coins",                                       "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),

    # 'Construction' Category
    LocationData("Have 3 Houses",                                       "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Build a Shed",                                        "Mainland",            CheckType.Default,        LocationProgressType.PRIORITY), # <- Required, increase priority
    LocationData("Build a Quarry",                                      "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Build a Lumber Camp",                                 "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Build a Farm",                                        "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Build a Brickyard",                                   "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Sell a Card at a Market",                             "Mainland",            CheckType.Default,        LocationProgressType.DEFAULT),

    # 'Longevity' Category
    LocationData("Reach Moon 6",                                        "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- These quests shouldn't be a priority as duration is not required, reduce priority
    LocationData("Reach Moon 12",                                       "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- These quests shouldn't be a priority as duration is not required, reduce priority
    LocationData("Reach Moon 24",                                       "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- These quests shouldn't be a priority as duration is not required, reduce priority
    LocationData("Reach Moon 36",                                       "Mainland",            CheckType.Default,        LocationProgressType.EXCLUDED), # <- These quests shouldn't be a priority as duration is not required, reduce priority

#endregion

#region The Dark Forest Quests

    LocationData("Find the Dark Forest",                                "The Dark Forest",     CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Complete the first wave",                             "The Dark Forest",     CheckType.Default,        LocationProgressType.DEFAULT), 
    LocationData("Build a Stable Portal",                               "The Dark Forest",     CheckType.Default,        LocationProgressType.DEFAULT),
    LocationData("Get to Wave 6",                                       "The Dark Forest",     CheckType.Default,        LocationProgressType.DEFAULT), 
    LocationData("Kill the Wicked Witch",                               "The Dark Forest",     CheckType.Default,        LocationProgressType.DEFAULT),

#endregion

#region Mobsanity Quests

    # Mobsanity
    LocationData("Kill a Bear",                                         "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Dark Elf",                                     "The Dark Forest",     CheckType.Mobsanity,      LocationProgressType.DEFAULT), # <- Found only in The Dark Forest waves
    LocationData("Kill an Elf",                                         "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill an Elf Archer",                                  "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill an Enchanted Shroom",                            "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill an Ent",                                         "The Dark Forest",     CheckType.Mobsanity,      LocationProgressType.DEFAULT), # <- Found only in The Dark Forest waves
    LocationData("Kill a Feral Cat",                                    "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Frog Man",                                     "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Ghost",                                        "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Giant Rat",                                    "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Giant Snail",                                  "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Goblin",                                       "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Goblin Archer",                                "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Goblin Shaman",                                "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Merman",                                       "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Mimic",                                        "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Mosquito",                                     "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill an Ogre",                                        "The Dark Forest",     CheckType.Mobsanity,      LocationProgressType.DEFAULT), # <- Found only in The Dark Forest waves
    LocationData("Kill an Orc Wizard",                                  "The Dark Forest",     CheckType.Mobsanity,      LocationProgressType.DEFAULT), # <- Found only in The Dark Forest waves
    LocationData("Kill a Slime",                                        "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Small Slime",                                  "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Snake",                                        "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Tiger",                                        "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),
    LocationData("Kill a Wolf",                                         "Mainland",            CheckType.Mobsanity,      LocationProgressType.DEFAULT),

#endregion
]

# Goal table ('Goal' option value mapped to goal name)
goal_table: Dict[int, LocationData] = {
    0   : LocationData("Kill the Demon",    "Mainland",    CheckType.Default,    LocationProgressType.DEFAULT),
}

base_id: int = 92000
current_id: int = base_id

name_to_id = {}

# Create locations lookup
for location in location_table:
    name_to_id[location.name] = current_id
    current_id += 1