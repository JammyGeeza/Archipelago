import json
import inspect
import logging
import sys

from bot.Utils import Jsonable
from dataclasses import MISSING, dataclass, field
from typing import Any, Callable, ClassVar, Dict, List, Optional, Type

@dataclass
class GameData(Jsonable):
    """Object containing game lookup data."""
    class_: str = field(default="GameData", metadata={"json": "class"})
    location_name_to_id: Dict[str, int] = field(default_factory=dict)
    item_name_to_id: Dict[str, int] = field(default_factory=dict)

@dataclass
class DataPackageObject(Jsonable):
    """Object containing data package data"""
    games: Dict[str, GameData] = field(default_factory=dict)

@dataclass
class PrintJSONSegment(Jsonable):
    """Object containing a PrintJSON text segment."""
    flags: int = 0
    player: int = 0
    text: str = ""
    type: str = ""

@dataclass
class NetworkItem(Jsonable):
    """Object containing item data."""
    class_: str = field(default="NetworkItem", metadata={"json": "class"})
    item: int = 0
    location: int = 0
    player: int = 0
    flags: int = 0

@dataclass
class NetworkPlayer(Jsonable):
    """Object containing player data."""
    class_: str = field(default="NetworkPlayer", metadata={"json": "class"})
    alias: str = ""
    name: str = ""
    slot: int = 0

@dataclass
class NetworkSlot(Jsonable):
    """Object containing player data."""
    class_: str = field(default="NetworkSlot", metadata={"json": "class"})
    game: str = ""
    name: str = ""

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
            logging.warning(f"Unregistered packet type '{pkt_type}'.")
            return None
        
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
        if not packet:
            return
        
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
    players: List[NetworkPlayer] = field(default_factory=list)
    slot_info: Dict[int, NetworkSlot] = field(default_factory=dict)

@register_packet
@dataclass
class DataPackagePacket(TrackerPacket):
    """Packet containing game lookup data"""
    cmd: ClassVar[str] = "DataPackage"
    data: DataPackageObject = field(default_factory=DataPackageObject)

@register_packet
@dataclass
class DiscordMessagePacket(TrackerPacket):
    """Packet containing a message to be posted to the discord channel."""
    cmd: ClassVar[str] = "DiscordMessage"
    message: str = ""

@register_packet
@dataclass
class GetPacket(TrackerPacket):
    """Packet sent to server to request key data."""
    cmd: ClassVar[str] = "Get"
    keys: List[str] = field(default_factory=list)

@register_packet
@dataclass
class GetDataPackagePacket(TrackerPacket):
    """Packet sent to server to request DataPackage."""
    cmd: ClassVar[str] = "GetDataPackage"
    games: List[str] = field(default_factory=dict)

# @register_packet
# @dataclass
# class ItemMessagePacket(TrackerPacket):
#     """Packet containing item(s) data to be posted to the discord channel."""
#     cmd: ClassVar[str] = "ItemMessage"
#     recipient: int = 0
#     items: Dict[int, int] = field(default_factory=dict)

# @register_packet
# @dataclass
# class HintMessagePacket(TrackerPacket):
#     """Packet containing hint(s) data to be posted to the discord channel"""
#     cmd: ClassVar[str] = "HintMessage"
#     recipient: int = 0
#     item: NetworkItem = field(default_factory=dict)

@register_packet
@dataclass
class PrintJSONPacket(TrackerPacket):
    """Packet received when messages are received."""
    cmd: ClassVar[str] = "PrintJSON"
    data: List[PrintJSONSegment] = field(default_factory=list)
    found: bool = False
    receiving: int = 0
    item: NetworkItem = field(default_factory=NetworkItem)
    slot: int = 0
    team: int = 0
    type: str = ""

@register_packet
@dataclass
class RetrievedPacket(TrackerPacket):
    """Packet received with data requested from 'Get' packet."""
    cmd: ClassVar[str] = "Retrieved"
    keys: Dict[str, Any] = field(default_factory=dict)

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
class SetNotifyPacket(TrackerPacket):
    """Packet sent to be notified when stored keys change."""
    cmd: ClassVar[str] = "SetNotify"
    keys: List[str] = field(default_factory=list)

@register_packet
@dataclass
class SetReplyPacket(TrackerPacket):
    """Packet received when notified of a key change."""
    cmd: ClassVar[str] = "SetReply"
    key: str = ""
    value: Any = ""
    original_value: Any = ""
    slot: int = 0

@register_packet
@dataclass
class StatusPacket(TrackerPacket):
    """Packet to respond with the status of an agent"""
    cmd: ClassVar[str] = "StatusResponse"
    message:str = ""
    status: str = ""