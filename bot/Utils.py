import inspect
import json

from dataclasses import MISSING, fields, is_dataclass
from typing import Any, get_args, get_origin


class Jsonable:
    """Base class for converting to json."""
    
    def to_dict(self) -> dict:
        """Convert to generic dict object."""
        out = {}
        for f in fields(self):
            key = f.metadata.get("json", f.name)
            out[key] = self.__encode(getattr(self, f.name))
        return out
    
    def to_json(self) -> str:
        """Convert to a json string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: dict) -> "Jsonable":
        """Create an instance of the class from a generic dict object."""
        by_json_name = {f.metadata.get("json", f.name): f for f in fields(cls)}
        kwargs = {}

        # Decode only known fields (ignore unknown JSON keys)
        for k, v in (data or {}).items():
            f = by_json_name.get(k)
            if f:
                kwargs[f.name] = cls.__decode(f.type, v)

        # Fill defaults for missing fields
        # for f in fields(cls):
        #     if f.name in kwargs:
        #         continue
        #     if f.default is not MISSING:
        #         kwargs[f.name] = f.default
        #     elif f.default_factory is not MISSING:  # type: ignore
        #         kwargs[f.name] = f.default_factory()  # type: ignore

        return cls(**kwargs)
    
    @classmethod
    def from_json(cls, raw_json: str) -> "Jsonable":
        """Create an instance of a class from a json string."""
        return cls.from_dict(json.loads(raw_json))
    
    @staticmethod
    def __encode(obj: Any):
        """Encode a value to be used in json."""
        if is_dataclass(obj):
            out = {}
            for prop in fields(obj):
                key = prop.metadata.get("json", prop.name)
                out[key] = Jsonable.__encode(getattr(obj, prop.name))
            return out
        elif isinstance(obj, list):
            return [Jsonable.__encode(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: Jsonable.__encode(v) for k, v in obj.items()}
        else:
            return obj
        
    @staticmethod
    def __decode(type_param, obj: Any) -> Any:
        """Decode a value from json"""

        if obj is None:
            return None
        
        origin = get_origin(type_param)

        if origin is list:
            (inner,) = get_args(type_param)
            return [Jsonable.__decode(inner, item) for item in obj]
        elif isinstance(type_param, type) and is_dataclass(type_param):
            return type_param.from_dict(obj) if issubclass(type_param, Jsonable) else type_param(**obj)
        else:
            return obj

class Hookable:
    def __init__(self):
        self._funcs = []

    def __call__(self, func):
        self._funcs.append(func)
        return func

    def __get__(self, obj, obj_type=None):
        if obj is None:
            return self

        funcs = self._funcs

        class BoundHook:
            async def run(_, *a, **k):
                for func in funcs:
                    result = func(obj, *a, **k)  # inject instance safely
                    if inspect.isawaitable(result):
                        await result

            def __call__(_, func):
                funcs.append(func)
                return func

        return BoundHook()