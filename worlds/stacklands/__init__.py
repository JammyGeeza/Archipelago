from typing import Dict, Any
from .Options import StacklandsOptions
from .Items import StacklandsItem, create_all_items, item_group_table, lookup_name_to_id as items_lookup_name_to_id
from .Locations import lookup_name_to_id as locations_lookup_name_to_id
from .Regions import create_all_regions
from .Rules import set_all_rules
from worlds.AutoWorld import World, WebWorld
from BaseClasses import Item, ItemClassification, Location, Region

class StacklandsWeb(WebWorld):
    theme = "jungle"
    # TODO: Set this up

class StacklandsWorld(World):
    """
    Stacklands - Description here
    """
    
    game = "Stacklands"
    web = StacklandsWeb()
    
    item_name_to_id = items_lookup_name_to_id
    location_name_to_id = locations_lookup_name_to_id
    item_name_groups = item_group_table

    options_dataclass = StacklandsOptions
    options: StacklandsOptions
    
    required_client_version = (0, 1, 9)
    
    def __init(self, multiworld, player):
        super(StacklandsWorld, self).__init(multiworld, player)

    def generate_early(self):
        self.basic_pack: bool = self.options.basic_pack.value
        self.death_link: bool = self.options.death_link.value
        self.goal: int = self.options.goal.value
        self.pause_enabled: bool = self.options.pause_enabled.value
    
    def create_event(self, event: str):
        return StacklandsItem(event, ItemClassification.progression_skip_balancing, None, self.player)
    
    # Create all items
    def create_items(self) -> None:
        create_all_items(self.multiworld, self.player, self.options)
    
    # Create all regions (and place all locations within each region)
    def create_regions(self) -> None:
        create_all_regions(self.multiworld, self.player, self.options)
    
    # Fill the slot data
    def fill_slot_data(self) -> Dict[str, Any]:
        return {
            "BasicPack": self.basic_pack,
            "DeathLink": self.death_link,
            "Goal": self.goal,
            "PauseEnabled": self.pause_enabled
        }
    
    # Set all access rules
    def set_rules(self):
        set_all_rules(self.multiworld, self.player)