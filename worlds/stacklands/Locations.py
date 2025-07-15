from .Enums import CheckFlags, RegionFlags
from dataclasses import dataclass
from enum import Enum, IntFlag
from typing import Dict, List, NamedTuple
from BaseClasses import MultiWorld, Location, LocationProgressType, Region

@dataclass
class LocationData():
    name: str
    region_flags: RegionFlags
    check_flags: CheckFlags
    progress_type: LocationProgressType

class StacklandsLocation(Location):
    game = "Stacklands"

    def __init__(self, player: int, location_data: LocationData, address: int | None = None, parent: Region | None = None):
        super(StacklandsLocation, self).__init__(
            player,
            location_data.name,
            address,
            parent
        )

        self.progress_type = location_data.progress_type


# Locations table
location_table: List[LocationData] = [

#region Mainland Quests

    # 'Welcome' Category
    LocationData("Open the Booster Pack"                                , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Drag the Villager on top of the Berry Bush"           , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Mine a Rock using a Villager"                         , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Sell a Card"                                          , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ), 
    LocationData("Buy the Humble Beginnings Pack"                       , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ), 
    LocationData("Harvest a Tree using a Villager"                      , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Make a Stick from Wood"                               , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.PRIORITY), # <- Prioritise to aid progression
    LocationData("Pause using the play icon in the top right corner"    , RegionFlags.Mainland     , CheckFlags.Pausing    , LocationProgressType.DEFAULT ), 
    LocationData("Grow a Berry Bush using Soil"                         , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Build a House"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Get a Second Villager"                                , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Create Offspring"                                     , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.PRIORITY), # <- Prioritise to aid progression

    # 'The Grand Scheme' Category
    LocationData("Unlock all Packs"                                     , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Get 3 Villagers"                                      , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Find the Catacombs"                                   , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Find a mysterious artifact"                           , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ), 
    LocationData("Build a Temple"                                       , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.PRIORITY), # <- Prioritise to aid progression
    LocationData("Bring the Goblet to the Temple"                       , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Kill the Demon"                                       , RegionFlags.Mainland     , CheckFlags.Goal       , LocationProgressType.DEFAULT ),

    # 'Power & Skill' Category
    LocationData("Train Militia"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Kill a Rat"                                           , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Kill a Skeleton"                                      , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),

    # 'Strengthen Up' Category
    LocationData("Train an Archer"                                      , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.EXCLUDED), # <- Relies heavily on RNG, reduce priority
    LocationData("Make a Villager wear a Rabbit Hat"                    , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Build a Smithy"                                       , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Train a Wizard"                                       , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Equip an Archer with a Quiver"                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.EXCLUDED), # <- Relies heavily on RNG, reduce priority
    LocationData("Have a Villager with Combat Level 20"                 , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Train a Ninja"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),

    # 'Potluck' Category
    LocationData("Start a Campfire"                                     , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.PRIORITY), # <- Prioritise to aid progression
    LocationData("Cook Raw Meat"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Cook an Omelette"                                     , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Cook a Frittata"                                      , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),

    # 'Discovery' Category
    LocationData("Explore a Forest"                                     , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Explore a Mountain"                                   , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Open a Treasure Chest"                                , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Find a Graveyard"                                     , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Get a Dog"                                            , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Train an Explorer"                                    , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Buy something from a Travelling Cart"                 , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),

    # 'Ways and Means' Category
    LocationData("Have 5 Ideas"                                         , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Ideas"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Wood"                                         , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Stone"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Get an Iron Bar"                                      , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Have 5 Food"                                          , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Food"                                         , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Have 20 Food"                                         , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Have 50 Food"                                         , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Coins"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Have 30 Coins"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Have 50 Coins"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),

    # 'Construction' Category
    LocationData("Have 3 Houses"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Build a Shed"                                         , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Build a Quarry"                                       , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Build a Lumber Camp"                                  , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Build a Farm"                                         , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Build a Brickyard"                                    , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Sell a Card at a Market"                              , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),

    # 'Longevity' Category
    LocationData("Reach Moon 6"                                         , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ), 
    LocationData("Reach Moon 12"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Reach Moon 24"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Reach Moon 36"                                        , RegionFlags.Mainland     , CheckFlags.NA         , LocationProgressType.DEFAULT ),

#endregion

#region The Dark Forest Quests

    LocationData("Find the Dark Forest"                                , RegionFlags.Forest        , CheckFlags.NA         , LocationProgressType.DEFAULT ),
    LocationData("Complete the first wave"                             , RegionFlags.Forest        , CheckFlags.NA         , LocationProgressType.DEFAULT ), 
    LocationData("Build a Stable Portal"                               , RegionFlags.Forest        , CheckFlags.NA         , LocationProgressType.PRIORITY), # <- Prioritise to aid progression 
    LocationData("Get to Wave 6"                                       , RegionFlags.Forest        , CheckFlags.NA         , LocationProgressType.DEFAULT ), 
    LocationData("Fight the Wicked Witch"                              , RegionFlags.Forest        , CheckFlags.Goal       , LocationProgressType.PRIORITY), # <- Prioritise to aid progression 

#endregion

#region Mobsanity Quests

    # Mobsanity
    LocationData("Kill a Bear"                                         , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Dark Elf"                                     , RegionFlags.Forest        , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill an Elf"                                         , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill an Elf Archer"                                  , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill an Enchanted Shroom"                            , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill an Ent"                                         , RegionFlags.Forest        , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Feral Cat"                                    , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Frog Man"                                     , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Ghost"                                        , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Giant Rat"                                    , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Giant Snail"                                  , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Goblin"                                       , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Goblin Archer"                                , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Goblin Shaman"                                , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Merman"                                       , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Mimic"                                        , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Mosquito"                                     , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill an Ogre"                                        , RegionFlags.Forest        , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill an Orc Wizard"                                  , RegionFlags.Forest        , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Slime"                                        , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Small Slime"                                  , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Snake"                                        , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Tiger"                                        , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),
    LocationData("Kill a Wolf"                                         , RegionFlags.Mainland      , CheckFlags.Mobsanity  , LocationProgressType.DEFAULT ),

#endregion
]

# # Goal table ('Goal' option value mapped to goal name)
# goal_table: Dict[int, LocationData] = {
#     0   : LocationData("Kill the Demon"                                , RegionFlags.Mainland      , CheckFlags.Goal       , LocationProgressType.DEFAULT ),
#     1   : LocationData("Fight the Wicked Witch"                        , RegionFlags.Forest        , CheckFlags.Goal       , LocationProgressType.DEFAULT ),
# }

base_id: int = 92000
current_id: int = base_id

name_to_id = {}

# Create locations lookup
for location in location_table:
    name_to_id[location.name] = current_id
    current_id += 1