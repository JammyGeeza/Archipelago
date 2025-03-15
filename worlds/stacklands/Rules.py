from typing import List
from BaseClasses import MultiWorld
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import set_rule

class StacklandsLogic(LogicMixin):

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


# Set all region and location rules
def set_rules(world: MultiWorld, player: int):
      
    # Region checks (to be implemented later)
    region_checks = {
        "Mainland": lambda state: True
    }

    # Get relevant options
    goal = world.worlds[player].options.goal.value
    pause_enabled = world.worlds[player].options.pause_enabled.value

    # Amounts
    set_rule(world.get_location("Have 10 Coins", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Have 30 Coins", player),
             lambda state: state.sl_has_idea("Coin Chest", player) and # <- Shed for helping with storage space >= 30 Coins
                           state.can_reach_location("Have 10 Coins", player))
    
    set_rule(world.get_location("Have 50 Coins", player), 
             lambda state: state.can_reach_location("Have 30 Coins", player))

    set_rule(world.get_location("Have 5 Food", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Have 10 Food", player),
             lambda state: state.can_reach_location("Have 5 Food", player))
    
    set_rule(world.get_location("Have 20 Food", player),
             lambda state: state.can_reach_location("Build a Shed", player) and # <- Shed for helping with storage space >= 20 food
                           state.can_reach_location("Have 10 Food", player))
    
    set_rule(world.get_location("Have 50 Food", player),
             lambda state: state.can_reach_location("Have 20 Food", player))
    
    set_rule(world.get_location("Have 3 Houses", player),
             lambda state: state.can_reach_location("Build a House", player))
    
    set_rule(world.get_location("Have 5 Ideas", player),
             lambda state: state.count_group("All Ideas", player) >= 5)
    
    set_rule(world.get_location("Have 10 Ideas", player),
             lambda state: state.count_group("All Ideas", player) >= 10)
    
    set_rule(world.get_location("Have 10 Stone", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Have 10 Wood", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    # Durations
    set_rule(world.get_location("Reach Moon 6", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Reach Moon 12", player),
             lambda state: state.sl_has_pack("Seeking Wisdom", player) and # <- Trialling to help increase chance of unrequired pack drops
                           state.can_reach_location("Reach Moon 6", player))
    
    set_rule(world.get_location("Reach Moon 24", player),
             lambda state: state.sl_has_pack("Logic and Reason", player) and # <- Trialling to help increase chance of unrequired pack drops
                           state.can_reach_location("Reach Moon 12", player))
    
    set_rule(world.get_location("Reach Moon 24", player),
             lambda state: state.can_reach_location("Reach Moon 36", player)) # <- Trialling to help increase chance of unrequired pack drops

    # Miscellaneous
    set_rule(world.get_location("Buy the Humble Beginnings Pack", player),
             lambda state: state.sl_has_pack("Humble Beginnings", player))
    
    set_rule(world.get_location("Sell a Card at a Market", player),
             lambda state: state.sl_has_all_ideas(["Market", "Brick", "Plank"], player) and
                           state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Unlock all Packs", player),
             lambda state: state.has_group_unique("All Booster Packs", player, 8))
    
    
    
    # 'Starting' Path - Quests that can be achieved immediately
    set_rule(world.get_location("Open the Booster Pack", player), lambda state: True)
    
    set_rule(world.get_location("Drag the Villager on top of the Berry Bush", player), lambda state: True)
    
    set_rule(world.get_location("Mine a Rock using a Villager", player), lambda state: True)
    
    set_rule(world.get_location("Sell a Card", player), lambda state: True)

    if pause_enabled: # <- Set location rule only if pausing is enabled
        set_rule(world.get_location("Pause using the play icon in the top right corner", player),
                    lambda state: True) 

    # 'Combat' Path
    set_rule(world.get_location("Train Militia", player),
             lambda state: state.has_any(set(["Idea: Slingshot", "Idea: Spear"]), player) and
                           state.sl_has_pack("Explorers", player) and
                           state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Train a Wizard", player),
             lambda state: state.sl_has_idea("Magic Wand", player) and
                           state.sl_has_pack("Explorers", player) and
                           state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Kill a Skeleton", player), # <- Minimum requirement for goal path (trialling this)
             lambda state: state.sl_has_pack("The Armory", player) and
                           state.can_reach_location("Train Militia", player) and
                           state.can_reach_location("Train a Wizard", player))
    
    set_rule(world.get_location("Train a Ninja", player), # <- Not required for goal path, but useful
             lambda state: state.sl_has_idea("Throwing Stars", player) and
                           state.can_reach_location("Kill a Skeleton", player))
    
    set_rule(world.get_location("Train an Archer", player), # <- Not required for goal path
             lambda state: state.sl_has_pack("Explorers", player) and
                           state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Equip an Archer with a Quiver", player), # <- Not required for goal path
             lambda state: state.can_reach_location("Train an Archer", player))
    
    set_rule(world.get_location("Make a Villager wear a Rabbit Hat", player), # <- Not required for goal path
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))

    set_rule(world.get_location("Have a Villager with Combat Level 20", player), # <- Not required for goal path
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Kill a Rat", player),  # <- Not required for goal path
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))

    # 'Cooking' Path
    set_rule(world.get_location("Make a Stick from Wood", player),
             lambda state: state.sl_has_idea("Stick", player) and
                           state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Start a Campfire", player),
             lambda state: state.sl_has_idea("Campfire", player) and
                           state.can_reach_location("Make a Stick from Wood", player))
    
    set_rule(world.get_location("Cook Raw Meat", player),
             lambda state: state.sl_has_idea("Cooked Meat", player) and
                           state.sl_has_pack("Reap & Sow", player) and # <- To help balance booster pack progression
                           state.can_reach_location("Start a Campfire", player))
    
    set_rule(world.get_location("Cook an Omelette", player), # <- Minimum requirement for goal path
             lambda state: state.sl_has_all_ideas(["Omelette", "Stove"], player) and
                           state.can_reach_location("Cook Raw Meat", player))
    
    set_rule(world.get_location("Cook a Frittata", player), # <- Not required for goal path, but useful to have
             lambda state: state.sl_has_idea("Frittata", player) and
                           state.sl_has_pack("Curious Cuisine", player) and # <- To help balance booster pack progression
                           state.can_reach_location("Cook an Omelette", player))
    
    # 'Brick' Path
    set_rule(world.get_location("Build a Quarry", player),
             lambda state: state.sl_has_idea("Quarry", player) and
                           state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Build a Brickyard", player),
             lambda state: state.sl_has_idea("Brickyard", player) and
                           state.can_reach_location("Get an Iron Bar", player) and # <- 'Brick' / 'Iron Bar' / 'Smelter' included in path
                           state.can_reach_location("Build a Quarry", player))
    
    # 'Exploring' Path
    set_rule(world.get_location("Find a Graveyard", player),
             lambda state: state.sl_has_all_packs(["Humble Beginnings", "Explorers"], player))
    
    set_rule(world.get_location("Find a mysterious artifact", player), # <- Minimum requirement for goal path
             lambda state: state.can_reach_location("Find a Graveyard", player))
    
    set_rule(world.get_location("Find the Catacombs", player), # <- Not required for goal path
             lambda state: state.can_reach_location("Find a mysterious artifact", player))
    
    set_rule(world.get_location("Open a Treasure Chest", player), # <- Not required for goal path
             lambda state: state.can_reach_location("Find a mysterious artifact", player))
    
    set_rule(world.get_location("Get a Dog", player), # <- Not required for goal path
             lambda state: state.can_reach_location("Find a mysterious artifact", player))
    
    set_rule(world.get_location("Train an Explorer", player), # <- Not required for goal path
             lambda state: state.can_reach_location("Find a mysterious artifact", player))
    
    set_rule(world.get_location("Explore a Forest", player), # <- Not required for goal path
             lambda state: state.can_reach_location("Find a mysterious artifact", player))
    
    set_rule(world.get_location("Explore a Mountain", player), # <- Not required for goal path
             lambda state: state.can_reach_location("Find a mysterious artifact", player))

    # 'Farming' Path
    set_rule(world.get_location("Grow a Berry Bush using Soil", player),
             lambda state: state.sl_has_all_ideas(["Growth", "Garden"], player) and
                           state.can_reach_location("Have 5 Food", player))
    
    set_rule(world.get_location("Build a Shed", player),
             lambda state: state.sl_has_idea("Shed", player) and
                           state.can_reach_location("Grow a Berry Bush using Soil", player))
    
    set_rule(world.get_location("Build a Farm", player), # <- Minimum requirement for goal
             lambda state: state.sl_has_all_ideas(["Farm", "Brick", "Plank"], player) and
                           state.sl_has_pack("Reap & Sow", player) and # <- To help balance booster pack progression
                           state.can_reach_location("Build a Shed", player))

    # 'Iron Bar' Path   
    set_rule(world.get_location("Get an Iron Bar", player),
             lambda state: state.sl_has_all_ideas(["Iron Bar", "Smelter", "Brick", "Plank", "Iron Mine"], player) and
                           state.sl_has_pack("Seeking Wisdom", player) and
                           state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Build a Smithy", player), # <- Minimum requirement for goal
             lambda state: state.sl_has_idea("Smithy", player) and
                           state.sl_has_pack("Order and Structure", player) and
                           state.can_reach_location("Get an Iron Bar", player))
    
    # 'Villager' Path
    set_rule(world.get_location("Get a Second Villager", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Build a House", player),
             lambda state: state.sl_has_idea("House", player) and state.can_reach_location("Get a Second Villager", player))
    
    set_rule(world.get_location("Create Offspring", player),
             lambda state: state.sl_has_idea("Offspring", player) and state.can_reach_location("Build a House", player))
    
    set_rule(world.get_location("Get 3 Villagers", player),
             lambda state: state.can_reach_location("Create Offspring", player) or state.can_reach_location("Get a Dog", player))
    
    # 'Plank' Path
    set_rule(world.get_location("Harvest a Tree using a Villager", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Build a Lumber Camp", player),
             lambda state: state.sl_has_idea("Lumber Camp", player) and
                           state.sl_has_pack("Seeking Wisdom", player) and
                           state.can_reach_location("Harvest a Tree using a Villager", player))

    # 'Goal' Path
    set_rule(world.get_location("Build a Temple", player), 
             lambda state: state.sl_has_all_ideas(["Temple", "Sawmill"], player) and # <- Trying to ensure the sawmill is provided at some point
                           state.can_reach_location("Create Offspring", player) and # <- 'House' is included in this path (and will provide 3x Villagers)
                           state.can_reach_location("Build a Smithy", player)) # <- 'Smelter' / 'Iron Bar' / 'Plank' / 'Brick' are included in this path
    
    set_rule(world.get_location("Bring the Goblet to the Temple", player),
             lambda state: state.can_reach_location("Build a Temple", player) and # <- Able to build the temple
                           state.can_reach_location("Build a Farm", player) and # <- 'Shed' is included in this path
                           state.can_reach_location("Cook an Omelette", player) and # <- 'Stick' / 'Campfire' are included in this path
                           state.can_reach_location("Find a mysterious artifact", player) and # <- Able to find the goblet
                           state.can_reach_location("Kill a Skeleton", player)) # <- Access to 'The Armory' for equipment drops
    
    set_rule(world.get_location("Kill the Demon", player), # <- Will be an Event if Goal is 'Kill the Demon' or a Location Check if Goal is 'Kill the Demon Lord'
                     lambda state: state.can_reach_location("Bring the Goblet to the Temple", player))
    
    if goal == 1:
        # If Goal is 'Kill the Demon Lord' set the Event conditions and set access to post-Kill the Demon
        set_rule(world.get_location("Kill the Demon Lord", player),
                     lambda state: state.can_reach_location("Kill the Demon", player))
    elif goal > 1:
        raise Exception(f"Unhandled value for 'Goal' in Options: {goal}")
    
    # Set completion condition
    world.completion_condition[player] = lambda state: state.has("Victory", player)