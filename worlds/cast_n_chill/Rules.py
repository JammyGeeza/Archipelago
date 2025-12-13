from BaseClasses import CollectionState
from typing import Any, Dict, List
from worlds.generic.Rules import set_rule

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
        return lambda state, items=argument: all(state.has(item, player) for item in items)

    if operand == "has_any":
        return lambda state, items=argument: any(state.has(item, player) for item in items)

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