import logging
from typing import Dict, Any
from .Options import StacklandsOptions
from .Items import StacklandsItem, create_all_items, item_table, group_table, name_to_id as item_lookup
from .Locations import name_to_id as location_lookup
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

    options_dataclass = StacklandsOptions
    options: StacklandsOptions

    item_name_to_id = item_lookup
    location_name_to_id = location_lookup
    item_name_groups = group_table
    
    required_client_version = (0, 1, 9)

    # trap_weights: Dict[str, int] = {}

    def generate_early(self) -> None:

        # Get trap item weights
        self.multiworld.trap_weights = {
            "Feed Villagers Trap": self.options.feed_villagers_trap_weight.value,
            "Mob Trap": self.options.mob_trap_weight.value,
            "Sell Cards Trap": self.options.sell_cards_trap_weight.value,
            "Strange Portal Trap": self.options.strange_portal_trap_weight.value,
        }

        logging.info("----- Trap Item Weights -----")
        for key, val in self.multiworld.trap_weights.items():
            logging.info(f"'{key}' weight: {val}")
    
    # Create all items
    def create_items(self):
        create_all_items(self.multiworld, self.player)

    def create_item(self, name: str) -> Item:
        item = next((item for item in item_table if item.name == name))
        return StacklandsItem(name, item, self.player)
    
    # Create all regions (and place all locations within each region)
    def create_regions(self):
        create_all_regions(self.multiworld, self.player)
    
    # Fill the slot data
    def fill_slot_data(self) -> Dict[str, Any]:
        slot_data = {}
        slot_data.update(self.options.as_dict("board_expansion_mode", "board_expansion_amount", "goal", "mobsanity", "moon_length", "packsanity", "pausing", "quest_checks", "sell_cards_trap_amount", "start_inventory"))
        slot_data.update({ "version": "0.1.7" })
        return slot_data
    
    # Set all access rules
    def set_rules(self):
        set_rules(self.multiworld, self.player)