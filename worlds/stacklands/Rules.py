from typing import List
from BaseClasses import MultiWorld
from .Enums import ExpansionType, GoalFlags, RegionFlags
from .Locations import location_table
from .Options import StacklandsOptions
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
                    self.sl_has_all_ideas(["Campfire", "Shed"], player)         # <- Player has access to basic ideas
                    if options.board_expansion_mode.value is ExpansionType.Ideas
                    else (
                        self.sl_has_idea("Campfire", player)                    # <- Player has campfire
                        and self.sl_has_count("Board Size Increase", 1, player) # <- Player has at least one Board Size increase
                        and self.sl_has_count("Card Limit Increase", 1, player) # <- Player has at least one Card Limit increase
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
                self.sl_has_all_ideas(["Iron Mine", "Lumber Camp", "Quarry"], player) and # <- Player can create infinite basic resources
                self.sl_has_pack("Logic and Reason", player)                              # <- Player has access to additional resources
                and (
                    options.board_expansion_mode.value is ExpansionType.Ideas  # Board Expansion Mode is 'Ideas'
                    or (                                                       # OR
                       self.sl_has_count("Board Size Increase", 2, player)     # Player has at least 2 board size increases
                       and self.sl_has_count("Card Limit Increase", 2, player) # AND Player has at least 2 card limit increases
                    )
                ))
    
    def sl_phase_five(self, options: StacklandsOptions, player: int) -> bool:
        return (self.sl_phase_four(options, player) and
                self.sl_has_all_ideas(["Brick", "Iron Bar", "Plank", "Smelter", "Temple"], player) and # <- Player has access to advanced resources
                self.sl_has_all_packs(["Curious Cuisine", "The Armory"], player)) # <- Player has increased access to advanced resources
    
    def sl_phase_six(self, options: StacklandsOptions, player: int) -> bool:
        return (self.sl_phase_five(options, player) and
                self.sl_has_all_ideas(["Smithy", "Sword"], player) and # <- Player can make an advanced weapon
                self.sl_has_pack("Order and Structure", player) # <- Player can find/fight harder enemies
                and (
                    options.board_expansion_mode.value is ExpansionType.Ideas  # Board Expansion Mode is 'Ideas'
                    or (                                                       # OR
                       self.sl_has_count("Board Size Increase", 3, player)     # Player has at least 3 board size increases
                       and self.sl_has_count("Card Limit Increase", 3, player) # AND Player has at least 3 card limit increases
                    )
                ))
 
# Set all region and location rules
def set_rules(world: MultiWorld, player: int):

    # Get relevant options
    options = world.worlds[player].options

    # Calculate selected boards
    mainland_board_selected: bool = bool(options.boards.value & RegionFlags.Mainland)
    forest_board_selected: bool = bool(options.boards.value & RegionFlags.Forest)

    # Calculate selected goals
    demon_goal_selected: bool = bool(options.goal.value & GoalFlags.Demon)
    witch_goal_selected: bool = bool(options.goal.value & GoalFlags.Witch)

#region 'Entrances'

    # Entrances
    set_rule(world.get_entrance("Start", player), lambda state: True)

    set_rule(world.get_entrance("Strange Portal", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player has access to basic equipment to fight mobs in Dark Forest
    
#endregion

#region 'Welcome' Quests

    set_rule(world.get_location("Open the Booster Pack", player), lambda state: True)

    set_rule(world.get_location("Drag the Villager on top of the Berry Bush", player), lambda state: True)

    set_rule(world.get_location("Mine a Rock using a Villager", player), lambda state: True)

    set_rule(world.get_location("Sell a Card", player), lambda state: True)

    set_rule(world.get_location("Buy the Humble Beginnings Pack", player),
             lambda state: state.sl_phase_zero(player))

    set_rule(world.get_location("Harvest a Tree using a Villager", player),
             lambda state: state.sl_phase_zero(player))

    set_rule(world.get_location("Make a Stick from Wood", player),
             lambda state: state.sl_phase_one(options, player))

    if options.pausing.value: # <- Set pausing location rule only if pausing is enabled
        set_rule(world.get_location("Pause using the play icon in the top right corner", player),
                 lambda state: True)

    set_rule(world.get_location("Grow a Berry Bush using Soil", player),
             lambda state: state.sl_phase_one(options, player))

    set_rule(world.get_location("Build a House", player),
             lambda state: state.sl_phase_three(options, player))
    
    set_rule(world.get_location("Get a Second Villager", player),
             lambda state: state.sl_phase_zero(player))

    set_rule(world.get_location("Create Offspring", player),
             lambda state:state.sl_phase_three(options, player))

#endregion

#region 'The Grand Scheme' Quests

    set_rule(world.get_location("Unlock all Packs", player),
             lambda state: state.count_group("All Mainland Booster Packs", player) == 8)

    set_rule(world.get_location("Get 3 Villagers", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player has access to House / Offspring

    set_rule(world.get_location("Find the Catacombs", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player has access to Explorers pack

    set_rule(world.get_location("Find a mysterious artifact", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player has access to Explorers pack

    set_rule(world.get_location("Build a Temple", player),
             lambda state: state.sl_phase_five(options, player)) # <- Player has access to Brick / Plank / Iron Bar / Smelter / Offspring

    set_rule(world.get_location("Bring the Goblet to the Temple", player),
             lambda state: state.can_reach_location("Build a Temple", player)) # <- Player can build a temple

    set_rule(world.get_location("Kill the Demon", player), # <- Will be an 'Event' location if Goal is 'Kill the Demon' or a Location Check if Goal is 'Kill the Demon Lord'
                    lambda state: state.sl_phase_six(options, player)) # <- Player has access to all 'required' items.
#endregion

#region 'Power & Skill' Quests

    set_rule(world.get_location("Train Militia", player),
             lambda state: state.sl_phase_three(options, player))

    set_rule(world.get_location("Kill a Rat", player),
             lambda state: state.sl_phase_zero(player)) # <- Player can find Rat in Humble Beginnings Pack

    set_rule(world.get_location("Kill a Skeleton", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player has at least one pack to find Skeletons in

#endregion

#region 'Strengthen Up' Quests

    set_rule(world.get_location("Train an Archer", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player can find/fight enemies to drop a Bow

    set_rule(world.get_location("Make a Villager wear a Rabbit Hat", player),
             lambda state: state.sl_phase_zero(player)) # <- Rabbit is found in Humble Beginnings

    set_rule(world.get_location("Build a Smithy", player),
             lambda state: state.sl_phase_six(options, player)) # <- Player has ideas for Brick / Plank / Iron Bar / Smelter / Smithy

    set_rule(world.get_location("Train a Wizard", player),
             lambda state: state.sl_has_idea("Magic Wand", player) and # <- Player has Idea for Magic Wand
                           state.sl_phase_three(options, player)) # <- Player can find/fight enemies to drop Magic Dust
 
    set_rule(world.get_location("Equip an Archer with a Quiver", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player can find/fight enemies to drop a Quiver

    set_rule(world.get_location("Have a Villager with Combat Level 20", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player has access to a basic weaponry

    set_rule(world.get_location("Train a Ninja", player),
             lambda state: state.sl_has_idea("Throwing Stars", player) and # <- Player has Idea for Throwing Stars
                           state.can_reach_location("Build a Smithy", player)) # <- Player is able to build a Smithy

#endregion

#region 'Potluck' Quests

    set_rule(world.get_location("Start a Campfire", player),
             lambda state: state.sl_phase_two(options, player)) # <- Player has ideas for Stick / Campfire

    set_rule(world.get_location("Cook Raw Meat", player),
             lambda state: state.sl_has_idea("Cooked Meat", player) and # <- Player has idea for Cooked Meat
                           state.sl_phase_two(options, player)) # <- Player has ideas for Stick / Campfire

    set_rule(world.get_location("Cook an Omelette", player),
             lambda state: state.sl_has_idea("Omelette", player) and # <- Player has idea for Omelette
                           state.sl_phase_three(options, player)) # <- Player has ideas for Stick / Campfire and Reap & Sow Pack

    set_rule(world.get_location("Cook a Frittata", player),
             lambda state: state.sl_has_idea("Frittata", player) and # <- Player has idea for Frittata
                           state.sl_phase_five(options, player)) # <- Player has ideas for Stick / Campfire and Curious Cuisine Pack

#endregion

#region 'Discovery' Quests

    set_rule(world.get_location("Explore a Forest", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player can discover a Forest from Explorers pack

    set_rule(world.get_location("Explore a Mountain", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player can discover a Mountain from Explorers pack

    set_rule(world.get_location("Open a Treasure Chest", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player can discover Treasure Chest from Catacombs / Forest / Mountain / Old Village from Explorers pack

    set_rule(world.get_location("Get a Dog", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player can discover Wolf from Catacombs / Plains from Explorers pack

    set_rule(world.get_location("Find a Graveyard", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player is able to get Bones from enemies or create Offspring for corpses

    set_rule(world.get_location("Train an Explorer", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player can find a Map from Enemies / Old Tome / Travelling Cart

    set_rule(world.get_location("Buy something from a Travelling Cart", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player can survive until a Travelling Cart spawns (10% every odd from Moon 9 or guaranteed Moon 19)


#endregion

#region 'Ways and Means' Quests

    set_rule(world.get_location("Have 5 Ideas", player),
             lambda state: state.count_group("All Ideas", player) >= 5)

    set_rule(world.get_location("Have 10 Ideas", player),
             lambda state: state.count_group("All Ideas", player) >= 10)

    set_rule(world.get_location("Have 10 Stone", player),
             lambda state: state.sl_phase_zero(player))

    set_rule(world.get_location("Have 10 Wood", player),
             lambda state: state.sl_phase_zero(player))

    set_rule(world.get_location("Get an Iron Bar", player),
             lambda state: state.sl_phase_five(options, player)) # <- Player has access to Brick / Plank / Iron Bar / Smelter

    set_rule(world.get_location("Have 5 Food", player),
             lambda state: state.sl_phase_zero(player))

    set_rule(world.get_location("Have 10 Food", player),
             lambda state: state.sl_phase_zero(player))

    set_rule(world.get_location("Have 20 Food", player),
             lambda state: state.sl_phase_two(options, player)) # <- Player has access to Growth / Shed

    set_rule(world.get_location("Have 50 Food", player),
             lambda state: state.sl_phase_three(options, player)) # <- Player has access to Growth / Shed / Reap & Sow
    
    set_rule(world.get_location("Have 10 Coins", player),
             lambda state: state.sl_phase_zero(player))

    set_rule(world.get_location("Have 30 Coins", player),
             lambda state: state.sl_phase_two(options, player)) # <- Player can access Humble Beginnings / Seeking Wisdom to generate gold

    set_rule(world.get_location("Have 50 Coins", player),
             lambda state: state.sl_phase_two(options, player)) # <- Player can access Humble Beginnings / Seeking Wisdom to generate gold

#endregion

#region 'Construction' Quests

    set_rule(world.get_location("Have 3 Houses", player),
             lambda state: state.can_reach_location("Build a House", player)) # <- Player can build a House

    set_rule(world.get_location("Build a Shed", player),
             lambda state: state.sl_phase_two(options, player)) # <- Player has access to Stick / Shed

    set_rule(world.get_location("Build a Quarry", player),
             lambda state: state.sl_phase_four(options, player)) # <- Player has access to Quarry

    set_rule(world.get_location("Build a Lumber Camp", player),
             lambda state: state.sl_phase_four(options, player)) # <- Player has access to Lumber Camp

    set_rule(world.get_location("Build a Farm", player),
             lambda state: state.sl_has_idea("Farm", player) and # <- Player has idea for Farm
                           state.sl_phase_five(options, player)) # <- Player has access to Growth / Brick / Plank / Reap & Sow / Curious Cuisine

    set_rule(world.get_location("Build a Brickyard", player),
             lambda state: state.sl_has_idea("Brickyard", player) and # <- Player has idea for Brickyard
                           state.sl_phase_five(options, player)) # <- Player has access to Brick / Iron Bar

    set_rule(world.get_location("Sell a Card at a Market", player),
             lambda state: state.sl_has_idea("Market", player) and # <- Player has Idea for Market
                           state.sl_phase_five(options, player)) # <- Player has access to Brick / Plank

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

#region 'The Dark Forest' Quests

    # Only apply rules if The Dark Forest is enabled
    if forest_board_selected:

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

    # Apply rule for Wicked Witch if The Dark Forest is enabled or if it is set as the goal
    if forest_board_selected or witch_goal_selected:
        set_rule(world.get_location("Fight the Wicked Witch", player),
                lambda state: state.sl_phase_six(options, player) and # <- Player has access to advanced weapon
                              state.can_reach_region("The Dark Forest", player))  # <- Player can reach The Dark Forest

#endregion

#region 'Mobsanity' Quests

    # Set rules if mobsanity is enabled
    if options.mobsanity.value:
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
        if forest_board_selected:

            set_rule(world.get_location("Kill a Dark Elf", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Only found in The Dark Forest from Wave 4
            
            set_rule(world.get_location("Kill an Ent", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Only found in The Dark Forest from Wave 4
            
            set_rule(world.get_location("Kill an Ogre", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Only found in The Dark Forest from Wave 4

            set_rule(world.get_location("Kill an Orc Wizard", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Only found in The Dark Forest from Wave 4

#endregion

    # Set completion condition
    world.completion_condition[player] = lambda state: state.has("Victory", player)