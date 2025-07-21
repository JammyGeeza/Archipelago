from .Enums import CheckFlags, CheckType, OptionFlags, RegionFlags
from dataclasses import dataclass
from enum import Enum, IntFlag
from typing import Dict, List, NamedTuple
from BaseClasses import MultiWorld, Location, LocationProgressType, Region

@dataclass
class LocationData():
    name: str
    region_flags: RegionFlags
    check_type: CheckType
    option_flags: OptionFlags
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
    LocationData("Open the Booster Pack"                                , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Drag the Villager on top of the Berry Bush"           , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Mine a Rock using a Villager"                         , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Sell a Card"                                          , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ), 
    LocationData("Buy the Humble Beginnings Pack"                       , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ), 
    LocationData("Harvest a Tree using a Villager"                      , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Make a Stick from Wood"                               , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.PRIORITY), # <- Prioritise to aid progression
    LocationData("Pause using the play icon in the top right corner"    , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.Pausing      , LocationProgressType.DEFAULT ), 
    LocationData("Grow a Berry Bush using Soil"                         , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Build a House"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Get a Second Villager"                                , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Create Offspring"                                     , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.PRIORITY), # <- Prioritise to aid progression

    # 'The Grand Scheme' Category
    LocationData("Unlock all Packs"                                     , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Get 3 Villagers"                                      , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Find the Catacombs"                                   , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Find a mysterious artifact"                           , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ), 
    LocationData("Build a Temple"                                       , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.PRIORITY), # <- Prioritise to aid progression
    LocationData("Bring the Goblet to the Temple"                       , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Kill the Demon"                                       , RegionFlags.Mainland     , CheckType.Goal     , OptionFlags.NA           , LocationProgressType.DEFAULT ),

    # 'Power & Skill' Category
    LocationData("Train Militia"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Kill a Rat"                                           , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Kill a Skeleton"                                      , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),

    # 'Strengthen Up' Category
    LocationData("Train an Archer"                                      , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.EXCLUDED), # <- Relies heavily on RNG, reduce priority
    LocationData("Make a Villager wear a Rabbit Hat"                    , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Build a Smithy"                                       , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Train a Wizard"                                       , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Equip an Archer with a Quiver"                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.EXCLUDED), # <- Relies heavily on RNG, reduce priority
    LocationData("Have a Villager with Combat Level 20"                 , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Train a Ninja"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),

    # 'Potluck' Category
    LocationData("Start a Campfire"                                     , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.PRIORITY), # <- Prioritise to aid progression
    LocationData("Cook Raw Meat"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Cook an Omelette"                                     , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Cook a Frittata"                                      , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),

    # 'Discovery' Category
    LocationData("Explore a Forest"                                     , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Explore a Mountain"                                   , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Open a Treasure Chest"                                , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Find a Graveyard"                                     , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Get a Dog"                                            , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Train an Explorer"                                    , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Buy something from a Travelling Cart"                 , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),

    # 'Ways and Means' Category
    LocationData("Have 5 Ideas"                                         , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Ideas"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Wood"                                         , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Stone"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Get an Iron Bar"                                      , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Have 5 Food"                                          , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Food"                                         , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Have 20 Food"                                         , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Have 50 Food"                                         , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Coins"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Have 30 Coins"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Have 50 Coins"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),

    # 'Construction' Category
    LocationData("Have 3 Houses"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Build a Shed"                                         , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.Expansion    , LocationProgressType.DEFAULT ),
    LocationData("Build a Quarry"                                       , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Build a Lumber Camp"                                  , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Build a Farm"                                         , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Build a Brickyard"                                    , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Sell a Card at a Market"                              , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),

    # 'Longevity' Category
    LocationData("Reach Moon 6"                                         , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ), 
    LocationData("Reach Moon 12"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Reach Moon 24"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Reach Moon 36"                                        , RegionFlags.Mainland     , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),

#endregion

#region The Dark Forest Quests

    LocationData("Find the Dark Forest"                                , RegionFlags.Forest        , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ),
    LocationData("Complete the first wave"                             , RegionFlags.Forest        , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ), 
    LocationData("Build a Stable Portal"                               , RegionFlags.Forest        , CheckType.Check    , OptionFlags.NA           , LocationProgressType.PRIORITY), # <- Prioritise to aid progression 
    LocationData("Get to Wave 6"                                       , RegionFlags.Forest        , CheckType.Check    , OptionFlags.NA           , LocationProgressType.DEFAULT ), 
    LocationData("Fight the Wicked Witch"                              , RegionFlags.Forest        , CheckType.Goal     , OptionFlags.NA           , LocationProgressType.PRIORITY), # <- Prioritise to aid progression 

#endregion

#region Mobsanity Quests

    # Mobsanity
    LocationData("Kill a Bear"                                         , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Dark Elf"                                     , RegionFlags.Forest        , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Elf"                                         , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Elf Archer"                                  , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Enchanted Shroom"                            , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Ent"                                         , RegionFlags.Forest        , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Feral Cat"                                    , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Frog Man"                                     , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Ghost"                                        , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Giant Rat"                                    , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Giant Snail"                                  , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Goblin"                                       , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Goblin Archer"                                , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Goblin Shaman"                                , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Merman"                                       , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Mimic"                                        , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Mosquito"                                     , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Ogre"                                        , RegionFlags.Forest        , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Orc Wizard"                                  , RegionFlags.Forest        , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Slime"                                        , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Small Slime"                                  , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Snake"                                        , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Tiger"                                        , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Wolf"                                         , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),

#endregion
]

base_id: int = 92000
current_id: int = base_id

name_to_id = {}

# Create locations lookup
for location in location_table:
    name_to_id[location.name] = current_id
    current_id += 1