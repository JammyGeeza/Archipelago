import json
import inspect

from dataclasses import dataclass
from typing import Callable, ClassVar, Dict, Optional, Type

@dataclass
class TrackerPacket:
    """Base class for agent packets"""

    _handlers: ClassVar[Dict[str, Callable[[dict], None]]] = {}
    _types: ClassVar[Dict[str, Type["TrackerPacket"]]] = {}
    type: ClassVar[str]
    
    def __init__(self):
        if not self.type:
            raise NotImplementedError(f"{self.__class__.__name__} must define a class-level type.")

    def to_dict(self) -> Dict[any, any]:
        dct = { k:v for k,v in self.__dict__.items() if not k.startswith("_") }
        dct["type"] = self.__class__.type
        return dct
    
    @classmethod
    def from_dict(cls, data: dict) -> "TrackerPacket":
        pkt_type = data.get("type")
        if pkt_type not in cls._types:
            raise KeyError(f"Unregistered packet type | Type: {pkt_type}")
        
        pkt_cls = cls._types[pkt_type]
        data = dict(data)
        data.pop("type", None)
        return pkt_cls(**data)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict()) 
    
    @classmethod
    def on_received(cls, fn):
        """Handler when packet is received"""

        if cls.type in TrackerPacket._handlers:
            raise RuntimeError(f"on_received() handler is already registered for {cls.type}")
        
        TrackerPacket._handlers[cls.type] = fn
        return fn
    
    @staticmethod
    async def receive(payload: str, ctx: Optional[any] = None):
        """Receive a raw packet payload"""
        data = json.loads(payload)
        packet = TrackerPacket.from_dict(data)
        
        handler = TrackerPacket._handlers.get(packet.type)
        if not handler:
            raise KeyError(f"No handler registered for type {packet.type}")
        
        result = handler(ctx, packet)
        if inspect.isawaitable(result):
            await result

def register_packet(cls: Type[TrackerPacket]):
    """Register packet type for json parsing"""
    TrackerPacket._types[cls.type] = cls
    return cls

@register_packet
@dataclass
class ConnectPacket(TrackerPacket):
    """Packet to reque"""

    type: ClassVar[str] = "Connect"

    def __init__(self):
        super().__init__()

@register_packet
@dataclass
class ConnectedPacket(TrackerPacket):
    """Packet received on successful connection."""
    type: ClassVar[str] = "Connected"

    def __init__(self):
        super().__init__()

@register_packet
@dataclass
class StatusPacket(TrackerPacket):
    """Packet to respond with the status of an agent"""

    type: ClassVar[str] = "StatusResponse"

    def __init__(self, status: str):
        super().__init__()

        self.status = status

