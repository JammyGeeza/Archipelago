from BaseClasses import MultiWorld
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import set_rule

class StacklandsLogic(LogicMixin):
    
    # Basic packs
    def stacklands_access_to_basic_pack(self, player: int) -> bool:
        return bool(self.multiworld.worlds[player].options.basic_pack) or self.has_group("Basic Booster Packs", player)
    
    def stacklands_access_to_enemies(self, player: int) -> bool:
        return self.has_any(set(["Explorers Booster Pack", "The Armory Booster Pack"]), player)
    
    def stacklands_access_all_packs(self, player: int) -> bool:
        return self.count_group("All Booster Packs", player) >= 8
    
    # Equipment
    def stacklands_can_make_spear(self, player: int) -> bool:
        return self.has("Idea: Spear", player) and self.stacklands_can_make_stick(player)
    
    def stacklands_can_make_sword(self, player: int) -> bool:
        return self.has_all(set(["Idea: Sword", "Idea: Stick"]), player) and self.stacklands_can_make_iron_bar(player)
    
    def stacklands_can_make_magic_staff(self, player: int) -> bool:
        return (self.stacklands_can_make_smithy(player)
                and self.stacklands_access_to_enemies(player)
                and self.stacklands_access_to_basic_pack(player))
    
    def stacklands_can_make_magic_wand(self, player: int) -> bool:
        return self.stacklands_can_make_stick(player) and self.stacklands_access_to_enemies(player)

    # Food
    def stacklands_can_make_cooked_meat(self, player: int) -> bool:
        return self.has("Idea: Cooked Meat", player) and self.stacklands_can_make_campfire(player)
    
    # Resources
    def stacklands_access_to_iron_ore(self, player: int) -> bool:
        return (self.has_any(set(["Explorers Booster Pack", "Logic and Reason Booster Pack", "Order and Structure Booster Pack"]), player)
                and self.stacklands_access_to_basic_pack(player)) # <- To help prevent above packs spawning before Humble Beginnings)
    
    def stacklands_can_make_iron_bar(self, player: int) -> bool:
        return (self.has("Idea: Iron Bar", player) 
                and self.stacklands_can_make_smelter(player)
                and self.stacklands_access_to_iron_ore(player)
                and self.stacklands_access_to_basic_pack(player))
    
    def stacklands_can_make_stick(self, player: int) -> bool:
        return self.has("Idea: Campfire", player) and self.stacklands_access_to_basic_pack(player)

    # Structures
    def stacklands_can_make_campfire(self, player: int) -> bool:
        return self.has("Idea: Campfire", player) and self.stacklands_access_to_basic_pack(player)
    
    def stacklands_can_make_farm(self, player: int) -> bool:
        return (self.has_all(set(["Idea: Farm", "Idea: Brick", "Idea: Plank"]), player)
               and self.stacklands_access_to_basic_pack(player))
    
    def stacklands_can_make_garden(self, player: int) -> bool:
        return (self.has("Idea: Garden", player)
               and self.stacklands_access_to_basic_pack(player))

    def stacklands_can_make_house(self, player: int) -> bool:
        return (self.has_all(set(["Idea: House", "Idea: Stick"]), player)
                and self.stacklands_access_to_basic_pack(player))
    
    def stacklands_can_make_shed(self, player: int) -> bool:
        return self.has("Idea: Shed", player) and self.stacklands_can_make_stick(player)

    def stacklands_can_make_smelter(self, player: int) -> bool:
        return (self.has_all(set(["Idea: Smelter", "Idea: Brick", "Idea: Plank"]), player)
                and self.stacklands_access_to_basic_pack(player))

    def stacklands_can_make_smithy(self, player: int) -> bool:
        return self.has("Idea: Smithy", player) and self.stacklands_can_make_iron_bar(player)
    
    def stacklands_can_make_temple(self, player: int) -> bool:
        return (self.has("Idea: Temple", player)
                and self.stacklands_can_make_house(player)
                and self.stacklands_can_make_iron_bar(player))
    
    # Other
    def stacklands_can_make_offspring(self, player: int) -> bool:
        return self.has("Idea: Offspring", player) and self.stacklands_can_make_house(player)


# Set all region and location rules
def set_all_rules(world: MultiWorld, player: int):
      
    # Region checks (to be implemented later)
    region_checks = {
        "Mainland": lambda state: True
    }
    
    ### Mainland Rules ###
    
    # 'Welcome Category'
    set_rule(world.get_location("Buy the Humble Beginnings Pack", player),
             lambda state: bool(world.worlds[player].options.basic_pack) or state.has("Humble Beginnings Booster Pack", player))
    
    set_rule(world.get_location("Harvest a Tree using a Villager", player),
             lambda state: state.stacklands_access_to_basic_pack(player))
    
    set_rule(world.get_location("Make a Stick from Wood", player),
             lambda state: state.stacklands_can_make_stick(player))
    
    set_rule(world.get_location("Grow a Berry Bush using Soil", player),
             lambda state: state.has("Idea: Growth", player) and state.has_any(set(["Humble Beginnings Booster Pack", "Reap & Sow Booster Pack"]), player))
    
    set_rule(world.get_location("Build a House", player),
             lambda state: state.stacklands_can_make_house(player))
    
    set_rule(world.get_location("Get a Second Villager", player),
             lambda state: state.stacklands_access_to_basic_pack(player))
    
    set_rule(world.get_location("Create Offspring", player),
             lambda state: state.stacklands_can_make_offspring(player))
    
    # 'The Grand Scheme' Category    
    set_rule(world.get_location("Get 3 Villagers", player),
             lambda state: state.stacklands_can_make_offspring(player))
    
    set_rule(world.get_location("Find the Catacombs", player),
             lambda state: state.has("Explorers Booster Pack", player) and state.stacklands_access_to_basic_pack(player))
    
    set_rule(world.get_location("Find a mysterious artifact", player),
             lambda state: state.has("Explorers Booster Pack", player) and state.stacklands_access_to_basic_pack(player))
    
    set_rule(world.get_location("Build a Temple", player),
             lambda state: state.stacklands_can_make_temple(player))
    
    set_rule(world.get_location("Bring the Goblet to the Temple", player),
             lambda state: state.stacklands_can_make_temple(player))
    
    set_rule(world.get_location("Find a mysterious artifact", player),
             lambda state: state.stacklands_can_make_temple(player))
    
    set_rule(world.get_location("Kill the Demon", player),
             lambda state: state.stacklands_can_make_temple(player))
    
    # 'The Dark Forest' Category 
    # To be added, potentially...
    
    # 'Power & Skill' Category
    set_rule(world.get_location("Train Militia", player),
             lambda state: state.stacklands_can_make_spear(player))
    
    set_rule(world.get_location("Kill a Rat", player),
             lambda state: state.has_any(set(["Humble Beginnings Booster Pack", "Explorers Booster Pack"]), player))
    
    set_rule(world.get_location("Kill a Skeleton", player),
             lambda state: (state.has_any(set(["Explorers Booster Pack", "The Armory Booster Pack"]), player))
                           and state.stacklands_access_to_basic_pack(player)) # <- To help prevent above packs spawning before Humble Beginnings)
    
    # 'Strengthen Up' Category   
    set_rule(world.get_location("Build a Smithy", player),
             lambda state: state.stacklands_can_make_smithy(player))
    
    set_rule(world.get_location("Train a Wizard", player),
             lambda state: state.stacklands_can_make_magic_wand(player)
                           or state.stacklands_can_make_magic_staff)
    
    set_rule(world.get_location("Have a Villager with Combat Level 20", player), 
             lambda state: state.stacklands_access_to_enemies(player)
                           or state.stacklands_can_make_spear(player)
                           or state.stacklands_can_make_sword(player)
                           or state.stacklands_can_make_magic_staff(player)
                           or state.stacklands_can_make_magic_wand(player))
    
    set_rule(world.get_location("Train a Ninja", player),
             lambda state: state.has("Idea: Throwing Stars", player) and state.stacklands_can_make_iron_bar(player))
    
    # 'Potluck' Category
    set_rule(world.get_location("Start a Campfire", player),
             lambda state: state.stacklands_can_make_campfire(player))
    
    set_rule(world.get_location("Cook Raw Meat", player),
             lambda state: state.has("Idea: Cooked Meat", player)
                           and state.has_any(set(["Humble Beginnings Booster Pack", "Reap & Sow Booster Pack", "Curious Cuisine Booster Pack"]), player)
                           and state.stacklands_can_make_campfire(player))
    
    set_rule(world.get_location("Cook an Omelette", player),
             lambda state: state.has("Curious Cuisine Booster Pack", player) and state.stacklands_can_make_campfire(player))
    
    set_rule(world.get_location("Cook an Omelette", player),
             lambda state: state.has("Curious Cuisine Booster Pack", player) and state.stacklands_can_make_campfire(player))
    
    # 'Discovery' Category
    set_rule(world.get_location("Explore a Forest", player),
             lambda state: state.has("Explorers Booster Pack", player))
    
    set_rule(world.get_location("Explore a Mountain", player),
             lambda state: state.has("Explorers Booster Pack", player))
             
    set_rule(world.get_location("Open a Treasure Chest", player),
             lambda state: state.has("Explorers Booster Pack", player))
             
    set_rule(world.get_location("Find a Graveyard", player),
             lambda state: state.has("Explorers Booster Pack", player))
             
    set_rule(world.get_location("Get a Dog", player),
             lambda state: (state.has_any(set(["Explorers Booster Pack", "The Armory Booster Pack"]), player))
                            and state.stacklands_access_to_basic_pack(player)) # <- To help prevent above packs spawning before Humble Beginnings, otherwise game is locked)
             
    set_rule(world.get_location("Train an Explorer", player),
             lambda state: (state.has("Explorers Booster Pack", player))
                           and state.stacklands_access_to_basic_pack(player)) # <- To help prevent above pack spawning before Humble Beginnings, otherwise game is locked)
             
    # 'Ways and Means' Category
    set_rule(world.get_location("Have 5 Ideas", player),
             lambda state: state.count_group("All Ideas", player) >= 5)
    
    set_rule(world.get_location("Have 10 Ideas", player),
             lambda state: state.count_group("All Ideas", player) >= 10)
    
    set_rule(world.get_location("Have 10 Wood", player),
             lambda state: state.stacklands_access_to_basic_pack(player))
             
    set_rule(world.get_location("Have 10 Stone", player),
             lambda state: state.stacklands_access_to_basic_pack(player))
             
    set_rule(world.get_location("Get an Iron Bar", player),
             lambda state: state.has("Explorers Booster Pack", player) or state.stacklands_can_make_iron_bar(player))
             
    set_rule(world.get_location("Have 5 Food", player),
             lambda state: state.stacklands_access_to_basic_pack(player))
             
    set_rule(world.get_location("Have 10 Food", player),
             lambda state: state.stacklands_access_to_basic_pack(player))
             
    set_rule(world.get_location("Have 20 Food", player), # Likely needs a shed to be able to keep enough food items on the board
             lambda state: state.has("Curious Cuisine Booster Pack", player) or state.stacklands_can_make_shed(player))
             
    set_rule(world.get_location("Have 50 Food", player), # Likely needs a shed to be able to keep enough food items on the board
             lambda state: state.has("Curious Cuisine Booster Pack", player) or state.stacklands_can_make_shed(player))
             
    # 'Construction' Category
    set_rule(world.get_location("Have 3 Houses", player),
             lambda state: state.stacklands_can_make_house(player))
             
    set_rule(world.get_location("Build a Shed", player),
             lambda state: state.stacklands_can_make_shed(player))
             
    set_rule(world.get_location("Build a Quarry", player),
             lambda state: state.has("Idea: Quarry", player) and state.stacklands_access_to_basic_pack(player))
    
    set_rule(world.get_location("Build a Lumber Camp", player),
             lambda state: state.has("Idea: Lumber Camp", player) and state.stacklands_access_to_basic_pack(player))
    
    set_rule(world.get_location("Build a Farm", player),
             lambda state: state.stacklands_can_make_farm(player))
    
    set_rule(world.get_location("Build a Brickyard", player),
             lambda state: state.has("Idea: Brickyard", player) and state.stacklands_can_make_iron_bar(player))