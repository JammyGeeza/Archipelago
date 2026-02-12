import json
import inspect
import logging
import sys

from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from typing import Any, Callable, ClassVar, Dict, List, Optional, Type, get_args, get_origin


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

@dataclass
class NetworkItem(Jsonable):
    """Object containing item data."""
    item: int = 0
    location: int = 0
    player: int = 0
    flags: int = 0


@dataclass
class NetworkVersion(Jsonable):
    """Object containing the 'supported' archipelago version"""
    class_: str = field(default="Version", metadata={"json": "class"})
    major: int = 0
    minor: int = 0
    build: int = 0


@dataclass
class TrackerPacket(Jsonable):
    """Base class for agent packets"""

    _handlers: ClassVar[Dict[str, Callable[[dict], None]]] = {}
    _types: ClassVar[Dict[str, Type["TrackerPacket"]]] = {}
    cmd: ClassVar[str]
    
    def __post_init__(self):
        if not getattr(self.__class__, "cmd", None):
            raise NotImplementedError(
                f"{self.__class__.__name__} must define a class-level type."
            )

    def to_dict(self) -> Dict[Any, Any]:
        dct = super().to_dict()
        dct["cmd"] = self.__class__.cmd
        return dct
    
    @classmethod
    def parse(cls, data: dict) -> "TrackerPacket":

        logging.info(data)

        pkt_type = data.get("cmd")
        if pkt_type not in cls._types:
            raise KeyError(f"Unregistered packet type | Type: {pkt_type}")
        
        pkt_cls = cls._types[pkt_type]

        data = dict(data)
        data.pop("cmd", None)

        return pkt_cls.from_dict(data)
    
    def to_json(self) -> str:
        return json.dumps([self.to_dict()])
    
    @classmethod
    def on_received(cls, fn):
        """Handler when packet is received"""

        if cls.cmd in TrackerPacket._handlers:
            raise RuntimeError(
                f"on_received() handler is already registered for {cls.cmd}"
            )
        
        TrackerPacket._handlers[cls.cmd] = fn
        return fn
    
    @staticmethod
    async def receive(json_obj: Dict[Any, Any], ctx: Optional[Any] = None):
        """Receive and convert a json packet payload"""
        packet = TrackerPacket.parse(json_obj)
        
        handler = TrackerPacket._handlers.get(packet.__class__.cmd)
        if not handler:
            raise KeyError(f"No handler registered for type {packet.__class__.cmd}")
        
        result = handler(ctx, packet)
        if inspect.isawaitable(result):
            await result


def register_packet(cls: Type[TrackerPacket]):
    """Register packet type for json parsing"""
    TrackerPacket._types[cls.cmd] = cls
    return cls


@register_packet
@dataclass
class ConnectPacket(TrackerPacket):
    """Packet to request connection to server"""
    cmd: ClassVar[str] = "Connect"
    game: str = ""
    items_handling: int = 0b000
    name: str = ""
    password: Optional[str] = None
    slot_data: bool = False
    tags: List[str] = field(default_factory=list)
    uuid: str = ""
    version: NetworkVersion = field(default_factory=NetworkVersion)


@register_packet
@dataclass
class ConnectionRefusedPacket(TrackerPacket):
    """Packet received when connection is refused by the server"""
    cmd: ClassVar[str] = "ConnectionRefused"
    errors: List[str] = field(default_factory=list)


@register_packet
@dataclass
class ConnectedPacket(TrackerPacket):
    """Packet received on successful connection."""
    cmd: ClassVar[str] = "Connected"


@register_packet
@dataclass
class ReceivedItemsPacket(TrackerPacket):
    """Packet received when a player receives item(s) from the multiworld."""
    cmd: ClassVar[str] = "ReceivedItems"
    index: int = 0
    items: List[NetworkItem] = field(default_factory=list)


@register_packet
@dataclass
class RoomInfoPacket(TrackerPacket):
    """Packet received on websocket connection."""
    cmd: ClassVar[str] = "RoomInfo"
    games: List[str] = field(default_factory=list)
    password: bool = False
    tags: List[str] = field(default_factory=list)


@register_packet
@dataclass
class StatusPacket(TrackerPacket):
    """Packet to respond with the status of an agent"""
    cmd: ClassVar[str] = "StatusResponse"
    status: str = ""