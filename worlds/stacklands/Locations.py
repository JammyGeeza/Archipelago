from typing import List, TypedDict
from BaseClasses import Location

class StacklandsLocation(Location):
    game = "Stacklands"


class LocationData(TypedDict):
    name: str
    region: str

# Locations table
locations_table: List[LocationData] = [
    
    # Mainland Quests
    
    # 'Welcome' Category
    {"name": "Open the Booster Pack", "region": "Mainland"},
    {"name": "Drag the Villager on top of the Berry Bush", "region": "Mainland"},
    {"name": "Mine a Rock using a Villager", "region": "Mainland"},
    {"name": "Sell a Card", "region": "Mainland"},
    {"name": "Buy the Humble Beginnings Pack", "region": "Mainland"},
    {"name": "Harvest a Tree using a Villager", "region": "Mainland"},
    {"name": "Make a Stick from Wood", "region": "Mainland"},
    {"name": "Pause using the play icon in the top right corner", "region": "Mainland"},
    {"name": "Grow a Berry Bush using Soil", "region": "Mainland"},
    {"name": "Build a House", "region": "Mainland"},
    {"name": "Get a Second Villager", "region": "Mainland"},
    {"name": "Create Offspring", "region": "Mainland"},
    
    # 'The Grand Scheme' Category
    # {"name": "Unlock All Packs", "region": "Mainland"}, <- Can ONLY be unlocked by receiving all packs from checks, seems pointless? (Also this quest triggers when Order and Structure pack is unlocked, so usually triggers far too early)
    {"name": "Get 3 Villagers", "region": "Mainland"},
    {"name": "Find the Catacombs", "region": "Mainland"},
    {"name": "Find a mysterious artifact", "region": "Mainland"},
    {"name": "Build a Temple", "region": "Mainland"},
    {"name": "Bring the Goblet to the Temple", "region": "Mainland"},
    {"name": "Kill the Demon", "region": "Mainland"},
    {"name": "Kill the Demon Lord", "region": "Mainland"},
    
    # 'Power & Skill' Category
    {"name": "Train Militia", "region": "Mainland"},
    {"name": "Kill a Rat", "region": "Mainland"},
    {"name": "Kill a Skeleton", "region": "Mainland"},
    
    # 'Strengthening Up' Category
    # {"name": "Train an Archer", "region": "Mainland"}, <- Bow / Crossbow require Rope (from Island) or is a chance drop from Elf Archer - seems unfair.
    {"name": "Make a Villager wear a Rabbit Hat", "region": "Mainland"},
    {"name": "Build a Smithy", "region": "Mainland"},
    {"name": "Train a Wizard", "region": "Mainland"},
    # {"name": "Equip an Archer with a Quiver", "region": "Mainland"}, <- Is a chance drop from Elf Archer - seems unfair.
    {"name": "Have a Villager with Combat Level 20", "region": "Mainland"},
    {"name": "Train a Ninja", "region": "Mainland"},
    
    # 'Potluck' Category
    {"name": "Start a Campfire", "region": "Mainland"},
    {"name": "Cook Raw Meat", "region": "Mainland"},
    {"name": "Cook an Omelette", "region": "Mainland"},
    {"name": "Cook a Frittata", "region": "Mainland"},
    
    # 'Discovery' Category
    {"name": "Explore a Forest", "region": "Mainland"},
    {"name": "Explore a Mountain", "region": "Mainland"},
    {"name": "Open a Treasure Chest", "region": "Mainland"},
    {"name": "Find a Graveyard", "region": "Mainland"},
    {"name": "Get a Dog", "region": "Mainland"},
    {"name": "Train an Explorer", "region": "Mainland"},
    {"name": "Buy something from a Travelling Cart", "region": "Mainland"},
    
    # 'Ways and Means' Category
    {"name": "Have 5 Ideas", "region": "Mainland"},
    {"name": "Have 10 Ideas", "region": "Mainland"},
    {"name": "Have 10 Wood", "region": "Mainland"},
    {"name": "Have 10 Stone", "region": "Mainland"},
    {"name": "Get an Iron Bar", "region": "Mainland"},
    {"name": "Have 5 Food", "region": "Mainland"},
    {"name": "Have 10 Food", "region": "Mainland"},
    {"name": "Have 20 Food", "region": "Mainland"},
    {"name": "Have 50 Food", "region": "Mainland"},
    {"name": "Have 10 Coins", "region": "Mainland"},
    {"name": "Have 30 Coins", "region": "Mainland"},
    {"name": "Have 50 Coins", "region": "Mainland"},
    
    # 'Construction' Category
    {"name": "Have 3 Houses", "region": "Mainland"},
    {"name": "Build a Shed", "region": "Mainland"},
    {"name": "Build a Quarry", "region": "Mainland"},
    {"name": "Build a Lumber Camp", "region": "Mainland"},
    {"name": "Build a Farm", "region": "Mainland"},
    {"name": "Build a Brickyard", "region": "Mainland"},
    {"name": "Sell a Card at a Market", "region": "Mainland"},
    
    # 'Longevity' Category
    {"name": "Reach Moon 6", "region": "Mainland"},
    {"name": "Reach Moon 12", "region": "Mainland"},
    {"name": "Reach Moon 24", "region": "Mainland"},
    {"name": "Reach Moon 36", "region": "Mainland"},
]

base_id: int = 91000
current_id: int = base_id

lookup_id_to_name = {}
lookup_name_to_id = {}
    
for location in locations_table:
        
    # Add to lookups
    lookup_id_to_name[current_id] = location["name"]
    lookup_name_to_id[location["name"]] = current_id
        
    # Increment ID
    current_id += 1
