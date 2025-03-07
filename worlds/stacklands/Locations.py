from typing import Dict, List, NamedTuple
from BaseClasses import MultiWorld, Location, LocationProgressType, Region

class LocationData(NamedTuple):
    name: str
    region: str
    progress_type: LocationProgressType

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
    LocationData("Open the Booster Pack"                               , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Drag the Villager on top of the Berry Bush"          , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Mine a Rock using a Villager"                        , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Sell a Card"                                         , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Buy the Humble Beginnings Pack"                      , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Harvest a Tree using a Villager"                     , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Make a Stick from Wood"                              , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Pause using the play icon in the top right corner"   , "Mainland", LocationProgressType.EXCLUDED),
    LocationData("Grow a Berry Bush using Soil"                        , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Build a House"                                       , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Get a Second Villager"                               , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Create Offspring"                                    , "Mainland", LocationProgressType.DEFAULT),
    
    # 'The Grand Scheme' Category
    LocationData("Get 3 Villagers"                                     , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Find the Catacombs"                                  , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Find a mysterious artifact"                          , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Build a Temple"                                      , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Bring the Goblet to the Temple"                      , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Kill the Demon"                                      , "Mainland", LocationProgressType.DEFAULT), # <- Will be a check if 'Kill the Demon Lord' is the goal
    
    # 'Power & Skill' Category
    LocationData("Train Militia"                                       , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Kill a Rat"                                          , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Kill a Skeleton"                                     , "Mainland", LocationProgressType.DEFAULT),
    
    # 'Strengthen Up' Category
    LocationData("Train an Archer"                                     , "Mainland", LocationProgressType.EXCLUDED), # <- Achievable mostly through RNG
    LocationData("Make a Villager wear a Rabbit Hat"                   , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Build a Smithy"                                      , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Train a Wizard"                                      , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Equip an Archer with a Quiver"                       , "Mainland", LocationProgressType.EXCLUDED), # <- Achievable mostly through RNG
    LocationData("Have a Villager with Combat Level 20"                , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Train a Ninja"                                       , "Mainland", LocationProgressType.DEFAULT), 
    
    # 'Potluck' Category
    LocationData("Start a Campfire"                                    , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Cook Raw Meat"                                       , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Cook an Omelette"                                    , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Cook a Frittata"                                     , "Mainland", LocationProgressType.DEFAULT),
    
    # 'Discovery' Category
    LocationData("Explore a Forest"                                    , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Explore a Mountain"                                  , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Open a Treasure Chest"                               , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Find a Graveyard"                                    , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Get a Dog"                                           , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Train an Explorer"                                   , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Buy something from a Travelling Cart"                , "Mainland", LocationProgressType.DEFAULT),
    
    # 'Ways and Means' Category
    LocationData("Have 5 Ideas"                                        , "Mainland", LocationProgressType.EXCLUDED),
    LocationData("Have 10 Ideas"                                       , "Mainland", LocationProgressType.EXCLUDED),
    LocationData("Have 10 Wood"                                        , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Have 10 Stone"                                       , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Get an Iron Bar"                                     , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Have 5 Food"                                         , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Have 10 Food"                                        , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Have 20 Food"                                        , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Have 50 Food"                                        , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Have 10 Coins"                                       , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Have 30 Coins"                                       , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Have 50 Coins"                                       , "Mainland", LocationProgressType.DEFAULT),
    
    # 'Construction' Category
    LocationData("Have 3 Houses"                                       , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Build a Shed"                                        , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Build a Quarry"                                      , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Build a Lumber Camp"                                 , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Build a Farm"                                        , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Build a Brickyard"                                   , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Sell a Card at a Market"                             , "Mainland", LocationProgressType.DEFAULT),
    
    # 'Longevity' Category
    LocationData("Reach Moon 6"                                        , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Reach Moon 12"                                       , "Mainland", LocationProgressType.DEFAULT),
    LocationData("Reach Moon 24"                                       , "Mainland", LocationProgressType.EXCLUDED), # <- Reaching higher moons for important items is arduous
    LocationData("Reach Moon 36"                                       , "Mainland", LocationProgressType.EXCLUDED), # <- Reaching higher moons for important items is arduous
]

# Goal table ('Goal' option value mapped to goal name)
goal_table: Dict[int, LocationData] = {
    0   : LocationData("Kill the Demon",        "Mainland", LocationProgressType.DEFAULT),
    1   : LocationData("Kill the Demon Lord",   "Mainland", LocationProgressType.DEFAULT)
}

base_id: int = 92000
current_id: int = base_id

name_to_id = {}

# Create locations lookup
for location in location_table:
    name_to_id[location.name] = current_id
    current_id += 1