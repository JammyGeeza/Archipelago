import inspect
import json

from dataclasses import MISSING, fields, is_dataclass
from datetime import datetime, timedelta
from typing import Any, ClassVar, Dict, Union, get_args, get_origin


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

        return cls(**kwargs)

    @staticmethod
    def __encode(value: Any) -> Any:
        """Encode values for JSON serialization."""
        if isinstance(value, Jsonable):
            return value.to_dict()
        if isinstance(value, dict):
            return {str(k): Jsonable.__encode(v) for k, v in value.items()}
        if isinstance(value, list):
            return [Jsonable.__encode(v) for v in value]
        return value

    @staticmethod
    def __decode(tp, value: Any) -> Any:
        """Decode JSON values into typed Python objects."""
        if value is None:
            return None

        origin = get_origin(tp)

        # Handle Optional[T] / Union[T, None]
        if origin is Union:
            args = [a for a in get_args(tp) if a is not type(None)]
            return Jsonable.__decode(args[0], value) if args else value

        # Handle List[T]
        if origin is list:
            (elem_t,) = get_args(tp)
            return [Jsonable.__decode(elem_t, v) for v in (value or [])]

        # Handle Dict[K, V]
        if origin is dict:
            key_t, val_t = get_args(tp)
            out = {}
            for k, v in (value or {}).items():
                # JSON object keys are always strings
                if key_t is int:
                    k2 = int(k)
                elif key_t is float:
                    k2 = float(k)
                else:
                    k2 = k
                out[k2] = Jsonable.__decode(val_t, v)
            return out

        # Handle nested Jsonable subclasses
        try:
            if isinstance(tp, type) and issubclass(tp, Jsonable):
                return tp.from_dict(value)
        except TypeError:
            pass

        # Primitive / fallback
        return value

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
    
class ItemQueue:
    def __init__(self):
        self.items: Dict[int, int] = {}
        self.expires: datetime = datetime.now()

    def add(self, item_id: int):
        self.items[item_id] = self.items.get(item_id, 0) + 1
        self.expires = datetime.now() + timedelta(seconds=2)
