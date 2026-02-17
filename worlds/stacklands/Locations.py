from .Enums import CheckFlags, CheckType, ProgressionPhase, OptionFlags, RegionFlags, SpendsanityType
from .Options import StacklandsOptions
from dataclasses import dataclass
from enum import Enum, IntFlag
from typing import Dict, List, NamedTuple, Optional
from BaseClasses import Callable, CollectionState, MultiWorld, Location, LocationProgressType, Region

@dataclass
class LocationData():
    name: str
    region_flags: RegionFlags
    prog_phase: ProgressionPhase
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
    LocationData("Open the Booster Pack"                                , RegionFlags.Mainland      , ProgressionPhase.General      , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Drag the Villager on top of the Berry Bush"           , RegionFlags.Mainland      , ProgressionPhase.General      , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Mine a Rock using a Villager"                         , RegionFlags.Mainland      , ProgressionPhase.General      , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Sell a Card"                                          , RegionFlags.Mainland      , ProgressionPhase.General      , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 
    LocationData("Buy the Humble Beginnings Pack"                       , RegionFlags.Mainland      , ProgressionPhase.General      , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Harvest a Tree using a Villager"                      , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Make a Stick from Wood"                               , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Pause using the play icon in the top right corner"    , RegionFlags.Mainland      , ProgressionPhase.General      , CheckType.Check    , OptionFlags.Pausing        , LocationProgressType.DEFAULT ), 
    LocationData("Grow a Berry Bush using Soil"                         , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Build a House"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Get a Second Villager"                                , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Create Offspring"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),

    # 'The Grand Scheme' Category
    LocationData("Unlock all Packs"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseFour    , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Get 3 Villagers"                                      , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Find the Catacombs"                                   , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Find a mysterious artifact"                           , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Build a Temple"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseFour    , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Bring the Goblet to the Temple"                       , RegionFlags.Mainland      , ProgressionPhase.PhaseFour    , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.EXCLUDED),  # <- Summons Demon immediately so shouldn't really contain any progression items
    LocationData("Kill the Demon"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseFour    , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.EXCLUDED),  # <- Goal check, don't include progression items

    # 'Power & Skill' Category
    LocationData("Train Militia"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Kill a Rat"                                           , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Kill a Skeleton"                                      , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),

    # 'Strengthen Up' Category
    LocationData("Make a Villager wear a Rabbit Hat"                    , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Build a Smithy"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Train a Wizard"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have a Villager with Combat Level 20"                 , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Train a Ninja"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),

    # 'Potluck' Category
    LocationData("Start a Campfire"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Cook Raw Meat"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Cook an Omelette"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Cook a Frittata"                                      , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),

    # 'Discovery' Category
    LocationData("Explore a Forest"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Explore a Mountain"                                   , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Open a Treasure Chest"                                , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Find a Graveyard"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Get a Dog"                                            , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Train an Explorer"                                    , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Buy something from a Travelling Cart"                 , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.EXCLUDED), # <- Is both RNG and a waiting game

    # 'Ways and Means' Category
    LocationData("Have 5 Ideas"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Ideas"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Wood"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Stone"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Get an Iron Bar"                                      , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 5 Food"                                          , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Food"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 20 Food"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 50 Food"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Coins"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 30 Coins"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 50 Coins"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),

    # 'Construction' Category
    LocationData("Have 3 Houses"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Build a Shed"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Build a Quarry"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Build a Lumber Camp"                                  , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Build a Farm"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Build a Brickyard"                                    , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Sell a Card at a Market"                              , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),

    # 'Longevity' Category
    LocationData("Reach Moon 6"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 
    LocationData("Reach Moon 12"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Reach Moon 24"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.EXCLUDED), # <- Is a waiting game
    LocationData("Reach Moon 36"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.EXCLUDED), # <- Is a waiting game

    # Additional Archipelago quests
    LocationData("Buy the Seeking Wisdom Pack"                          , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Buy the Reap & Sow Pack"                              , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Buy the Curious Cuisine Pack"                         , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Buy the Logic and Reason Pack"                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Buy the The Armory Pack"                              , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Buy the Explorers Pack"                               , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Buy the Order and Structure Pack"                     , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Buy 5 Mainland Booster Packs"                         , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Buy 10 Mainland Booster Packs"                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Buy 25 Mainland Booster Packs"                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),

    LocationData("Sell 5 Cards"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 
    LocationData("Sell 10 Cards"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 
    LocationData("Sell 25 Cards"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 

    LocationData("Reach Moon 18"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.EXCLUDED), # <- Is a waiting game
    LocationData("Reach Moon 30"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.EXCLUDED), # <- Is a waiting game
    
    LocationData("Get 5 Villagers"                                      , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Get 7 Villagers"                                      , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),

    LocationData("Have 10 Bricks"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Flint"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Iron Bars"                                    , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Iron Ore"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Planks"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Sticks"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),

#endregion

#region The Dark Forest Quests

    LocationData("Find the Dark Forest"                                 , RegionFlags.Forest        , ProgressionPhase.General      , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ),
    LocationData("Complete the first wave"                              , RegionFlags.Forest        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 
    LocationData("Build a Stable Portal"                                , RegionFlags.Forest        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 
    LocationData("Get to wave 6"                                        , RegionFlags.Forest        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 
    LocationData("Fight the Wicked Witch"                               , RegionFlags.Forest        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.EXCLUDED), # <- Goal check, don't include progression items

    # Additional Archipelago quests
    LocationData("Get to wave 2"                                        , RegionFlags.Forest        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 
    LocationData("Get to wave 4"                                        , RegionFlags.Forest        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 
    LocationData("Get to wave 8"                                        , RegionFlags.Forest        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.NONE           , LocationProgressType.DEFAULT ), 

#endregion

#region The Island Quests

    # 'The Grand Scheme' Category
    LocationData("Build a Rowboat"                                     , RegionFlags.Island        , ProgressionPhase.General       , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Build a Cathedral on the Mainland"                   , RegionFlags.Island        , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Bring the Island Relic to the Cathedral"             , RegionFlags.Island        , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.EXCLUDED), # <- Summons Demon Lord immediately so shouldn't really contain any progression items
    LocationData("Kill the Demon Lord"                                 , RegionFlags.Island        , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.EXCLUDED), # <- Goal check, don't include progression items

    # 'Marooned' Category
    LocationData("Get 2 Bananas"                                       , RegionFlags.Island        , ProgressionPhase.General       , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Punch some Driftwood"                                , RegionFlags.Island        , ProgressionPhase.General       , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Have 3 Shells"                                       , RegionFlags.Island        , ProgressionPhase.General       , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Catch a Fish"                                        , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Make Rope"                                           , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Make a Fish Trap"                                    , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Make a Sail"                                         , RegionFlags.Island        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Build a Sloop"                                       , RegionFlags.Island        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),

    # 'Mystery of The Island' Category
    LocationData("Unlock all Island Packs"                             , RegionFlags.Island        , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Find a Treasure Map"                                 , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Find Treasure"                                       , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Forge Sacred Key"                                    , RegionFlags.Island        , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Open the Sacred Chest"                               , RegionFlags.Island        , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Kill the Kraken"                                     , RegionFlags.Island        , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    
    # 'Island Grub' Category
    LocationData("Make Sushi"                                          , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Cook Crab Meat"                                      , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Make Ceviche"                                        , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Make a Seafood Stew"                                 , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Make a Bottle of Rum"                                , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),

    # 'Island Ambitions' Category
    LocationData("Have 10 Shells"                                      , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Get a Villager Drunk"                                , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Make Sandstone"                                      , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Build a Mess Hall"                                   , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Build a Greenhouse"                                  , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Have a Poisoned Villager"                            , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Cure a Poisoned Villager"                            , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Build a Composter"                                   , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Bribe a Pirate Boat"                                 , RegionFlags.Island        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Befriend a Pirate"                                   , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Make a Gold Bar"                                     , RegionFlags.Island        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Make Glass"                                          , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    
    # 'Strengthen Up' Category
    LocationData("Train an Archer"                                     , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Break a Bottle"                                      , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Equip an Archer with a Quiver"                       , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.EXCLUDED), # <- Relies on RNG to drop Quiver, so don't include progression items
    LocationData("Make a Villager wear Crab Scale Armor"               , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Craft the Amulet of the Forest"                      , RegionFlags.Island        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),

    # Additional Archipelago Quests
    LocationData("Buy the On the Shore Pack"                           , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Buy the Island of Ideas Pack"                        , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Buy the Grilling and Brewing Pack"                   , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Buy the Island Insights Pack"                        , RegionFlags.Island        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Buy the Advanced Archipelago Pack"                   , RegionFlags.Island        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Buy the Enclave Explorers Pack"                      , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Buy 5 Island Booster Packs"                          , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Buy 10 Island Booster Packs"                         , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Buy 25 Island Booster Packs"                         , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),

    LocationData("Have 30 Shells"                                      , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Have 50 Shells"                                      , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    
    LocationData("Have 10 Cotton"                                      , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Fabric"                                      , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Glass"                                       , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Gold Bars"                                   , RegionFlags.Island        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Rope"                                        , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Sails"                                       , RegionFlags.Island        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),
    LocationData("Have 10 Sandstone"                                   , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.NONE         , LocationProgressType.DEFAULT ),

#endregion

#region Equipmentsanity Quests

    # Mainland
    LocationData("Make a Bone Spear"                                    , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Boomerang"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Club"                                          , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make Chainmail Armor"                                 , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make an Iron Shield"                                  , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Magic Blade"                                   , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Magic Ring"                                    , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Magic Staff"                                   , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Magic Tome"                                    , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Magic Wand"                                    , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Slingshot"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Spear"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Spiked Plank"                                  , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Sword"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make Throwing Stars"                                  , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Wooden Shield"                                 , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),

    # The Island
    LocationData("Make a Blunderbuss"                                   , RegionFlags.Island        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Bone Staff"                                    , RegionFlags.Island        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Crossbow"                                      , RegionFlags.Island        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Golden Chestplate"                             , RegionFlags.Island        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Mountain Amulet"                               , RegionFlags.Island        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),
    LocationData("Make a Wizard Robe"                                   , RegionFlags.Island        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Equipmentsanity  , LocationProgressType.DEFAULT ),

#endregion

#region Foodsanity Quests

    # Mainland
    LocationData("Cook a Stew"                                          , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Foodsanity       , LocationProgressType.DEFAULT ),
    LocationData("Make a Fruit Salad"                                   , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Foodsanity       , LocationProgressType.DEFAULT ),
    LocationData("Make a Milkshake"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Foodsanity       , LocationProgressType.DEFAULT ),

    # The Island
    LocationData("Make a Bottle of Water"                               , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Foodsanity       , LocationProgressType.DEFAULT ),
    LocationData("Make Grilled Fish"                                    , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Foodsanity       , LocationProgressType.DEFAULT ),
    LocationData("Make Tamago Sushi"                                    , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Foodsanity       , LocationProgressType.DEFAULT ),

#endregion

#region Locationsanity Quests

    # Mainland
    LocationData("Explore a Catacombs"                                  , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Locationsanity   , LocationProgressType.DEFAULT ),
    LocationData("Explore a Graveyard"                                  , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Locationsanity   , LocationProgressType.DEFAULT ),
    LocationData("Explore an Old Village"                               , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Locationsanity   , LocationProgressType.DEFAULT ),
    LocationData("Explore a Plains"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Locationsanity   , LocationProgressType.DEFAULT ),

    # The Island
    LocationData("Explore a Cave"                                       , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Locationsanity   , LocationProgressType.DEFAULT ),
    LocationData("Explore a Jungle"                                     , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Locationsanity   , LocationProgressType.DEFAULT ),

#endregion

#region Mobsanity Quests

    # Mainland
    LocationData("Kill a Bear"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Elf"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Elf Archer"                                  , RegionFlags.Mainland      , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Enchanted Shroom"                            , RegionFlags.Mainland      , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Feral Cat"                                    , RegionFlags.Mainland      , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Frog Man"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Ghost"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Giant Rat"                                    , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Giant Snail"                                  , RegionFlags.Mainland      , ProgressionPhase.PhaseThree    , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Goblin"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Goblin Archer"                                , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Goblin Shaman"                                , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Merman"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Mimic"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Mosquito"                                     , RegionFlags.All           , ProgressionPhase.General       , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Slime"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Small Slime"                                  , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Wolf"                                         , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),

    # The Dark Forest
    LocationData("Kill a Dark Elf"                                     , RegionFlags.Forest        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Ent"                                         , RegionFlags.Forest        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Ogre"                                        , RegionFlags.Forest        , ProgressionPhase.PhaseTwo      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    
    # The Island
    LocationData("Kill an Eel"                                         , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Momma Crab"                                   , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill an Orc Wizard"                                  , RegionFlags.Island_and_Forest, ProgressionPhase.General    , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Pirate"                                       , RegionFlags.Island_and_Forest, ProgressionPhase.General    , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Seagull"                                      , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Shark"                                        , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Snake"                                        , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Tentacle"                                     , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),
    LocationData("Kill a Tiger"                                        , RegionFlags.Island        , ProgressionPhase.PhaseOne      , CheckType.Check    , OptionFlags.Mobsanity    , LocationProgressType.DEFAULT ),

#endregion

#region Structuresanity Quests

    # Mainland
    LocationData("Build an Animal Pen"                                  , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Breeding Pen"                                 , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Butchery"                                     , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Coin Chest"                                   , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Crane"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Dustbin"                                      , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Garden"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Hotpot"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build an Iron Mine"                                   , RegionFlags.Mainland      , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Market"                                       , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Resource Chest"                               , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Sawmill"                                      , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Smelter"                                      , RegionFlags.Mainland      , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Stove"                                        , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a University"                                   , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Warehouse"                                    , RegionFlags.Mainland      , ProgressionPhase.PhaseThree   , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),

    # The Island
    LocationData("Build an Aquarium"                                    , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Distillery"                                   , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Frigate"                                      , RegionFlags.Island        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Gold Mine"                                    , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Lighthouse"                                   , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Magic Glue"                                   , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Resource Magnet"                              , RegionFlags.Island        , ProgressionPhase.PhaseTwo     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Sand Quarry"                                  , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Shell Chest"                                  , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),
    LocationData("Build a Wishing Well"                                 , RegionFlags.Island        , ProgressionPhase.PhaseOne     , CheckType.Check    , OptionFlags.Structuresanity  , LocationProgressType.DEFAULT ),

# endregion

#region Spendsanity

    # LocationData("Buy {count} Spendsanity Packs"                       , RegionFlags.Mainland      , CheckType.Check    , OptionFlags.Spendsanity   , LocationProgressType.DEFAULT ),

#endregion

#region Goal

    LocationData("Goal Complete"                                        , RegionFlags.All       , ProgressionPhase.PhaseFour       , CheckType.Goal     , OptionFlags.NONE          , LocationProgressType.DEFAULT ),

#endregion

]

base_id: int = 92000
current_id: int = base_id

name_to_id = {}

# Create locations lookup
for location in location_table:
    name_to_id[location.name] = current_id
    current_id += 1
        
    # # If location check is for Spendsanity, add it the maximum amount of times
    # if (location.option_flags is OptionFlags.Spendsanity):
    #     for x in range(1, 26):
    #         name_to_id[location.name.format(count=x)] = current_id
    #         current_id +=1
    # else:
    #     name_to_id[location.name] = current_id
    #     current_id += 1