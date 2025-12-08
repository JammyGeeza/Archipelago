import logging
from typing import Dict, Any
from .Options import StacklandsOptions
from .Enums import GoalFlags, RegionFlags
from .Items import StacklandsItem, create_all_items, item_table, group_table, name_to_id as item_lookup
from .Locations import name_to_id as location_lookup
from .Regions import create_all_regions
from .Rules import set_rules
from worlds.AutoWorld import World, WebWorld
from BaseClasses import Item
from Options import OptionGroup
from . import Options

class StacklandsWeb(WebWorld):
    theme = "jungle"

    option_groups = [
        OptionGroup("Run Settings", [
            Options.Boards,
            Options.BoardExpansionMode,
            Options.BoardExpansionAmount,
            Options.BoardExpansionCount,
            Options.MoonLength,
            Options.Pausing
        ]),
        OptionGroup("Goal", [
            Options.Goal
        ]),
        OptionGroup("Sanities", [
            Options.Equipmentsanity,
            Options.Foodsanity,
            Options.Locationsanity,
            Options.Mobsanity,
            Options.MobsanityBalancing,
            Options.Structuresanity
        ]),
        OptionGroup("Traps", [
            Options.TrapFill,
            Options.FeedVillagersTrapWeight,
            Options.MobTrapWeight,
            Options.SellCardsTrapWeight,
            Options.SellCardsTrapAmount,
            Options.StrangePortalTrapWeight
        ]),
        OptionGroup("QoL", [
            Options.RedStructureSpawn
        ])
    ]

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

    def generate_early(self) -> None:

        # Define goal weights based on options
        goal_weights: Dict[RegionFlags, int] = {
            RegionFlags.Mainland: 1 if bool(self.options.boards.value & RegionFlags.Mainland) else 0,
            RegionFlags.Forest: 1 if bool(self.options.boards.value & RegionFlags.Forest) else 0,
            RegionFlags.Island: 1 if bool(self.options.boards.value & RegionFlags.Island) else 0
        }

        # Set goal bosses as all bosses if selected, otherwise select random boss
        self.multiworld.goal_boards = (
            self.options.boards.value 
            if self.options.goal.value is GoalFlags.AllBosses else 
            self.multiworld.random.choices(
                population=list(goal_weights.keys()),
                weights=list(goal_weights.values()),
                k=1
            ).pop()
        )

        # Get resource booster item weights
        self.multiworld.filler_booster_weights = {
            "Mainland Resource Booster Pack": 1 if bool(self.options.boards.value & RegionFlags.Mainland) else 0,
            "Island Resource Booster Pack": 1 if bool(self.options.boards.value & RegionFlags.Island) else 0,
        }

        # Get trap item weights
        self.multiworld.trap_weights = {
            "Feed Villagers Trap": self.options.feed_villagers_trap_weight.value,
            "Mob Trap": self.options.mob_trap_weight.value,
            "Sell Cards Trap": self.options.sell_cards_trap_weight.value,
            "Strange Portal Trap": self.options.strange_portal_trap_weight.value,
        }
    
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
        slot_data.update(self.options.as_dict(
            "boards",
            "board_expansion_mode",
            "board_expansion_amount",
            "equipmentsanity",
            "foodsanity",
            "goal",
            "locationsanity",
            "mobsanity",
            "mobsanity_balancing",
            "moon_length",
            "pausing",
            "red_structure_spawn",
            "sell_cards_trap_amount",
            # "spendsanity",
            # "spendsanity_cost",
            # "spendsanity_count",
            "start_inventory",
            "structuresanity"
        ))

        # Add additional data to slot data
        slot_data.update({
            "goal_boards": self.multiworld.goal_boards,
            "version": "0.2.4"
        })

        return slot_data
    
    # Set all access rules
    def set_rules(self):
        set_rules(self.multiworld, self.player)