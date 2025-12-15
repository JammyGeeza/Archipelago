from dataclasses import dataclass
from BaseClasses import ItemClassification, Options
from .Enums import GoalType
from .Items import item_table
import logging
from Options import Choice, OptionDict, OptionList, ItemDict, PerGameCommonOptions, StartInventoryPool
from .Regions import region_table
from typing import Dict, List

# Get all spot names
_spot_names: List[str] = [ region.name for region in region_table if region.is_spot ]
_filler_item_names: List[str] = [ item.name for item in item_table if item.classification is ItemClassification.filler ]

class Goal(Choice):
    """
    Select the goal for your session.

    Catch All Fish          -> Catch at least one of every fish from each <Spot>.
    Catch All Legendaries   -> Catch the Legendary fish from each <Spot>.

    More goals coming soon ...
    """
    display_name = "Goal"
    option_catch_all_fish = GoalType.CatchAllFish.value
    option_catch_all_legendaries = GoalType.CatchAllLegendaries.value
    default = option_catch_all_legendaries

class Spots(OptionList):
    """
    The spots to include in your session.

    Option Usage
      - Use [ "All" ] to include all supported spots
      - Use [ "The Fork", "The Mistwood" ] etc. to include a custom set of spots.

    Currently Supports:
       - The Fork
       - Beaver Dam
       - The Mistwood

    More spots coming soon ...
    """

    display_name = "Included Spots"
    valid_keys_casefold = False
    valid_keys = [ "All" ] + _spot_names
    default = _spot_names

class StartingSpot(OptionDict):
    """
    The spot to start your session from - you will receive the license for this spot in your Starting Items.

    Option Usage
      - Use { "Random": 50 } to randomly select your starting spot from all included spots from the <Spots> option.
      - Use { "The Fork": 50, "The Mistwood": 50 } to randomly select from a custom set of included spots from the <Spots> option.

    Currently Supports:
      - The Fork
      - Beaver Dam
      - The Mistwood

    NOTE: This option will ONLY select from spots that match your included spots from the <Spots> option.
          If no matching spots found, generation will default to "Random".
    """

    display_name = "Starting Spot"
    valid_keys_casefold = False
    valid_keys = [ "Random" ] + _spot_names
    default = { spot: 50 for spot in _spot_names }

class FillerItemWeights(ItemDict):
    """
    The weightings for filler item frequency in the item pool.
    The higher the number for each item (relative to the other items), the more times it is likely to appear in the pool.

    EXAMPLE: { "Gold": 5, "Nothing": 15 }
    The 'Nothing' item is likely to appear 3x as often as the 'Gold' item.
    """

    display_name = "Filler Item Weights"
    valid_keys_casefold = False
    valid_keys = _filler_item_names
    default = { item: 50 for item in _filler_item_names }

@dataclass
class CastNChillOptions(PerGameCommonOptions):
    """"""
    # Goal settings
    goal: Goal
    spots: Spots
    starting_spot: StartingSpot

    # Item Weights
    filler_weights: FillerItemWeights

    # Built-in
    start_inventory_from_pool: StartInventoryPool

    def resolve_options(self):
        """Resolve options to ensure successful generation."""

        logging.info(f"Initial included spots: {self.spots.value}")

        # Check if no Spots provided or 'All' exists and return to default
        if len(self.spots.value) == 0 or "All" in self.spots.value:
            logging.warning(f"No spots provided in 'Included Spots' option OR 'All' entry found, including all spots ...")
            self.spots.value = _spot_names

        logging.info(f"Resolved included spots value: {self.spots.value}")

        logging.info(f"Initial starting spots value: {self.starting_spot.value}")

        # Check if any Starting Spots match included Spots
        included_spots: List[str] = self.spots.value
        if len(included_spots) == 0 or "Random" in included_spots or not bool(set(self.starting_spot.value.keys()) & set(included_spots)):
            logging.warning(f"No spots provided in 'Starting Spot' option OR 'Random' entry found OR no matching included spots, randomly selecting starting spot from all included spots ...")
            self.starting_spot.value = { spot: 50 for spot in included_spots }

        # Remove any starting spots that are not in the included spots
        starting_spots: Dict[str, int] = self.starting_spot.value
        self.starting_spot.value = { spot: starting_spots[spot] for spot in starting_spots.keys() & included_spots }

        logging.info(f"Resolved starting spots value: {self.starting_spot.value}")

        logging.info(f"Starting filler weights value: {self.filler_weights.value}")

        # Check if no Filler Weights provided and return to default
        if len(self.filler_weights.value) == 0:
            logging.warning(f"No filler weights provided, weighting all filler items ...")
            self.filler_weights.value = self.filler_weights.default

        logging.info(f"Resolved filler weights value: {self.filler_weights.value}")