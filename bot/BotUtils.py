import enum
import inspect
import logging
import json
import sqlite3
import sys
import uuid

from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Callable, ClassVar, Dict, List, Optional, Type, Union, get_args, get_origin
from uuid import UUID

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

class HintStatus(enum.IntEnum):
    HINT_UNSPECIFIED = 0
    HINT_NO_PRIORITY = 10
    HINT_AVOID = 20
    HINT_PRIORITY = 30
    HINT_FOUND = 40

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
    
class PlayerSend(enum.IntEnum):
    """Player send enum values"""
    NONE        = 0
    ITEM        = 1
    LOCATION    = 2

class PlayerState(enum.IntFlag):
    """Player state enum values"""
    NONE        = 0
    COLLECT     = 1 << 0
    RELEASE     = 1 << 1
    GOAL        = 1 << 2
    
#endregion

class Jsonable:
    """Base class for converting to json."""
    def to_dict(self) -> dict:
        out = {}
        for f in fields(self):
            key = f.metadata.get("json", f.name)
            out[key] = self.__encode(getattr(self, f.name))
        return out

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> "Jsonable":
        by_json_name = {f.metadata.get("json", f.name): f for f in fields(cls)}
        kwargs = {}

        for k, v in (data or {}).items():
            f = by_json_name.get(k)
            if f:
                kwargs[f.name] = cls.__decode(f.type, v)

        return cls(**kwargs)

    @staticmethod
    def __encode(value: Any) -> Any:
        if isinstance(value, Jsonable):
            return value.to_dict()
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, (Decimal, UUID)):
            return str(value)
        elif isinstance(value, Enum):
            return value.value
        elif isinstance(value, dict):
            return {str(k): Jsonable.__encode(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [Jsonable.__encode(v) for v in value]
        elif isinstance(value, tuple):
            return [Jsonable.__encode(v) for v in value]

        return value

    @staticmethod
    def __decode(tp, value: Any) -> Any:
        if value is None:
            return None

        origin = get_origin(tp)

        if origin is Union:
            args = [a for a in get_args(tp) if a is not type(None)]
            return Jsonable.__decode(args[0], value) if args else value

        elif origin is list:
            (elem_t,) = get_args(tp)
            return [Jsonable.__decode(elem_t, v) for v in (value or [])]

        elif origin is dict:
            key_t, val_t = get_args(tp)
            out = {}
            for k, v in (value or {}).items():
                if key_t is int:
                    k2 = int(k)
                elif key_t is float:
                    k2 = float(k)
                else:
                    k2 = k
                out[k2] = Jsonable.__decode(val_t, v)
            return out
        
        if origin in (tuple,):
            args = get_args(tp)

            # Tuple[T, ...]
            if len(args) == 2 and args[1] is Ellipsis:
                elem_t = args[0]
                return tuple(Jsonable.__decode(elem_t, v) for v in (value or []))

            # Tuple[T1, T2, ...]
            if args:
                seq = value or []
                return tuple(
                    Jsonable.__decode(args[i], seq[i]) if i < len(seq) else None
                    for i in range(len(args))
                )

            # plain tuple with no args
            return tuple(value or [])

        try:
            if isinstance(tp, type) and issubclass(tp, Jsonable):
                return tp.from_dict(value)
        except TypeError:
            pass

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
class NotificationCount(Jsonable):
    item_id: int
    count: int
    end_at: int

    # "Private"
    class_: str = field(default="NotificationCount", metadata={"json": "class"})
    id: Optional[int] = field(default=None)
    item_name: Optional[str] = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "NotificationCount":
        """Create a notification count instance from a row."""
        return cls(
            id=row["id"],
            item_id=row["item_id"],
            count=row["count"],
            end_at=row["end_at"]
        )
    
    @staticmethod
    def merge(set_one, set_two):
        """Merge two lists together, keeping the last (set two)"""

        index = { (x.item_id, x.count): x for x in set_one }

        for x in set_two:
            key = (x.item_id, x.count)

            if key in index:
                # If key matches, update set one's values
                existing = index[key]
                existing.end_at = x.end_at
            else:
                # Otherwise, append to set_one from set_two
                set_one.append(x)
                index[key] = x
        
        return set_one
    
    @staticmethod
    def unmerge(set_one, set_two):
        """Unmerge two lists together, removing with matching id/count"""
        to_remove = [(x.item_id, x.count) for x in set_two]
        return [x for x in set_one if (x.item_id, x.count) not in to_remove]

@dataclass
class Notification(Jsonable):
    port: int
    user_id: int
    slot_id: int
    hints: int = 0
    types: int = 0
    terms: List[str] = field(default_factory=list)
    counts: List[NotificationCount] = field(default_factory=list)
    
    # "Private"
    class_: str = field(default="Notification", metadata={"json": "class"})
    id: Optional[int] = field(default=None)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Notification":
        """Create a notification instance from a row."""

        # TODO: Also include last_modified for notifs?
        #       Why does excluding ID from the constructor break it?

        return cls(
            id=row["id"],
            port=row["port"],
            user_id=row["user_id"],
            slot_id=row["slot_id"],
            hints=row["hints"],
            types=row["types"],
            terms=row["terms"].split(",") if row["terms"] else [],
        )

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

@dataclass
class Hint(Jsonable):
    receiving_player: int
    finding_player: int
    location: int
    item: int
    found: bool
    entrance: str = ""
    item_flags: int = 0
    status: HintStatus = HintStatus.HINT_UNSPECIFIED
    class_: str = field(default="Hint", metadata={"json": "class"})

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
    deaths: int = 0
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
class NotificationSettingsDTO(Jsonable):
    slot_name: str
    hint_flags: NotifyFlags
    item_flags: NotifyFlags
    terms: list[str]
    counts: list[tuple[str, int]]

    @classmethod
    def from_entity(cls, client, binding: Binding):
        """Convert a binding entity object to a DTO for json encode/decoding"""
        return cls(
            slot_name=client.get_player_name(binding.slot_id),
            hint_flags=NotifyFlags(binding.hint_flags),
            item_flags=NotifyFlags(binding.item_flags),
            terms=[ t.term for t in binding.terms ],
            counts=[ (client.get_item_name(binding.slot_id, c.item_id), c.amount) for c in binding.counts ]
        )

@dataclass
class SessionStats(Jsonable):
    """Object containing stats for a session."""
    class_: str = field(default="SessionStats", metadata={"json": "class"})
    checked: int = 0
    deaths: int = 0
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
        return self.cmd in [ InvalidPacket.cmd, ErrorPacket.cmd ]

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
            logging.warning(f"Cannot parse un-registered packet type '{pkt_type}'.")
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
class BouncedPacket(TrackerPacket):
    """Packet received for deathlinks and other cross-world events"""
    cmd: ClassVar[str] = "Bounced"
    games: List[str] = field(default_factory=list),
    tags: List[str] = field(default_factory=list),
    slots: List[int] = field(default_factory=list)
    data: dict[str, any] = field(default_factory=dict)

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
class HintRequestPacket(IdentifiablePacket):
    """Packet sent to request a hint."""
    cmd: ClassVar[str] = "HintRequest"
    slot_name: str
    item_name: str
    password: Optional[str] = None

@TrackerPacket.register_packet
@dataclass
class HintResponsePacket(IdentifiablePacket):
    """Packet received in response to a HintRequest packet."""
    cmd: ClassVar[str] = "HintResponse"
    comment: str
    success: bool
    hints: List[Hint] = field(default_factory=list)

@TrackerPacket.register_packet
@dataclass
class InvalidPacket(TrackerPacket):
    """Packet received when a packet is invalid."""
    cmd: ClassVar[str] = "InvalidPacket"
    id: Optional[str] = ""
    original_cmd: Optional[str] = ""
    text: str = ""

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
class ReceivedCountRequestPacket(IdentifiablePacket):
    """Packet sent to server to request item received count"""
    cmd: ClassVar[str] = "ReceivedCountRequest"
    slot_items: Dict[int, List[int]] = field(default_factory=Dict) # <- { slot_id: List[item_ids] }

@TrackerPacket.register_packet
@dataclass
class ReceivedCountResponsePacket(IdentifiablePacket):
    """Packet received in response to 'ReceivedCountRequest' packet."""
    cmd: ClassVar[str] = "ReceivedCountResponse"
    counts: Dict[int, Dict[int, int]] = field(default_factory=dict)

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
class SendPlayerRequestPacket(TrackerPacket):
    """Packet sent to request player sending"""
    cmd: ClassVar[str] = "SendPlayerRequest"
    slot_id: int
    location_id: Optional[int] = None
    item_id: Optional[int] = None
    amount: Optional[int] = 1

@TrackerPacket.register_packet
@dataclass
class SendPlayerResponsePacket(TrackerPacket):
    """Packet received in response to a SendPlayerRequest"""
    cmd: ClassVar[str] = "SendPlayerResponse"
    slot_id: int
    location_id: Optional[int] = None
    item_id: Optional[int] = None
    amount: Optional[int] = 1

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
class CommandRequestPacket(IdentifiablePacket):
    """Packet sent when requesting a command be performed"""
    cmd: ClassVar[str] = "CommandRequest"
    command: str

@TrackerPacket.register_packet
@dataclass
class CommandResponsePacket(IdentifiablePacket):
    """Packet received in response to a CommandRequest packet."""
    cmd: ClassVar[str] = "CommandResponse"
    success: bool

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
    text: str = ""

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
    counts: Optional[Dict[str, int]] = field(default_factory=dict)

@TrackerPacket.register_packet
@dataclass
class NotificationsResponsePacket(IdentifiablePacket):
    """Packet sent to gateway in response to a NotificationRequest packet."""
    cmd: ClassVar[str] = "NotificationsResponse"
    notification: NotificationSettingsDTO

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

#region Shared Methods

def setup_logging(service: str, log_dir="logs", logtime: bool = True, level=logging.INFO):

    root = logging.getLogger()
    root.setLevel(level)

    # If we already configured logging in THIS process, don't do it again
    if getattr(root, "_bot_logging_configured", False):
        return

    # Make directory if it doesn't exist already
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logfile = Path(log_dir) / f"{service}_{ts}.log"

    fmt = logging.Formatter(
        f"{"[%(asctime)s]\t" if logtime else ""}[{service.upper()}.%(name)s]\t%(levelname)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    # Add stderr handler ONLY if none exists
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        sh = logging.StreamHandler(sys.stderr)
        sh.setFormatter(fmt)
        root.addHandler(sh)

    # Add file handler (don’t clear others)
    fh = logging.FileHandler(str(logfile), encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)

    root._bot_logging_configured = True

def format_error(action: str, ex: Exception) -> str:
    return f"Error {action}: *'{ex}'*"

def format_port(port: int) -> str:
    return f"`:{port}`"

def format_slot(slot_name: str) -> str:
    return f"`{slot_name}`"

def format_port_slot(port: int, slot_name: str) -> str:
    return f"{format_port(port)} / {format_slot(slot_name)}"

def split_at_separator(text: str, limit: int = 2000, separator: str = ", ") -> List[str]:
    """Split a string into chunks no longer than <limit> by <separator>"""

    # If not longer than the limit, return it
    if len(text) <= limit:
        return [ text ]

    parts = text.split(separator)
    chunks = []
    current_chunk = ""

    # Cycle through split parts
    for part in parts:
        # Include separator if current chunk is not empty
        test_chunk = current_chunk + separator + part if current_chunk else part

        if len(test_chunk) > limit:
            # Next chunk is too long, append what we have
            chunks.append(current_chunk)
            current_chunk = part
        else:
            current_chunk = test_chunk

    # Add any remaining chunks
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

#endregion