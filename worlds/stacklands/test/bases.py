from test.bases import WorldTestBase
from typing import List

class StacklandsWorldTestBase(WorldTestBase):
    game = "Stacklands"

    # Dark forest items
    dark_forest_items = [
        "Idea: Stable Portal"
    ]

    # All dark forest locations
    dark_forest_locations = [
        "Find the Dark Forest",
        "Complete the first wave",
        "Build a Stable Portal",
        "Get to wave 2",
        "Get to wave 4",
        "Get to wave 6",
        "Get to wave 8",
        "Fight the Wicked Witch",
    ]

    # Mobsanity locations specific to the dark forest
    dark_forest_mobsanity_locations = [
        "Kill a Dark Elf",
        "Kill an Ent",
        "Kill an Ogre",
        "Kill an Orc Wizard"
    ]

    # Island locations
    island_locations = [
        "Build a Rowboat",
        "Build a Cathedral on the Mainland",
        "Bring the Island Relic to the Cathedral",
        "Kill the Demon Lord",

        "Get 2 Bananas",
        "Punch some Driftwood",
        "Have 3 Shells",
        "Catch a Fish",
        "Make Rope",
        "Make a Fish Trap",
        "Make a Sail",
        "Build a Sloop",

        "Unlock all Island Packs",
        "Find a Treasure Map",
        "Find Treasure",
        "Forge Sacred Key",
        "Open the Sacred Chest",
        "Kill the Kraken",

        "Make Sushi",
        "Cook Crab Meat",
        "Make Ceviche",
        "Make a Seafood Stew",
        "Make a Bottle of Rum",

        "Have 10 Shells",
        "Get a Villager Drunk",
        "Make Sandstone",
        "Build a Mess Hall",
        "Build a Greenhouse",
        "Have a Poisoned Villager",
        "Cure a Poisoned Villager",
        "Build a Composter",
        "Bribe a Pirate Boat",
        "Befriend a Pirate",
        "Make a Gold Bar",
        "Make Glass",

        "Train an Archer",
        "Break a Bottle",
        "Equip an Archer with a Quiver",
        "Make a Villager wear Crab Scale Armor",
        "Craft the Amulet of the Forest",

        "Buy the On the Shore Pack",
        "Buy the Island of Ideas Pack",
        "Buy the Grilling and Brewing Pack",
        "Buy the Island Insights Pack",
        "Buy the Advanced Archipelago Pack",
        "Buy the Enclave Explorers Pack",
        "Buy 5 Island Booster Packs",
        "Buy 10 Island Booster Packs",
        "Buy 25 Island Booster Packs",

        "Have 30 Shells",
        "Have 50 Shells",

        "Have 10 Cotton",
        "Have 10 Fabric",
        "Have 10 Glass",
        "Have 10 Gold Bars",
        "Have 10 Rope",
        "Have 10 Sails",
        "Have 10 Sandstone"
    ]

    # Mainland locations
    mainland_locations = [
        "Open the Booster Pack",
        "Drag the Villager on top of the Berry Bush",
        "Mine a Rock using a Villager",
        "Sell a Card",
        "Buy the Humble Beginnings Pack",
        "Harvest a Tree using a Villager",
        "Make a Stick from Wood",
        "Pause using the play icon in the top right corner",
        "Grow a Berry Bush using Soil",
        "Build a House",
        "Get a Second Villager",
        "Create Offspring",

        "Unlock all Packs",
        "Get 3 Villagers",
        "Find the Catacombs",
        "Find a mysterious artifact",
        "Build a Temple",
        "Bring the Goblet to the Temple",
        "Kill the Demon",

        "Train Militia",
        "Kill a Rat",
        "Kill a Skeleton",

        "Make a Villager wear a Rabbit Hat",
        "Build a Smithy",
        "Train a Wizard",
        "Have a Villager with Combat Level 20",
        "Train a Ninja",

        "Start a Campfire",
        "Cook Raw Meat",
        "Cook an Omelette",
        "Cook a Frittata",

        "Explore a Forest",
        "Explore a Mountain",
        "Open a Treasure Chest",
        "Find a Graveyard",
        "Get a Dog",
        "Train an Explorer",
        "Buy something from a Travelling Cart",

        "Have 5 Ideas",
        "Have 10 Ideas",
        "Have 10 Wood",
        "Have 10 Stone",
        "Get an Iron Bar",
        "Have 5 Food",
        "Have 10 Food",
        "Have 20 Food",
        "Have 50 Food",
        "Have 10 Coins",
        "Have 30 Coins",
        "Have 50 Coins",

        "Have 3 Houses",
        "Build a Shed",
        "Build a Quarry",
        "Build a Lumber Camp",
        "Build a Farm",
        "Build a Brickyard",
        "Sell a Card at a Market",

        "Reach Moon 6",
        "Reach Moon 12",
        "Reach Moon 24",
        "Reach Moon 36",

        "Buy the Seeking Wisdom Pack",
        "Buy the Reap & Sow Pack",
        "Buy the Curious Cuisine Pack",
        "Buy the Logic and Reason Pack",
        "Buy the The Armory Pack",
        "Buy the Explorers Pack",
        "Buy the Order and Structure Pack",
        "Buy 5 Mainland Booster Packs",
        "Buy 10 Mainland Booster Packs",
        "Buy 25 Mainland Booster Packs",

        "Sell 5 Cards",
        "Sell 10 Cards",
        "Sell 25 Cards",

        "Reach Moon 18",
        "Reach Moon 30",

        "Get 5 Villagers",
        "Get 7 Villagers",

        "Have 10 Bricks",
        "Have 10 Flint",
        "Have 10 Iron Bars",
        "Have 10 Iron Ore",
        "Have 10 Planks",
        "Have 10 Sticks"
    ]

    # All mobsanity locations
    mobsanity_locations = [
        "Kill a Bear",
        "Kill an Elf",
        "Kill an Elf Archer",
        "Kill an Enchanted Shroom",
        "Kill a Feral Cat",
        "Kill a Frog Man",
        "Kill a Ghost",
        "Kill a Giant Rat",
        "Kill a Giant Snail",
        "Kill a Goblin",
        "Kill a Goblin Archer",
        "Kill a Goblin Shaman",
        "Kill a Merman",
        "Kill a Mimic",
        "Kill a Mosquito",
        "Kill a Slime",
        "Kill a Small Slime",
        "Kill a Snake",
        "Kill a Tiger",
        "Kill a Wolf"
    ]

    # Pausing location(s)
    pausing_locations = [
        "Pause using the play icon in the top right corner"
    ]

    # Trap item(s)
    trap_items = [
        "Chickens",
        "Goop",
        "Rabbits",
        "Rat",
        "Slime",
        "Snake"
    ]

    def check_items_exist(self, items) -> None:
        """Check that all specified items exist in the item pool."""
        for item in items:
            try:
                self.assertIsNotNone(self.get_item_by_name(item))
            except Exception as ex:
                self.fail(f"Failed on item '{item}' with exception: {ex}")

    def check_locations_exist(self, locations) -> None:
        """"""
        for location in locations:
            try:
                self.assertIsNotNone(self.world.get_location(location))
            except Exception as ex:
                self.fail(f"Failed on location '{location}' with exception: {ex}")

    @property
    def base_locations(self) -> List[str]:
        return []
    
    @property
    def base_items(self) -> List[str]:
        return []

    def test_base_items(self) -> None:
        """Test that all base items are in the item pool."""
        self.check_items_exist(self.base_items)

    def test_base_locations(self) -> None:
        """Test that all base locations are in the location pool."""
        self.check_locations_exist(self.base_locations)
