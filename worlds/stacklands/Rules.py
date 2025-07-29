from typing import List
from BaseClasses import MultiWorld
from .Enums import ExpansionType, GoalFlags, RegionFlags, SpendsanityType
from .Locations import location_table
from .Options import StacklandsOptions
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import set_rule

class StacklandsLogic(LogicMixin):

    def sl_mainland_capacity(self, options: StacklandsOptions, player: int) -> bool:
        return (
            1000 if self.sl_has_idea("Shed", player) else 0 
            if options.board_expansion_mode.value is ExpansionType.Ideas else
            self.count("Mainland Board Expansion", player) * options.board_expansion_amount
        )

    def sl_can_expand_mainland(self, type: ExpansionType, player: int) -> bool:
        return (
            (type is ExpansionType.Ideas) and self.can_reach_location("Build a Shed", player)
            or (type is ExpansionType.Items and self.count("Mainland Board Expansion", player))
        )
    
    def sl_can_expand_island(self, type: ExpansionType, player: int) -> bool:
        return (
            (type is ExpansionType.Ideas) and self.can_reach_location("Build a Shed", player)
            or (type is ExpansionType.Items and self.count("Island Board Expansion", player))
        )

    def sl_can_start_mainland(self, player: int) -> bool:
        return self.sl_has_pack("Humble Beginnings", player)
    
    def sl_can_start_forest(self, player: int) -> bool:
        return self.sl_

    def sl_can_start_island(self, player: int) -> bool:
        return (
            self.can_reach_location("The Island", player)
            and self.sl_has_pack("On the Shore", player)
        )
    
    def sl_can_reach_all_quests(self, quests: List[str], player: int) -> bool:
        return all(self.can_reach_location(quest, player) for quest in quests)
    
    def sl_can_reach_any_quests(self, quests: List[str], player: int) -> bool:
        return any(self.can_reach_location(quest, player) for quest in quests)

    # Check if player has received booster pack
    def sl_has_idea(self, name: str, player: int) -> bool:
        return self.has("Idea: " + name, player)

    def sl_has_all_ideas(self, ideas: List[str], player: int) -> bool:
        return self.has_all(set(["Idea: " + idea for idea in ideas]), player)

    def sl_has_any_ideas(self, ideas: List[str], player: int) -> bool:
        return self.has_any(set(["Idea: " + idea for idea in ideas]), player)

    def sl_has_pack(self, name: str, player: int) -> bool:
        return self.has(name + " Booster Pack", player)

    def sl_has_all_packs(self, packs: List[str], player: int) -> bool:
        return self.has_all(set([pack + " Booster Pack" for pack in packs]), player)

    def sl_has_any_packs(self, packs: List[str], player: int) -> bool:
        return self.has_any(set([pack + " Booster Pack" for pack in packs]), player)
    
    def sl_has_count(self, name: str, count: int, player: int) -> bool:
        return self.count(name, player) >= count
    
    # NOTE: Attempting a phased ideas / packs release to attempt to better spread ideas and packs throughout the run in a 'logical' order.

    def sl_phase_zero(self, player: int) -> bool:
        return self.sl_has_pack("Humble Beginnings", player)
    
    def sl_phase_one(self, options: StacklandsOptions, player: int) -> bool:
        return (self.sl_phase_zero(player) and
                self.sl_has_all_ideas(["Growth", "Stick"], player)) # <- Player has access to simple ideas
    
    def sl_phase_two(self, options: StacklandsOptions, player: int) -> bool:
        return (self.sl_phase_one(options, player) and
                (
                    self.sl_has_all_ideas(["Campfire", "Shed"], player)             # <- Player has access to basic ideas
                    and (                                                           # AND
                        options.board_expansion_mode.value is ExpansionType.Ideas   # Board expansion mode is 'ideas' 
                        or self.sl_has_count("Board Expansion", 1, player)          # OR Player has at least one 'Board Expansion' item
                    )
                ) and
                self.sl_has_pack("Seeking Wisdom", player)) # <- Player has access to more basic resources
    
    def sl_phase_three(self, options: StacklandsOptions, player: int) -> bool:
        return (self.sl_phase_two(options, player) and
                self.sl_has_any_ideas(["Slingshot", "Spear"], player) and # <- Player can make at least one basic weapon
                self.sl_has_all_ideas(["House", "Offspring"], player) and # <- Player can begin training multiple villagers
                self.sl_has_all_packs(["Explorers", "Reap & Sow"], player)) # <- Player can find/fight enemies and gather more food
    
    def sl_phase_four(self, options: StacklandsOptions, player: int) -> bool:
        return (self.sl_phase_three(options, player) and
                self.sl_has_all_ideas(["Iron Mine", "Lumber Camp", "Quarry"], player) and                       # Player can create infinite basic resources
                self.sl_has_pack("Logic and Reason", player)                                                    # AND Player has access to additional resources
                and (                                                                                           # AND
                    options.board_expansion_mode.value is ExpansionType.Ideas                                   # Board Expansion Mode is 'Ideas'
                    or self.sl_has_count("Board Expansion", options.board_expansion_count.value / 3, player)    # Player has at least a third of board expansions
                ))
    
    def sl_phase_five(self, options: StacklandsOptions, player: int) -> bool:
        return (self.sl_phase_four(options, player) and
                self.sl_has_all_ideas(["Brick", "Iron Bar", "Plank", "Smelter", "Temple"], player) and  # Player has access to advanced resources
                self.sl_has_all_packs(["Curious Cuisine", "The Armory"], player))                       # AND Player has increased access to advanced resources
    
    def sl_phase_six(self, options: StacklandsOptions, player: int) -> bool:
        return (self.sl_phase_five(options, player) and
                self.sl_has_all_ideas(["Smithy", "Sword"], player) and                                          # Player can make an advanced weapon
                self.sl_has_pack("Order and Structure", player)                                                 # AND Player can find/fight harder enemies
                and (                                                                                           # AND
                    options.board_expansion_mode.value is ExpansionType.Ideas                                   # Board Expansion Mode is 'Ideas'
                    or self.sl_has_count("Board Expansion", options.board_expansion_count.value / 2, player)    # Player has at least half of board expansions
                ))
 
# Set all region and location rules
def set_rules(world: MultiWorld, player: int):

    # Get relevant options
    options = world.worlds[player].options

    # Calculate board options
    mainland_selected: bool = bool(options.boards.value & RegionFlags.Mainland)
    forest_selected: bool = bool(options.boards.value & RegionFlags.Forest)
    island_selected: bool = bool(options.boards.value & RegionFlags.Island)

    # Calculate goal options
    bosses_goal: bool = bool(options.goal.value & GoalFlags.Bosses)
    quests_goal: bool = bool(options.goal.value & GoalFlags.Quests)

    # Calculate sanity options
    mobsanity_selected: bool = options.mobsanity.value
    packsanity_selected: bool = options.packsanity.value
    spendsanity_selected: bool = options.spendsanity.value is not SpendsanityType.Off

    # Calculate other options
    expansion_items_selected: bool = options.board_expansion_mode.value is ExpansionType.Items
    pausing_selected: bool = options.pausing.value

#region 'Entrances'

    # Entrances
    set_rule(world.get_entrance("Start", player), lambda state: True)

    set_rule(world.get_entrance("Strange Portal", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player has access to basic equipment to fight mobs in Dark Forest
    
    set_rule(world.get_entrance("Rowboat", player),
             lambda state:
                state.can_reach_location("Build a Rowboat")            # Player can build a Rowboat
                and state.can_reach_location("Get a Second Villager")) # AND player can have more than one villager (one must stay in Mainland to travel)
    
#endregion

    #region 'Mainland' Quests

    if mainland_selected:

        #region 'Welcome' Quests

        set_rule(world.get_location("Open the Booster Pack", player), 
                 lambda state: True)    # Player can perform immediately

        set_rule(world.get_location("Drag the Villager on top of the Berry Bush", player),
                 lambda state: True)    # Player can perform immediately

        set_rule(world.get_location("Mine a Rock using a Villager", player),
                 lambda state: True)    # Player can perform immediately

        set_rule(world.get_location("Sell a Card", player),
                 lambda state: True)    # Player can perform immediately

        set_rule(world.get_location("Buy the Humble Beginnings Pack", player),
                 lambda state: state.sl_can_start_mainland(player)) # Player can start Mainland

        set_rule(world.get_location("Harvest a Tree using a Villager", player),
                lambda state: state.sl_can_start_mainland(player))  # Player can start Mainland

        set_rule(world.get_location("Make a Stick from Wood", player),
                lambda state: 
                    state.sl_can_start_mainland(player)     # Player can start Mainland
                    and state.sl_has_idea("Stick", player)) # AND has 'Stick' idea

        # Set this rule only if Pausing is enabled
        if pausing_selected:
            set_rule(world.get_location("Pause using the play icon in the top right corner", player),
                    lambda state: True) # Player can perform immediately

        set_rule(world.get_location("Grow a Berry Bush using Soil", player),
                 lambda state: 
                    state.sl_can_start_mainland(player)      # Player can start Mainland
                    and state.sl_has_idea("Growth", player)) # AND has 'Growth' idea

        set_rule(world.get_location("Build a House", player),
                 lambda state: 
                    state.sl_can_start_mainland(player)     # Player can start Mainland
                    and state.sl_has_idea("House", player)) # AND has 'Growth' idea
        
        set_rule(world.get_location("Get a Second Villager", player),
                 lambda state: state.sl_can_start_mainland(player)) # Player can start Mainland

        set_rule(world.get_location("Create Offspring", player),
                 lambda state:
                    state.can_reach_location("Build a House", player)   # Player can build a House
                    and state.sl_has_idea("Offspring", player))         # AND has 'Offspring' idea

        #endregion

        #region 'The Grand Scheme' Quests

        set_rule(world.get_location("Unlock all Packs", player),
                 lambda state:
                    state.sl_can_start_mainland(player)                                 # Player can start Mainland
                    and state.count_group("All Mainland Booster Packs", player) == 8)   # AND has all mainland booster packs

        set_rule(world.get_location("Get 3 Villagers", player),
                 lambda state:
                    state.sl_can_expand_mainland(player, options.board_expansion_mode.value, player) # Player can expand mainland board
                    and state.can_reach_location("Create Offspring", player))                        # AND can create Offspring

        set_rule(world.get_location("Find the Catacombs", player),
                 lambda state:
                    state.can_reach_location("Get a Second Villager", player)   # Player can get a second villager
                    and state.sl_has_pack("Explorers", player))                 # AND has the Explorers pack

        set_rule(world.get_location("Find a mysterious artifact", player),
                 lambda state:
                  state.can_reach_location("Find the Catacombs", player))   # Player can find the Catacombs

        set_rule(world.get_location("Build a Temple", player),
                 lambda state:
                    state.can_reach_location("Get an Iron Bar", player) # Player can make Iron Bar / Plank / Brick / Smelter
                    and state.sl_has_idea("Temple", player))            # AND has 'Temple' idea

        set_rule(world.get_location("Bring the Goblet to the Temple", player),
                 lambda state:
                    state.can_reach_location("Find a mysterious artifact", player)  # Player can find the Golden Goblet
                    and state.can_reach_location("Build a Temple", player))         # AND can build a Temple

        set_rule(world.get_location("Kill the Demon", player),
                 lambda state:
                    state.sl_can_reach_all_quests([         
                        "Bring the Goblet to the Temple",   # Player can bring the goblet to the temple
                        "Get 3 Villagers",                  # AND can have multiple villagers
                        "Kill a Skeleton",                  # AND has access to weapons
                        "Cook an Omelette"])                # AND has access to cooking
                    and (
                        not expansion_items_selected        # AND expansion mode is 'items' OR player has half their board expansions
                        or state.count("Mainland Board Expansion", player) >= (options.board_expansion_count / 2)
                    ))
        #endregion

        #region 'Power & Skill' Quests

        set_rule(world.get_location("Train Militia", player),
                 lambda state:
                    state.can_reach_location("Make a Stick from Wood", player)  # Player can make a Stick
                    and state.sl_has_any_ideas(["Slingshot", "Spear"], player)) # AND can create a basic Militia weapon

        set_rule(world.get_location("Kill a Rat", player),
                lambda state: state.sl_can_start_mainland(player))  # Player can start Mainland (found in Humble Beginnings)

        set_rule(world.get_location("Kill a Skeleton", player),
                 lambda state:
                    state.can_reach_location("Have a Villager with Combat Level 20", player)    # Player can create basic weapons & shield
                    and state.sl_has_any_packs([ "Explorers", "The Armory" ], player))          # AND player has a pack containing 'Skeleton'

        #endregion

        #region 'Strengthen Up' Quests

        # set_rule(world.get_location("Train an Archer", player),
        #         lambda state: state.sl_phase_three(options, player)) # <- Player can find/fight enemies to drop a Bow

        set_rule(world.get_location("Make a Villager wear a Rabbit Hat", player),
                 lambda state: state.sl_can_start_mainland(player))   # Player can find Rabbit in Humble Beginnings

        set_rule(world.get_location("Build a Smithy", player),
                 lambda state:
                    state.can_reach_location("Get an Iron Bar", player) # Player can create Iron Bars
                    and state.sl_has_idea("Smithy", player))            # AND has 'Smithy' idea

        set_rule(world.get_location("Train a Wizard", player),
                 lambda state:
                    state.can_reach_location("Make a Stick from Wood", player)  # Player can make a Stick
                    and state.sl_has_pack("Explorers", player)                  # AND has a pack containing Magic Dust
                    and state.sl_has_idea("Magic Wand", player))                # AND has 'Magic Wand' idea
    
        # set_rule(world.get_location("Equip an Archer with a Quiver", player),
        #         lambda state: state.sl_phase_three(options, player)) # <- Player can find/fight enemies to drop a Quiver

        set_rule(world.get_location("Have a Villager with Combat Level 20", player),
                 lambda state:
                    state.sl_can_reach_any_quests(["Train Militia", "Train a Wizard"], player)  # Player can create basic weapons
                    and state.sl_has_all_ideas([ "Plank", "Stick", "Wooden Shield" ], player))  # AND can create a Wooden Shield

        set_rule(world.get_location("Train a Ninja", player),
                 lambda state: 
                    state.can_reach_location("Build a Smithy", player)  # Player can build a Smithy
                    and state.sl_has_idea("Throwing Stars", player))    # AND has 'Throwing Stars' idea

        #endregion

        #region 'Potluck' Quests

        set_rule(world.get_location("Start a Campfire", player),
                 lambda state:
                    state.can_reach_location("Make a Stick from Wood", player)  # Player can make a Stick
                    and state.sl_has_idea("Campfire", player))                  # AND has the 'Campfire' idea

        set_rule(world.get_location("Cook Raw Meat", player),
                 lambda state:
                    state.can_reach_location("Start a Campfire", player)    # Player can make a Campfire
                    and state.sl_has_idea("Cooked Meat", player))           # AND has the 'Cooked Meat' idea

        set_rule(world.get_location("Cook an Omelette", player),
                lambda state:
                    state.can_reach_location("Cook Raw Meat", player)   # Player can make a campfire
                    and state.sl_has_pack("Reap & Sow", player)         # AND has the 'Reap & Sow' pack
                    and state.sl_has_idea("Omelette", player))          # AND has the 'Omelette' idea

        set_rule(world.get_location("Cook a Frittata", player),
                lambda state:
                    state.can_reach_location("Cook an Omelette", player)    # Player can make an Omelette
                    and state.sl_has_pack("Curious Cuisine", player)        # AND has the 'Curious Cuisine' pack
                    and state.sl_has_idea("Frittata", player))              # AND has the 'Frittata' idea

        #endregion

        #region 'Discovery' Quests

        set_rule(world.get_location("Explore a Forest", player),
                 lambda state:
                    state.sl_can_start_mainland(player)                                     # Player can start Mainland
                    and state.sl_has_all_packs(["Seeking Wisdom", "Explorers"], player))    # AND has pack containing Forest

        set_rule(world.get_location("Explore a Mountain", player),
                 lambda state: state.can_reach_location("Explore a Forest", player)) # Player has a pack containing Mountain

        set_rule(world.get_location("Open a Treasure Chest", player),
                 lambda state: state.can_reach_location("Explore a Forest", player)) # Player has a pack containing Treasure Chest

        set_rule(world.get_location("Get a Dog", player),
                 lambda state: state.can_reach_location("Explore a Forest", player)) # Player has packs containing Wolf and Bone

        set_rule(world.get_location("Find a Graveyard", player),
                 lambda state: state.can_reach_location("Create Offspring", player)) # Player can create Corpses to make Graveyard

        set_rule(world.get_location("Train an Explorer", player),
                 lambda state:
                    state.can_reach_location("Explore a Forest", player)) # Player can find a Map from Enemies / Old Tome / Travelling Cart

        set_rule(world.get_location("Buy something from a Travelling Cart", player),
                 lambda state: state.can_reach_location("Reach Moon 24", player))   # Player can get Travelling Cart from Moon 19


        #endregion

        #region 'Ways and Means' Quests

        set_rule(world.get_location("Have 5 Ideas", player),
                 lambda state: state.count_group("All Ideas", player) >= 5)

        set_rule(world.get_location("Have 10 Ideas", player),
                 lambda state: state.count_group("All Ideas", player) >= 10)

        set_rule(world.get_location("Have 10 Stone", player),
                 lambda state: state.sl_can_start_mainland(player)) # Player can start Mainland

        set_rule(world.get_location("Have 10 Wood", player),
                 lambda state: state.sl_can_start_mainland(player)) # Player can start Mainland

        set_rule(world.get_location("Get an Iron Bar", player),
                 lambda state:
                    state.sl_can_start_mainland(player)                                             # Player can start Mainland
                    and state.sl_has_pack("Seeking Wisdom", player)                                 # AND has Seeking Wisdom pack
                    and state.sl_has_all_ideas(["Brick", "Plank", "Iron Bar", "Smelter"], player))  # AND has ideas to make Brick / Plank / Iron Bar / Smelter

        set_rule(world.get_location("Have 5 Food", player),
                 lambda state: state.sl_can_start_mainland(player)) # Player can start Mainland

        set_rule(world.get_location("Have 10 Food", player),
                  lambda state: state.can_reach_location("Have 5 Food", player)) # Player can get at least 5 food

        set_rule(world.get_location("Have 20 Food", player),
                 lambda state:
                    state.can_reach_location("Have 10 Food", player)        # Player can get at least 10 food
                    and state.sl_has_pack("Reap & Sow", player)             # AND has Reap & Sow pack
                    and state.sl_mainland_capacity(options, player) >= 5)   # AND has extra capacity for food items     

        set_rule(world.get_location("Have 50 Food", player),
                 lambda state:
                    state.can_reach_location("Have 20 Food", player)         # Player can get at least 10 food
                    and state.sl_has_pack("Curious Cuisine", player)         # AND has Curious Cuisine pack
                    and state.sl_mainland_capacity(options, player) >= 12)   # AND has extra capacity for food items     
        
        set_rule(world.get_location("Have 10 Coins", player),
                 lambda state: state.sl_can_start_mainland(player)) # Player can start Mainland

        set_rule(world.get_location("Have 30 Coins", player),
                 lambda state:
                    state.can_reach_location("Have 10 Coins", player)   # Player can get at least 10 coins
                    and state.sl_has_pack("Seeking Wisdom", player))    # AND has Seeking Wisdom pack

        set_rule(world.get_location("Have 50 Coins", player),
                 lambda state: state.can_reach_location("Have 30 Coins", player))    # Player can already get at least 30 coins

        #endregion

        #region 'Construction' Quests

        set_rule(world.get_location("Have 3 Houses", player),
                 lambda state: state.can_reach_location("Build a House", player)) # Player can build at least one House

        set_rule(world.get_location("Build a Shed", player),
                 lambda state:
                    state.can_reach_location("Make a Stick from Wood", player)    # Player can make a Stick
                    and state.sl_has_idea("Shed", player))                        # AND has 'Shed' idea


        set_rule(world.get_location("Build a Quarry", player),
                 lambda state:
                    state.sl_can_start_mainland(player)         # Player can start Mainland
                    and state.sl_has_idea("Quarry", player))    # AND has 'Quarry' idea

        set_rule(world.get_location("Build a Lumber Camp", player),
                 lambda state:
                    state.sl_can_start_mainland(player)             # Player can start Mainland
                    and state.sl_has_idea("Lumber Camp", player))   # AND has 'Lumber Camp' idea

        set_rule(world.get_location("Build a Farm", player),
                 lambda state:
                    state.sl_can_start_mainland(player)                             # Player can start Mainland
                    and state.sl_has_pack("Reap & Sow", player)                     # AND has Reap & Sow pack
                    and state.sl_has_all_ideas(["Brick", "Farm", "Plank"], player)) # AND has Brick / Farm / Plank ideas

        set_rule(world.get_location("Build a Brickyard", player),
                 lambda state:
                    state.can_reach_location("Get an Iron Bar", player) # Player can make Iron Bar
                    and state.sl_has_idea("Brickyard", player))         # AND has 'Brickyard' idea

        set_rule(world.get_location("Sell a Card at a Market", player),
                 lambda state:
                    state.sl_can_start_mainland(player)                                 # Player can start Mainland
                    and state.sl_has_pack("Seeking Wisdom", player)                     # AND has Seeking Wisdom pack
                    and state.sl_has_all_ideas(["Brick", "Market", "Plank"], player))   # AND has Brick / Farm / Plank ideas

        #endregion

        #region 'Longevity' Quests

        set_rule(world.get_location("Reach Moon 6", player),
                lambda state: state.sl_phase_one(options, player)) # <- Player is able to reach Moon 12

        set_rule(world.get_location("Reach Moon 12", player),
                lambda state: state.sl_phase_two(options, player)) # <- Player is able to reach Moon 12

        set_rule(world.get_location("Reach Moon 24", player),
                lambda state: state.sl_phase_four(options, player)) # <- Player is able to reach Moon 24

        set_rule(world.get_location("Reach Moon 36", player),
                lambda state: state.sl_phase_six(options, player)) # <- Player is able to reach Moon 36

        #endregion

    #endregion

    #region 'The Dark Forest' Quests

    if forest_selected:

        set_rule(world.get_location("Find the Dark Forest", player),
                lambda state: state.can_reach_region("The Dark Forest", player)) # <- Player has access to Basic Weapons / Offspring / Food

        set_rule(world.get_location("Complete the first wave", player),
                lambda state: state.can_reach_region("The Dark Forest", player)) # <- Player has access to Basic Weapons / Offspring / Food

        set_rule(world.get_location("Build a Stable Portal", player),
                lambda state: state.sl_has_all_ideas(["Brick", "Stable Portal"], player) and # <- Player has idea for Stable Portal
                              state.can_reach_region("The Dark Forest", player))  # <- Player has Idea for Stable Portal

        set_rule(world.get_location("Get to Wave 6", player),
                lambda state: state.sl_phase_six(options, player) and # <- Player has access to advanced weapon
                              state.can_reach_region("The Dark Forest", player))  # <- Player can reach The Dark Forest
        
        set_rule(world.get_location("Fight the Wicked Witch", player),
                lambda state: state.sl_phase_six(options, player) and # <- Player has access to advanced weapon
                              state.can_reach_region("The Dark Forest", player))  # <- Player can reach The Dark Forest

    #endregion

    #region 'The Island' Quests

    if island_selected:

        #region 'The Grand Scheme' Category

        set_rule(world.get_location("Build a Rowboat", player),
                 lambda state:
                    state.sl_can_reach_all_quests([ "Get an Iron Bar" ], player) # Player can make Iron Bar / Brick / Plank / Smelter
                    and state.sl_has_idea("Rowboat", player))                    # AND has the 'Rowboat' idea

        set_rule(world.get_location("Build a Cathedral on the Mainland", player),
                 lambda state:
                    state.sl_can_reach_all_quests([ "Make a Gold Bar", "Make Glass" ], player)        # AND player can make Glass / Gold Bar / Plank / Brick / Smelter
                    and state.sl_has_idea("Cathedral", player))                                       # AND has the 'Cathedral' idea
        
        set_rule(world.get_location("Bring the Island Relic to the Cathedral", player),
                 lambda state:
                    state.sl_can_reach_all_quests([ "Build a Cathedral on the Mainland", "Open the Sacred Chest" ], player)) # Player can make Cathedral and open the Sacred Chest
        
        set_rule(world.get_location("Kill the Demon Lord", player),
                 lambda state:
                    state.can_reach_location("Bring the Island Relic to the Cathedral", player)) # Player has both the Relic and Cathedral

        #endregion

        #region 'Marooned' Category

        set_rule(world.get_location("Get 2 Bananas", player),
                 lambda state:
                    state.can_reach_region("The Island", player))   # Player can reach The Island 
        
        set_rule(world.get_location("Punch some Driftwood", player),
                 lambda state:
                    state.can_reach_region("The Island", player))   # Player can reach The Island 
        
        set_rule(world.get_location("Have 3 Shells", player),
                 lambda state:
                    state.can_reach_region("The Island", player))   # Player can reach The Island 
        
        set_rule(world.get_location("Catch a Fish", player),
                 lambda state:
                    state.sl_can_start_island(player))              # Player can start The Island 
        
        set_rule(world.get_location("Make Rope", player),
                 lambda state:
                    state.can_reach_island(player)                  # Player can start The Island
                    and state.sl_has_idea("Rope", player))          # AND has the 'Rope' idea
        
        set_rule(world.get_location("Make a Fish Trap", player),
                 lambda state:
                    state.can_reach_location("Make Rope", player)   # Player can make Rope
                    and state.sl_has_idea("Fish Trap", player))     # AND has the 'Fish Trap' idea
        
        set_rule(world.get_location("Make a Sail", player),
                 lambda state:
                    state.can_reach_location("Make Rope", player)               # Player can make Rope
                    and state.sl_has_all_ideas([ "Fabric", "Sail" ], player))   # AND has the 'Fabric' and 'Sail' ideas

        set_rule(world.get_location("Build a Sloop", player),
                 lambda state:
                    state.can_reach_location("Make a Sail", player) # Player can make a Sail
                    and state.sl_has_idea("Sloop", player))         # AND has the 'Sloop' idea
        #endregion

        #region 'Mystery of The Island' Category

        set_rule(world.get_location("Unlock all Island Packs", player),
                 lambda state:
                    state.sl_can_start_island(player)                               # Player can start The Island 
                    and state.count_group("All Island Booster Packs", player) == 6) # AND has all booster packs
        
        set_rule(world.get_location("Find a Treasure Map", player),
                 lambda state:
                    state.sl_can_start_island(player)                   # Player can start The Island
                    and state.sl_has_pack("Enclave Explorers", player)) # AND has a pack containing Cave

        set_rule(world.get_location("Find Treasure", player),
                 lambda state:
                    state.can_reach_location("Find a Treasure Map", player)) # Player can find the treasure map
        
        set_rule(world.get_location("Forge Sacred Key", player),
                 lambda state:
                    state.sl_can_reach_all_quests([ "Make Glass", "Make a Gold Bar" ], player)   # Player can make Glass and Gold Bars
                    and state.sl_has_idea("Sacred Key", player))                                    # AND has the 'Sacred Key' idea
        
        set_rule(world.get_location("Open the Sacred Chest", player),
                 lambda state:
                    state.sl_can_reach_all_quests([ "Forge Sacred Key", "Find Treasure" ], player))   # Player can forge key and find the chest
        
        set_rule(world.get_location("Kill the Kraken", player),
                 lambda state:
                    state.can_reach_location("Open the Sacred Chest", player))  # Player can open the chest

        #endregion

        #region 'Island Grub'

        set_rule(world.get_location("Make Sushi", player),
                 lambda state:
                    state.state.can_reach_island(player)            # Player can start The Island
                    and state.sl_has_idea("Sushi", player))         # AND has the 'Sushi' idea
        
        set_rule(world.get_location("Cook Crab Meat", player),
                 lambda state:
                    state.state.can_reach_island(player)                   # Player can start The Island
                    and state.sl_has_pack("Grilling and Brewing", player)  # AND has pack containing Crab
                    and state.sl_has_idea("Campfire", player))             # AND player has 'Campfire' idea

        set_rule(world.get_location("Make Ceviche", player),
                 lambda state:
                    state.state.can_reach_island(player)                                                # Player can start The Island
                    and state.sl_has_any_packs([ "Grilling and Brewing", "Island Insights" ], player)   # AND has a pack containing Lime
                    and state.sl_has_idea("Ceviche", player))                                           # AND has the 'Ceviche' idea

        set_rule(world.get_location("Make a Seafood Stew", player),
                 lambda state:
                    state.state.can_reach_island(player)                                                # Player can start The Island
                    and state.sl_has_any_packs([ "Grilling and Brewing", "Island Insights" ], player)   # AND has a pack containing Crab and Chili Pepper
                    and state.sl_has_all_ideas(["Campfire", "Seafood Stew" ], player))                  # AND has 'Campfire' and 'Seafood Stew' ideas
        
        set_rule(world.get_location("Make a Bottle of Rum", player),
                 lambda state:
                    state.sl_can_reach_locations("Make Glass", player)                                  # Player can make glass
                    and state.sl_has_any_packs([ "Advanced Archipelago", "Enclave Explorers" ], player) # AND has a pack containing 'Spring'
                    and state.sl_has_all_ideas([ "Bottle of Rum", "Distillery", "Stove" ], player))     # AND has 'Bottle of Rum', 'Distillery' and 'Stove' ideas
        
        #endregion

        #region 'Island Ambitions' Category

        set_rule(world.get_location("Have 10 Shells", player),
                 lambda state:
                    state.sl_can_start_island(player)               # Player can start The Island
                    and state.sl_has_pack("On the Shore", player))  # AND has the 'On the Shore' pack
        
        set_rule(world.get_location("Get a Villager Drunk", player),
                 lambda state:
                    state.can_reach_location("Make a Bottle of Rum", player)) # Player can make a bottle of rum
        
        set_rule(world.get_location("Make Sandstone", player),
                 lambda state:
                    state.sl_can_start_island(player)               # Player can start The Island
                    and state.sl_has_idea("Sandstone", player))     # AND has the 'Sandstone' idea
        
        set_rule(world.get_location("Build a Mess Hall", player),
                 lambda state:
                    state.sl_can_start_island(player)                                   # Player can start The Island
                    and state.sl_has_all_ideas([ "Campfire", "Mess Hall" ], player))    # AND has the 'Campfire' and 'Mess Hall' ideas
        
        set_rule(world.get_location("Build a Greenhouse", player),
                 lambda state:
                    state.sl_can_reach_all_quests([ "Build a Composter", "Make Glass" ], player)  # Player can make Composter / Glass / Iron Bars
                    and state.sl_has_idea("Greenhouse", player))                                                     # AND has the 'Greenhouse' idea
        
        set_rule(world.get_location("Have a Poisoned Villager", player),
                 lambda state:
                    state.sl_can_start_island(player)                      # Player can start The Island
                    and state.sl_has_pack("Enclave Explorers", player))    # AND has a pack that contains a Snake
        
        set_rule(world.get_location("Cure a Poisoned Villager", player),
                 lambda state:
                    state.can_reach_location("Have a Poisoned Villager", player)    # Player can poison a villager
                    and state.sl_has_all_ideas([ "Campfire", "Charcoal" ], player)) # AND has the 'Campfire' and 'Charcoal' ideas

        set_rule(world.get_location("Build a Composter", player),
                 lambda state:
                    state.sl_can_start_island(player)               # Player can start The Island
                    and state.sl_has_idea("Composter", player))     # AND has the 'Composter' idea
        
        set_rule(world.get_location("Bribe a Pirate Boat", player),
                 lambda state:
                    state.can_reach_location("Build a Sloop", player))   # Player can build a Sloop (to bring coins back)
        
        set_rule(world.get_location("Befriend a Pirate", player),
                 lambda state:
                    state.sl_can_start_island(player)                                                       # Player can start The Island
                    and state.sl_has_any_packs([ "Enclave Explorers", "Grilling and Brewing" ], player))    # AND has a pack containing Parrot
        
        set_rule(world.get_location("Make a Gold Bar", player),
                 lambda state:
                    state.sl_can_start_island(player)                                                       # Player can start The Island
                    and state.sl_has_any_packs([ "Advanced Archipelago", "Enclave Explorers" ], player)     # AND has a pack containing Gold Deposit
                    and state.sl_has_idea("Gold Bar", player))                                              # AND player has 'Gold Bar' idea

        set_rule(world.get_location("Make Glass", player),
                 lambda state:
                    state.sl_can_start_island(player)                                                       # Player can start The Island
                    and state.sl_has_idea("Glass", player))                                                 # AND player has 'Glass' idea

        #endregion

        #region 'Strengthen Up' Category

        set_rule(world.get_location("Train an Archer", player),
                 lambda state:
                    state.can_reach_location("Make Rope", player)   # Player can make Rope
                    and state.sl_has_idea("Bow", player))           # AND has the 'Bow' idea
        
        set_rule(world.get_location("Break a Bottle", player),
                 lambda state:
                    state.sl_can_start_island(player)                                                       # Player can start The Island
                    and state.sl_has_all_ideas([ "Campfire", "Broken Bottle", "Empty Bottle" ], player))    # AND has 'Campfire', 'Broken Bottle' and 'Empty Bottle' ideas
        
        set_rule(world.get_location("Equip an Archer with a Quiver", player),
                 lambda state:
                    state.sl_can_reach_all_quests([ "Train an Archer", "Train Militia" ], player))          # Player can train an Archer and fight mobs to gain Quiver
        
        set_rule(world.get_location("Make a Villager wear Crab Scale Armor", player),
                 lambda state:
                    state.sl_can_start_island(player)                                                   # Player can start The Island
                    and state.sl_has_pack("Grilling and Brewing", player)                               # AND player has pack containing Crab
                    and state.sl_can_reach_any_quests([ "Train an Archer", "Train Militia" ], player))  # AND player can fight Melee mobs
        
        set_rule(world.get_location("Craft the Amulet of the Forest", player),
                 lambda state:
                    state.sl_can_reach_all_quests([ "Build a Smithy", "Make a Gold Bar" ], player)      # Player can build a Smithy and make Gold Bars
                    and state.sl_has_idea("Forest Amulet", player))                                     # AND has 'Forest Amulet' idea

        #endregion

    #endregion

    #region 'Mobsanity' Quests

    if mobsanity_selected:

        set_rule(world.get_location("Kill a Bear", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Bear in Explorers or Strange Portals from Moon 16

        set_rule(world.get_location("Kill an Elf", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Elf in Strange Portals from Moon 24 (or Dark Forest from Wave 1)

        set_rule(world.get_location("Kill an Elf Archer", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Elf Archer in Strange Portals from Moon 24 (or Dark Forest from Wave 1)

        set_rule(world.get_location("Kill an Enchanted Shroom", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Enchanted Shroom in Strange Portals from Moon 24 (or Dark Forest from Wave 1)

        set_rule(world.get_location("Kill a Feral Cat", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Enchanted Shroom in Explorers / Strange Portals from Moon 24 (or Dark Forest from Wave 1)

        set_rule(world.get_location("Kill a Frog Man", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Frog Man in Explorers or Strange Portals from Moon 16

        set_rule(world.get_location("Kill a Ghost", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Ghost in Strange Portals from Moon 24 (or Dark Forest from Wave 1)

        set_rule(world.get_location("Kill a Giant Rat", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Giant Rat in Explorers or Strange Portals from Moon 16

        set_rule(world.get_location("Kill a Giant Snail", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Giant Snail in Strange Portals from Moon 24 (or Dark Forest from Wave 1)

        set_rule(world.get_location("Kill a Goblin", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Goblin in Explorers or Strange Portals from Moon 12

        set_rule(world.get_location("Kill a Goblin Archer", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Goblin Archer in Explorers or Strange Portals from Moon 12

        set_rule(world.get_location("Kill a Goblin Shaman", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Goblin Shaman in Explorers or Strange Portals from Moon 16

        set_rule(world.get_location("Kill a Merman", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Merman in Strange Portals from Moon 24 (or Dark Forest from Wave 1)

        set_rule(world.get_location("Kill a Mimic", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Merman in Explorers / Strange Portals from Moon 16 (or Dark Forest from Wave 1)

        set_rule(world.get_location("Kill a Mosquito", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Merman in Strange Portals from Moon 24 (or Dark Forest from Wave 1)

        set_rule(world.get_location("Kill a Slime", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Merman in Strange Portals from Moon 16 (or Dark Forest from Wave 1)

        set_rule(world.get_location("Kill a Small Slime", player),
                 lambda state: state.can_reach_location("Kill a Slime", player)) # <- Found from killing a Slime

        set_rule(world.get_location("Kill a Snake", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Snake in Explorers (Cave)

        set_rule(world.get_location("Kill a Tiger", player),
                 lambda state: state.sl_phase_three(options, player)) # <- Player has basic weapon / food / offspring and can find Snake in Explorers (Cave)

        set_rule(world.get_location("Kill a Wolf", player),
                 lambda state: state.can_reach_location("Get a Dog", player)) # <- Player is able to find and fight a Wolf instead of giving it a Bone

        # Only apply these rules if The Dark Forest is enabled
        if forest_selected:

            set_rule(world.get_location("Kill a Dark Elf", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Only found in The Dark Forest from Wave 4
            
            set_rule(world.get_location("Kill an Ent", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Only found in The Dark Forest from Wave 4
            
            set_rule(world.get_location("Kill an Ogre", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Only found in The Dark Forest from Wave 4

            set_rule(world.get_location("Kill an Orc Wizard", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Only found in The Dark Forest from Wave 4

        # Only apply these rules if The Island is enabled 
        if island_selected:

            set_rule(world.get_location("Kill an Eel", player),     
                lambda state:
                    state.can_reach_location("Make a Fish Trap", player)) # Found using Fish Trap with a Banana
            
            set_rule(world.get_location("Kill a Momma Crab", player),   
                lambda state:
                    state.can_reach_location("Make a Villager wear Crab Scale Armor", player)) # Found after killing 3 crabs

            set_rule(world.get_location("Kill a Seagull", player), 
                 lambda state:
                    state.sl_can_start_island(player))   # Found in 'On the Shore' pack
            
            set_rule(world.get_location("Kill a Shark", player),
                 lambda state:
                    state.can_reach_location("Make a Fish Trap", player)) # Found using Fish Trap with Raw Meat
            
            set_rule(world.get_location("Kill a Tentacle", player),
                 lambda state:
                    state.can_reach_location("Open the Sacred Chest", player)) # Found after opening sacred chest
        
        # Apply these rules if either Forest or Island are enabled
        if forest_selected or island_selected:

            set_rule(world.get_location("Kill a Pirate", player),   
                 lambda state:
                    (forest_selected and state.can_reach_location("Get to Wave 6", player))             # Found after Dark Forest Wave 4
                    or (island_selected and state.can_reach_location("Bribe a Pirate Boat", player)))   # OR on Pirate Boat

    #endregion

    #region 'Packsanity Quests'

    if packsanity_selected:

        set_rule(world.get_location("Buy the Seeking Wisdom Pack", player),
                 lambda state: state.sl_phase_one(options, player) and
                               state.sl_has_pack("Seeking Wisdom", player))

        set_rule(world.get_location("Buy the Reap & Sow Pack", player),
                 lambda state: state.sl_phase_two(options, player) and
                               state.sl_has_pack("Reap & Sow", player))
        
        set_rule(world.get_location("Buy the Curious Cuisine Pack", player),
                 lambda state: state.sl_phase_four(options, player) and
                               state.sl_has_pack("Curious Cuisine", player))
        
        set_rule(world.get_location("Buy the Logic and Reason Pack", player),
                 lambda state: state.sl_phase_three(options, player) and
                               state.sl_has_pack("Logic and Reason", player))
        
        set_rule(world.get_location("Buy the The Armory Pack", player),
                 lambda state: state.sl_phase_four(options, player) and
                               state.sl_has_pack("The Armory", player))
        
        set_rule(world.get_location("Buy the Explorers Pack", player),
                 lambda state: state.sl_phase_two(options, player) and
                               state.sl_has_pack("Explorers", player))
        
        set_rule(world.get_location("Buy the Order and Structure Pack", player),
                 lambda state: state.sl_phase_five(options, player) and
                               state.sl_has_pack("Order and Structure", player))
        
        # Apply these rules if The Island board is selected
        if island_selected:

            set_rule(world.get_location("Buy the On the Shore Pack", player),
                lambda state: 
                    state.sl_can_start_island(player))  # Player can reach island and has On the Shore pack

            set_rule(world.get_location("Buy the Island of Ideas Pack", player),
                lambda state:
                    state.sl_can_start_island(player)                   # Player can reach The Island
                    and state.sl_has_pack("Island of Ideas", player))   # AND has 'Island of Ideas' pack
            
            set_rule(world.get_location("Buy the Grilling and Brewing Pack", player),
                lambda state:
                    state.sl_can_start_island(player)                       # Player can reach The Island
                    and state.sl_has_pack("Grilling and Brewing", player))  # AND has 'Grilling and Brewing' pack
            
            set_rule(world.get_location("Buy the Island Insights Pack", player),
                lambda state:
                    state.sl_can_start_island(player)                   # Player can reach The Island
                    and state.sl_has_pack("Island Insights", player))   # AND has 'Island of Ideas' pack
            
            set_rule(world.get_location("Buy the Advanced Archipelago Pack", player),
                lambda state:
                    state.sl_can_start_island(player)                       # Player can reach The Island
                    and state.sl_has_pack("Advanced Archipelago", player))  # AND has 'Advanced Archipelago' pack
            
            set_rule(world.get_location("Buy the Enclave Explorers Pack", player),
                lambda state:
                    state.sl_can_start_island(player)                   # Player can reach The Island
                    and state.sl_has_pack("Enclave Explorers", player)) # AND has 'Enclave Explorers' pack

    #endregion
        
    # If spendsanity enabled, include spendsanity checks in rules
    if spendsanity_selected:
        for x in range(1, options.spendsanity_count.value + 1):
            # Attempt to spread the checks across spheres
            set_rule(world.get_location("Buy {count} Spendsanity Packs".format(count=x), player),
                     lambda state: state.sl_phase_zero(player)                                      # Spread 1 - 2 across phase zero
                        if x < 3 else state.sl_phase_one(options, player)                           # Spread 3 - 6 across phase one 
                            if x < 7 else state.sl_phase_two(options, player)                       # Spread 7 - 10 across phase two
                                if x < 11 else state.sl_phase_three(options, player)                # Spread 11 - 14 across phase three
                                    if x < 15 else state.sl_phase_four(options, player)             # Spread 15 - 18 across phase four
                                        if x < 19 else state.sl_phase_five(options, player)         # Spread 19 - 22 across phase five
                                            if x < 23 else state.sl_phase_six(options, player))     # Spread 23 - 25 across phase six

#endregion

    # Set completion condition
    world.completion_condition[player] = lambda state: state.has("Victory", player)