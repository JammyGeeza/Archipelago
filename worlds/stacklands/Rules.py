from BaseClasses import MultiWorld
from worlds.generic.Rules import set_rule

# Set all region and location rules
def set_all_rules(world: MultiWorld, player: int):
      
    # Region checks (to be implemented later)
    region_checks = {
        "Mainland": lambda state: True
    }
    
    ### Mainland Rules ###

    # Coins
    set_rule(world.get_location("Have 10 Coins", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Have 30 Coins", player),
             lambda state: state.has("Idea: Coin Chest", player) and
                           state.can_reach_location("Have 10 Coins", player))
    
    set_rule(world.get_location("Have 50 Coins", player),
             lambda state: state.can_reach_location("Have 30 Coins", player))

    # Ideas
    set_rule(world.get_location("Have 5 Ideas", player),
             lambda state: state.count_group("All Ideas", player) >= 5)
    
    set_rule(world.get_location("Have 10 Ideas", player),
             lambda state: state.count_group("All Ideas", player) >= 10)
    
    # Moons
    set_rule(world.get_location("Reach Moon 6", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Reach Moon 12", player), # Trialling this to help release un-required boosters
             lambda state: state.has("Seeking Wisdom Booster Pack", player) and
                           state.can_reach_location("Reach Moon 6", player))
    
    set_rule(world.get_location("Buy something from a Travelling Cart", player),
             lambda state: state.can_reach_location("Reach Moon 12", player))
    
    set_rule(world.get_location("Reach Moon 24", player), # Trialling this to help release un-required boosters
             lambda state: state.has("Logic and Reason Booster Pack", player) and
                           state.can_reach_location("Reach Moon 12", player)) 
    
    set_rule(world.get_location("Reach Moon 36", player), # Trialling this to help release un-required boosters
             lambda state: state.has("Order and Structure Booster Pack", player) and
                           state.can_reach_location("Reach Moon 24", player))
    
    # Miscellaneous
    set_rule(world.get_location("Buy the Humble Beginnings Pack", player),
             lambda state: world.worlds[player].options.basic_pack.value == True or 
                           state.has("Humble Beginnings Booster Pack", player))

    set_rule(world.get_location("Sell a Card at a Market", player),
             lambda state: state.has_all(set(["Idea: Market", "Idea: Brick", "Idea: Plank"]), player))

    # 'Combat' Path
    set_rule(world.get_location("Make a Villager wear a Rabbit Hat", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Kill a Rat", player),
             lambda state: state.can_reach_location("Make a Villager wear a Rabbit Hat", player))
    
    set_rule(world.get_location("Train Militia", player), # Trialling this
             lambda state: state.has("Explorers Booster Pack", player) and
                           state.has_any(set(["Idea: Slingshot", "Idea: Spear"]), player) and
                           state.can_reach_location("Kill a Rat", player))
    
    set_rule(world.get_location("Train a Wizard", player), # Trialling this
             lambda state: state.has("Explorers Booster Pack", player) and
                           state.has("Idea: Magic Wand", player) and
                           state.can_reach_location("Kill a Rat", player))
    
    set_rule(world.get_location("Have a Villager with Combat Level 20", player),
             lambda state: state.has("Explorers Booster Pack", player) and
                           state.can_reach_location("Train Militia", player) and
                           state.can_reach_location("Train a Wizard", player))
    
    set_rule(world.get_location("Kill a Skeleton", player), # Trialling this
             lambda state: state.has("The Armory Booster Pack", player) and
                           state.can_reach_location("Have a Villager with Combat Level 20", player))

    set_rule(world.get_location("Train a Ninja", player), # Trialling this
             lambda state: state.has("Idea: Throwing Stars", player) and
                           state.can_reach_location("Build a Smithy", player) and
                           state.can_reach_location("Have a Villager with Combat Level 20", player))

    # 'Cooking' Path
    set_rule(world.get_location("Make a Stick from Wood", player),
             lambda state: state.has("Idea: Stick", player) and
                           state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Start a Campfire", player),
             lambda state: state.has("Idea: Campfire", player) and
                           state.can_reach_location("Make a Stick from Wood", player))
    
    set_rule(world.get_location("Cook Raw Meat", player),
             lambda state: state.has_all(set(["Idea: Cooked Meat", "Reap and Sow Booster Pack"]), player) and
                           state.can_reach_location("Start a Campfire", player))
    
    set_rule(world.get_location("Cook an Omelette", player),
             lambda state: state.has("Idea: Omelette", player) and
                           state.can_reach_location("Cook Raw Meat", player))
    
    set_rule(world.get_location("Cook a Frittata", player),
             lambda state: state.has_all(set(["Idea: Frittata", "Idea: Stove", "Curious Cuisine Booster Pack"]), player) and
                           state.can_reach_location("Cook an Omelette", player))
    
    # 'Exploring' Path
    set_rule(world.get_location("Find a Graveyard", player),
             lambda state: state.has("Explorers Booster Pack", player) and
                           state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Find the Catacombs", player),
             lambda state: state.can_reach_location("Find a Graveyard", player)) # <- Can be Found from Graveyard

    set_rule(world.get_location("Open a Treasure Chest", player),
             lambda state: state.can_reach_location("Find the Catacombs", player))
    
    set_rule(world.get_location("Find a mysterious artifact", player), # <- Minimum Requirement for Goal Path
             lambda state: state.can_reach_location("Open a Treasure Chest", player))
    
    set_rule(world.get_location("Get a Dog", player),
             lambda state: state.can_reach_location("Open a Treasure Chest", player))
    
    set_rule(world.get_location("Train an Explorer", player),
             lambda state: state.can_reach_location("Open a Treasure Chest", player))
    
    set_rule(world.get_location("Explore a Forest", player),
             lambda state: state.can_reach_location("Open a Treasure Chest", player))
    
    set_rule(world.get_location("Explore a Mountain", player),
             lambda state: state.can_reach_location("Open a Treasure Chest", player))
    
    # 'Farming' Path
    set_rule(world.get_location("Have 5 Food", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Grow a Berry Bush using Soil", player),
             lambda state: state.has("Idea: Growth", player) and
                           state.can_reach_location("Have 5 Food", player))
    
    set_rule(world.get_location("Have 10 Food", player),
             lambda state: state.can_reach_location("Grow a Berry Bush using Soil", player))

    set_rule(world.get_location("Build a Shed", player),
             lambda state: state.has("Idea: Shed", player) and
                           state.can_reach_location("Have 10 Food", player))

    set_rule(world.get_location("Have 20 Food", player),
             lambda state: state.can_reach_location("Build a Shed", player))

    set_rule(world.get_location("Build a Garden", player), # <- Minimum requirement for Goal Path
             lambda state: state.has("Idea: Garden", player) and
                           state.can_reach_location("Have 20 Food", player))
    
    set_rule(world.get_location("Build a Farm", player),
             lambda state: state.has_all(set(["Idea: Farm", "Idea: Brick", "Idea: Plank"]), player) and
                           state.can_reach_location("Build a Garden", player))
    
    set_rule(world.get_location("Have 50 Food", player),
             lambda state: state.can_reach_location("Build a Farm", player))
    
    # 'Metal' Path
    set_rule(world.get_location("Build a Mine", player),
             lambda state: state.has("Idea: Iron Mine", player) and
                           state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Build a Smelter", player),
             lambda state: state.has_all(set(["Idea: Smelter", "Idea: Brick", "Idea: Plank"]), player) and
                           state.can_reach_location("Build a Mine", player))
    
    set_rule(world.get_location("Get an Iron Bar", player),
             lambda state: state.has("Idea: Iron Bar", player) and
                           state.can_reach_location("Build a Smelter", player))
    
    set_rule(world.get_location("Build a Smithy", player),
             lambda state: state.has("Idea: Smithy", player) and
                           state.can_reach_location("Get an Iron Bar", player))
    
    # 'Stone' Path
    set_rule(world.get_location("Have 10 Stone", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Build a Quarry", player),
             lambda state: state.has_all(set(["Idea: Quarry", "Idea: Brick"]), player) and
                           state.can_reach_location("Have 10 Stone", player))
    
    set_rule(world.get_location("Build a Brickyard", player),
             lambda state: state.has("Idea: Brickyard", player) and
                           state.can_reach_location("Get an Iron Bar", player) and
                           state.can_reach_location("Build a Quarry", player))

    # 'Villager' Path
    set_rule(world.get_location("Get a Second Villager", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))

    set_rule(world.get_location("Build a House", player),
             lambda state: state.has("Idea: House", player) 
                           and state.can_reach_location("Get a Second Villager", player))
    
    set_rule(world.get_location("Have 3 Houses", player),
             lambda state: state.can_reach_location("Build a House", player))
    
    set_rule(world.get_location("Create Offspring", player),
             lambda state: state.has("Idea: Offspring", player) 
                           and state.can_reach_location("Build a House", player))
    
    set_rule(world.get_location("Get 3 Villagers", player),
             lambda state: state.can_reach_location("Create Offspring", player))

    # 'Wood' Path
    set_rule(world.get_location("Harvest a Tree using a Villager", player),
             lambda state: state.can_reach_location("Buy the Humble Beginnings Pack", player))
    
    set_rule(world.get_location("Have 10 Wood", player),
             lambda state: state.can_reach_location("Harvest a Tree using a Villager", player))
    
    set_rule(world.get_location("Build a Lumber Camp", player),
             lambda state: state.has_all(set(["Idea: Lumber Camp", "Idea: Plank"]), player) and
                           state.can_reach_location("Have 10 Wood", player))
    
    set_rule(world.get_location("Build a Sawmill", player),
             lambda state: state.has("Idea: Sawmill", player) and
                           state.can_reach_location("Get an Iron Bar", player) and
                           state.can_reach_location("Build a Lumber Camp", player))
    
    # 'Goal' Path (Other paths converge here)
    set_rule(world.get_location("Build a Temple", player), # Trialling this
             lambda state: state.has("Idea: Temple", player) and
                           state.can_reach_location("Get 3 Villagers", player) and # <- 'House' is included as part of this path
                           state.can_reach_location("Get an Iron Bar", player) and # <- 'Smelter' is included as part of this path
                           state.can_reach_location("Build a Quarry", player) and # <- 'Brick' is included as part of this path
                           state.can_reach_location("Build a Lumber Camp", player)) # <- 'Plank' is included as part of this path
    
    set_rule(world.get_location("Bring the Goblet to the Temple", player), # Trialling this
             lambda state: state.can_reach_location("Build a Temple", player) and
                           state.can_reach_location("Cook Raw Meat", player) and # <- 'Campfire' is included as part of this path
                           state.can_reach_location("Kill a Skeleton", player) and
                           state.can_reach_location("Build a Garden", player) and # <- 'Shed' is included as part of this path
                           state.can_reach_location("Find a mysterious artifact", player))
    
    set_rule(world.get_location("Kill the Demon", player),
             lambda state: state.can_reach_location("Bring the Goblet to the Temple", player))
    
    # Include this rule if demon lord is the goal
    if world.worlds[player].options.goal == 1:
        set_rule(world.get_location("Kill the Demon Lord", player),
                lambda state: state.can_reach_location("Kill the Demon", player))