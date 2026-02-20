import enum
import inspect
import logging
import json
import sqlite3
import uuid

from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, ClassVar, Dict, List, Optional, Type, Union, get_args, get_origin

#region Enums / Flags

class Action(enum.IntEnum):
    """Action enum values"""
    ADD         = 1 << 0
    REMOVE      = 1 << 1
    CLEAR       = 1 << 2
    VIEW        = 1 << 3

class ClientStatus(enum.IntEnum):
    """Client status enum values"""
    UNKNOWN     = 0
    CONNECTED   = 5
    READY       = 10
    PLAYING     = 20
    GOAL        = 30

class ItemFlags(enum.IntEnum):
    """Archipelago's item type flags"""
    FILLER      = 0
    PROGRESSION = 1 << 0
    USEFUL      = 1 << 1
    TRAP        = 1 << 2

class NotifyFlags(enum.IntFlag):
    """Notification item type flags"""
    NONE        = 0
    FILLER      = 1 << 0
    PROGRESSION = 1 << 1
    USEFUL      = 1 << 2
    TRAP        = 1 << 3

    @staticmethod
    def item_to_notify_flags(item_flags: int) -> "NotifyFlags":
        """Convert an AP item flag to the Notify flags."""

        notify_flags = NotifyFlags.NONE

        # Map to notify flags
        if item_flags & ItemFlags.PROGRESSION: notify_flags |= NotifyFlags.PROGRESSION
        if item_flags & ItemFlags.USEFUL: notify_flags |= NotifyFlags.USEFUL
        if item_flags & ItemFlags.TRAP: notify_flags |= NotifyFlags.TRAP

        # If no meaningful flags are set, default it to filler
        if notify_flags is NotifyFlags.NONE: notify_flags = NotifyFlags.FILLER
        
        return notify_flags

    def to_text(self) -> str:
        """Get text representation of all applied flags."""
        if self == NotifyFlags.NONE:
            return NotifyFlags.NONE.name.title()
        
        return ", ".join(
            flag.name.title() for flag in type(self) if flag != 0 and flag in self
        )
    
#endregion

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

#region Store Objects

@dataclass
class Binding:
    channel_id: int
    guild_id: int
    port: int
    slot_name: str
    password: Optional[str] = None

    # Exclude from constructor
    last_modified: datetime = field(default=None, init=False)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Binding":
        """Create a binding instance from a row."""

        binding = cls(
            channel_id=row["channel_id"],
            guild_id=row["guild_id"],
            port=row["port"],
            slot_name=row["slot_name"],
            password=row["password"]
        )
        binding.last_modified = row["last_modified"]
        return binding

@dataclass
class Notification(Jsonable):
    port: int
    user_id: int
    slot_id: int
    hints: int = 0
    types: int = 0
    terms: List[str] = field(default_factory=list)
    class_: str = field(default="Notification", metadata={"json": "class"})
    id: Optional[int] = field(default=None)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Notification":
        """Create a notification instance from a row."""

        # TODO: Also include last_modified for notifs?
        #       Why does excluding ID from the constructor break it?

        notif = cls(
            id=row["id"],
            port=row["port"],
            user_id=row["user_id"],
            slot_id=row["slot_id"],
            hints=row["hints"],
            types=row["types"],
            terms=row["terms"].split(",") if row["terms"] else []
        )

        return notif

#endregion

#region Data Objects

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

# TODO: Make this match other data classes??
class ItemQueue:
    def __init__(self):
        self.items: Dict[int, QueuedItemData] = {}
        self.expires: datetime = datetime.now()

    def add(self, item: "NetworkItem"):
        # Get or create existing queued item and increment count
        queued_item = self.items.get(item.item, QueuedItemData(item.flags, 0))
        queued_item.count += 1

        # Update item and set expiry
        self.items[item.item] = queued_item
        self.expires = datetime.now() + timedelta(seconds=2)

@dataclass
class QueuedItemData:
    flags: int
    count: int

@dataclass
class PlayerStats(Jsonable):
    """Object containing stats for a player"""
    class_: str = field(default="PlayerStats", metadata={"json": "class"})
    checked: int = 0
    goal: bool = False
    received: int = 0
    remaining: int = 0

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
class SessionStats(Jsonable):
    """Object containing stats for a session."""
    class_: str = field(default="SessionStats", metadata={"json": "class"})
    checked: int = 0
    goals: int = 0
    remaining: int = 0

#endregion

#region Packet Base Classes

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
    
    def is_error(self) -> bool:
        """Is this packet related to an error?"""
        return self.cmd in [
            InvalidPacket.cmd,
            ErrorPacket.cmd
        ]

    def to_dict(self) -> Dict[Any, Any]:
        dct = super().to_dict()
        dct["cmd"] = self.__class__.cmd
        return dct
    
    def to_json(self) -> str:
        return json.dumps([self.to_dict()])
    
    @classmethod
    def parse(cls, data: dict) -> "TrackerPacket":

        pkt_type = data.get("cmd")
        if pkt_type not in cls._types:
            logging.warning(f"Unregistered packet type '{pkt_type}'.")
            return None
        
        pkt_cls = cls._types[pkt_type]

        data = dict(data)
        data.pop("cmd", None)

        return pkt_cls.from_dict(data)
    
    @classmethod
    def register_packet(cls, packet_cls: Type["TrackerPacket"]):
        """Register packet type for json parsing"""
        TrackerPacket._types[packet_cls.cmd] = packet_cls
        return packet_cls

@dataclass
class IdentifiablePacket(TrackerPacket):
    """Base class for request packets"""
    cmd: ClassVar[str] = "Request"
    id: str

    def __post_init__(self):
        # Force an ID to be provided
        if not self.id or not isinstance(self.id, str):
            self.id = uuid.uuid4().hex

#endregion

#region Archipelago Packets

@TrackerPacket.register_packet
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

@TrackerPacket.register_packet
@dataclass
class ConnectionRefusedPacket(TrackerPacket):
    """Packet received when connection is refused by the server"""
    cmd: ClassVar[str] = "ConnectionRefused"
    errors: List[str] = field(default_factory=list)


@TrackerPacket.register_packet
@dataclass
class ConnectedPacket(TrackerPacket):
    """Packet received on successful connection."""
    cmd: ClassVar[str] = "Connected"
    players: List[NetworkPlayer] = field(default_factory=list)
    slot_info: Dict[int, NetworkSlot] = field(default_factory=dict)

@TrackerPacket.register_packet
@dataclass
class DataPackagePacket(TrackerPacket):
    """Packet containing game lookup data"""
    cmd: ClassVar[str] = "DataPackage"
    data: DataPackageObject = field(default_factory=DataPackageObject)

@TrackerPacket.register_packet
@dataclass
class GetPacket(TrackerPacket):
    """Packet sent to server to request key data."""
    cmd: ClassVar[str] = "Get"
    keys: List[str] = field(default_factory=list)

@TrackerPacket.register_packet
@dataclass
class GetDataPackagePacket(TrackerPacket):
    """Packet sent to server to request DataPackage."""
    cmd: ClassVar[str] = "GetDataPackage"
    games: List[str] = field(default_factory=dict)

@TrackerPacket.register_packet
@dataclass
class GetStatsPacket(TrackerPacket):
    """Packet sent to server to request stats."""
    cmd: ClassVar[str] = "GetStats"
    slots: List[int] = field(default_factory=list)

@TrackerPacket.register_packet
@dataclass
class InvalidPacket(TrackerPacket):
    """Packet received when a packet is invalid."""
    cmd: ClassVar[str] = "InvalidPacket"
    id: Optional[str] = ""
    original_cmd: Optional[str] = ""
    message: str = ""

@TrackerPacket.register_packet
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

@TrackerPacket.register_packet
@dataclass
class RetrievedPacket(TrackerPacket):
    """Packet received with data requested from 'Get' packet."""
    cmd: ClassVar[str] = "Retrieved"
    keys: Dict[str, Any] = field(default_factory=dict)

@TrackerPacket.register_packet
@dataclass
class RoomInfoPacket(TrackerPacket):
    """Packet received on websocket connection."""
    cmd: ClassVar[str] = "RoomInfo"
    games: List[str] = field(default_factory=list)
    password: bool = False
    tags: List[str] = field(default_factory=list)

@TrackerPacket.register_packet
@dataclass
class SetNotifyPacket(TrackerPacket):
    """Packet sent to be notified when stored keys change."""
    cmd: ClassVar[str] = "SetNotify"
    keys: List[str] = field(default_factory=list)

@TrackerPacket.register_packet
@dataclass
class SetReplyPacket(TrackerPacket):
    """Packet received when notified of a key change."""
    cmd: ClassVar[str] = "SetReply"
    key: str = ""
    value: Any = ""
    original_value: Any = ""
    slot: int = 0

@TrackerPacket.register_packet
@dataclass
class StatsPacket(TrackerPacket):
    """Packet received as a response to 'GetStats' packet."""
    cmd: ClassVar[str] = "Stats"
    stats: Dict[int, PlayerStats] = field(default_factory=dict)

#endregion

#region Tracker Packets

@TrackerPacket.register_packet
@dataclass
class DiscordMessagePacket(TrackerPacket):
    """Packet containing a message to be posted to the discord channel."""
    cmd: ClassVar[str] = "DiscordMessage"
    message: str = ""

@TrackerPacket.register_packet
@dataclass
class ErrorPacket(TrackerPacket):
    """Packet sent when an error occurs during an operation."""
    cmd: ClassVar[str] = "Error"
    id: Optional[str] = ""
    original_cmd: Optional[str] = ""
    message: str = ""

@TrackerPacket.register_packet
@dataclass
class InvalidRequestPacket(IdentifiablePacket):
    """Packet sent to gateway in response to an invalid Request packet"""
    cmd: ClassVar[str] = "InvalidRequest"
    original_cmd: str = ""
    message: str = ""

@TrackerPacket.register_packet
@dataclass
class NotificationsRequestPacket(IdentifiablePacket):
    """Packet sent to agent to request Notification setup."""
    cmd: ClassVar[str] = "NotificationsRequest"
    action: int = 0
    channel_id: int = 0
    user_id: int = 0
    player: str = ""
    hints: Optional[int] = None
    types: Optional[int] = None
    terms: Optional[List[str]] = field(default_factory=list)

@TrackerPacket.register_packet
@dataclass
class NotificationsResponsePacket(IdentifiablePacket):
    """Packet sent to gateway in response to a NotificationRequest packet."""
    cmd: ClassVar[str] = "NotificationsResponse"
    notification: Notification

@TrackerPacket.register_packet
@dataclass
class StatisticsRequestPacket(IdentifiablePacket):
    """Packet sent to agent to request statistics for players."""
    cmd: ClassVar[str] = "StatisticsRequest"
    players: List[str] = field(default_factory=list)
    include_session: bool = False

@TrackerPacket.register_packet
@dataclass
class StatisticsResponsePacket(IdentifiablePacket):
    """Packet sent to gateway in response to StatisticsRequest packet."""
    cmd: ClassVar[str] = "StatisticsResponse"
    slots: Dict[int, PlayerStats] = field(default_factory=dict)
    session: Optional[SessionStats] = None

@TrackerPacket.register_packet
@dataclass
class StatusRequestPacket(IdentifiablePacket):
    """Packet sent to agent to request its current status."""
    cmd: ClassVar[str] = "StatusRequest"

@TrackerPacket.register_packet
@dataclass
class StatusResponsePacket(IdentifiablePacket):
    """Packet sent to gateway in response to StatusRequest packet."""
    cmd: ClassVar[str] = "StatusResponse"
    status: str = ""

@TrackerPacket.register_packet
@dataclass
class TrackerInfoPacket(TrackerPacket):
    """Packet sent to gateway containing basic tracker data."""
    cmd: ClassVar[str] = "TrackerInfo"
    players: Dict[int, str] = field(default_factory=dict)

#endregion