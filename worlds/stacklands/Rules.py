from typing import List
from BaseClasses import MultiWorld
from .Locations import CheckType, location_table
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
    
    def sl_progressive_count(self, name: str, count: int, player: int) -> bool:
        return self.count("Progressive: " + name, player) >= count

# Set all region and location rules
def set_rules(world: MultiWorld, player: int):
      
    # Get relevant options
    options = world.worlds[player].options

    # Entrances
    set_rule(world.get_entrance("Start", player), lambda state: True)

    set_rule(world.get_entrance("Portal", player),
             lambda state: state.can_reach_location("Reach Moon 12", player)) # <- Moon 12 is when Strange Portals appear

#region 'Welcome' Quests

    set_rule(world.get_location("Open the Booster Pack", player), lambda state: True)
    
    set_rule(world.get_location("Drag the Villager on top of the Berry Bush", player), lambda state: True)
    
    set_rule(world.get_location("Mine a Rock using a Villager", player), lambda state: True)
    
    set_rule(world.get_location("Sell a Card", player), lambda state: True)

    set_rule(world.get_location("Buy the Humble Beginnings Pack", player),
             lambda state: state.sl_has_pack("Humble Beginnings", player))
    
    set_rule(world.get_location("Harvest a Tree using a Villager", player),
             lambda state: state.sl_has_pack("Humble Beginnings", player))
    
    set_rule(world.get_location("Make a Stick from Wood", player), # <- Player has Idea to make a Stick
             lambda state: state.sl_progressive_count("Cooking", 1, player) and
                           state.sl_has_pack("Humble Beginnings", player))
    
    if options.pausing_enabled.value: # <- Set pausing location rule only if pausing is enabled
        set_rule(world.get_location("Pause using the play icon in the top right corner", player),
                 lambda state: True)
        
    set_rule(world.get_location("Grow a Berry Bush using Soil", player), # <- Player has Idea for Growth
             lambda state: state.sl_progressive_count("Growing", 1, player) and
                           state.sl_has_pack("Humble Beginnings", player))
    
    set_rule(world.get_location("Build a House", player), # <- Player has Idea to make a House
             lambda state: state.sl_progressive_count("Villagers", 1, player) and
                           state.sl_has_pack("Humble Beginnings", player))
    
    set_rule(world.get_location("Create Offspring", player), # <- Player has Idea to make a House and Offspring
             lambda state: state.sl_progressive_count("Villagers", 2, player) and
                           state.sl_has_pack("Humble Beginnings", player))

#endregion

#region 'The Grand Scheme' Quests

    set_rule(world.get_location("Unlock all Packs", player),
             lambda state: state.count_group("All Booster Packs", player) == 8)
    
    set_rule(world.get_location("Get 3 Villagers", player), 
             lambda state: state.can_reach_location("Create Offspring", player) or # <- Player can create offspring
                           state.can_reach_location("Kill a Wolf", player)) # <- Player is able to find a Wolf

    set_rule(world.get_location("Find the Catacombs", player), 
             lambda state: state.sl_has_pack("Explorers", player) and # <- Player has Explorers pack for chance to find Catacombs
                           state.can_reach_location("Find a Graveyard", player)) # <- Player can create a graveyard from corpses
    
    set_rule(world.get_location("Find a mysterious artifact", player), 
             lambda state: state.can_reach_location("Find the Catacombs", player)) # <- Player can find Golden Goblet in Catacombs
    
    set_rule(world.get_location("Build a Temple", player), 
             lambda state: state.can_reach_location("Create Offspring", player) and # <- Player can have 3 villagers
                           state.can_reach_location("Get an Iron Bar", player) and # <- Player can make Iron Bars (Planks included)
                           state.can_reach_location("Build a Brickyard", player)) # <- Player can make Bricks

    set_rule(world.get_location("Bring the Goblet to the Temple", player), 
             lambda state: state.can_reach_location("Find a mysterious artifact", player) and # <- Player can find Golden Goblet
                           state.can_reach_location("Build a Temple", player))
    
    set_rule(world.get_location("Kill the Demon", player), # <- Will be an 'Event' location if Goal is 'Kill the Demon' or a Location Check if Goal is 'Kill the Demon Lord'
                    lambda state: state.sl_progressive_count("Growing", 2, player) and # <- Player can make a Garden
                                #   state.can_reach_location("Build a Shed", player) and # <- Player can build a Shed
                                  state.can_reach_location("Cook an Omelette", player) and # <- Player can make an Omelette
                                  state.can_reach_location("Reach Moon 36", player) and # <- Player has all equipment and Shed
                                #   state.can_reach_location("Unlock all Packs", player) and # <- Player has all packs
                                  state.can_reach_location("Bring the Goblet to the Temple", player))
#endregion

#region 'Power & Skill' Quests

    set_rule(world.get_location("Train Militia", player),
             lambda state: state.sl_has_any_ideas(["Slingshot", "Spear"], player) and # <- Player has at least one Militia weapon
                           state.can_reach_location("Make a Stick from Wood", player)) # <- Player can make a Stick (for weapons)) 
    
    set_rule(world.get_location("Kill a Rat", player),
             lambda state: state.sl_has_pack("Humble Beginnings", player)) # <- Player can find Rat in Humble Beginnings Pack
    
    set_rule(world.get_location("Kill a Skeleton", player),
             lambda state: state.can_reach_location("Reach Moon 12", player) and # <- Player has access to all basic equipment
                           state.sl_has_any_packs(["The Armory", "Explorers"], player)) # <- Player has at least one pack to find Skeletons in

#endregion

#region 'Strengthen Up' Quests

    set_rule(world.get_location("Train an Archer", player),
             lambda state: state.can_reach_location("Kill a Giant Rat", player) or # <- Player can find Giant Rat to drop Bow
                           state.can_reach_location("Kill an Elf Archer", player)) # <- Player can find an Elf Archer to drop Bow
    
    set_rule(world.get_location("Make a Villager wear a Rabbit Hat", player),
             lambda state: state.sl_has_pack("Humble Beginnings", player)) # <- Player can find Rabbit in Humble Beginnings
    
    set_rule(world.get_location("Build a Smithy", player),
             lambda state: state.sl_progressive_count("Iron Bars", 4, player) and # <- Player has Ideas for Smelter, Iron Bar and Smithy
                           state.sl_progressive_count("Bricks", 2, player) and # <- Player has Idea for Brick 
                           state.sl_has_all_packs(["Humble Beginnings", "Logic and Reason"], player)) # <- Has packs for resources

    set_rule(world.get_location("Train a Wizard", player),
             lambda state: state.sl_has_idea("Magic Wand", player) and # <- Player has Idea for Magic Wand
                           state.can_reach_location("Make a Stick from Wood", player)) # <- Player can make a Stick (for Magic Wand)
    
    set_rule(world.get_location("Equip an Archer with a Quiver", player),
             lambda state: state.can_reach_location("Train an Archer", player) and # <- Player can get a Bow to train an Archer
                           state.can_reach_location("Kill an Elf Archer", player)) # <- Player can find a Quiver from an Elf Archer
    
    set_rule(world.get_location("Have a Villager with Combat Level 20", player),
             lambda state: state.can_reach_location("Reach Moon 12", player) and # <- Player has access to all basic equipment
                           state.sl_progressive_count("Planks", 2, player)) # <- Player can make Planks for Wooden Shield
    
    set_rule(world.get_location("Train a Ninja", player),
             lambda state: state.sl_has_idea("Throwing Stars", player) and # <- Player has Idea for Throwing Stars
                           state.can_reach_location("Reach Moon 24", player)) # <- Player can build a Smithy to create equipment
    
#endregion

#region 'Potluck' Quests

    set_rule(world.get_location("Start a Campfire", player),
             lambda state: state.sl_progressive_count("Cooking", 2, player) and # <- Player has Idea for Stick and Campfire
                           state.sl_has_pack("Humble Beginnings", player)) 
    
    set_rule(world.get_location("Cook Raw Meat", player),
             lambda state: state.sl_has_idea("Cooked Meat", player) and # <- Player has idea for Cooked Meat
                           state.can_reach_location("Start a Campfire", player)) # <- Player can build a Campfire
    
    set_rule(world.get_location("Cook an Omelette", player),
             lambda state: state.sl_has_idea("Omelette", player) and # <- Player has idea for Omelette
                           state.sl_has_pack("Reap & Sow", player) and # <- Player has access to animals for Raw Meat
                           state.can_reach_location("Cook Raw Meat", player)) # <- Player can build a Campfire
    
    set_rule(world.get_location("Cook a Frittata", player),
             lambda state: state.sl_has_idea("Frittata", player) and # <- Player has idea for Frittata
                           state.sl_has_pack("Curious Cuisine", player) and # <- Player has pack for additional food items
                           state.can_reach_location("Cook an Omelette", player)) # <- Player can build a Campfire

#endregion

#region 'Discovery' Quests

    set_rule(world.get_location("Explore a Forest", player),
             lambda state: state.sl_has_all_packs(["Humble Beginnings", "Explorers"], player)) # <- Has packs to find Mountain
    
    set_rule(world.get_location("Explore a Mountain", player),
             lambda state: state.can_reach_location("Explore a Forest", player)) # <- Player has packs to find Mountain
    
    set_rule(world.get_location("Open a Treasure Chest", player),
             lambda state: state.can_reach_location("Explore a Forest", player)) # <- Player has packs to find Treasure Chest in Locations
    
    set_rule(world.get_location("Get a Dog", player),
             lambda state: state.can_reach_location("Kill a Wolf", player)) # <- Player is able to find a Wolf

    set_rule(world.get_location("Find a Graveyard", player),
             lambda state: state.can_reach_location("Create Offspring", player)) # <- Player is able to create Villagers for Corpses
    
    set_rule(world.get_location("Train an Explorer", player),
             lambda state: state.can_reach_location("Explore a Forest", player)) # <- Player has all packs to find a Map
    
    set_rule(world.get_location("Buy something from a Travelling Cart", player),
             lambda state: state.can_reach_location("Reach Moon 12", player)) # <- Cart always spawns on Moon 19 or 10% chance every odd moon from Moon 9

#endregion

#region 'Ways and Means' Quests

    set_rule(world.get_location("Have 5 Ideas", player),
             lambda state: state.count_group("All Ideas", player) >= 5)
    
    set_rule(world.get_location("Have 10 Ideas", player),
             lambda state: state.count_group("All Ideas", player) >= 10)
    
    set_rule(world.get_location("Have 10 Stone", player),
             lambda state: state.sl_has_pack("Humble Beginnings", player))
    
    set_rule(world.get_location("Have 10 Wood", player),
             lambda state: state.sl_has_pack("Humble Beginnings", player))
    
    set_rule(world.get_location("Get an Iron Bar", player),
             lambda state: state.sl_progressive_count("Iron Bars", 3, player) and # <- Has Ideas for Iron Mine, Smelter and Iron Bar
                           state.sl_progressive_count("Bricks", 2, player) and # <- Has Idea for Bricks (for Smelter)
                           state.sl_progressive_count("Planks", 2, player) and # <- Has idea for Planks (for Smelter)
                           state.sl_has_all_packs(["Humble Beginnings", "Logic and Reason"], player)) # <- Has packs for additional resources
    
    set_rule(world.get_location("Have 5 Food", player),
             lambda state: state.sl_has_pack("Humble Beginnings", player))
    
    set_rule(world.get_location("Have 10 Food", player),
             lambda state: state.can_reach_location("Have 5 Food", player))
    
    set_rule(world.get_location("Have 20 Food", player), 
             lambda state: state.sl_has_pack("Reap & Sow", player) and # <- Player has additional pack for resources
                           state.can_reach_location("Build a Shed", player) and # <- Player can build a shed
                           state.can_reach_location("Have 10 Food", player))
    
    set_rule(world.get_location("Have 50 Food", player), 
             lambda state: state.can_reach_location("Have 20 Food", player))
    
    set_rule(world.get_location("Have 10 Coins", player),
             lambda state: state.sl_has_pack("Humble Beginnings", player))
    
    set_rule(world.get_location("Have 30 Coins", player),
             lambda state: state.can_reach_location("Have 10 Coins", player))
    
    set_rule(world.get_location("Have 50 Coins", player), 
             lambda state: state.can_reach_location("Have 30 Coins", player))
    
#endregion

#region 'Construction' Quests

    set_rule(world.get_location("Have 3 Houses", player), 
             lambda state: state.can_reach_location("Build a House", player)) # <- Player can build a House
    
    set_rule(world.get_location("Build a Shed", player), 
             lambda state: state.sl_has_idea("Shed", player) and # <- Player has Idea for Shed
                           state.can_reach_location("Make a Stick from Wood", player)) # <- Player can make a Stick (for Shed)
    
    set_rule(world.get_location("Build a Quarry", player), 
             lambda state: state.sl_progressive_count("Bricks", 1, player) and # <- Player has Idea for Quarry
                           state.sl_has_pack("Humble Beginnings", player)) # <- Player has packs for additional resources
    
    set_rule(world.get_location("Build a Lumber Camp", player), 
             lambda state: state.sl_progressive_count("Planks", 1, player) and # <- Player has Idea for Lumber Camp
                           state.sl_has_pack("Humble Beginnings", player)) # <- Player has packs for additional resources
    
    set_rule(world.get_location("Build a Farm", player), 
             lambda state: state.sl_progressive_count("Growing", 3, player) and # <- Player has Idea for Farm
                           state.sl_progressive_count("Bricks", 2, player) and # <- Player can make Bricks (for Farm)
                           state.sl_progressive_count("Planks", 1, player) and # <- Player can make Planks (for Farm)
                           state.sl_has_all_packs(["Humble Beginnings", "Reap & Sow"], player)) # <- Player has packs for additional resources
    
    set_rule(world.get_location("Build a Brickyard", player), 
             lambda state: state.sl_progressive_count("Bricks", 3, player) and # <- Player has Idea for Brickyard
                           state.can_reach_location("Get an Iron Bar", player)) # <- Player can make Iron bars
    
    set_rule(world.get_location("Sell a Card at a Market", player), 
             lambda state: state.sl_has_idea("Market", player) and # <- Player has Idea for Market
                           state.sl_progressive_count("Bricks", 2, player) and # <- Player can make Bricks (for Market)
                           state.sl_progressive_count("Planks", 2, player) and # <- Player can make Planks (for Market)
                           state.sl_has_all_packs(["Humble Beginnings", "Logic and Reason"], player)) # <- Player has packs for additional resources
    
#endregion
    
#region 'Longevity' Quests

    set_rule(world.get_location("Reach Moon 6", player),
             lambda state: state.sl_has_any_ideas(["Slingshot", "Spear", "Magic Wand"], player) and # <- Player has at least one basic weapon
                           state.can_reach_location("Make a Stick from Wood", player)) # <- Can make a Stick (for weapons)
    
    set_rule(world.get_location("Reach Moon 12", player), 
             lambda state: state.count_group("Basic Equipment", player) >= 5 and # <- Player has all basic equipment
                           state.can_reach_location("Build a Shed", player) and # <- Player can build a Shed
                           state.can_reach_location("Reach Moon 6", player)) # <- Player can make a Stick (for weapons)
    
    set_rule(world.get_location("Reach Moon 24", player),
             lambda state: state.count_group("Advanced Equipment", player) >= 1 and # <- Player has at least one advanced equipment
                           state.can_reach_location("Build a Smithy", player) and # <- Player can craft advanced equipment
                           state.can_reach_location("Reach Moon 12", player))
    
    set_rule(world.get_location("Reach Moon 36", player),
             lambda state: state.count_group("Advanced Equipment", player) >= 3 and # <- Player has all advanced equipment
                           state.can_reach_location("Reach Moon 24", player))

#endregion

#region 'The Dark Forest' Quests

    set_rule(world.get_location("Find the Dark Forest", player),
             lambda state: state.can_reach_location("Reach Moon 12", player)) # <- Stable Portal first spawns on Moon 12
    
    set_rule(world.get_location("Complete the first wave", player),
             lambda state: state.can_reach_location("Get a Second Villager", player) and # <- Player can have two Villagers
                           state.can_reach_location("Find the Dark Forest", player)) # <- Player can reach The Dark Forest
    
    set_rule(world.get_location("Build a Stable Portal", player),
             lambda state: state.sl_has_idea("Stable Portal", player) and # <- Player has Idea for Stable Portal
                           state.can_reach_location("Build a Brickyard", player) and # <- Player can make Bricks (for Stable Portal)
                           state.can_reach_location("Complete the first wave", player))
    
    set_rule(world.get_location("Get to Wave 6", player),
             lambda state: state.can_reach_location("Reach Moon 24", player) and # <-- Player has access to some Advanced Equipment
                           state.can_reach_location("Create Offspring", player) and # <-- Player can have multiple villagers
                           state.can_reach_location("Build a Stable Portal", player)) # <-- Player can build a stable portal
             
    set_rule(world.get_location("Kill the Wicked Witch", player),
             lambda state: state.can_reach_location("Reach Moon 36", player) and # <-- Player has access to all Advanced Equipment
                           state.can_reach_location("Get to Wave 6", player))

#endregion

#region 'Mobsanity' Quests

    # Set rules if mobsanity is enabled
    if options.mobsanity_enabled.value:
        set_rule(world.get_location("Kill a Bear", player),
                 lambda state: state.can_reach_location("Kill a Skeleton", player)) # <- From Strange Portals after Moon 16 or from Explorers / The Armory
        
        set_rule(world.get_location("Kill a Dark Elf", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Spawns from Wave 4 of Dark Forest
        
        set_rule(world.get_location("Kill an Elf", player),
                 lambda state: state.can_reach_location("Reach Moon 24", player) or # <- Found from Strange Portals from Moon 24
                               state.can_reach_location("Complete the first wave", player)) # <- Found in The Dark Forest
        
        set_rule(world.get_location("Kill an Elf Archer", player),
                 lambda state: state.can_reach_location("Reach Moon 24", player) or # <- Found from Strange Portals from Moon 24
                               state.can_reach_location("Complete the first wave", player)) # <- Found in The Dark Forest
        
        set_rule(world.get_location("Kill an Enchanted Shroom", player),
                 lambda state: state.can_reach_location("Reach Moon 24", player) or # <- Found from Strange Portals from Moon 24
                               state.can_reach_location("Complete the first wave", player)) # <- Found in The Dark Forest
        
        set_rule(world.get_location("Kill an Ent", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Spawns from Wave 4 of Dark Forest
        
        set_rule(world.get_location("Kill a Feral Cat", player),
                 lambda state: state.can_reach_location("Reach Moon 24", player) or # <- Found from Strange Portals from Moon 24
                               state.can_reach_location("Complete the first wave", player)) # <- Found in The Dark Forest
        
        set_rule(world.get_location("Kill a Frog Man", player),
                 lambda state: state.can_reach_location("Kill a Skeleton", player)) # <- From Strange Portals after Moon 16 or from Explorers / The Armory
        
        set_rule(world.get_location("Kill a Ghost", player),
                 lambda state: state.can_reach_location("Reach Moon 24", player) or # <- Found from Strange Portals from Moon 24
                               state.can_reach_location("Complete the first wave", player)) # <- Found in The Dark Forest
        
        set_rule(world.get_location("Kill a Giant Rat", player),
                 lambda state: state.can_reach_location("Kill a Skeleton", player)) # <- From Strange Portals after Moon 16 or from Explorers / The Armory
        
        set_rule(world.get_location("Kill a Giant Snail", player),
                 lambda state: state.can_reach_location("Reach Moon 24", player) or # <- Found from Strange Portals from Moon 24
                               state.can_reach_location("Complete the first wave", player)) # <- Found in The Dark Forest
        
        set_rule(world.get_location("Kill a Goblin", player),
                 lambda state: state.can_reach_location("Reach Moon 12", player) and # <- From Strange Portals after Moon 12
                               state.sl_has_pack("Explorers", player)) # <- From Explorers
        
        set_rule(world.get_location("Kill a Goblin Archer", player),
                 lambda state: state.can_reach_location("Reach Moon 12", player) and # <- From Strange Portals after Moon 12
                               state.sl_has_pack("Explorers", player)) # <- From Explorers
        
        set_rule(world.get_location("Kill a Goblin Shaman", player),
                 lambda state: state.can_reach_location("Kill a Skeleton", player)) # <- From Strange Portals after Moon 16 or from Explorers / The Armory
        
        set_rule(world.get_location("Kill a Merman", player),
                 lambda state: state.can_reach_location("Reach Moon 24", player) or # <- Found from Strange Portals from Moon 24
                               state.can_reach_location("Complete the first wave", player)) # <- Found in The Dark Forest
        
        set_rule(world.get_location("Kill a Mimic", player),
                 lambda state: state.can_reach_location("Kill a Skeleton", player) or # <- From Strange Portals after Moon 16 or from Explorers / The Armory
                               state.can_reach_location("Get to Wave 6", player)) # <- Found in The Dark Forest after Wave 4
        
        set_rule(world.get_location("Kill a Mosquito", player),
                 lambda state: state.can_reach_location("Reach Moon 24", player) or # <- Found from Strange Portals from Moon 24
                               state.can_reach_location("Complete the first wave", player)) # <- Found in The Dark Forest
        
        set_rule(world.get_location("Kill an Ogre", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Spawns from Wave 4
        
        set_rule(world.get_location("Kill an Orc Wizard", player),
                 lambda state: state.can_reach_location("Get to Wave 6", player)) # <- Spawns from Wave 4
        
        set_rule(world.get_location("Kill a Slime", player),
                 lambda state: state.can_reach_location("Kill a Skeleton", player)) # <- From Strange Portals after Moon 16 or from Explorers / The Armory
        
        set_rule(world.get_location("Kill a Small Slime", player),
                 lambda state: state.can_reach_location("Kill a Slime", player)) # <- From killing a Slime
        
        set_rule(world.get_location("Kill a Snake", player),
                 lambda state: state.can_reach_location("Reach Moon 6", player) and # <- Player has access to basic equipment to fight
                               state.sl_has_pack("Explorers", player)) # <- From Explorers (Cave)
        
        set_rule(world.get_location("Kill a Tiger", player),
                 lambda state: state.can_reach_location("Reach Moon 12", player) and # <- Player has access to basic equipment to fight
                               state.sl_has_pack("Explorers", player)) # <- From Explorers (Cave / Jungle)
        
        set_rule(world.get_location("Kill a Wolf", player),
                 lambda state: state.can_reach_location("Kill a Skeleton", player)) # <- From Strange Portals after Moon 16 or from Explorers / The Armory

#endregion
    
    # Set completion condition
    world.completion_condition[player] = lambda state: state.has("Victory", player)