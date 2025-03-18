from enum import Enum
from typing import Dict, List, NamedTuple
from BaseClasses import MultiWorld, Location, LocationProgressType, Region

class CheckType(Enum):
    Default = 0
    Mobsanity = 1

class LocationData(NamedTuple):
    name: str
    region: str
    progress_type: LocationProgressType = LocationProgressType.DEFAULT
    check_type: CheckType = CheckType.Default

class StacklandsLocation(Location):
    game = "Stacklands"

    def __init__(self, player: int, loc: LocationData, code: int = None, region: Region = None):
        super(StacklandsLocation, self).__init__(
            player,
            loc.name,
            code,
            region
        )

        # Set progress type
        self.progress_type = loc.progress_type

# Locations table
location_table: List[LocationData] = [

    # 'Welcome' Category
    LocationData("Open the Booster Pack"                               , "Mainland"),
    LocationData("Drag the Villager on top of the Berry Bush"          , "Mainland"),
    LocationData("Mine a Rock using a Villager"                        , "Mainland"),
    LocationData("Sell a Card"                                         , "Mainland"),
    LocationData("Buy the Humble Beginnings Pack"                      , "Mainland"),
    LocationData("Harvest a Tree using a Villager"                     , "Mainland"),
    LocationData("Make a Stick from Wood"                              , "Mainland"),
    LocationData("Pause using the play icon in the top right corner"   , "Mainland"         , LocationProgressType.EXCLUDED),
    LocationData("Grow a Berry Bush using Soil"                        , "Mainland"),
    LocationData("Build a House"                                       , "Mainland"),
    LocationData("Get a Second Villager"                               , "Mainland"),
    LocationData("Create Offspring"                                    , "Mainland"),
    
    # 'The Grand Scheme' Category
    LocationData("Unlock all Packs"                                    , "Mainland"         , LocationProgressType.EXCLUDED), # <- Achievable only from receiving items from checks
    LocationData("Get 3 Villagers"                                     , "Mainland"),
    LocationData("Find the Catacombs"                                  , "Mainland"),
    LocationData("Find a mysterious artifact"                          , "Mainland"),
    LocationData("Build a Temple"                                      , "Mainland"),
    LocationData("Bring the Goblet to the Temple"                      , "Mainland"),
    LocationData("Kill the Demon"                                      , "Mainland"), # <- Will be a check if 'Kill the Demon Lord' is the goal
    
    # 'Power & Skill' Category
    LocationData("Train Militia"                                       , "Mainland"),
    LocationData("Kill a Rat"                                          , "Mainland"),
    LocationData("Kill a Skeleton"                                     , "Mainland"),
    
    # 'Strengthen Up' Category
    LocationData("Train an Archer"                                     , "Mainland"         , LocationProgressType.EXCLUDED), # <- Achievable mostly through RNG
    LocationData("Make a Villager wear a Rabbit Hat"                   , "Mainland"),
    LocationData("Build a Smithy"                                      , "Mainland"),
    LocationData("Train a Wizard"                                      , "Mainland"),
    LocationData("Equip an Archer with a Quiver"                       , "Mainland"         , LocationProgressType.EXCLUDED), # <- Achievable mostly through RNG
    LocationData("Have a Villager with Combat Level 20"                , "Mainland"),
    LocationData("Train a Ninja"                                       , "Mainland"), 
    
    # 'Potluck' Category
    LocationData("Start a Campfire"                                    , "Mainland"),
    LocationData("Cook Raw Meat"                                       , "Mainland"),
    LocationData("Cook an Omelette"                                    , "Mainland"),
    LocationData("Cook a Frittata"                                     , "Mainland"),
    
    # 'Discovery' Category
    LocationData("Explore a Forest"                                    , "Mainland"),
    LocationData("Explore a Mountain"                                  , "Mainland"),
    LocationData("Open a Treasure Chest"                               , "Mainland"),
    LocationData("Find a Graveyard"                                    , "Mainland"),
    LocationData("Get a Dog"                                           , "Mainland"),
    LocationData("Train an Explorer"                                   , "Mainland"),
    LocationData("Buy something from a Travelling Cart"                , "Mainland"),
    
    # 'Ways and Means' Category
    LocationData("Have 5 Ideas"                                        , "Mainland"         , LocationProgressType.EXCLUDED), # <- Quite literally depends on receiving ideas from checks
    LocationData("Have 10 Ideas"                                       , "Mainland"         , LocationProgressType.EXCLUDED), # <- Quite literally depends on receiving ideas from checks
    LocationData("Have 10 Wood"                                        , "Mainland"),
    LocationData("Have 10 Stone"                                       , "Mainland"),
    LocationData("Get an Iron Bar"                                     , "Mainland"),
    LocationData("Have 5 Food"                                         , "Mainland"),
    LocationData("Have 10 Food"                                        , "Mainland"),
    LocationData("Have 20 Food"                                        , "Mainland"),
    LocationData("Have 50 Food"                                        , "Mainland"),
    LocationData("Have 10 Coins"                                       , "Mainland"),
    LocationData("Have 30 Coins"                                       , "Mainland"),
    LocationData("Have 50 Coins"                                       , "Mainland"),
    
    # 'Construction' Category
    LocationData("Have 3 Houses"                                       , "Mainland"),
    LocationData("Build a Shed"                                        , "Mainland"),
    LocationData("Build a Quarry"                                      , "Mainland"),
    LocationData("Build a Lumber Camp"                                 , "Mainland"),
    LocationData("Build a Farm"                                        , "Mainland"),
    LocationData("Build a Brickyard"                                   , "Mainland"),
    LocationData("Sell a Card at a Market"                             , "Mainland"),
    
    # 'Longevity' Category
    LocationData("Reach Moon 6"                                        , "Mainland"),
    LocationData("Reach Moon 12"                                       , "Mainland"),
    LocationData("Reach Moon 24"                                       , "Mainland"         , LocationProgressType.EXCLUDED), # <- Reaching higher moons for important items is just a waiting game
    LocationData("Reach Moon 36"                                       , "Mainland"         , LocationProgressType.EXCLUDED), # <- Reaching higher moons for important items is just a waiting game

    # Mobsanity
    LocationData("Kill a Bear"                                         , "Mainland"         , check_type=CheckType.Mobsanity),
    # LocationData("Kill a Dark Elf"                                     , "The Dark Forest"  , check_type=CheckType.Mobsanity),
    LocationData("Kill an Elf"                                         , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill an Elf Archer"                                  , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill an Enchanted Shroom"                            , "Mainland"         , check_type=CheckType.Mobsanity),
    # LocationData("Kill an Ent"                                         , "The Dark Forest"  , check_type=CheckType.Mobsanity),
    LocationData("Kill a Feral Cat"                                    , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Frog Man"                                     , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Ghost"                                        , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Giant Rat"                                    , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Giant Snail"                                  , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Goblin"                                       , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Goblin Archer"                                , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Goblin Shaman"                                , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Merman"                                       , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Mimic"                                        , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Mosquito"                                     , "Mainland"         , check_type=CheckType.Mobsanity),
    # LocationData("Kill an Ogre"                                        , "The Dark Forest"  , check_type=CheckType.Mobsanity),
    # LocationData("Kill an Orc Wizard"                                  , "The Dark Forest"  , check_type=CheckType.Mobsanity),
    LocationData("Kill a Slime"                                        , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Small Slime"                                  , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Snake"                                        , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Tiger"                                        , "Mainland"         , check_type=CheckType.Mobsanity),
    LocationData("Kill a Wolf"                                         , "Mainland"         , check_type=CheckType.Mobsanity),
]

# Goal table ('Goal' option value mapped to goal name)
goal_table: Dict[int, LocationData] = {
    0   : LocationData("Kill the Demon",        "Mainland"),
    1   : LocationData("Kill the Demon Lord",   "Mainland")
}

base_id: int = 92000
current_id: int = base_id

name_to_id = {}

# Create locations lookup
for location in location_table:
    name_to_id[location.name] = current_id
    current_id += 1