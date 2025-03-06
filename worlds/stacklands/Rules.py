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
    
    ### Mainland Rules ###

    # Should be Sphere 1(?)
    set_rule(world.get_location("Open the Booster Pack", player), lambda state: True)

    # Should be Sphere 2(?)
    set_rule(world.get_location("Make a Stick from Wood", player), lambda state: state.sl_has_idea("Stick", player))

    # Should be Sphere 3(?)
    set_rule(world.get_location("Start a Campfire", player), lambda state: state.sl_has_idea("Campfire", player) and state.can_reach_location("Make a Stick from Wood", player))

    # Should be Sphere 2(?)
    # set_rule(world.get_location("Make a Stick from Wood", player), lambda state: state.has("Idea: Stick", player))
    # set_rule(world.get_location("Start a Campfire", player), lambda state: state.has_all(set(["Idea: Stick", "Idea: Campfire"]), player))
    # set_rule(world.get_location("Task 1", player), lambda state: state.has_all(set(["Idea: Stick", "Idea: Campfire"]), player))

    # set_rule(world.get_location("Ability to Build Campfire", player), lambda state: state.sl_has_all_ideas(["Stick", "Campfire"], player))

    # Should be Sphere 3(?)
    # set_rule(world.get_location("Task 1", player), lambda state: state.has("Campfire", player))
    # set_rule(world.get_location("Task 2", player), lambda state: state.has("Campfire", player))
    # set_rule(world.get_location("Build a Sawmill", player), lambda state: state.has("Campfire", player) and state.has_all(set(["Idea: Sawmill", "Idea: Plank"]), player))

    # set_rule(world.get_location("Ability to Build Sawmill", player), lambda state: state.has("Campfire", player) and state.sl_has_all_ideas(["Sawmill", "Plank"], player))
    
    # Should be Sphere 4(?)
    # set_rule(world.get_location("Task 3", player), lambda state: lambda state: state.has("Sawmill", player))
    # set_rule(world.get_location("Task 4", player), lambda state: lambda state: state.has("Sawmill", player))
    # set_rule(world.get_location("Task 5", player), lambda state: lambda state: state.has("Sawmill", player))
    # set_rule(world.get_location("Build a Smelter", player), lambda state: state.has("Sawmill", player) and state.has_all(set(["Idea: Smelter", "Idea: Brick", "Idea: Iron Bar"]), player))

    # set_rule(world.get_location("Ability to Build Smelter", player), lambda state: state.has("Sawmill", player) and state.sl_has_all_ideas(["Smelter", "Brick", "Iron Bar"], player))
    
    # Should be Sphere 4(?)
    set_rule(world.get_location("Bring the Goblet to the Temple", player), lambda state: state.can_reach_location("Start a Campfire", player))

    # set_rule(world.get_location("Bring the Goblet to the Temple", player), 
    #          lambda state: state.can_reach_location("Start a Capfire", player) and
    #                        state.can_reach_location("Build a Sawmill", player) and
    #                        state.can_reach_location("Build a Smelter", player))
    # set_rule(world.get_location("Bring the Goblet to the Temple", player), lambda state: state.has_all(set(["Campfire", "Sawmill", "Smelter"]), player))
    
    set_rule(world.get_location("Defeat Boss", player), lambda state: state.can_reach_location("Bring the Goblet to the Temple", player))

    # Completion event
    world.completion_condition[player] = lambda state: state.has("Victory", player)