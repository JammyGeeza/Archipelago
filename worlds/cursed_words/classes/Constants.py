from typing import Dict, Tuple

# All available character names, in order
CHARACTER_NAMES: Tuple[str, ...] = ("Rodman", "Nina Nix", "Hayley Bayles", "Bones the Dog", "Sam Gambit", "Octacles")

# All crown colours, in unlock order
CROWN_NAMES: Tuple[str, ...] = ("Purple", "Yellow", "Orange", "Pink", "Green", "Blue", "Red")

# 'Bare Minimum' builds for characters for stage access rule gating
# Can be overridden with 'Stamp Builds' and 'Sticker Builds' player options
CHARACTER_BUILDS: Dict[Tuple[str, str], Tuple[str, str, str, str, str]] = {

    ("Rodman", "Stickers"): ("Fountain", "Worn-out Jeans", "Glass of Milk", "Stilton", "Blueberries"),
    ("Rodman", "Stamps"): ("Kimono", "Xray", "Bubble Tea", "Shaved Ice", "Dango"),

    ("Nina Nix", "Stickers"): ("Game Pad", "Magic Wand", "Fish Cake", "Dusty Coffin", "Ornate Key"),
    ("Nina Nix", "Stamps"): ("Jellyfish", "Flamingo", "Four Leaf Clover", "Akoya Pearl", "Dango"),

    ("Hayley Bayles", "Stickers"): ("Petri Dish", "Alembic Flask", "Lab Coat", "Boomerang", "Brain"),
    ("Hayley Bayles", "Stamps"): ("Magnet", "Go Fish!", "Test Tube", "Giraffe", "Full Battery"),

    ("Sam Gambit", "Stickers"): ("Raccoon", "Carousel Horse", "Moai", "Zebra", "Footprints"),
    ("Sam Gambit", "Stamps"): ("King of the Bridge", "Business Goose", "Jolly Roger", "Bento Box", "Banana"),

    ("Bones the Dog", "Stickers"): ("Postal Horn", "Celestial Body", "Rolodex", "Las Vegas", "Peacock"),
    ("Bones the Dog", "Stamps"): ("Martini", "Card Shark", "Four Leaf Clover", "Go Fish!", "Oden"),

    ("Octacles", "Stickers"): ("Amphora", "Ghost", "Moai", "Mischievous Imp", "Creaky Chair"),
    ("Octacles", "Stamps"): ("Haunted House", "Supervillain", "Giraffe", "Bubble Tea", "Oden"),
}

# Money earned location mapping
MONEY_EARNED_THRESHOLDS: Tuple[int, ...] = [
    10, 15, 20, 25,     # Stage One, increments of 5
    30, 40, 50, 60,     # Stage Two, increments of 10
    70, 80, 90,         # Stage Three, increments of 10
    100, 125, 150,      # Stage Four, increments of 25
    175, 200, 225,      # Stage Five, increments of 25
    250, 275, 300,      #             increments of 25 (advanced)
    350, 400, 450, 500  #             increments of 50 (expert)
]

# Required Sticker/Stamp item percentages for each stage.
STAGE_PERCENTAGES: Dict[str, Tuple[float, float, float, float, float]] = {
    "Rodman": (0.0, 0.2, 0.4, 0.8, 1.0),
    "Nina Nix": (0.0, 0.2, 0.4, 0.8, 1.0),
    "Hayley Bayles": (0.0, 0.2, 0.4, 0.8, 1.0),
    "Bones the Dog": (0.0, 0.2, 0.4, 0.8, 1.0),
    "Sam Gambit": (0.0, 0.2, 0.4, 0.8, 1.0),
    "Octacles": (0.0, 0.2, 0.4, 0.8, 1.0),
}

# # Required Sticker/Stamp item percentages for each stage.
# # (Yes, it's gross that it's hard-coded but it makes tweaking them easier in future)
# STAGE_PERCENTAGES: Dict[Tuple[str, str], Tuple[float, float, float, float, float]] = {

#     ("Rodman", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
#     ("Rodman", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
#     ("Rodman", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
#     ("Rodman", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
#     ("Rodman", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
#     ("Rodman", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
#     ("Rodman", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
#     ("Rodman", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),

#     ("Nina Nix", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
#     ("Nina Nix", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
#     ("Nina Nix", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
#     ("Nina Nix", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
#     ("Nina Nix", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
#     ("Nina Nix", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
#     ("Nina Nix", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
#     ("Nina Nix", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),

#     ("Hayley Bayles", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
#     ("Hayley Bayles", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
#     ("Hayley Bayles", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
#     ("Hayley Bayles", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
#     ("Hayley Bayles", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
#     ("Hayley Bayles", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
#     ("Hayley Bayles", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
#     ("Hayley Bayles", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),

#     ("Sam Gambit", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
#     ("Sam Gambit", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
#     ("Sam Gambit", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
#     ("Sam Gambit", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
#     ("Sam Gambit", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
#     ("Sam Gambit", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
#     ("Sam Gambit", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
#     ("Sam Gambit", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),

#     ("Bones the Dog", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
#     ("Bones the Dog", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
#     ("Bones the Dog", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
#     ("Bones the Dog", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
#     ("Bones the Dog", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
#     ("Bones the Dog", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
#     ("Bones the Dog", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
#     ("Bones the Dog", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),

#     ("Octacles", "Base"): (0.0, 0.1, 0.25, 0.4, 0.55),
#     ("Octacles", "Purple"): (0.0, 0.15, 0.3, 0.45, 0.6),
#     ("Octacles", "Yellow"): (0.05, 0.2, 0.35, 0.5, 0.65),
#     ("Octacles", "Orange"): (0.1, 0.25, 0.4, 0.55, 0.7),
#     ("Octacles", "Pink"): (0.15, 0.3, 0.45, 0.6, 0.75),
#     ("Octacles", "Green"): (0.2, 0.35, 0.5, 0.65, 0.8),
#     ("Octacles", "Blue"): (0.25, 0.4, 0.55, 0.7, 0.85),
#     ("Octacles", "Red"): (0.3, 0.45, 0.6, 0.75, 0.90),
# }

# Word score locations mapping
WORD_SCORE_THRESHOLDS: Tuple[int, ...] = [
    5, 10, 15, 20, 25,                  # Stage One, increments of 5
    50, 75, 100, 125, 150, 175, 200,    # Stage Two, increments of 25
    250, 300, 350, 400, 450, 500,       # Stage Three, increments of 50
    600, 700, 800, 900, 1000,           # Stage Four, increments of 100
    1250, 1500, 1750, 2000, 2250, 2500, # Stage Five, increments of 250
    3000, 3500, 4000, 4500, 5000,       #             increments of 500 (advanced)
    6000, 7000, 8000, 9000, 10000       #             increments of 1000 (expert)
]