from test.bases import WorldTestBase

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
        "Get to Wave 6",
        "Fight the Wicked Witch",
    ]

    # Mobsanity locations specific to the dark forest
    dark_forest_mobsanity_locations = [
        "Kill a Dark Elf",
        "Kill an Ent",
        "Kill an Ogre",
        "Kill an Orc Wizard"
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
