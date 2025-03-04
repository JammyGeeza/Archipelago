from typing import List, TypedDict
from BaseClasses import Location, LocationProgressType

class StacklandsLocation(Location):
    game = "Stacklands"


class LocationData(TypedDict):
    name: str
    region: str
    classification: LocationProgressType

# Locations table
locations_table: List[LocationData] = [
    
    # Mainland Quests
    
    # 'Welcome' Category
    {"name": "Open the Booster Pack",                               "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Drag the Villager on top of the Berry Bush",          "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Mine a Rock using a Villager",                        "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Sell a Card",                                         "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Buy the Humble Beginnings Pack",                      "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Harvest a Tree using a Villager",                     "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Make a Stick from Wood",                              "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Pause using the play icon in the top right corner",   "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Grow a Berry Bush using Soil",                        "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Build a House",                                       "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Get a Second Villager",                               "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Create Offspring",                                    "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    
    # 'The Grand Scheme' Category
    # {"name": "Unlock All Packs", "region": "Mainland"}, <- Can ONLY be unlocked by receiving all packs from checks, seems pointless? (Also this quest triggers when Order and Structure pack is unlocked, so usually triggers far too early)
    {"name": "Get 3 Villagers",                                     "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Find the Catacombs",                                  "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Find a mysterious artifact",                          "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Build a Temple",                                      "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Bring the Goblet to the Temple",                      "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Kill the Demon",                                      "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Kill the Demon Lord",                                 "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    
    # 'Power & Skill' Category
    {"name": "Train Militia",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Kill a Rat",                                          "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Kill a Skeleton",                                     "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    
    # 'Strengthening Up' Category
    # {"name": "Train an Archer", "region": "Mainland"}, <- Bow / Crossbow require Rope (from Island) or is a chance drop from Elf Archer - seems unfair.
    {"name": "Make a Villager wear a Rabbit Hat",                   "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Build a Smithy",                                      "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Train a Wizard",                                      "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    # {"name": "Equip an Archer with a Quiver", "region": "Mainland"}, <- Is a chance drop from Elf Archer - seems unfair.
    {"name": "Have a Villager with Combat Level 20",                "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Train a Ninja",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    
    # 'Potluck' Category
    {"name": "Start a Campfire",                                    "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Cook Raw Meat",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Cook an Omelette",                                    "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Cook a Frittata",                                     "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    
    # 'Discovery' Category
    {"name": "Explore a Forest",                                    "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Explore a Mountain",                                  "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Open a Treasure Chest",                               "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Find a Graveyard",                                    "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Get a Dog",                                           "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Train an Explorer",                                   "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Buy something from a Travelling Cart",                "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    
    # 'Ways and Means' Category
    {"name": "Have 5 Ideas",                                        "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Have 10 Ideas",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Have 10 Wood",                                        "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Have 10 Stone",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Get an Iron Bar",                                     "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Have 5 Food",                                         "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Have 10 Food",                                        "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Have 20 Food",                                        "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Have 50 Food",                                        "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Have 10 Coins",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Have 30 Coins",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Have 50 Coins",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    
    # 'Construction' Category
    {"name": "Have 3 Houses",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Build a Shed",                                        "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Build a Quarry",                                      "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Build a Lumber Camp",                                 "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Build a Farm",                                        "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Build a Brickyard",                                   "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Sell a Card at a Market",                             "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    
    # 'Longevity' Category
    {"name": "Reach Moon 6",                                        "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Reach Moon 12",                                       "region": "Mainland",   "classification": LocationProgressType.PRIORITY },
    {"name": "Reach Moon 24",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Reach Moon 36",                                       "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },

    # 'Side Quests' Category
    {"name": "Build a Garden",                                      "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Build a Sawmill",                                     "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Build a Mine",                                        "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
    {"name": "Build a Smelter",                                     "region": "Mainland",   "classification": LocationProgressType.DEFAULT  },
]

base_id: int = 91000
current_id: int = base_id

lookup_id_to_name = {}
lookup_name_to_id = {}
    
for location in locations_table:
        
    # Add to lookups
    lookup_id_to_name[current_id] = location["name"]
    lookup_name_to_id[location["name"]] = current_id
        
    # Increment ID
    current_id += 1
