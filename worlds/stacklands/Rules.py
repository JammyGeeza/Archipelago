from typing import List
from BaseClasses import MultiWorld
from .Enums import ExpansionType, GoalFlags, RegionFlags, SpendsanityType
from .Locations import location_table
from .Options import StacklandsOptions
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import set_rule

class StacklandsLogic(LogicMixin):

   def sl_mainland_board_capacity(self, options: StacklandsOptions, player: int) -> int:
      return (
            100 if (
               self.sl_has_pack("Seeking Wisdom", player)
               and self.can_reach_location("Build a Shed", player) # Can build a shed?                             
               or (
                  self.can_reach_location("Get an Iron Bar", player)
                  and self.sl_has_idea("Warehouse", player) # Can build a warehouse?           
               )
            )
            else 0
            if options.board_expansion_mode.value is ExpansionType.Vanilla else
            self.count("Mainland Board Expansion", player) * options.board_expansion_amount
      )

   def sl_island_board_capacity(self, options: StacklandsOptions, player: int) -> int:
      return (
            100 if self.sl_has_idea("Sandstone", player)
            and self.sl_has_pack("Island of Ideas", player)    # Has resources?
            and (
               self.can_reach_location("Build a Shed", player) # Can build a shed?                             
               or (
                  self.can_reach_location("Get an Iron Bar", player)
                  and self.sl_has_idea("Warehouse", player) # Can build a warehouse?           
               )
               or (
                  self.can_reach_location("Make Glass", player)
                  and self.sl_has_pack("Island of Ideas", player)
                  and self.sl_has_all_ideas(["Campfire", "Lighthouse", "Stick"], player) # Can build a lighthouse?
               )
            ) 
            else 0
            if options.board_expansion_mode.value is ExpansionType.Vanilla else
            self.count("Island Board Expansion", player) * options.board_expansion_amount # How much additional card limit increase has been received?
      )

   def sl_can_reach_all_quests(self, quests: List[str], player: int) -> bool:
      return all(self.can_reach_location(quest, player) for quest in quests)

   def sl_can_reach_any_quests(self, quests: List[str], player: int) -> bool:
      return any(self.can_reach_location(quest, player) for quest in quests)

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


# Set all region and location rules
def set_rules(world: MultiWorld, player: int):

   # Get relevant options
   options = world.worlds[player].options

   # Calculate board options
   forest_enabled: bool = bool(options.boards.value & RegionFlags.Forest)
   island_enabled: bool = bool(options.boards.value & RegionFlags.Island)

   # Calculate sanity options
   equipmentsanity_enabled: bool = options.equipmentsanity.value
   foodsanity_enabled: bool = options.foodsanity.value
   locationsanity_enabled: bool = options.locationsanity.value
   mobsanity_enabled: bool = options.mobsanity.value
   # packsanity_selected: bool = options.packsanity.value
   # spendsanity_selected: bool = options.spendsanity.value != SpendsanityType.Off
   structuresanity_enabled: bool = options.structuresanity.value

   # Calculate other options
   pausing_enabled: bool = options.pausing.value

#region 'Exits'

   #region Menu Exit(s)

   set_rule(world.get_entrance("Start", player), lambda state: True)

   #endregion

   #region Mainland Exit(s)
   
   set_rule(world.get_entrance("Forward to Mainland: Progression Phase One", player),
            lambda state:
               state.sl_has_pack("Humble Beginnings", player)) # Player has the 'Humble Beginnings' pack)
   
   set_rule(world.get_entrance("Forward to Mainland: Progression Phase Two", player),
            lambda state:
               state.sl_has_all_packs(["Seeking Wisdom", "Explorers"], player)
               and state.sl_has_all_ideas([
                  "Growth",
                  "House",
                  "Offspring",
                  "Shed",
                  "Stick",
               ], player)
               and state.sl_has_any_ideas(["Magic Wand", "Slingshot", "Spear"], player))
   
   set_rule(world.get_entrance("Forward to Mainland: Progression Phase Three", player),
            lambda state:
               state.sl_has_any_packs(["Curious Cuisine", "Reap & Sow"], player)
               and state.sl_has_all_ideas([
                  "Brick",
                  "Campfire",
                  "Cooked Meat",
                  "Plank",
                  "Smelter",
                  "Wooden Shield"
               ], player)
               and state.sl_has_any_ideas(["Club", "Spiked Plank"], player)
               and state.sl_mainland_board_capacity(options, player) >= 8)
   
   set_rule(world.get_entrance("Forward to Mainland: Progression Phase Four", player),
            lambda state:
               state.sl_has_any_packs(["Logic and Reason", "Order and Structure"], player)
               and state.sl_has_all_ideas([
                  "Iron Bar",
                  "Iron Shield",
                  "Smithy",
               ], player)
               and state.sl_has_any_ideas(["Sword", "Throwing Stars"], player)
               and state.sl_mainland_board_capacity(options, player) >= 16)

   #endregion

   #region Dark Forest Entrances

   set_rule(world.get_entrance("Portal", player),      
            lambda state:  # Can create Offspring to be able to use Strange Portal
               not forest_enabled
               or (
                  state.sl_has_all_packs(["Humble Beginnings", "Explorers", "Seeking Wisdom"], player)
                  and state.sl_has_all_ideas(["House", "Offspring"], player)
               ))
   
   set_rule(world.get_entrance("Forward to The Dark Forest: Progression Phase One", player),
            lambda state:  # Can make a basic weapon to start at Wave One
               not forest_enabled
               or (
                  state.sl_has_idea("Stick", player)
                  and state.sl_has_any_ideas(["Magic Wand", "Slingshot", "Spear"], player)
               ))
   
   set_rule(world.get_entrance("Forward to The Dark Forest: Progression Phase Two", player),
            lambda state:  # Can make all basic weapons and Stable Portal for easier travel
               not forest_enabled
               or (
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_all_ideas([
                     "Magic Wand",
                     "Slingshot",
                     "Spear",
                     "Stable Portal",
                     "Wooden Shield"
                  ], player)
               ))

   #endregion

   #region Island Entrances / Exits

   set_rule(world.get_entrance("Rowboat", player),
            lambda state:  # Can create Rowboat and Offspring to be able to use Rowboat
               not island_enabled
               or (
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_any_packs(["Logic and Reason", "Order and Structure"], player)
                  and state.sl_has_all_ideas(["Brick", "House", "Iron Bar", "Offspring", "Plank", "Rowboat", "Smelter"], player)
               ))

   set_rule(world.get_entrance("Forward to The Island: Progression Phase One", player),
            lambda state:  # Has the 'On the Shore' booster pack
               not island_enabled
               or state.sl_has_pack("On the Shore", player))
   
   set_rule(world.get_entrance("Forward to The Island: Progression Phase Two", player),
            lambda state:  # Can make basic, early progression ideas
               not island_enabled
               or (
                  state.sl_has_all_packs(["Island of Ideas", "Enclave Explorers", "Grilling and Brewing"], player)
                  and state.sl_has_all_ideas([
                     "Glass",
                     "Fabric",
                     "Rope",
                     "Sandstone",
                     "Stick",
                     "Sword"
                  ], player)
                  and state.sl_can_reach_any_quests([
                     "Train an Archer",
                     "Train Militia",
                     "Train a Wizard"
                  ], player)
                  and state.sl_island_board_capacity(options, player) >= 6
               ))
   
   set_rule(world.get_entrance("Forward to The Island: Progression Phase Three", player),
            lambda state:  # Can make advanced, later progression ideas
               not island_enabled
               or (
                  state.sl_has_all_packs(["Island Insights", "Advanced Archipelago"], player)
                  and state.sl_has_all_ideas([
                     "Forest Amulet",
                     "Gold Bar",
                     "Iron Shield",
                     "Sail",
                     "Smithy",
                     "Sloop",
                     "Throwing Stars"
                  ], player)
                  and state.sl_island_board_capacity(options, player) >= 12
               ))

   #endregion

#endregion

#region 'Mainland' Quests

   #region 'Welcome' Quests

   set_rule(world.get_location("Open the Booster Pack", player),
            lambda state: True)  # Phase Zero

   set_rule(world.get_location("Drag the Villager on top of the Berry Bush", player),
            lambda state: True)  # Phase Zero

   set_rule(world.get_location("Mine a Rock using a Villager", player),
            lambda state: True)  # Phase Zero

   set_rule(world.get_location("Sell a Card", player),
            lambda state: True)  # Phase Zero

   set_rule(world.get_location("Buy the Humble Beginnings Pack", player),
            lambda state:        # Phase Zero
               state.sl_has_pack("Humble Beginnings", player))

   set_rule(world.get_location("Harvest a Tree using a Villager", player),
            lambda state: True)  # Phase One

   set_rule(world.get_location("Make a Stick from Wood", player),
            lambda state:        # Phase One
               state.sl_has_idea("Stick", player))

   # Set this rule only if Pausing is enabled
   if pausing_enabled:
      set_rule(world.get_location("Pause using the play icon in the top right corner", player),
               lambda state: True)  # Phase Zero

   set_rule(world.get_location("Grow a Berry Bush using Soil", player),
            lambda state:        # Phase One
               state.sl_has_idea("Growth", player))

   set_rule(world.get_location("Build a House", player),
            lambda state:        # Phase One
               state.sl_has_idea("House", player))

   set_rule(world.get_location("Get a Second Villager", player),
            lambda state: True)  # Phase One

   set_rule(world.get_location("Create Offspring", player),
            lambda state:        # Phase One
               state.sl_has_all_ideas(["House", "Offspring"], player))

   #endregion

   #region 'The Grand Scheme' Quests

   set_rule(world.get_location("Unlock all Packs", player),
            lambda state:  # Phase Four
               state.count_group("All Mainland Booster Packs", player) == 8)

   set_rule(world.get_location("Get 3 Villagers", player),
            lambda state:  # Phase One
               state.can_reach_location("Create Offspring", player))

   set_rule(world.get_location("Get 5 Villagers", player),
            lambda state:  # Phase Two
               state.can_reach_location("Get 3 Villagers", player)
               and state.sl_has_all_packs(["Reap & Sow", "Seeking Wisdom"], player)
               and state.sl_mainland_board_capacity(options, player) >= 8)

   set_rule(world.get_location("Get 7 Villagers", player),
            lambda state:  # Phase Three
               state.can_reach_location("Get 5 Villagers", player)
               and state.sl_mainland_board_capacity(options, player) >= 16)

   set_rule(world.get_location("Find the Catacombs", player),
            lambda state:  # Phase One
               state.sl_has_all_packs(["Humble Beginnings", "Explorers"], player))

   set_rule(world.get_location("Find a mysterious artifact", player),
            lambda state:  # Phase One
               state.can_reach_location("Find the Catacombs", player))

   set_rule(world.get_location("Build a Temple", player),
            lambda state:  # Phase Four
               state.sl_can_reach_all_quests(["Get an Iron Bar", "Get 5 Villagers"], player)
               and state.sl_has_idea("Temple", player))

   set_rule(world.get_location("Bring the Goblet to the Temple", player),
            lambda state:  # Phase Four
               state.sl_can_reach_all_quests(["Build a Temple", "Find a mysterious artifact"], player))

   set_rule(world.get_location("Kill the Demon", player),
            lambda state:  # Phase Four
               state.can_reach_location("Bring the Goblet to the Temple", player))
   
   set_rule(world.get_location("Defeat Mainland Boss", player),
            lambda state:  # Phase Four
               state.can_reach_location("Kill the Demon", player))
   
   #endregion

   #region 'Power & Skill' Quests

   set_rule(world.get_location("Train Militia", player),
            lambda state:  # Phase Two
               state.sl_has_any_ideas(["Slingshot", "Spear"], player))

   set_rule(world.get_location("Kill a Rat", player),
            lambda state: True) # Phase One

   set_rule(world.get_location("Kill a Skeleton", player),
            lambda state:  # Phase Two
               state.sl_has_pack("The Armory", player))

   #endregion

   #region 'Strengthen Up' Quests

   set_rule(world.get_location("Make a Villager wear a Rabbit Hat", player),
            lambda state: True)  # Phase One

   set_rule(world.get_location("Build a Smithy", player),
            lambda state:  # Phase Three
               state.sl_has_any_packs(["Logic and Reason", "Order and Structure"], player)
               and state.sl_has_idea("Smithy", player))

   set_rule(world.get_location("Train a Wizard", player),
            lambda state:  # Phase Two
                  state.sl_has_pack("Explorers", player)
                  and state.sl_has_all_ideas(["Magic Wand", "Stick"], player))

   set_rule(world.get_location("Have a Villager with Combat Level 20", player),
            lambda state:  # Phase Two
               state.sl_can_reach_any_quests([
                  "Train Militia",
                  "Train a Wizard",
                  "Train a Ninja"
               ], player)
               and state.sl_has_all_ideas(["Plank", "Wooden Shield"], player))

   set_rule(world.get_location("Train a Ninja", player),
            lambda state:  # Phase Three
               state.can_reach_location("Get an Iron Bar", player)
               and state.sl_has_all_ideas(["Smithy", "Throwing Stars"], player))

   #endregion

   #region 'Potluck' Quests

   set_rule(world.get_location("Start a Campfire", player),
            lambda state:  # Phase Two
               state.sl_has_all_ideas(["Campfire", "Stick"], player))

   set_rule(world.get_location("Cook Raw Meat", player),
            lambda state:  # Phase Two
               state.can_reach_location("Start a Campfire", player)
               and state.sl_has_pack("Reap & Sow", player)
               and state.sl_has_idea("Cooked Meat", player))

   set_rule(world.get_location("Cook an Omelette", player),
            lambda state:  # Phase Two
               state.can_reach_location("Start a Campfire", player)
               and state.sl_has_pack("Reap & Sow", player)
               and state.sl_has_idea("Omelette", player))

   set_rule(world.get_location("Cook a Frittata", player),
            lambda state:  # Phase Two
               state.can_reach_location("Start a Campfire", player)
               and state.sl_has_all_packs(["Reap & Sow", "Curious Cuisine"], player)
               and state.sl_has_idea("Frittata", player))

   #endregion

   #region 'Discovery' Quests

   set_rule(world.get_location("Explore a Forest", player),
            lambda state:  # Phase One
               state.sl_has_pack("Explorers", player))

   set_rule(world.get_location("Explore a Mountain", player),
            lambda state:  # Phase One
               state.sl_has_pack("Explorers", player))

   set_rule(world.get_location("Open a Treasure Chest", player),
            lambda state:  # Phase One
               state.sl_has_pack("Explorers", player))

   set_rule(world.get_location("Get a Dog", player),
            lambda state:  # Phase One
               state.sl_has_pack("Explorers", player))

   set_rule(world.get_location("Find a Graveyard", player),
            lambda state:  # Phase One
               state.can_reach_location("Create Offspring", player))

   set_rule(world.get_location("Train an Explorer", player),
            lambda state:  # Phase One
               state.sl_has_pack("Explorers", player))

   set_rule(world.get_location("Buy something from a Travelling Cart", player),
            lambda state:
               state.count_group("All Mainland Ideas", player) >= 12)

   #endregion

   #region 'Ways and Means' Quests

   set_rule(world.get_location("Have 5 Ideas", player),
            lambda state:  # Phase One
               state.count_group("All Ideas", player) >= 5)

   set_rule(world.get_location("Have 10 Ideas", player),
            lambda state:  # Phase One
               state.count_group("All Ideas", player) >= 10)

   set_rule(world.get_location("Have 10 Stone", player),
            lambda state:  # Phase One
               state.sl_has_pack("Seeking Wisdom", player))

   set_rule(world.get_location("Have 10 Wood", player),
            lambda state:  # Phase One
               state.sl_has_pack("Seeking Wisdom", player))

   set_rule(world.get_location("Get an Iron Bar", player),
            lambda state:  # Phase Three
               state.sl_has_any_packs(["Logic and Reason", "Order and Structure"], player)
               and state.sl_has_all_ideas(["Brick", "Iron Bar", "Plank", "Smelter"], player))

   set_rule(world.get_location("Have 5 Food", player),
            lambda state: True)  # Phase One

   set_rule(world.get_location("Have 10 Food", player),
            lambda state: True)  # Phase One

   set_rule(world.get_location("Have 20 Food", player),
            lambda state:  # Phase Two
               state.sl_has_pack("Reap & Sow", player)
               and state.sl_mainland_board_capacity(options, player) >= 8)

   set_rule(world.get_location("Have 50 Food", player),
            lambda state:  # Phase Two
               state.can_reach_location("Have 20 Food", player)
               and state.sl_has_pack("Curious Cuisine", player)
               and state.sl_mainland_board_capacity(options, player) >= 16)

   set_rule(world.get_location("Have 10 Coins", player),
            lambda state: True)  # Phase One

   set_rule(world.get_location("Have 30 Coins", player),
            lambda state:  # Phase One
               state.sl_has_pack("Seeking Wisdom", player)
               and state.sl_has_idea("Coin Chest", player))

   set_rule(world.get_location("Have 50 Coins", player),
            lambda state:  # Phase One
               state.can_reach_location("Have 30 Coins", player))

   #endregion

   #region 'Construction' Quests

   set_rule(world.get_location("Have 3 Houses", player),
            lambda state:  # Phase One
               state.sl_has_pack("Seeking Wisdom", player))

   set_rule(world.get_location("Build a Shed", player),
            lambda state:  # Phase One
               state.sl_has_all_ideas(["Shed", "Stick"], player))

   set_rule(world.get_location("Build a Quarry", player),
            lambda state:  # Phase One
               state.sl_has_idea("Quarry", player))

   set_rule(world.get_location("Build a Lumber Camp", player),
            lambda state:  # Phase One
               state.sl_has_idea("Lumber Camp", player))

   set_rule(world.get_location("Build a Farm", player),
            lambda state:  # Phase Two
               state.sl_has_all_ideas(["Brick", "Farm", "Plank"], player))

   set_rule(world.get_location("Build a Brickyard", player),
            lambda state:  # Phase Three
               state.can_reach_location("Get an Iron Bar", player)
               and state.sl_has_idea("Brickyard", player))

   set_rule(world.get_location("Sell a Card at a Market", player),
            lambda state:  # Phase Two
               state.sl_has_all_ideas(["Brick", "Market", "Plank"], player))

   #endregion

   #region 'Longevity' Quests

   set_rule(world.get_location("Reach Moon 6", player),
            lambda state:  # Phase One
               state.count_group("All Ideas", player) >= 5)

   set_rule(world.get_location("Reach Moon 12", player),
            lambda state:  # Phase One
               state.count_group("All Ideas", player) >= 10)

   set_rule(world.get_location("Reach Moon 18", player),
            lambda state:  # Phase Two
               state.count_group("All Booster Packs", player) >= 2
               and state.count_group("All Ideas", player) >= 15)

   set_rule(world.get_location("Reach Moon 24", player),
            lambda state:  # Phase Two
               state.count_group("All Booster Packs", player) >= 3
               and state.count_group("All Mainland Ideas", player) >= 20)

   set_rule(world.get_location("Reach Moon 30", player),
            lambda state:  # Phase Three
               state.count_group("All Booster Packs", player) >= 4
               and state.count_group("All Mainland Ideas", player) >= 25)

   set_rule(world.get_location("Reach Moon 36", player),
            lambda state:  # Phase Three
               state.count_group("All Booster Packs", player) >= 5
               and state.count_group("All Mainland Ideas", player) >= 30)

   #endregion

   #region Additional Archipelago Quests

   # Buying Booster Packs
   set_rule(world.get_location("Buy the Seeking Wisdom Pack", player),
            lambda state:  # Phase One
               state.sl_has_pack("Seeking Wisdom", player))

   set_rule(world.get_location("Buy the Reap & Sow Pack", player),
            lambda state:  # Phase One
               state.sl_has_pack("Reap & Sow", player))

   set_rule(world.get_location("Buy the Curious Cuisine Pack", player),
            lambda state:  # Phase One
               state.sl_has_pack("Curious Cuisine", player))

   set_rule(world.get_location("Buy the Logic and Reason Pack", player),
            lambda state:  # Phase One
               state.sl_has_pack("Logic and Reason", player))

   set_rule(world.get_location("Buy the The Armory Pack", player),
            lambda state:  # Phase One
               state.sl_has_pack("The Armory", player))

   set_rule(world.get_location("Buy the Explorers Pack", player),
            lambda state:  # Phase One
               state.sl_has_pack("Explorers", player))

   set_rule(world.get_location("Buy the Order and Structure Pack", player),
            lambda state:  # Phase One
               state.sl_has_pack("Order and Structure", player))

   set_rule(world.get_location("Buy 5 Mainland Booster Packs", player),
            lambda state: True)  # Phase One

   set_rule(world.get_location("Buy 10 Mainland Booster Packs", player),
            lambda state:  # Phase One
               state.count_group("All Mainland Booster Packs", player) >= 2)

   set_rule(world.get_location("Buy 25 Mainland Booster Packs", player),
            lambda state:  # Phase One
               state.count_group("All Mainland Booster Packs", player) >= 3)

   # Selling Cards
   set_rule(world.get_location("Sell 5 Cards", player),
            lambda state: True)  # Phase One

   set_rule(world.get_location("Sell 10 Cards", player),
            lambda state: True)  # Phase One

   set_rule(world.get_location("Sell 25 Cards", player),
            lambda state:  # Phase One
               state.sl_has_pack("Seeking Wisdom", player))

   # Having Resources
   set_rule(world.get_location("Have 10 Bricks", player),
            lambda state:  # Phase Two
               state.sl_has_idea("Brick", player))

   set_rule(world.get_location("Have 10 Iron Bars", player),
            lambda state:  # Phase Three
               state.can_reach_location("Get an Iron Bar", player)
               and state.sl_mainland_board_capacity(options, player) >= 8)

   set_rule(world.get_location("Have 10 Iron Ore", player),
            lambda state:  # Phase Three
               state.sl_has_any_packs(["Logic and Reason", "Order and Structure"], player))

   set_rule(world.get_location("Have 10 Flint", player),
            lambda state:  # Phase One
               state.sl_has_pack("Seeking Wisdom", player))

   set_rule(world.get_location("Have 10 Planks", player),
            lambda state:  # Phase Two
               state.sl_has_idea("Plank", player))

   set_rule(world.get_location("Have 10 Sticks", player),
            lambda state:  # Phase one
               state.sl_has_idea("Stick", player))

   #endregion

#endregion

#region 'The Dark Forest' Quests

   if forest_enabled:

      #region Vanilla Quests

      set_rule(world.get_location("Find the Dark Forest", player),
               lambda state: True)  # Phase Zero

      set_rule(world.get_location("Complete the first wave", player),
               lambda state: True)  # Phase One

      set_rule(world.get_location("Build a Stable Portal", player),
               lambda state: True)  # Phase Two

      set_rule(world.get_location("Get to wave 6", player),
               lambda state:  # Phase Two
                  state.sl_has_idea("Sword", player))

      set_rule(world.get_location("Fight the Wicked Witch", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get to wave 8", player)
                  and state.sl_has_idea("Throwing Stars", player))
   
      set_rule(world.get_location("Defeat The Dark Forest Boss", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Fight the Wicked Witch", player))
      
      #endregion
      
      #region Additional Archipelago Quests

      set_rule(world.get_location("Get to wave 2", player),
               lambda state:  # Phase One
                  state.sl_has_all_ideas(["Slingshot", "Spear"], player)
                  or state.sl_has_all_ideas(["Magic Wand", "Slingshot"], player)
                  or state.sl_has_all_ideas(["Magic Wand", "Spear"], player))
      
      set_rule(world.get_location("Get to wave 4", player),
               lambda state:  # Phase One
                  state.sl_has_all_ideas([
                     "Magic Wand",
                     "Plank",
                     "Slingshot",
                     "Spear",
                     "Wooden Shield",
                  ], player))
      
      set_rule(world.get_location("Get to wave 8", player),
               lambda state:  # Phase Two
                  state.can_reach_location("Get to wave 6", player)
                  and state.sl_has_all_ideas(["Iron Shield", "Smithy"], player))
      
      #endregion
      

#endregion

#region 'The Island' Quests

   if island_enabled:

      #region 'The Grand Scheme' Category

      set_rule(world.get_location("Build a Rowboat", player),
               lambda state: True)  # Phase Zero

      set_rule(world.get_location("Build a Cathedral on the Mainland", player),
               lambda state:  # Phase Three
                  state.sl_can_reach_all_quests(["Make a Gold Bar", "Make Glass"], player)
                  and state.sl_has_idea("Cathedral", player))

      set_rule(world.get_location("Bring the Island Relic to the Cathedral", player),
               lambda state:  # Phase Three
                  state.sl_can_reach_all_quests([
                     "Build a Cathedral on the Mainland",
                     "Open the Sacred Chest"
                  ], player))

      set_rule(world.get_location("Kill the Demon Lord", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Bring the Island Relic to the Cathedral", player))

      set_rule(world.get_location("Defeat The Island Boss", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Kill the Demon Lord", player))

      #endregion

      #region 'Marooned' Category

      set_rule(world.get_location("Get 2 Bananas", player),
               lambda state: True)  # Phase Zero

      set_rule(world.get_location("Punch some Driftwood", player),
               lambda state: True)  # Phase Zero

      set_rule(world.get_location("Have 3 Shells", player),
               lambda state: True)  # Phase Zero

      set_rule(world.get_location("Catch a Fish", player),
               lambda state: True)  # Phase One

      set_rule(world.get_location("Make Rope", player),
               lambda state:  # Phase One
                  state.sl_has_idea("Rope", player))

      set_rule(world.get_location("Make a Fish Trap", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make Rope", player)
                  and state.sl_has_idea("Fish Trap", player))

      set_rule(world.get_location("Make a Sail", player),
               lambda state:  # Phase Two
                  state.can_reach_location("Make Rope", player)
                  and state.sl_has_idea("Sail", player))

      set_rule(world.get_location("Build a Sloop", player),
               lambda state:  # Phase Two
                  state.can_reach_location("Make a Sail", player)
                  and state.sl_has_idea("Sloop", player))
      #endregion

      #region 'Mystery of The Island' Category

      set_rule(world.get_location("Unlock all Island Packs", player),
               lambda state:  # Phase Three
                  state.count_group("All Island Booster Packs", player) == 6)

      set_rule(world.get_location("Find a Treasure Map", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Enclave Explorers", player))

      set_rule(world.get_location("Find Treasure", player),
               lambda state:  # Phase One
                  state.can_reach_location("Find a Treasure Map", player))

      set_rule(world.get_location("Forge Sacred Key", player),
               lambda state:  # Phase Three
                  state.sl_can_reach_all_quests([
                     "Make a Gold Bar",
                     "Make Glass"
                  ], player)
                  and state.sl_has_idea("Sacred Key", player))

      set_rule(world.get_location("Open the Sacred Chest", player),
               lambda state:  # Phase Three
                  state.sl_can_reach_all_quests([
                     "Forge Sacred Key",
                     "Find Treasure"
                  ], player))

      set_rule(world.get_location("Kill the Kraken", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Open the Sacred Chest", player))

      #endregion

      #region 'Island Grub'

      set_rule(world.get_location("Make Sushi", player),
               lambda state:  # Phase One
                  state.sl_has_idea("Sushi", player))

      set_rule(world.get_location("Cook Crab Meat", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Grilling and Brewing", player)
                  and state.sl_has_all_ideas(["Campfire", "Stick"], player))

      set_rule(world.get_location("Make Ceviche", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Grilling and Brewing", player)
                  and state.sl_has_idea("Ceviche", player))

      set_rule(world.get_location("Make a Seafood Stew", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Grilling and Brewing", player)
                  and state.sl_has_all_ideas(["Campfire", "Seafood Stew", "Stick"], player))

      set_rule(world.get_location("Make a Bottle of Rum", player),
               lambda state:  # Phase One
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_pack("Island of Ideas", player)
                  and state.sl_has_all_ideas([
                     "Bottle of Rum",
                     "Bottle of Water",
                     "Empty Bottle",
                     "Distillery",
                     "Glass",
                     "Stove",
                     "Sandstone"
                  ], player))

      #endregion

      #region 'Island Ambitions' Category

      set_rule(world.get_location("Have 10 Shells", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Island of Ideas", player))

      set_rule(world.get_location("Get a Villager Drunk", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make a Bottle of Rum", player))

      set_rule(world.get_location("Make Sandstone", player),
               lambda state:  # Phase One
                  state.sl_has_idea("Sandstone", player))

      set_rule(world.get_location("Build a Mess Hall", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Island of Ideas", player)
                  and state.sl_has_all_ideas(["Campfire", "Mess Hall", "Stick"], player))

      set_rule(world.get_location("Build a Greenhouse", player),
               lambda state:  # Phase One
                  state.sl_can_reach_all_quests(["Build a Composter", "Make Glass"], player)
                  and state.sl_has_idea("Greenhouse", player))

      set_rule(world.get_location("Have a Poisoned Villager", player),
               lambda state:  # Phase One
                  state.sl_has_pack("On the Shore", player)
                  and state.sl_has_pack("Enclave Explorers", player))

      set_rule(world.get_location("Cure a Poisoned Villager", player),
               lambda state:  # Phase One
                  state.can_reach_location("Have a Poisoned Villager", player)
                  and state.sl_has_all_ideas(["Campfire", "Charcoal", "Stick"], player))

      set_rule(world.get_location("Build a Composter", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make Sandstone", player)
                  and state.sl_has_all_packs(["Island of Ideas", "Grilling and Brewing"], player)
                  and state.sl_has_idea("Composter", player))

      set_rule(world.get_location("Bribe a Pirate Boat", player),
               lambda state:  # Phase Two
                  state.can_reach_location("Make a Gold Bar", player)
                  and state.sl_has_idea("Coin", player))

      set_rule(world.get_location("Befriend a Pirate", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Grilling and Brewing", player)
                  and state.sl_has_any_packs([ "Enclave Explorers", "Grilling and Brewing" ], player))

      set_rule(world.get_location("Make a Gold Bar", player),
               lambda state:  # Phase Two
                  state.sl_has_pack("Island of Ideas", player)
                  and state.sl_has_any_packs([ "Advanced Archipelago", "Enclave Explorers" ], player)
                  and state.sl_has_idea("Gold Bar", player))

      set_rule(world.get_location("Make Glass", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Island of Ideas", player)
                  and state.sl_has_idea("Glass", player))

      #endregion

      #region 'Strengthen Up' Category

      set_rule(world.get_location("Train an Archer", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make Rope", player)
                  and state.sl_has_idea("Bow", player))

      set_rule(world.get_location("Break a Bottle", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make Glass", player)
                  and state.sl_has_all_ideas([
                     "Campfire",
                     "Broken Bottle",
                     "Empty Bottle",
                     "Sandstone",
                     "Stick"
                  ], player))

      set_rule(world.get_location("Equip an Archer with a Quiver", player),
               lambda state:  # Phase One
                  state.can_reach_location("Train an Archer", player)
                  and state.sl_has_pack("Enclave Explorers", player))

      set_rule(world.get_location("Make a Villager wear Crab Scale Armor", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Grilling and Brewing", player)
                  and state.sl_can_reach_all_quests([
                     "Train an Archer",
                     "Train Militia",
                     "Train a Wizard"
                  ], player)
                  and state.sl_has_all_ideas(["Plank","Wooden Shield"], player))

      set_rule(world.get_location("Craft the Amulet of the Forest", player),
               lambda state:  # Phase Two
                  state.can_reach_location("Make a Gold Bar", player)
                  and state.sl_has_pack("Explorers", player)
                  and state.sl_has_all_ideas(["Forest Amulet", "Sloop", "Smithy"], player))

      #endregion

      #region Additional Archipelago Quests

      # Buying Booster Packs
      set_rule(world.get_location("Buy the On the Shore Pack", player),
               lambda state: True)  # Phase One

      set_rule(world.get_location("Buy the Island of Ideas Pack", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Island of Ideas", player))

      set_rule(world.get_location("Buy the Grilling and Brewing Pack", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Grilling and Brewing", player))

      set_rule(world.get_location("Buy the Island Insights Pack", player),
               lambda state:  # Phase Two
                  state.sl_has_pack("Island Insights", player))

      set_rule(world.get_location("Buy the Advanced Archipelago Pack", player),
               lambda state:  # Phase Two
                  state.sl_has_pack("Advanced Archipelago", player))

      set_rule(world.get_location("Buy the Enclave Explorers Pack", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Enclave Explorers", player))
      
      set_rule(world.get_location("Buy 5 Island Booster Packs", player),
               lambda state: True)  # Phase One

      set_rule(world.get_location("Buy 10 Island Booster Packs", player),
               lambda state:  # Phase One
                  state.count_group("All Island Booster Packs", player) >= 2)

      set_rule(world.get_location("Buy 25 Island Booster Packs", player),
               lambda state:  # Phase One
                  state.count_group("All Island Booster Packs", player) >= 3)
      
      # Shells
      set_rule(world.get_location("Have 30 Shells", player),
               lambda state:  # Phase One
                  state.can_reach_location("Have 10 Shells", player)
                  and state.sl_has_idea("Shell Chest", player))
      
      set_rule(world.get_location("Have 50 Shells", player),
               lambda state:  # Phase One
                  state.can_reach_location("Have 30 Shells", player))
      
      # Having Resources
      set_rule(world.get_location("Have 10 Cotton", player),
               lambda state:  # Phase One
                  state.sl_island_board_capacity(options, player) >= 4)
      
      set_rule(world.get_location("Have 10 Fabric", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Island of Ideas", player)
                  and state.sl_has_idea("Fabric", player)
                  and state.sl_island_board_capacity(options, player) >= 4)
      
      set_rule(world.get_location("Have 10 Glass", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make Glass", player)
                  and state.sl_island_board_capacity(options, player) >= 4)
      
      set_rule(world.get_location("Have 10 Gold Bars", player),
               lambda state:  # Phase Two
                  state.can_reach_location("Make a Gold Bar", player)
                  and state.sl_island_board_capacity(options, player) >= 8)
      
      set_rule(world.get_location("Have 10 Rope", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make Rope", player)
                  and state.sl_island_board_capacity(options, player) >= 4)
      
      set_rule(world.get_location("Have 10 Sails", player),
               lambda state:  # Phase Two
                  state.can_reach_location("Make a Sail", player)
                  and state.sl_island_board_capacity(options, player) >= 8)
      
      set_rule(world.get_location("Have 10 Sandstone", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make Sandstone", player)
                  and state.sl_island_board_capacity(options, player) >= 4)

      #endregion

#endregion

#region 'Equipmentsanity' Quests

   if equipmentsanity_enabled:

      #region Mainland Equipment

      set_rule(world.get_location("Make a Bone Spear", player),
               lambda state:  # Phase Two
                  state.can_reach_location("Make a Spear", player)
                  and state.sl_has_pack("Explorers", player)
                  and state.sl_has_idea("Bone Spear", player))
      
      set_rule(world.get_location("Make a Boomerang", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_all_ideas(["Boomerang", "Smithy"], player))
      
      set_rule(world.get_location("Make a Club", player),
               lambda state:  # Phase One
                  state.sl_has_all_ideas(["Club", "Stick"], player))

      set_rule(world.get_location("Make Chainmail Armor", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_all_ideas(["Chainmail Armor", "Smithy"], player))
      
      set_rule(world.get_location("Make an Iron Shield", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_all_ideas(["Iron Shield", "Smithy"], player))
      
      set_rule(world.get_location("Make a Magic Blade", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Make a Sword", player)
                  and state.sl_has_all_ideas(["Magic Blade", "Smithy"], player))
      
      set_rule(world.get_location("Make a Magic Ring", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_all_ideas(["Magic Ring", "Smithy"], player))
      
      set_rule(world.get_location("Make a Magic Staff", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_all_ideas(["Magic Staff", "Smithy"], player))
      
      set_rule(world.get_location("Make a Magic Tome", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_all_ideas(["Magic Tome", "Smithy"], player))
      
      set_rule(world.get_location("Make a Magic Wand", player),
               lambda state:  # Phase Two
                  state.sl_has_pack("Explorers", player)
                  and state.sl_has_all_ideas(["Magic Wand", "Stick"], player))
      
      set_rule(world.get_location("Make a Slingshot", player),
               lambda state:  # Phase Two
                  state.sl_has_all_ideas(["Slingshot", "Stick"], player))
      
      set_rule(world.get_location("Make a Spear", player),
               lambda state:  # Phase Two
                  state.sl_has_all_ideas(["Spear", "Stick"], player))
      
      set_rule(world.get_location("Make a Spiked Plank", player),
               lambda state:  # Phase Two
                  state.sl_has_all_ideas(["Plank", "Spiked Plank"], player))
      
      set_rule(world.get_location("Make a Sword", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_idea("Sword", player))
      
      set_rule(world.get_location("Make Throwing Stars", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_all_ideas(["Smithy", "Throwing Stars"], player))
      
      set_rule(world.get_location("Make a Wooden Shield", player),
               lambda state:  # Phase Two
                  state.sl_has_all_ideas(["Plank","Wooden Shield"], player))
      
      if island_enabled:

         #region The Island Equipment

         set_rule(world.get_location("Make a Blunderbuss", player),
               lambda state:  # Phase Two
                  state.can_reach_location("Make a Gold Bar", player)
                  and state.sl_has_all_ideas(["Blunderbuss", "Smithy"], player))
      
         set_rule(world.get_location("Make a Bone Staff", player),
                  lambda state:  # Phase Two
                     state.sl_can_reach_all_quests(["Make a Gold Bar", "Make a Magic Staff"], player)
                     and state.sl_has_all_ideas(["Bone Staff", "Smithy"], player))
         
         set_rule(world.get_location("Make a Crossbow", player),
                  lambda state:  # Phase Two
                     state.can_reach_location("Make Rope", player)
                     and state.sl_has_all_ideas(["Crossbow", "Smithy"], player))
         
         set_rule(world.get_location("Make a Golden Chestplate", player),
                  lambda state:  # Phase Two
                     state.can_reach_location("Make a Gold Bar", player)
                     and state.sl_has_all_ideas(["Golden Chestplate", "Smithy"], player))
         
         set_rule(world.get_location("Make a Mountain Amulet", player),
                  lambda state:  # Phase Two
                     state.can_reach_location("Make a Gold Bar", player)
                     and state.sl_has_all_ideas(["Mountain Amulet", "Smithy"], player))
         
         set_rule(world.get_location("Make a Wizard Robe", player),
                  lambda state:  # Phase Two
                     state.can_reach_location("Make Rope", player)
                     and state.sl_has_all_ideas(["Fabric", "Smithy", "Wizard Robe"], player))

         #endregion
   
   #endregion

#endregion

#region 'Foodsanity' Quests

   if foodsanity_enabled:

      #region Mainland Foods

      set_rule(world.get_location("Cook a Stew", player),
            lambda state:  # Phase Two
               state.sl_has_all_packs(["Curious Cuisine","Reap & Sow"], player)
               and state.sl_has_all_ideas(["Campfire", "Stew",], player))

      set_rule(world.get_location("Make a Fruit Salad", player),
               lambda state:  # Phase Two
                  state.sl_has_any_packs(["Curious Cuisine", "Reap & Sow"], player)
                  and state.sl_has_idea("Fruit Salad", player))

      set_rule(world.get_location("Make a Milkshake", player),
               lambda state:  # Phase Two
                  state.sl_has_pack("Curious Cuisine", player)
                  and state.sl_has_idea("Milkshake", player))

      #endregion

      if island_enabled:

         #region The Island Foods

         set_rule(world.get_location("Make a Bottle of Water", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Enclave Explorers", player)
                  and state.sl_has_all_ideas([
                     "Bottle of Water",
                     "Campfire",
                     "Empty Bottle",
                     "Glass",
                     "Stick"
                  ], player))
      
         set_rule(world.get_location("Make Grilled Fish", player),
                  lambda state:  # Phase One
                     state.sl_has_all_ideas(["Campfire", "Stick"], player))
         
         set_rule(world.get_location("Make Tamago Sushi", player),
                  lambda state:  # Phase One
                     state.can_reach_location("Cook an Omelette", player)
                     and state.sl_has_idea("Tamago Sushi", player))
         
         #endregion

#endregion

#region 'Locationsanity' Quests

   if locationsanity_enabled:

      #region Mainland Locations

      set_rule(world.get_location("Explore a Catacombs", player),
            lambda state:  # Phase One
               state.sl_has_pack("Explorers", player))

      set_rule(world.get_location("Explore a Graveyard", player),
               lambda state:  # Phase One
                  state.can_reach_location("Create Offspring", player))

      set_rule(world.get_location("Explore an Old Village", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Explorers", player))

      set_rule(world.get_location("Explore a Plains", player),
               lambda state:  # Phase One
                  state.sl_has_pack("Explorers", player))

      #endregion

      if island_enabled:

         #region The Island Locations

         set_rule(world.get_location("Explore a Cave", player),
               lambda state: # Phase One
                  state.sl_has_pack("Enclave Explorers", player))
      
         set_rule(world.get_location("Explore a Jungle", player),
                  lambda state: # Phase One
                     state.sl_has_pack("Enclave Explorers", player))
         
         #endregion

#endregion

#region 'Mobsanity' Quests

   if mobsanity_enabled:

      #region Mainland Mobs

      set_rule(world.get_location("Kill a Bear", player),
               lambda state:  # Phase Two (Moon 16)
                  state.sl_has_pack("The Armory", player)
                  and state.sl_has_all_ideas(["Plank", "Wooden Shield"], player))
      
      set_rule(world.get_location("Kill an Elf", player),
               lambda state:  # Phase Three (Moon 24)
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_idea("Sword", player))

      set_rule(world.get_location("Kill an Elf Archer", player),
               lambda state:  # Phase Three (Moon 24)
                  state.can_reach_location("Kill an Elf", player))

      set_rule(world.get_location("Kill an Enchanted Shroom", player),
               lambda state:  # Phase Three (Moon 24)
                  state.can_reach_location("Kill an Elf", player))

      set_rule(world.get_location("Kill a Feral Cat", player),
               lambda state:  # Phase Three (Moon 24)
                  state.can_reach_location("Kill an Elf", player))

      set_rule(world.get_location("Kill a Frog Man", player),
               lambda state:  # Phase Two (Moon 16) or Phase One of The Island
                  (
                     state.can_reach_location("Kill a Bear", player)
                     or (
                        island_enabled
                        and state.can_reach_region("The Island: Progression Phase One", player)
                        and state.sl_has_pack("Advanced Archipelago", player)
                        and state.sl_has_all_ideas(["Sandstone", "Wooden Shield"], player)
                     )
                  ))

      set_rule(world.get_location("Kill a Ghost", player),
               lambda state:  # Phase Three (Moon 24)
                  state.can_reach_location("Kill an Elf", player))

      set_rule(world.get_location("Kill a Giant Rat", player),
               lambda state:  # Phase Two (Moon 16)
                  state.can_reach_location("Kill a Bear", player))

      set_rule(world.get_location("Kill a Giant Snail", player),
               lambda state:  # Phase Three (Moon 24)
                  state.can_reach_location("Kill an Elf", player))

      set_rule(world.get_location("Kill a Goblin", player),
               lambda state: True)  # Phase Two (Moon 12)

      set_rule(world.get_location("Kill a Goblin Archer", player),
               lambda state: True)  # Phase Two (Moon 12)

      set_rule(world.get_location("Kill a Goblin Shaman", player),
               lambda state:  # Phase Two (Moon 16)
                  state.can_reach_location("Kill a Bear", player))

      set_rule(world.get_location("Kill a Merman", player),
               lambda state:  # Phase Two (Moon 16) or Phase One of The Island
                  state.can_reach_location("Kill a Frog Man", player))

      set_rule(world.get_location("Kill a Mimic", player),
               lambda state:  # Phase Two (Moon 16)
                  state.can_reach_location("Kill a Bear", player))

      set_rule(world.get_location("Kill a Mosquito", player),
               lambda state:  # Phase Zero (so can be ambiguous between Mainland / Forest / Island)
                  (
                     state.can_reach_location("Kill an Elf", player)
                     or (
                        forest_enabled
                        and state.can_reach_location("Get to wave 4", player)
                     )
                     or (
                        island_enabled
                        and state.can_reach_region("The Island: Progression Phase One", player)
                        and state.sl_has_pack("Enclave Explorers", player)
                     )
                  ))

      set_rule(world.get_location("Kill a Slime", player),
               lambda state:  # Phase Two (Moon 12, but actually 16 for logic reasons)
                  state.can_reach_location("Kill a Bear", player))

      set_rule(world.get_location("Kill a Small Slime", player),
               lambda state:  # Phase Two (Moon 12, but actually 16 for logic reasons)
                  state.can_reach_location("Kill a Slime", player))

      set_rule(world.get_location("Kill a Wolf", player),
               lambda state:  # Phase Two (Moon 16)
                  state.can_reach_location("Kill a Bear", player))
      
      #endregion

      if forest_enabled:

         #region The Dark Forest Mobs

         set_rule(world.get_location("Kill a Dark Elf", player),
                  lambda state:  # Phase Two (Wave 6 but appears Wave 4 so giving leway)
                     state.can_reach_location("Get to wave 6", player))

         set_rule(world.get_location("Kill an Ent", player),
                  lambda state:  # Phase Two (Wave 6 but appears Wave 4 so giving leway)
                        state.can_reach_location("Get to wave 6", player))

         set_rule(world.get_location("Kill an Ogre", player),
                  lambda state:  # Phase Two (Wave 6 but appears Wave 4 so giving leway)
                        state.can_reach_location("Get to wave 6", player))
         
         #endregion

      if island_enabled:

         #region The Island Mobs

         set_rule(world.get_location("Kill an Eel", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make a Fish Trap", player))

         set_rule(world.get_location("Kill a Momma Crab", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make a Villager wear Crab Scale Armor", player)) # Found after killing 3 crabs

         set_rule(world.get_location("Kill a Seagull", player),
               lambda state: True)  # Phase One

         set_rule(world.get_location("Kill a Shark", player),
               lambda state:  # Phase One
                  state.can_reach_location("Make a Fish Trap", player)
                  and state.sl_can_reach_any_quests([
                     "Train an Archer",
                     "Train Militia",
                     "Train a Wizard"
                  ], player))
         
         set_rule(world.get_location("Kill a Snake", player),
               lambda state:
                  state.sl_has_pack("Enclave Explorers", player))

         set_rule(world.get_location("Kill a Tentacle", player),
               lambda state:
                  state.can_reach_location("Open the Sacred Chest", player)) # Found after opening sacred chest

         set_rule(world.get_location("Kill a Tiger", player),
               lambda state:
                  state.sl_can_reach_any_quests(["Train Militia", "Train a Wizard"], player)  # AND has access to basic weapons
                  and state.sl_has_pack("Enclave Explorers", player))                             # AND has pack containing 'Tiger'
         
      #endregion

      if forest_enabled or island_enabled:

         #region The Dark Forest OR The Island Mobs

         set_rule(world.get_location("Kill an Orc Wizard", player),
               lambda state:  # Phase Zero (so can be ambiguous between Forest / Island)
                  (
                     forest_enabled
                     and state.can_reach_location("Get to wave 6", player)
                  )
                  or (
                     island_enabled
                     and state.can_reach_region("The Island: Progression Phase Two", player)
                     and state.sl_has_pack("Advanced Archipelago", player)
                  ))

         set_rule(world.get_location("Kill a Pirate", player),
               lambda state:  # Phase Zero (so can be ambiguous between Forest / Island)
                  state.can_reach_location("Kill an Orc Wizard", player))
         
         #endregion

#endregion

#region 'Structuresanity' Quests

   if structuresanity_enabled:

      #region Mainland Structures

      set_rule(world.get_location("Build a Coin Chest", player),
               lambda state:  # Phase One
                  state.sl_has_idea("Coin Chest", player))

      set_rule(world.get_location("Build a Garden", player),
               lambda state:  # Phase One
                  state.sl_has_idea("Garden", player))

      set_rule(world.get_location("Build a Hotpot", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_idea("Hotpot", player))
            
      set_rule(world.get_location("Build an Iron Mine", player),
               lambda state:  # Phase One
                  state.sl_has_idea("Iron Mine", player))

      set_rule(world.get_location("Build a Market", player),
               lambda state:  # Phase Two
                  state.sl_has_all_ideas(["Brick", "Market", "Plank"], player))

      set_rule(world.get_location("Build a Resource Chest", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_idea("Resource Chest", player))

      set_rule(world.get_location("Build a Sawmill", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_idea("Sawmill", player))

      set_rule(world.get_location("Build a Smelter", player),
               lambda state:  # Phase Two
                  state.sl_has_all_ideas(["Brick", "Plank", "Smelter"], player))

      set_rule(world.get_location("Build a Stove", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_idea("Stove", player))

      set_rule(world.get_location("Build a Warehouse", player),
               lambda state:  # Phase Three
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_idea("Warehouse", player))
      
      #endregion
         
      if island_enabled:

         #region The Island Structures

         set_rule(world.get_location("Build a Distillery", player),
               lambda state:  # Phase One
                  state.can_reach_location("Get an Iron Bar", player)
                  and state.sl_has_all_ideas(["Distillery", "Stove", "Sandstone"], player))
      
         set_rule(world.get_location("Build a Frigate", player),
                  lambda state:  # Phase Two
                     state.can_reach_location("Make a Sail", player)
                     and state.sl_has_idea("Frigate", player)
                     and state.sl_island_board_capacity(options, player) >= 8)
         
         set_rule(world.get_location("Build a Gold Mine", player),
                  lambda state:  # Phase One
                     state.sl_has_pack("Enclave Explorers", player)
                     and state.sl_has_all_ideas(["Gold Mine", "Sandstone"], player))
         
         set_rule(world.get_location("Build a Lighthouse", player),
                  lambda state:  # Phase One
                     state.can_reach_location("Make Glass", player)
                     and state.sl_has_pack("Island of Ideas", player)
                     and state.sl_has_all_ideas(["Campfire", "Lighthouse", "Sandstone", "Stick"], player))
         
         set_rule(world.get_location("Build a Sand Quarry", player),
                  lambda state:  # Phase One
                     state.sl_has_idea("Sand Quarry", player))
         
         set_rule(world.get_location("Build a Shell Chest", player),
                  lambda state:  # Phase One
                     state.sl_has_idea("Shell Chest", player))
         
         #endregion

#endregion

#region 'Spendsanity' Quests

   # TODO: Re-write these
   # If spendsanity enabled, include spendsanity checks in rules
   # if spendsanity_selected:
   #    for x in range(1, options.spendsanity_count.value + 1):
   #       set_rule(world.get_location("Buy {count} Spendsanity Packs".format(count=x), player),
   #                lambda state: state.sl_has_pack("Humble Beginnings", player))

         # # Attempt to spread the checks across spheres
         # set_rule(world.get_location("Buy {count} Spendsanity Packs".format(count=x), player),
         #          lambda state: state.sl_phase_zero(player)                                      # Spread 1 - 2 across phase zero
         #             if x < 3 else state.sl_phase_one(options, player)                           # Spread 3 - 6 across phase one
         #                 if x < 7 else state.sl_phase_two(options, player)                       # Spread 7 - 10 across phase two
         #                     if x < 11 else state.sl_phase_three(options, player)                # Spread 11 - 14 across phase three
         #                         if x < 15 else state.sl_phase_four(options, player)             # Spread 15 - 18 across phase four
         #                             if x < 19 else state.sl_phase_five(options, player)         # Spread 19 - 22 across phase five
         #                                 if x < 23 else state.sl_phase_six(options, player))     # Spread 23 - 25 across phase six

#endregion

   # Set goal condition
   set_rule(world.get_location("Goal Complete", player),
            lambda state: (
               bool(options.goal.value & (GoalFlags.AllBosses | GoalFlags.RandomBoss))
               and (not bool(world.goal_boards & RegionFlags.Mainland) or state.has("Demon", player))
               and (not bool(world.goal_boards & RegionFlags.Forest) or state.has("Wicked Witch", player))
               and (not bool(world.goal_boards & RegionFlags.Island) or state.has("Demon Lord", player))
            ))
               

   # Set completion condition
   world.completion_condition[player] = lambda state: state.has("Victory", player)