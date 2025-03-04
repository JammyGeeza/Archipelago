from BaseClasses import MultiWorld
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import set_rule

class StacklandsLogic(LogicMixin):

    def stacklands_access_enemies(self, player: int) -> bool:
        return self.stacklands_access_humble_beginnings(player) and self.has_any(set(["Explorers Booster Pack", "The Armory Booster Pack"]), player)

    def stacklands_access_humble_beginnings(self, player: int) -> bool:
        return self.can_reach_location("Buy the Humble Beginnings Pack", player)


# Set all region and location rules
def set_all_rules(world: MultiWorld, player: int):
      
    # Region checks (to be implemented later)
    region_checks = {
        "Mainland": lambda state: True
    }
    
    ### Mainland Rules ###
    
    # 'Welcome' Category
    set_rule(world.get_location("Buy the Humble Beginnings Pack", player),
             lambda state: bool(world.worlds[player].options.basic_pack.value) or state.has("Humble Beginnings Booster Pack", player))
    
    set_rule(world.get_location("Harvest a Tree using a Villager", player),
             lambda state: state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Make a Stick from Wood", player),
             lambda state: state.has("Idea: Stick", player) and state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Grow a Berry Bush using Soil", player),
             lambda state: state.has("Idea: Growth", player) and state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Build a House", player),
             lambda state: state.has("Idea: House", player) and state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Get a Second Villager", player),
             lambda state: state.stacklands_access_humble_beginnings(player)) # <- Second villager is received from humble beginnings
    
    set_rule(world.get_location("Create Offspring", player),
             lambda state: state.has("Idea: Offspring", player) and state.can_reach_location("Build a House", player)) # <- Need a house to make offspring
    
    # 'The Grand Scheme' Category    
    set_rule(world.get_location("Get 3 Villagers", player),
             lambda state: state.can_reach_location("Create Offspring", player) or state.can_reach_location("Get a Dog", player)) # <- Third villager can be from offspring or a dog
    
    set_rule(world.get_location("Find the Catacombs", player),
             lambda state: state.can_reach_location("Get a Second Villager", player) # <- Catacombs can be retrieved from Graveyard (2x Corpses)
                           or (state.stacklands_access_humble_beginnings(player) and state.has("Explorers Booster Pack", player))) # <- Catacombs can be found from Explorers pack
    
    set_rule(world.get_location("Find a mysterious artifact", player),
             lambda state: state.can_reach_location("Find the Catacombs", player) # <- Goblet can be retrieved from Catacombs
                           or state.stacklands_access_humble_beginnings(player)) # <- or from travelling cart
    
    set_rule(world.get_location("Build a Temple", player),
             lambda state: state.has_all(set(["Idea: Temple", "Idea: Plank", "Idea: Brick"]), player) # <- Ideas required
                           and state.can_reach_location("Get an Iron Bar", player) # <- Need to be able to create iron bars
                           and state.can_reach_location("Create Offspring", player)) # <- 3x Villagers Needed
    
    set_rule(world.get_location("Bring the Goblet to the Temple", player),
             lambda state: state.can_reach_location("Find a mysterious artifact", player) # <- Goblet required
                           and state.can_reach_location("Build a Temple", player)) # <- Temple required
    
    set_rule(world.get_location("Find a mysterious artifact", player),
             lambda state: state.stacklands_access_humble_beginnings(player)) # <- Goblet can be found in Catacombs or from travelling cart
    
    set_rule(world.get_location("Kill the Demon", player),
             lambda state: state.can_reach_location("Bring the Goblet to the Temple", player)) # <- Goblet and Temple required
    
    # 'The Dark Forest' Category 
    # To be added, potentially...
    
    # 'Power & Skill' Category
    set_rule(world.get_location("Train Militia", player),
             lambda state: (state.has("Idea: Spear", player) and state.can_reach_location("Make a Stick from Wood", player)) # <- Self-craft the spear 
                           or state.stacklands_access_enemies(player)) # <- Get weapons from enemy drop

    set_rule(world.get_location("Kill a Rat", player),
             lambda state: state.stacklands_access_humble_beginnings(player)) # <- Rats can drop from Humble Beginnings / Strange Portal
    
    set_rule(world.get_location("Kill a Skeleton", player),
             lambda state: state.can_reach_location("Find the Catacombs", player) or state.stacklands_access_enemies(player)) # Skeletons from enemy packs or catacombs / graveyard / strange portal
    
    # 'Strengthen Up' Category
    set_rule(world.get_location("Make a Villager wear a Rabbit Hat", player),
             lambda state: state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Build a Smithy", player),
             lambda state: state.has("Idea: Smithy", player) and state.can_reach_location("Get an Iron Bar", player))
    
    set_rule(world.get_location("Train a Wizard", player),
             lambda state: (state.has("Idea: Magic Wand", player) and state.can_reach_location("Make a Stick from Wood", player))
                           or state.stacklands_access_enemies(player))
    
    set_rule(world.get_location("Have a Villager with Combat Level 20", player), 
             lambda state: state.can_reach_location("Make a Villager wear a Rabbit Hat", player)
                           and (state.can_reach_location("Train Militia", player) or state.can_reach_location("Train a Wizard", player))
                           or state.stacklands_access_enemies(player))
    
    set_rule(world.get_location("Train a Ninja", player),
             lambda state: state.has("Idea: Throwing Stars", player) 
                           and state.can_reach_location("Get an Iron Bar", player) # <- Needed for recipe
                           and state.can_reach_location("Build a Smithy", player)) # <- Needed for recipe
    
    # 'Potluck' Category
    set_rule(world.get_location("Start a Campfire", player),
             lambda state: state.has("Idea: Campfire", player) and state.can_reach_location("Make a Stick from Wood", player))
    
    set_rule(world.get_location("Cook Raw Meat", player),
             lambda state: state.has("Idea: Cooked Meat", player) and state.can_reach_location("Start a Campfire", player))
    
    set_rule(world.get_location("Cook an Omelette", player),
             lambda state: state.has("Idea: Omelette", player)
                           and state.has_any(set(["Reap & Sow Booster Pack", "Curious Cuisine Booster Pack"]), player) # Can get eggs from either pack
                           and state.can_reach_location("Start a Campfire", player))
    
    set_rule(world.get_location("Cook a Frittata", player),
             lambda state: state.has("Idea: Frittata", player)
                           and state.has("Curious Cuisine Booster Pack", player) # <- Potatoes and Eggs can both come from this pack
                           and state.can_reach_location("Start a Campfire", player)) # <- Needed for recipe
    
    # 'Discovery' Category
    set_rule(world.get_location("Explore a Forest", player),
             lambda state: state.has("Explorers Booster Pack", player) and state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Explore a Mountain", player),
             lambda state: state.has("Explorers Booster Pack", player) and state.stacklands_access_humble_beginnings(player))
             
    set_rule(world.get_location("Open a Treasure Chest", player),
             lambda state: state.stacklands_access_humble_beginnings(player)) # <- Can get early from travelling cart / graveyard / catacombs
             
    set_rule(world.get_location("Find a Graveyard", player),
             lambda state: state.can_reach_location("Get a Second Villager", player)) # <- Graveyard can be made with 2x corpses
             
    set_rule(world.get_location("Get a Dog", player),
             lambda state: state.can_reach_location("Find the Catacombs", player)  # <- Wolf can be found in catacombs / strange portal
                           or state.stacklands_access_enemies(player)) # <- Wolf can be found in enemy packs
             
    set_rule(world.get_location("Train an Explorer", player),
             lambda state: state.stacklands_access_humble_beginnings(player)) # <- Map can be found from Travelling Cart / Old Tome
             
    # 'Ways and Means' Category
    set_rule(world.get_location("Have 5 Ideas", player),
             lambda state: state.stacklands_access_humble_beginnings(player) and state.count_group("All Ideas", player) >= 5)
    
    set_rule(world.get_location("Have 10 Ideas", player),
             lambda state: state.stacklands_access_humble_beginnings(player) and state.count_group("All Ideas", player) >= 10)
    
    set_rule(world.get_location("Have 10 Wood", player),
             lambda state: state.stacklands_access_humble_beginnings(player))
             
    set_rule(world.get_location("Have 10 Stone", player),
             lambda state: state.stacklands_access_humble_beginnings(player))
             
    set_rule(world.get_location("Get an Iron Bar", player),
             lambda state: state.has("Idea: Iron Bar", player) 
                           and state.can_reach_location("Build a Smelter", player)
                           and (state.can_reach_location("Build a Mine", player) or state.has_any(set(["Logic and Reason Booster Pack", "Order and Structure Booster Pack"]), player)))
             
    set_rule(world.get_location("Have 5 Food", player),
             lambda state: state.stacklands_access_humble_beginnings(player))
             
    set_rule(world.get_location("Have 10 Food", player),
             lambda state: state.can_reach_location("Have 5 Food", player))
             
    set_rule(world.get_location("Have 20 Food", player),
             lambda state: state.can_reach_location("Have 10 Food", player)
                           and (state.can_reach_location("Build a Shed", player) # <- Player can build shed to allow more basic food on the board
                           or (state.stacklands_access_humble_beginnings(player) and state.has("Curious Cuisine Booster Pack", player)))) # <- Or player has access to better foods
             
    set_rule(world.get_location("Have 50 Food", player), 
             lambda state: state.can_reach_location("Have 20 Food", player)) # <- If player can gather 20, they should be able to gather 50
             
    # 'Construction' Category
    set_rule(world.get_location("Have 3 Houses", player),
             lambda state: state.can_reach_location("Build a House", player))
             
    set_rule(world.get_location("Build a Shed", player),
             lambda state: state.has("Idea: Shed", player) and state.can_reach_location("Make a Stick from Wood", player))
             
    set_rule(world.get_location("Build a Quarry", player),
             lambda state: state.has("Idea: Quarry", player) and state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Build a Lumber Camp", player),
             lambda state: state.has("Idea: Lumber Camp", player) and state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Build a Farm", player),
             lambda state: state.has_all(set(["Idea: Farm", "Idea: Brick", "Idea: Plank"]), player) and state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Build a Brickyard", player),
             lambda state: state.has_all(set(["Idea: Brickyard", "Idea: Brick"]), player) and state.can_reach_location("Get an Iron Bar", player))
    
    set_rule(world.get_location("Sell a Card at a Market", player),
             lambda state: state.has("Idea: Market", player) and state.stacklands_access_humble_beginnings(player))
    
    # 'Longevity' Category
    set_rule(world.get_location("Reach Moon 6", player),
             lambda state: state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Reach Moon 12", player),
             lambda state: state.can_reach_location("Reach Moon 6", player))
    
    set_rule(world.get_location("Reach Moon 24", player),
             lambda state: state.can_reach_location("Reach Moon 12", player))
             
    set_rule(world.get_location("Reach Moon 36", player),
             lambda state: state.can_reach_location("Reach Moon 24", player))
    
    # 'Side Quests' Category
    set_rule(world.get_location("Build a Garden", player),
             lambda state: state.has("Idea: Garden", player) and state.can_reach_location("Grow a Berry Bush using Soil", player))
    
    set_rule(world.get_location("Build a Sawmill", player),
             lambda state: state.has_all(set(["Idea: Sawmill", "Idea: Plank"]), player) and state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Build a Mine", player),
             lambda state: state.has("Idea: Iron Mine", player) and state.stacklands_access_humble_beginnings(player))
    
    set_rule(world.get_location("Build a Smelter", player),
             lambda state: state.has_all(set(["Idea: Smelter", "Idea: Brick"]), player) and state.stacklands_access_humble_beginnings(player))