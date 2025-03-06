from typing import Dict, Any
from .Options import StacklandsOptions
from .Items import StacklandsItem, create_all_items, item_table
from .Locations import location_table
from .Regions import create_all_regions
from .Rules import set_rules
from worlds.AutoWorld import World, WebWorld
from BaseClasses import Item

class StacklandsWeb(WebWorld):
    theme = "jungle"
    # TODO: Set this up

class StacklandsWorld(World):
    """
    Stacklands - Description here
    """
    
    game = "Stacklands"
    web = StacklandsWeb()
    topology_present = False
    item_name_to_id = { name: data.code for name, data in item_table.items() }
    location_name_to_id = { name: data.code for name, data in location_table.items() }
    # item_name_groups = item_group_table

    options_dataclass = StacklandsOptions
    options: StacklandsOptions
    
    required_client_version = (0, 1, 9)
    
    # Create all items
    def create_items(self):
        create_all_items(self.multiworld, self.player)

    def create_item(self, name: str) -> Item:
        return StacklandsItem(name, self.player)
    
    # Create all regions (and place all locations within each region)
    def create_regions(self):
        create_all_regions(self.multiworld, self.player)
    
    # Fill the slot data
    def fill_slot_data(self) -> Dict[str, Any]:
        return {
            "BasicPack": bool(self.options.basic_pack.value),
            "DeathLink": bool(self.options.death_link.value),
            "Goal": int(self.options.goal.value),
            "PauseEnabled": bool(self.options.pause_enabled.value)
        }
    
    # Set all access rules
    def set_rules(self):
        set_rules(self.multiworld, self.player)