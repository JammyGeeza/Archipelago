from typing import List
from BaseClasses import MultiWorld
from .Enums import ExpansionType, GoalFlags, RegionFlags, SpendsanityType
from .Locations import location_table
from .Options import StacklandsOptions
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import set_rule

class StacklandsLogic(LogicMixin):

   def sl_rowboat_from_mainland(self, player: int) -> bool:
      return (
         self.sl_has_all_packs(["Humble Beginnings", "Seeking Wisdom", "Order and Structure"], player)
         and self.sl_has_all_ideas(["Brick", "Iron Bar", "Plank", "Rowboat", "Smelter"], player)
      )

   def sl_rowboat_from_island(self, player: int) -> bool:
      return (
         self.sl_has_all_packs(["On The Shore", "Advanced Archipelago", "Enclave Explorers"], player)
         and self.sl_has_all_ideas(["Brick", "Iron Bar", "Plank", "Rowboat", "Smelter"], player)
      )

   def sl_stable_portal_from_mainland(self, player: int) -> bool:
      return (
         self.sl_has_all_packs(["Humble Beginnings", "Explorers", "The Armory"], player)
         and self.sl_has_all_ideas(["Brick", "House", "Offspring", "Stable Portal"], player)
      )

   def sl_stable_portal_from_island(self, player: int) -> bool:
      return (
         self.sl_has_all_packs(["On The Shore", "Advanced Archipelago", "Enclave Explorers"], player)
         and self.sl_has_all_ideas(["Brick", "House", "Offspring", "Stable Portal"], player)
      )

   def sl_mainland_board_capacity(self, options: StacklandsOptions, player: int) -> int:
      return (
         100 if self.sl_can_reach_any_quests(["Build a Shed", "Build a Warehouse"], player) else 0
         if options.board_expansion_mode.value is ExpansionType.Ideas else
         self.count("Mainland Board Expansion", player) * options.board_expansion_amount
      )

   def sl_island_board_capacity(self, options: StacklandsOptions, player: int) -> int:
      return (
         100 if self.sl_can_reach_any_quests(["Build a Shed", "Build a Warehouse"], player) else 0
         if options.board_expansion_mode.value is ExpansionType.Ideas else
         self.count("Island Board Expansion", player) * options.board_expansion_amount
      )

   def sl_can_progress_mainland_or_island(self, player: int) -> bool:
      return (
         self.sl_can_progress_mainland(player)
         or self.sl_can_progress_island(player)
      )

   def sl_can_progress_mainland(self, player: int) -> bool:
      return (
         # self.can_reach_region("Mainland", player)
         self.sl_has_pack("Humble Beginnings", player)
      )

   def sl_can_progress_forest(self, player: int) -> bool:
      return (
         self.can_reach_region("The Dark Forest", player)
         and self.sl_can_reach_any_quests(["Train Militia", "Train a Wizard"], player)
         and self.can_reach_location("Cook Raw Meat", player)
      )

   def sl_can_progress_island(self, player: int) -> bool:
      return (
         self.can_reach_region("The Island", player)
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

   def sl_has_humble_beginnings(self, player: int) -> bool:
      return self.sl_has_pack("Humble Beginnings", player)
   
   def sl_can_reach_mainland_moon(self, player: int, moon: int) -> bool:
      return self.can_reach_region(f"Mainland: Moon {moon}", player)
   
   def sl_can_reach_mainland_phase(self, player: int, phase: str) -> bool:
      return self.can_reach_region(f"Mainland: Progression Phase {phase}", player)
   
   def sl_can_reach_mainland_moon_2(self, player: int) -> bool:
      return self.sl_has_pack("Humble Beginnings", player)        # Player has Humble Beginnings
   
   def sl_can_reach_mainland_moon_6(self, player: int) -> bool:
      return (
         self.sl_can_reach_mainland_moon(player, 2)          # Player can reach Moon 2
         and self.sl_has_all_ideas([
            "Campfire",                                           # AND make a Campfire
            "Stick"                                               # AND make a Stick
         ], player)
         and self.sl_has_pack("Seeking Wisdom", player)           # AND has the Seeking Wisdom pack
      )
   
   def sl_can_reach_mainland_moon_12(self, player: int) -> bool:
      return (
         self.sl_can_reach_mainland_moon(player, 6)          # Player can reach Moon 6
         and self.sl_has_all_ideas([
            "Growth",                                             # AND can use Growth
            "House"                                               # AND can make a House
         ], player)
         and self.sl_has_any_packs([
            "Reap & Sow",                                         # AND has either the Reap & Sow
            "Curious Cuisine"], player)                           # OR Curious Cuisine pack
      )
   
   def sl_can_reach_mainland_moon_18(self, player: int) -> bool:
      return (
         self.sl_can_reach_mainland_moon(player, 12)         # Player can reach Moon 12
         and self.sl_has_all_ideas([
            "Brick",                                              # AND can make Bricks
            # "Coin Chest",                                         # AND can make Coin Chest
            "Cooked Meat",                                        # AND can make Cooked Meat
            "Plank",                                              # AND can make Planks
            "Offspring",                                          # AND can make Offspring
            "Shed",                                               # AND can make Sheds
            "Wooden Shield"                                       # AND can make Wooden Shields
         ], player)
         and self.sl_has_any_ideas([
            "Slingshot",                                          # AND can make Slingshots
            "Spear"], player)                                     # OR Spears
         and self.sl_has_pack("Explorers", player)                # AND has the Explorers pack
      )
   
   def sl_can_reach_mainland_moon_24(self, player: int) -> bool:
      return (
         self.sl_can_reach_mainland_moon(player, 18)         # Player can reach Moon 18
         and self.sl_has_all_ideas([
            "Iron Bar",                                           # AND can make Iron Bars
            # "Resource Chest",                                     # AND can make Resource Chests
            "Smelter"                                             # AND can make Smelter
         ], player)
         and self.sl_has_pack("Order and Structure", player)      # AND has the Order and Structure pack
      )
   
   def sl_can_reach_mainland_moon_30(self, player: int) -> bool:
      return (
         self.sl_can_reach_mainland_moon(player, 24)         # Player can reach Moon 24
         and self.sl_has_all_ideas([
            "Iron Shield",                                        # AND can make Iron Shields
            "Smithy"                                              # AND can make Smithy
         ], player)
         and self.sl_has_any_ideas([
            "Sword",                                              # AND can make Swords
            "Throwing Stars"                                      # OR Throwing Stars
         ], player)
         and self.sl_has_pack("The Armory", player)               # AND has The Armory pack
      )
   
   def sl_can_reach_mainland_moon_36(self, player: int) -> bool:
      return self.sl_can_reach_mainland_moon(player, 30)     # Player can reach Moon 30


# Set all region and location rules
def set_rules(world: MultiWorld, player: int):

   # Get relevant options
   options = world.worlds[player].options

   # Calculate board options
   mainland_selected: bool = bool(options.goal.value & RegionFlags.Mainland)
   forest_selected: bool = bool(options.goal.value & RegionFlags.Forest)
   island_selected: bool = bool(options.goal.value & RegionFlags.Island)

   # Calculate sanity options
   mobsanity_selected: bool = options.mobsanity.value
   packsanity_selected: bool = options.packsanity.value
   spendsanity_selected: bool = options.spendsanity.value != SpendsanityType.Off

   # Calculate other options
   expansion_items_selected: bool = options.board_expansion_mode.value is ExpansionType.Items
   pausing_selected: bool = options.pausing.value

#region 'Exits'

   #region Menu Exit(s)

   set_rule(world.get_entrance("Start", player), lambda state: True)

   #endregion

   #region Mainland Exit(s)

   set_rule(world.get_entrance("Portal from Mainland to Dark Forest", player),
            lambda state:
               state.sl_stable_portal_from_mainland(player))               # Can build a Stable Portal from Mainland resources

   set_rule(world.get_entrance("Rowboat from Mainland to The Island", player),
            lambda state:
               state.sl_rowboat_from_mainland(player))                     # Can build a Rowboat from Mainland resources
   
   set_rule(world.get_entrance("Forward to Mainland: Progression Phase One", player),
            lambda state:
               state.sl_has_pack("Humble Beginnings", player)) # Player has the 'Humble Beginnings' pack)
   
   set_rule(world.get_entrance("Forward to Mainland: Progression Phase Two", player),
            lambda state:
               state.sl_has_all_ideas([
                  # "Campfire",                  
                  # "Cooked Meat",
                  # "Growth",
                  "House",
                  "Offspring",
                  # "Stick"
               ], player))
               # and state.sl_has_all_packs([
               #    "Reap & Sow",
               #    "Seeking Wisdom"
               # ], player))
   
   set_rule(world.get_entrance("Forward to Mainland: Progression Phase Three", player),
            lambda state:
               state.sl_has_all_ideas([
                  "Brick",
                  "Plank",
                  "Shed",                 
                  # "Wooden Shield"
               ], player)
               # and state.sl_has_any_ideas([
               #    "Slingshot",
               #    "Spear"
               # ], player)
               and state.sl_has_all_packs([
                  "Explorers"
               ], player))
   
   set_rule(world.get_entrance("Forward to Mainland: Progression Phase Four", player),
            lambda state:
               state.sl_has_all_ideas([
                  "Iron Bar",                  
                  # "Iron Shield",                  
                  "Smelter",
                  # "Smithy"
               ], player))
               # and state.sl_has_any_ideas([
               #    "Sword",
               #    "Throwing Stars"
               # ], player)
               # and state.sl_has_all_packs([
               #    "Logic and Reason",
               #    "Order and Structure"
               # ], player))
   
   # set_rule(world.get_entrance("Forward to Mainland: Moon 2", player),
   #          lambda state:
   #             state.sl_has_pack("Humble Beginnings", player)) # Player has the 'Humble Beginnings' pack
   
   # set_rule(world.get_entrance("Forward to Mainland: Moon 6", player),
   #          lambda state:
   #             state.sl_has_all_ideas([
   #                "Campfire",                                     # Player can also make a 'Campfire'
   #                "Stick"                                         # AND make a 'Stick'
   #             ], player)
   #             and state.sl_has_pack("Seeking Wisdom", player))   # AND has the 'Seeking Wisdom' pack
   
   # set_rule(world.get_entrance("Forward to Mainland: Moon 12", player),
   #          lambda state:
   #             state.sl_has_all_ideas([
   #                "Growth",                     # Player can also use 'Growth'
   #                "House"                       # AND can make a 'House'
   #             ], player)
   #             and state.sl_has_any_packs([
   #                "Reap & Sow",                 # AND has either the 'Reap & Sow'
   #                "Curious Cuisine"], player)   # OR 'Curious Cuisine' pack
   #          )
   
   # set_rule(world.get_entrance("Forward to Mainland: Moon 18", player),
   #          lambda state:
   #             state.sl_has_all_ideas([
   #             "Brick",                                  # Player can also 'Bricks'
   #             "Cooked Meat",                            # AND can make 'Cooked Meat'
   #             "Plank",                                  # AND can make 'Planks'
   #             "Offspring",                              # AND can make 'Offspring'
   #             "Shed",                                   # AND can make 'Shed'
   #             "Wooden Shield"                           # AND can make 'Wooden Shield'
   #          ], player)
   #          and state.sl_has_any_ideas([
   #             "Slingshot",                              # AND can make 'Slingshot'
   #             "Spear"], player)                         # OR can make 'Spear'
   #          and state.sl_has_pack("Explorers", player))  # AND has the 'Explorers' pack
   
   # set_rule(world.get_entrance("Forward to Mainland: Moon 24", player),
   #          lambda state:
   #             state.sl_has_all_ideas([
   #                "Iron Bar",                                        # Player can also make 'Iron Bar'
   #                "Smelter"                                          # AND can make 'Smelter'
   #             ], player)
   #             and state.sl_has_pack("Order and Structure", player)) # AND has the 'Order and Structure' pack
   
   # set_rule(world.get_entrance("Forward to Mainland: Moon 30", player),
   #          lambda state:
   #             state.sl_has_all_ideas([
   #                "Iron Shield",                            # Player can also make 'Iron Shield'
   #                "Smithy",                                 # AND can make 'Smithy'
   #                "Temple"                                  # AND can make 'Temple'
   #             ], player)
   #             and state.sl_has_any_ideas([
   #                "Sword",                                  # AND can make 'Sword'
   #                "Throwing Stars"                          # OR can make 'Throwing Star'
   #             ], player)
   #             and state.sl_has_pack("The Armory", player)) # AND has 'The Armory' pack
   
   # set_rule(world.get_entrance("Forward to Mainland: Moon 36", player),
   #          lambda state: True)  # If player can reach Moon 30 they can reach Moon 36

   
   

   #endregion

   #region Dark Forest Exit(s)

   #endregion

   #region Island Exit(s)

   set_rule(world.get_entrance("Portal from The Island to Dark Forest", player),
            lambda state:
               state.sl_stable_portal_from_island(player))                 # Can re-build a Stable Portal from Island resources

   set_rule(world.get_entrance("Rowboat from The Island to Mainland", player),
            lambda state:
               state.sl_rowboat_from_island(player))                       # Can re-build a rowboat from Island resources

   #endregion

#endregion

    #region 'Mainland' Quests

   if mainland_selected:

      #region 'Welcome' Quests

      set_rule(world.get_location("Open the Booster Pack", player),
               lambda state: True) # Can be performed immediately on Mainland

      set_rule(world.get_location("Drag the Villager on top of the Berry Bush", player),
               lambda state: True) # Can be performed immediately on Mainland

      set_rule(world.get_location("Mine a Rock using a Villager", player),
               lambda state: True) # Can be performed immediately on Mainland

      set_rule(world.get_location("Sell a Card", player),
               lambda state: True) # Can be performed immediately on Mainland

      set_rule(world.get_location("Buy the Humble Beginnings Pack", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)) # Player has the Humble Beginnings pack

      set_rule(world.get_location("Harvest a Tree using a Villager", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)) # Player has the Humble Beginnings pack

      set_rule(world.get_location("Make a Stick from Wood", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)    # Player has the Humble Beginnings pack
                  and state.sl_has_idea("Stick", player))   # AND has the 'Stick' idea

      # Set this rule only if Pausing is enabled
      if pausing_selected:
         set_rule(world.get_location("Pause using the play icon in the top right corner", player),
                  lambda state: True) # Can be performed immediately on Mainland

      set_rule(world.get_location("Grow a Berry Bush using Soil", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)  # Player has the Humble Beginnings pack
                  and state.sl_has_idea("Growth", player))        # AND has the 'Growth' Idea

      set_rule(world.get_location("Build a House", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)  # Player has the Humble Beginnings pack
                  and state.sl_has_idea("House", player))         # AND has the 'House' Idea

      set_rule(world.get_location("Get a Second Villager", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)) # Player has the Humble Beginnings pack

      set_rule(world.get_location("Create Offspring", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)              # Player has the Humble Beginnings pack
                  and state.sl_has_all_ideas(["House", "Offspring"], player)) # AND has the 'House' and 'Offspring' ideas

      #endregion

      #region 'The Grand Scheme' Quests

      set_rule(world.get_location("Unlock all Packs", player),
               lambda state:
                  state.count_group("All Mainland Booster Packs", player) == 8)

      set_rule(world.get_location("Get 3 Villagers", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_all_ideas([
                     "House",
                     "Offspring"
                  ], player))

      set_rule(world.get_location("Get 5 Villagers", player),
               lambda state:
                  state.can_reach_location("Get 3 Villagers", player)
                  and state.sl_has_all_packs(["Reap & Sow", "Seeking Wisdom"], player))

      set_rule(world.get_location("Get 7 Villagers", player),
               lambda state:
                  state.can_reach_location("Get 5 Villagers", player))

      set_rule(world.get_location("Find the Catacombs", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player))

      set_rule(world.get_location("Find a mysterious artifact", player),
               lambda state:
                  state.can_reach_location("Find the Catacombs", player))

      set_rule(world.get_location("Build a Temple", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "House",
                     "Iron Bar",
                     "Offspring",
                     "Plank",
                     "Smelter",
                     "Temple"
                  ], player))

      set_rule(world.get_location("Bring the Goblet to the Temple", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom",
                     "Explorers"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "House",
                     "Iron Bar",
                     "Offspring",
                     "Plank",
                     "Smelter",
                     "Temple"
                  ], player))

      set_rule(world.get_location("Kill the Demon", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom",
                     "Explorers"
                  ], player)
                  and state.sl_has_any_packs([
                     "Reap & Sow",
                     "Curious Cuisine"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Growth",
                     "House",
                     "Iron Bar",
                     "Offspring",
                     "Plank",
                     "Smelter",
                     "Temple"
                  ], player))
      
      #endregion

      #region 'Power & Skill' Quests

      set_rule(world.get_location("Train Militia", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_idea("Stick", player)
                  and state.sl_has_any_ideas(["Slingshot", "Spear"], player))

      set_rule(world.get_location("Kill a Rat", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player))

      set_rule(world.get_location("Kill a Skeleton", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers",
                     "The Armory"
                  ], player)
                  and state.sl_has_idea("Stick", player)
                  and state.sl_has_any_ideas([
                     "Magic Wand",
                     "Slingshot",
                     "Spear"
                  ], player))

      #endregion

      #region 'Strengthen Up' Quests

      set_rule(world.get_location("Make a Villager wear a Rabbit Hat", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player))

      set_rule(world.get_location("Build a Smithy", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure",
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Plank",
                     "Smelter",
                     "Smithy"
                  ], player))

      set_rule(world.get_location("Train a Wizard", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Magic Wand",
                     "Stick"
                  ], player))

      set_rule(world.get_location("Have a Villager with Combat Level 20", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_all_ideas([
                     "Plank",
                     "Stick",
                     "Wooden Shield"
                  ], player)
                  and state.sl_has_any_ideas([
                     "Magic Wand",
                     "Slingshot",
                     "Spear"
                  ], player))

      set_rule(world.get_location("Train a Ninja", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Plank",
                     "Smelter",
                     "Smithy",
                     "Throwing Stars"
                  ], player))

      #endregion

      #region 'Potluck' Quests

      set_rule(world.get_location("Start a Campfire", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_all_ideas([
                     "Campfire",
                     "Stick"
                  ], player))

      set_rule(world.get_location("Cook Raw Meat", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Reap & Sow"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Campfire",
                     "Cooked Meat",
                     "Stick"
                  ], player))

      set_rule(world.get_location("Cook an Omelette", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Reap & Sow"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Campfire",
                     "Omelette",
                     "Stick"
                  ], player))

      set_rule(world.get_location("Cook a Frittata", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Curious Cuisine",
                     "Reap & Sow"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Campfire",
                     "Frittata",
                     "Stick"
                  ], player))

      #endregion

      #region 'Discovery' Quests

      set_rule(world.get_location("Explore a Forest", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player))

      set_rule(world.get_location("Explore a Mountain", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player))

      set_rule(world.get_location("Open a Treasure Chest", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player))

      set_rule(world.get_location("Get a Dog", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player))

      set_rule(world.get_location("Find a Graveyard", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_all_ideas([
                     "House",
                     "Offspring"
                  ], player))

      set_rule(world.get_location("Train an Explorer", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player))

      set_rule(world.get_location("Buy something from a Travelling Cart", player),
               lambda state:
                  state.count_group("All Mainland Ideas", player) >= 15)

      #endregion

      #region 'Ways and Means' Quests

      set_rule(world.get_location("Have 5 Ideas", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.count_group("All Ideas", player) >= 5)

      set_rule(world.get_location("Have 10 Ideas", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.count_group("All Ideas", player) >= 10)

      set_rule(world.get_location("Have 10 Stone", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player))

      set_rule(world.get_location("Have 10 Wood", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player))

      set_rule(world.get_location("Get an Iron Bar", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Plank",
                     "Smelter"
                  ], player))

      set_rule(world.get_location("Have 5 Food", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player))

      set_rule(world.get_location("Have 10 Food", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player))

      set_rule(world.get_location("Have 20 Food", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Reap & Sow"
                  ], player))
                  # TODO: Add board capacity rule

      set_rule(world.get_location("Have 50 Food", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Curious Cuisine",
                     "Reap & Sow"
                  ], player))
                  # TODO: Add board capacity rule

      set_rule(world.get_location("Have 10 Coins", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player))

      set_rule(world.get_location("Have 30 Coins", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player))

      set_rule(world.get_location("Have 50 Coins", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_idea("Coin Chest", player))

      #endregion

      #region 'Construction' Quests

      set_rule(world.get_location("Have 3 Houses", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_idea("House", player))

      set_rule(world.get_location("Build a Shed", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_all_ideas([
                     "Shed",
                     "Stick"
                  ], player))

      set_rule(world.get_location("Build a Quarry", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_idea("Quarry", player))

      set_rule(world.get_location("Build a Lumber Camp", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_idea("Lumber Camp", player))

      set_rule(world.get_location("Build a Farm", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Farm",
                     "Plank"
                  ], player))

      set_rule(world.get_location("Build a Brickyard", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Brickyard",
                     "Iron Bar",
                     "Plank",
                     "Smelter"
                  ], player))

      set_rule(world.get_location("Sell a Card at a Market", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Market",
                     "Plank"
                  ], player))

      #endregion

      #region 'Longevity' Quests

      set_rule(world.get_location("Reach Moon 6", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.count_group("All Mainland Ideas", player) >= 5)

      set_rule(world.get_location("Reach Moon 12", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.count_group("All Ideas", player) >= 10)

      set_rule(world.get_location("Reach Moon 18", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.count_group("All Booster Packs", player) >= 2
                  and state.count_group("All Ideas", player) >= 15)

      set_rule(world.get_location("Reach Moon 24", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.count_group("All Booster Packs", player) >= 3
                  and state.count_group("All Mainland Ideas", player) >= 20)

      set_rule(world.get_location("Reach Moon 30", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.count_group("All Booster Packs", player) >= 4
                  and state.count_group("All Mainland Ideas", player) >= 25)

      set_rule(world.get_location("Reach Moon 36", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.count_group("All Booster Packs", player) >= 5
                  and state.count_group("All Mainland Ideas", player) >= 30)

      #endregion

      #region Additional Archipelago Quests

      # Booster Packs
      set_rule(world.get_location("Buy the Seeking Wisdom Pack", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player))

      set_rule(world.get_location("Buy the Reap & Sow Pack", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Reap & Sow"
                  ], player))

      set_rule(world.get_location("Buy the Curious Cuisine Pack", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Curious Cuisine"
                  ], player))

      set_rule(world.get_location("Buy the Logic and Reason Pack", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Logic and Reason"
                  ], player))

      set_rule(world.get_location("Buy the The Armory Pack", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "The Armory"
                  ], player))

      set_rule(world.get_location("Buy the Explorers Pack", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player))

      set_rule(world.get_location("Buy the Order and Structure Pack", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Order and Structure"
                  ], player))

      # Buying Packs
      set_rule(world.get_location("Buy 5 Booster Packs", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player))

      set_rule(world.get_location("Buy 10 Booster Packs", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.count_group("All Booster Packs", player) >= 2)

      set_rule(world.get_location("Buy 25 Booster Packs", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.count_group("All Booster Packs", player) >= 3)

      # Selling Cards
      set_rule(world.get_location("Sell 5 Cards", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player))

      set_rule(world.get_location("Sell 10 Cards", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player))

      set_rule(world.get_location("Sell 25 Cards", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player))

      # Building Structures
      set_rule(world.get_location("Build a Coin Chest", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_idea("Coin Chest", player))

      set_rule(world.get_location("Build a Garden", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_idea("Garden", player))

      set_rule(world.get_location("Build an Iron Mine", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_idea("Iron Mine", player))

      set_rule(world.get_location("Build a Hotpot", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Hotpot",
                     "Iron Bar",
                     "Plank",
                     "Smelter"
                  ], player)
                  and (
                     state.sl_has_idea("Stove", player)
                     or state.sl_has_all_ideas(["Campfire", "Stick"], player)
                  ))

      set_rule(world.get_location("Build a Market", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Market",
                     "Plank"
                  ], player))

      set_rule(world.get_location("Build a Resource Chest", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Plank",
                     "Resource Chest",
                     "Smelter"
                  ], player))

      set_rule(world.get_location("Build a Sawmill", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Plank",
                     "Sawmill",
                     "Smelter"
                  ], player))

      set_rule(world.get_location("Build a Smelter", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Plank",
                     "Smelter"
                  ], player))

      set_rule(world.get_location("Build a Stove", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Plank",
                     "Smelter",
                     "Stove"
                  ], player))

      set_rule(world.get_location("Build a Warehouse", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Plank",
                     "Smelter",
                     "Warehouse"
                  ], player))
      
      # Making Weapons
      set_rule(world.get_location("Make an Iron Shield", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Iron Shield",
                     "Plank",
                     "Smelter",
                     "Smithy"
                  ], player))
      
      set_rule(world.get_location("Make a Magic Wand", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Magic Wand",
                     "Stick"
                  ], player))
      
      set_rule(world.get_location("Make a Slingshot", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                  ], player)
                  and state.sl_has_all_ideas([
                     "Slingshot",
                     "Stick"
                  ], player))
      
      set_rule(world.get_location("Make a Spear", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                  ], player)
                  and state.sl_has_all_ideas([
                     "Spear",
                     "Stick"
                  ], player))
      
      set_rule(world.get_location("Make a Sword", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Plank",
                     "Smelter",
                     "Sword",
                     "Stick"
                  ], player))
      
      set_rule(world.get_location("Make Throwing Stars", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Plank",
                     "Smelter",
                     "Smithy",
                     "Throwing Stars"
                  ], player))
      
      set_rule(world.get_location("Make a Wooden Shield", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Plank",
                     "Stick",
                     "Wooden Shield"
                  ], player))

      # Making Food
      set_rule(world.get_location("Cook a Stew", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Curious Cuisine",
                     "Reap & Sow"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Campfire",
                     "Stew",
                     "Stick"
                  ], player))

      set_rule(world.get_location("Make a Fruit Salad", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_any_packs([
                     "Curious Cuisine",
                     "Reap & Sow"
                  ], player)
                  and state.sl_has_idea("Fruit Salad", player))

      set_rule(world.get_location("Make a Milkshake", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Curious Cuisine",
                  ], player)
                  and state.sl_has_idea("Milkshake", player))

      # Having Resources
      set_rule(world.get_location("Have 10 Bricks", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_idea("Brick", player))

      set_rule(world.get_location("Have 10 Iron Bars", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player)
                  and state.sl_has_all_ideas([
                     "Brick",
                     "Iron Bar",
                     "Plank",
                     "Smelter",
                     "Warehouse"
                  ], player))

      set_rule(world.get_location("Have 10 Iron Ore", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_any_packs([
                     "Logic and Reason",
                     "Order and Structure"
                  ], player))

      set_rule(world.get_location("Have 10 Flint", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player))

      set_rule(world.get_location("Have 10 Planks", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Seeking Wisdom"
                  ], player)
                  and state.sl_has_idea("Plank", player))

      set_rule(world.get_location("Have 10 Sticks", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_idea("Stick", player))

      # Exploring Locations
      set_rule(world.get_location("Explore a Catacombs", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player))

      set_rule(world.get_location("Explore a Graveyard", player),
               lambda state:
                  state.sl_has_pack("Humble Beginnings", player)
                  and state.sl_has_all_ideas([
                     "House",
                     "Offspring"
                  ], player))

      set_rule(world.get_location("Explore an Old Village", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player))

      set_rule(world.get_location("Explore a Plains", player),
               lambda state:
                  state.sl_has_all_packs([
                     "Humble Beginnings",
                     "Explorers"
                  ], player))
      
      #endregion

   #region Events

   # set_rule(world.get_location("Milestone: Advanced Equipment", player),
   #          lambda state:
   #             state.has_all(["Iron Bars"], player)                      # Requires ability to make Iron Bars
   #             and state.sl_has_all_ideas(["Iron Shield", "Smithy"], player)        # AND 'Iron Shield' and 'Smithy' ideas
   #             and state.sl_has_any_ideas(["Sword", "Throwing Stars"], player))     # AND 'Sword' OR 'Throwing Stars' ideas

   # set_rule(world.get_location("Milestone: Basic Equipment", player),
   #          lambda state:
   #             state.sl_has_humble_beginnings(player)                                     # Requires Humble Beginnings
   #             and state.has("Sustainable Village", player)                               # AND a sustainable village
   #             and state.sl_has_pack("Seeking Wisdom", player)                            # AND Seeking Wisdom pack
   #             and state.sl_has_all_ideas(["Plank", "Stick", "Wooden Shield"], player)    # AND 'Plank', 'Stick' and 'Wooden Shield' ideas
   #             and state.sl_has_any_ideas(["Slingshot", "Spear"], player))                # AND 'Slingshot' OR 'Spear' idea
   
   # set_rule(world.get_location("Milestone: Iron Bars", player),
   #          lambda state:
   #             state.sl_has_humble_beginnings(player)                                           # Requires Humble Beginnings
   #             and state.has("Basic Equipment", player)                                   # AND basic equipment
   #             and state.sl_has_all_packs(["Order and Structure"], player)                      # AND the 'Order and Structure' pack
   #             and state.sl_has_all_ideas(["Brick", "Plank", "Iron Bar", "Smelter"], player))   # AND the 'Brick', 'Plank', 'Iron Bar' and 'Smelter' ideas

   # set_rule(world.get_location("Milestone: Basic Cooking", player),
   #          lambda state:
   #             state.sl_has_humble_beginnings(player)                                                    # Requires Humble Beginnings
   #             and state.sl_has_all_packs(["Seeking Wisdom", "Reap & Sow", "Curious Cuisine"], player)   # AND Reap & Sow and Curious Cuisine packs
   #             and state.sl_has_all_ideas(["Campfire", "Cooked Meat", "Growth", "Stick"], player)        # AND the 'Campfire', 'Cooked Meat', 'Growth' and 'Stick' ideas
   #             and state.sl_has_any_ideas(["Frittata", "Fruit Salad", "Milkshake", "Omelette"], player)) # AND 'Frittata', OR 'Fruit Salad' OR 'Milkshake' OR 'Omelette' idea

   # set_rule(world.get_location("Milestone: Offspring", player),
   #          lambda state:
   #             state.sl_has_humble_beginnings(player)                         # Requires Humble Beginnings
   #             and state.sl_has_all_packs(["Seeking Wisdom"], player)         # AND Seeking Wisdom and Reap & Sow packs
   #             and state.sl_has_all_ideas(["House", "Offspring"], player))    # AND the 'House' and 'Offspring' ideas

   # set_rule(world.get_location("Milestone: Sustainable Village", player),
   #          lambda state:
   #             state.has_all(["Cooking", "Offspring"], player)                # Reqiores ability to Cook and create Offspring
   #             and state.sl_mainland_board_capacity(options, player) >= 7)    # AND at least one warehouse worth of expansion

   # set_rule(world.get_location("Kill the Demon", player),
   #             lambda state:
   #                state.can_reach_location("Bring the Goblet to the Temple", player))

   #endregion

   #endregion

   #region 'The Dark Forest' Quests

   if forest_selected:

      set_rule(world.get_location("Find the Dark Forest", player),
               lambda state: state.sl_can_reach_any_quests(["Build a Stable Portal", "Reach Moon 12"], player)) # Player can reach Moon 12 for Strange Portals or build a Stable Portal

      set_rule(world.get_location("Complete the first wave", player),
               lambda state:
                  state.can_reach_location("Find the Dark Forest", player)                        # Player can reach The Dark Forest
                  and state.sl_can_reach_any_quests(["Train Militia", "Train a Wizard"], player)) # AND has access to basic weapons

      set_rule(world.get_location("Build a Stable Portal", player),
               lambda state:
                  state.sl_can_progress_mainland(player)                             # Player can start Mainland
                  and state.sl_has_pack("Explorers", player)                      # AND has pack containing 'Magic Dust'
                  and state.sl_has_all_ideas(["Brick", "Stable Portal"], player)) # AND has 'Brick' and 'Stable Portal' ideas

      set_rule(world.get_location("Get to Wave 6", player),
               lambda state:
                  state.sl_can_reach_all_quests([
                     "Complete the first wave",  # Player can complete the first wave
                     "Kill a Skeleton",          # AND has access to weapons and shield
                     "Create Offspring",         # AND can create villagers
                     "Cook Raw Meat"], player))  # AND has access to cooking

      set_rule(world.get_location("Fight the Wicked Witch", player),
               lambda state:
                  state.sl_can_reach_all_quests(["Get to Wave 6", "Train a Ninja"], player)) # Player can complete 6 waves and has all weapons

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
                  state.sl_can_progress_island(player))              # Player can start The Island

      set_rule(world.get_location("Make Rope", player),
               lambda state:
                  state.sl_can_progress_island(player)                  # Player can start The Island
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
                  state.sl_can_progress_island(player)                               # Player can start The Island
                  and state.count_group("All Island Booster Packs", player) == 6) # AND has all booster packs

      set_rule(world.get_location("Find a Treasure Map", player),
               lambda state:
                  state.sl_can_progress_island(player)                   # Player can start The Island
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
                  state.sl_can_progress_island(player)            # Player can start The Island
                  and state.sl_has_idea("Sushi", player))         # AND has the 'Sushi' idea

      set_rule(world.get_location("Cook Crab Meat", player),
               lambda state:
                  state.sl_can_progress_island(player)                   # Player can start The Island
                  and state.sl_has_pack("Grilling and Brewing", player)  # AND has pack containing Crab
                  and state.sl_has_idea("Campfire", player))             # AND player has 'Campfire' idea

      set_rule(world.get_location("Make Ceviche", player),
               lambda state:
                  state.sl_can_progress_island(player)                                                # Player can start The Island
                  and state.sl_has_any_packs([ "Grilling and Brewing", "Island Insights" ], player)   # AND has a pack containing Lime
                  and state.sl_has_idea("Ceviche", player))                                           # AND has the 'Ceviche' idea

      set_rule(world.get_location("Make a Seafood Stew", player),
               lambda state:
                  state.sl_can_progress_island(player)                                                # Player can start The Island
                  and state.sl_has_any_packs([ "Grilling and Brewing", "Island Insights" ], player)   # AND has a pack containing Crab and Chili Pepper
                  and state.sl_has_all_ideas(["Campfire", "Seafood Stew" ], player))                  # AND has 'Campfire' and 'Seafood Stew' ideas

      set_rule(world.get_location("Make a Bottle of Rum", player),
               lambda state:
                  state.can_reach_location("Make Glass", player)                                  # Player can make glass
                  and state.sl_has_any_packs([ "Advanced Archipelago", "Enclave Explorers" ], player) # AND has a pack containing 'Spring'
                  and state.sl_has_all_ideas([ "Bottle of Rum", "Distillery", "Stove" ], player))     # AND has 'Bottle of Rum', 'Distillery' and 'Stove' ideas

      #endregion

      #region 'Island Ambitions' Category

      set_rule(world.get_location("Have 10 Shells", player),
               lambda state:
                  state.sl_can_progress_island(player)               # Player can start The Island
                  and state.sl_has_pack("On the Shore", player))  # AND has the 'On the Shore' pack

      set_rule(world.get_location("Get a Villager Drunk", player),
               lambda state:
                  state.can_reach_location("Make a Bottle of Rum", player)) # Player can make a bottle of rum

      set_rule(world.get_location("Make Sandstone", player),
               lambda state:
                  state.sl_can_progress_island(player)               # Player can start The Island
                  and state.sl_has_idea("Sandstone", player))     # AND has the 'Sandstone' idea

      set_rule(world.get_location("Build a Mess Hall", player),
               lambda state:
                  state.sl_can_progress_island(player)                                   # Player can start The Island
                  and state.sl_has_all_ideas([ "Campfire", "Mess Hall" ], player))    # AND has the 'Campfire' and 'Mess Hall' ideas

      set_rule(world.get_location("Build a Greenhouse", player),
               lambda state:
                  state.sl_can_reach_all_quests([ "Build a Composter", "Make Glass" ], player)  # Player can make Composter / Glass / Iron Bars
                  and state.sl_has_idea("Greenhouse", player))                                                     # AND has the 'Greenhouse' idea

      set_rule(world.get_location("Have a Poisoned Villager", player),
               lambda state:
                  state.sl_can_progress_island(player)                      # Player can start The Island
                  and state.sl_has_pack("Enclave Explorers", player))    # AND has a pack that contains a Snake

      set_rule(world.get_location("Cure a Poisoned Villager", player),
               lambda state:
                  state.can_reach_location("Have a Poisoned Villager", player)    # Player can poison a villager
                  and state.sl_has_all_ideas([ "Campfire", "Charcoal" ], player)) # AND has the 'Campfire' and 'Charcoal' ideas

      set_rule(world.get_location("Build a Composter", player),
               lambda state:
                  state.sl_can_progress_island(player)               # Player can start The Island
                  and state.sl_has_idea("Composter", player))     # AND has the 'Composter' idea

      set_rule(world.get_location("Bribe a Pirate Boat", player),
               lambda state:
                  state.can_reach_location("Build a Sloop", player))   # Player can build a Sloop (to bring coins back)

      set_rule(world.get_location("Befriend a Pirate", player),
               lambda state:
                  state.sl_can_progress_island(player)                                                       # Player can start The Island
                  and state.sl_has_any_packs([ "Enclave Explorers", "Grilling and Brewing" ], player))    # AND has a pack containing Parrot

      set_rule(world.get_location("Make a Gold Bar", player),
               lambda state:
                  state.sl_can_progress_island(player)                                                       # Player can start The Island
                  and state.sl_has_any_packs([ "Advanced Archipelago", "Enclave Explorers" ], player)     # AND has a pack containing Gold Deposit
                  and state.sl_has_idea("Gold Bar", player))                                              # AND player has 'Gold Bar' idea

      set_rule(world.get_location("Make Glass", player),
               lambda state:
                  state.sl_can_progress_island(player)                                                       # Player can start The Island
                  and state.sl_has_idea("Glass", player))                                                 # AND player has 'Glass' idea

      #endregion

      #region 'Strengthen Up' Category

      set_rule(world.get_location("Train an Archer", player),
               lambda state:
                  state.can_reach_location("Make Rope", player)   # Player can make Rope
                  and state.sl_has_idea("Bow", player))           # AND has the 'Bow' idea

      set_rule(world.get_location("Break a Bottle", player),
               lambda state:
                  state.sl_can_progress_island(player)                                                       # Player can start The Island
                  and state.sl_has_all_ideas([ "Campfire", "Broken Bottle", "Empty Bottle" ], player))    # AND has 'Campfire', 'Broken Bottle' and 'Empty Bottle' ideas

      set_rule(world.get_location("Equip an Archer with a Quiver", player),
               lambda state:
                  state.sl_can_reach_all_quests([ "Train an Archer", "Train Militia" ], player))          # Player can train an Archer and fight mobs to gain Quiver

      set_rule(world.get_location("Make a Villager wear Crab Scale Armor", player),
               lambda state:
                  state.sl_can_progress_island(player)                                                   # Player can start The Island
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
               lambda state: state.can_reach_location("Kill a Skeleton", player))    # Player has weapons and explorers / armory

      set_rule(world.get_location("Kill an Elf", player),
               lambda state:
                  state.sl_can_reach_any_quests(["Kill a Skeleton", "Complete the first wave"], player)   # Player can get to Dark Forest or make it to Moon 24
                  if forest_selected else
                  state.can_reach_location("Kill a Skeleton", player))

      set_rule(world.get_location("Kill an Elf Archer", player),
               lambda state: state.can_reach_location("Kill an Elf", player)) # Player can get to Dark Forest or make it to Moon 24

      set_rule(world.get_location("Kill an Enchanted Shroom", player),
               lambda state: state.can_reach_location("Kill an Elf", player)) # Player can get to Dark Forest or make it to Moon 24

      set_rule(world.get_location("Kill a Feral Cat", player),
               lambda state: state.can_reach_location("Kill an Elf", player)) # Player can get to Dark Forest or make it to Moon 24 or find Ruins

      set_rule(world.get_location("Kill a Frog Man", player),
               lambda state:
                  state.can_reach_location("Kill a Skeleton", player)         # Player has weapons and explorers / armory
                  or (                                                        # OR
                     state.sl_can_progress_island(player)                       # Player can start The Island
                     and state.sl_has_pack("Advanced Archipelago", player)   # AND has the 'Advanced Archipelago' pack
                  ))

      set_rule(world.get_location("Kill a Ghost", player),
               lambda state: state.can_reach_location("Kill an Elf", player)) # Player can get to Dark Forest or make it to Moon 24

      set_rule(world.get_location("Kill a Giant Rat", player),
               lambda state: state.can_reach_location("Kill a Skeleton", player))    # Player has weapons and explorers / armory

      set_rule(world.get_location("Kill a Giant Snail", player),
               lambda state: state.can_reach_location("Kill an Elf", player)) # Player can get to Dark Forest or make it to Moon 24

      set_rule(world.get_location("Kill a Goblin", player),
               lambda state:
                  state.can_reach_location("Have a Villager with Combat Level 20", player)    # Player has basic weapon and shield
                  and state.sl_has_pack("Explorers", player))                                 # AND has pack containing 'Goblin'

      set_rule(world.get_location("Kill a Goblin Archer", player),
               lambda state: state.can_reach_location("Kill a Goblin", player))   # Player has basic weapon and packs containing 'Goblin Archer'

      set_rule(world.get_location("Kill a Goblin Shaman", player),
               lambda state: state.can_reach_location("Kill a Skeleton", player))    # Player has weapons and explorers / armory

      set_rule(world.get_location("Kill a Merman", player),
               lambda state:
                  state.can_reach_location("Kill a Frog Man", player)     # Player has weapons and explorers / armory or can reach island with packs containing 'Merman'
                  or (
                     forest_selected
                     and state.can_reach_location("Complete the first wave", player)  # OR can complete a wave of The Dark Forest
                  ))

      set_rule(world.get_location("Kill a Mimic", player),
               lambda state:
                  state.sl_can_reach_any_quests(["Kill a Skeleton", "Get to Wave 6"], player) # Player has weaapons and Armory / Explorers or can get to Wave 6 of Dark Forest
                  if forest_selected else
                  state.can_reach_location("Kill a Skeleton", player))

      set_rule(world.get_location("Kill a Mosquito", player),
               lambda state: state.can_reach_location("Kill a Merman", player))   # Player has weapons and explorers / armory or can reach island with packs containing 'Mosquito' or complete first wave of forest

      set_rule(world.get_location("Kill a Slime", player),
               lambda state: state.can_reach_location("Kill a Skeleton", player)) # Player has weapons and explorers / armory

      set_rule(world.get_location("Kill a Small Slime", player),
               lambda state: state.can_reach_location("Kill a Slime", player))    # Player can find and kill a slime

      set_rule(world.get_location("Kill a Wolf", player),
               lambda state: state.can_reach_location("Get a Dog", player)) # Player has packs containing 'Wolf'

      # Only apply these rules if The Dark Forest is enabled
      if forest_selected:

         set_rule(world.get_location("Kill a Dark Elf", player),
               lambda state: state.can_reach_location("Get to Wave 6", player)) # Found in The Dark Forest from Wave 4

         set_rule(world.get_location("Kill an Ent", player),
               lambda state: state.can_reach_location("Get to Wave 6", player)) # Found in The Dark Forest from Wave 4

         set_rule(world.get_location("Kill an Ogre", player),
               lambda state: state.can_reach_location("Get to Wave 6", player)) # Found in The Dark Forest from Wave 4

         set_rule(world.get_location("Kill an Orc Wizard", player),
               lambda state: state.can_reach_location("Get to Wave 6", player)) # Found in The Dark Forest from Wave 4

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
                  state.sl_can_progress_island(player))   # Found in 'On the Shore' pack

         set_rule(world.get_location("Kill a Shark", player),
               lambda state:
                  state.can_reach_location("Make a Fish Trap", player)) # Found using Fish Trap with Raw Meat

         set_rule(world.get_location("Kill a Snake", player),
               lambda state:
                  state.sl_can_progress_island(player)                   # Player can start The Island
                  and state.sl_has_pack("Enclave Explorers", player)) # AND has Enclave Explorers pack

         set_rule(world.get_location("Kill a Tentacle", player),
               lambda state:
                  state.can_reach_location("Open the Sacred Chest", player)) # Found after opening sacred chest

         set_rule(world.get_location("Kill a Tiger", player),
               lambda state:
                  state.sl_can_progress_island(player)                                               # Player can start The Island
                  and state.sl_can_reach_any_quests(["Train Militia", "Train a Wizard"], player)  # AND has access to basic weapons
                  and state.sl_has_pack("Enclave Explorers", player))                             # AND has pack containing 'Tiger'

      # Apply these rules if either Forest or Island are enabled
      if forest_selected or island_selected:

         set_rule(world.get_location("Kill a Pirate", player),
               lambda state:
                  (forest_selected and state.can_reach_location("Get to Wave 6", player))             # Found after Dark Forest Wave 4
                  or (island_selected and state.can_reach_location("Bribe a Pirate Boat", player)))   # OR on Pirate Boat

   #endregion

   #region 'Packsanity Quests'

   if packsanity_selected:

      # set_rule(world.get_location("Buy the Seeking Wisdom Pack", player),
      #          lambda state:
      #             state.sl_can_progress_mainland(player)                 # Player can start Mainland
      #             and state.sl_has_pack("Seeking Wisdom", player))    # AND has 'Seeking Wisdom' pack

      # set_rule(world.get_location("Buy the Reap & Sow Pack", player),
      #          lambda state:
      #             state.sl_can_progress_mainland(player)             # Player can start Mainland
      #             and state.sl_has_pack("Reap & Sow", player))    # AND has 'Reap & Sow' pack

      # set_rule(world.get_location("Buy the Curious Cuisine Pack", player),
      #          lambda state:
      #             state.sl_can_progress_mainland(player)                 # Player can start Mainland
      #             and state.sl_has_pack("Curious Cuisine", player))   # AND has 'Curious Cuisine' pack

      # set_rule(world.get_location("Buy the Logic and Reason Pack", player),
      #          lambda state:
      #             state.sl_can_progress_mainland(player)                 # Player can start Mainland
      #             and state.sl_has_pack("Logic and Reason", player))  # AND has 'Logic and Reason' pack

      # set_rule(world.get_location("Buy the The Armory Pack", player),
      #          lambda state:
      #             state.sl_can_progress_mainland(player)             # Player can start Mainland
      #             and state.sl_has_pack("The Armory", player))    # AND has 'The Armory' pack

      # set_rule(world.get_location("Buy the Explorers Pack", player),
      #          lambda state:
      #             state.sl_can_progress_mainland(player)             # Player can start Mainland
      #             and state.sl_has_pack("Explorers", player))    # AND has 'Explorers' pack

      # set_rule(world.get_location("Buy the Order and Structure Pack", player),
      #          lambda state:
      #             state.sl_can_progress_mainland(player)                     # Player can start Mainland
      #             and state.sl_has_pack("Order and Structure", player))   # AND has 'Order and Structure' pack

      # Apply these rules if The Island board is selected
      if island_selected:

         set_rule(world.get_location("Buy the On the Shore Pack", player),
               lambda state:
                  state.sl_can_progress_island(player))  # Player can reach island and has On the Shore pack

         set_rule(world.get_location("Buy the Island of Ideas Pack", player),
               lambda state:
                  state.sl_can_progress_island(player)                   # Player can reach The Island
                  and state.sl_has_pack("Island of Ideas", player))   # AND has 'Island of Ideas' pack

         set_rule(world.get_location("Buy the Grilling and Brewing Pack", player),
               lambda state:
                  state.sl_can_progress_island(player)                       # Player can reach The Island
                  and state.sl_has_pack("Grilling and Brewing", player))  # AND has 'Grilling and Brewing' pack

         set_rule(world.get_location("Buy the Island Insights Pack", player),
               lambda state:
                  state.sl_can_progress_island(player)                   # Player can reach The Island
                  and state.sl_has_pack("Island Insights", player))   # AND has 'Island of Ideas' pack

         set_rule(world.get_location("Buy the Advanced Archipelago Pack", player),
               lambda state:
                  state.sl_can_progress_island(player)                       # Player can reach The Island
                  and state.sl_has_pack("Advanced Archipelago", player))  # AND has 'Advanced Archipelago' pack

         set_rule(world.get_location("Buy the Enclave Explorers Pack", player),
               lambda state:
                  state.sl_can_progress_island(player)                   # Player can reach The Island
                  and state.sl_has_pack("Enclave Explorers", player)) # AND has 'Enclave Explorers' pack

   #endregion

   # TODO: Re-write these
   # If spendsanity enabled, include spendsanity checks in rules
   if spendsanity_selected:
      for x in range(1, options.spendsanity_count.value + 1):
         set_rule(world.get_location("Buy {count} Spendsanity Packs".format(count=x), player),
                  lambda state: state.sl_can_progress_mainland(player))

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
            lambda state:
               (not mainland_selected or state.can_reach_location("Kill the Demon", player))
               and (not forest_selected or state.can_reach_location("Fight the Wicked Witch", player))
               and (not island_selected or state.can_reach_location("Kill the Demon Lord", player)))

   # Set completion condition
   world.completion_condition[player] = lambda state: state.has("Victory", player)