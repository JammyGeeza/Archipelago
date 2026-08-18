from typing import Dict, List

def _substitute_placeholders(value: any, placeholder_values: Dict[str, any]) -> any:
    """Substitute the {placeholder} across all string values."""
    
    # If value is a string...
    if isinstance(value, str):
        
        # Find placeholder marker and replace with value
        if value.startswith("{") and value.endswith("}") and value.count("{") == 1:
            key = value[1:-1]
            
            if key in placeholder_values:
                return placeholder_values[key]
        
        return value.format(**placeholder_values) if "{" in value else value
    
    # If value is a dict, substitute the values within
    if isinstance(value, dict):
        return {k: _substitute_placeholders(v, placeholder_values) for k, v in value.items()}
    
    # If value is a list, substitute the values within
    if isinstance(value, list):
        return [_substitute_placeholders(v, placeholder_values) for v in value]
    
    return value

def _expand(entry: Dict[any, any], axes: List[Dict[any, any]], placeholder_values: Dict[str, any], tags: Dict[str, List[str]], shared_lookups: Dict[str, List[any]]) -> List[Dict[any, any]]:
    """Traverse 'iterate' property and resolve each axis"""

    # If no axes, just substitute the placeholders
    if not axes:
        clone = {k: v for k, v in entry.items() if k != "iterate"}
        clone = _substitute_placeholders(clone, placeholder_values)
        
        for tag_field, values in tags.items():
            clone[tag_field] = list(dict.fromkeys(entry.get(tag_field, []) + values))

        return [clone]

    axis = axes[0]
    remaining = axes[1:]
    format = axis.get("format", "{value}")

    # If 'range' axis, resolve values as (start + count * step)
    if "range" in axis:
        r = axis["range"]
        step = r.get("step", 1)
        count = r.get("count", 1)
        raw_values = [r["start"] + i * step for i in range(count)]

    # If 'values' axis and it's a list, take the values as they are
    elif isinstance(axis["values"], list):
        raw_values = axis["values"]

    # Otherwise, attempt to get values from shared lookup
    else:
        raw_values = shared_lookups[axis["values"]]

    # Add placeholder values to appropriate character/option tags
    results = []
    for raw_value in raw_values:
        next_placeholder_values = {
            **placeholder_values,
            axis["placeholder"]: format.format(value=raw_value),
            f"{axis['placeholder']}_raw": raw_value,
        }

        next_tags = dict(tags)
        if "tag" in axis:
            next_tags[axis["tag"]] = tags.get(axis["tag"], []) + [str(raw_value)]

        results += _expand(entry, remaining, next_placeholder_values, next_tags, shared_lookups)

    return results


def expand_item(entry: Dict[any, any], shared_lookups: Dict[str, List[any]]) -> List[Dict[any, any]]:
    """Expand an item by its 'iterate' property."""
    
    # Ignore if no iterate property
    if "iterate" not in entry:
        return [entry]
    
    # Expand iterate property
    return _expand(entry, entry["iterate"], {}, {}, shared_lookups)