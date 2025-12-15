from BaseClasses import CollectionState, Item, ItemClassification, Location, MultiWorld, Region
from .Enums import GoalType as gt
import logging
from .Options import CastNChillOptions
from typing import Any, Dict, List
from worlds.generic.Rules import set_rule

def set_goal(multiworld: MultiWorld, player: int):
    """"""

    # Get menu region
    menu_region: Region = multiworld.get_region("Menu", player)

    # Create goal event
    goal_location: Location = Location(player, "Goal Complete", None, menu_region)
    goal_location.place_locked_item(Item("Victory", ItemClassification.progression, None, player))
    goal_location.access_rule = __get_goal_rule(multiworld, player)
    
    # Add goal event menu region
    menu_region.locations.append(goal_location)

    # Set rule to require victory event item
    multiworld.completion_condition[player] = lambda state: state.has("Victory", player) 

def __get_goal_rule(multiworld: MultiWorld, player: int) -> CollectionState:

    # Get goal option
    options: CastNChillOptions = multiworld.worlds[player].options
    goal_value: gt = gt(options.goal.value)
    # spots_value: List[str] = options.spots.value
    
    # Get items in this world
    location_list: List[Location] = [ location for location in multiworld.get_locations(player) ]
    
    match goal_value:
        case gt.CatchAllFish:
            return lambda state: all([ state.can_reach_location(location.name, player) for location in location_list if "Catch" in location.name ])
        case gt.CatchAllLegendaries:
            return lambda state: all([ state.can_reach_location(location.name, player) for location in location_list if "Catch a Legendary" in location.name ])
        case _:
            return lambda state: True


def compile_access_rules(access_rules: Dict[str, Any], player: int) -> CollectionState:
    """"""

    if not access_rules:
        return lambda state: True

    if len(access_rules) != 1:
        raise ValueError(f"Access rule object must contain only 1 key, but {len(access_rules)} were found.")
    
    operand, argument = next(iter(access_rules.items()))

    # Boolean operators
    if operand == "and":
        parts = [ compile_access_rules(p, player) for p in __handle_list(operand, argument) ]
        return lambda state, ps=tuple(parts): all(p(state) for p in ps)
    
    if operand == "or":
        parts = [ compile_access_rules(p, player) for p in __handle_list(operand, argument) ]
        return lambda state, ps=tuple(parts): any(p(state) for p in ps)
    
    if operand == "not":
        parts = [ compile_access_rules(__handle_dict(operand, argument), player) ]
        return lambda state, ps=tuple(parts): all(p(state) for p in ps)
    
    # Inventory predicates
    if operand == "has_all":
        logging.info(f"---> Must have all items from: {argument}")
        return lambda state, items=argument: all(state.has(item, player) for item in items)

    if operand == "has_any":
        logging.info(f"---> Must have any item from: {argument}")
        return lambda state, items=argument: any(state.has(item, player) for item in items)

    if operand == "has_count":
        logging.info(f"---> Must have amount of item(s): {argument}")
        return lambda state, items=argument: all(state.count(item, player) >= count for item, count in items.items())
    
    if operand == "can_reach":
        logging.info(f"---> Must be able to reach location(s): {argument}")
        return lambda state, locations=argument: all(state.can_reach_location(location, player) for location in locations)

def __handle_list(operand: str, argument: Any) -> List[Any]:
    """"""
    if not isinstance(argument, list):
        raise TypeError(f"Operand '{operand}' expects a List, but found a {type(argument).__name__}")
    return argument

def __handle_dict(operand: str, argument: Any) -> Dict[str, Any]:
    """"""
    if not isinstance(argument, dict):
        raise TypeError(f"Operand '{operand}' expects a Dict, but found a {type(argument).__name__}")
    return argument