import logging
import sqlite3
from dataclasses import dataclass
from typing import ClassVar, Optional, List

@dataclass
class Agent:
    guild_id: int
    channel_id: int
    port: int
    password: Optional[str]

@dataclass
class Notification:
    port: int
    user_id: int
    channel_id: int
    slot_id: int
    hints: Optional[int]
    types: Optional[int]
    terms: Optional[str]

@dataclass
class Room:
    port: int
    multidata: str
    savedata: str

@dataclass
class RoomConfig:
    port: int
    password: Optional[str]
    multidata: str
    savedata: str
    guild_id: Optional[int]
    channel_id: Optional[int]

class Store:

    def __init__(self, path: str = "discord_gateway.db"):
        self.path = path
        # self._init()

        self.configs = RoomConfigRepo(self._conn)
        # self.notifications = NotificationRepo(self._conn)

        # self.agents = AgentRepo(self._conn)
        # self.rooms = RoomRepo(self._conn)

    def _conn(self):
        return sqlite3.connect(self.path)
    
    def _init(self):

        # Create table if it doesn't exist already
        with self._conn() as connection:

            # Create table for agent bindings
            connection.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                      id            INTEGER PRIMARY KEY AUTOINCREMENT,
                      guild_id      INTEGER NOT NULL,
                      channel_id    INTEGER NOT NULL,
                      port          INTEGER NOT NULL,
                      password      TEXT,

                      UNIQUE (guild_id, channel_id),
                      UNIQUE (port)
                )
            """)

            # Create table for room data
            connection.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    port        INTEGER PRIMARY KEY,
                    multidata   TEXT    NOT NULL,
                    savedata    TEXT    NOT NULL,
                               
                    UNIQUE(multidata),
                    UNIQUE(savedata)
                )
            """)

            connection.commit()

class NotificationRepo:

    table_name: ClassVar[str] = "notifications"

    def __init__(self, connection_factory: sqlite3.Connection):
        self._conn: sqlite3.Connection = connection_factory
        self._init()

    def _init(self):
        with self._conn() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    port        INTEGER PRIMARY KEY,
                    user_Id     INTEGER NOT NULL,
                    channel_id  INTEGER NOT NULL,
                    slot_id     INTEGER NOT NULL,
                    hints       INTEGER,
                    types       INTEGER,
                    terms       TEXT,
                    
                    UNIQUE(port, user_id channel_id, slot_id)
                )
            """)

    def upsert(self, notif: Notification) -> Optional[Notification]:
        """Insert or update a notification."""

        try:
            with self._conn() as connection:
                connection.execute(f"""
                    INSERT INTO {self.table_name} (port, user_id, channel_id, slot_id, hints, types, terms)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(port, user_id, channel_id, slot_id) DO UPDATE SET
                        hints = excluded.hints,
                        types = excluded.types,
                        terms = excluded.terms
                    """,
                    (notif.port, notif.user_id, notif.channel_id, notif.slot_id, notif.hints, notif.types, notif.terms)
                )
                connection.commit()

            return self.get(notif.port, notif.user_id, notif.channel_id, notif.slot_id)

        except Exception as ex:
            logging.warning(f"Error in {self.table_name} upsert: {ex}")
            return None

    def get(self, port: int, user_id: int, channel_id: int, slot_id: int) -> Optional[Notification]:
        """Get a notification."""

        try:
            with self._conn() as connection:
                notif = connection.execute(f"""
                    SELECT port, user_id, channel_id, slot_id, hints, types, terms
                    FROM {self.table_name}
                    WHERE port = ?
                        AND user_id = ?
                        AND channel_id = ?
                        AND slot_id = ?
                    """,
                    (port, user_id, channel_id, slot_id)
                ).fetchone()
                
                return Notification(*notif)
            
        except Exception as ex:
            logging.warning(f"Error in {self.table_name} get: {ex}")
            return None
        
    def delete(self, notif: Notification) -> bool:
        """Delete a notification"""

        try:
            with self._conn() as connection:
                notif = connection.execute(f"""
                    DELETE
                    FROM {self.table_name}
                    WHERE port = ?
                        AND user_id = ?
                        AND channel_id = ?
                        AND slot_id = ?
                    """,
                    (notif.port, notif.user_id, notif.channel_id, notif.slot_id)
                )
                
                return True
            
        except Exception as ex:
            logging.warning(f"Error in {self.table_name} delete: {ex}")
            return False

class RoomConfigRepo:

    def __init__(self, connection_factory: sqlite3.Connection):
        self._conn: sqlite3.Connection = connection_factory
        self._init()

    def _init(self):

        with self._conn() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS room_configs (
                    port        INTEGER PRIMARY KEY,
                    password    TEXT,
                    multidata   TEXT NOT NULL,
                    savedata    TEXT NOT NULL,
                    guild_id    INTEGER,
                    channel_id  INTEGER,
                               
                    UNIQUE(guild_id, channel_id)
                )
            """)

            connection.commit()

    def bind(self, port: int, guild_id: int, channel_id: int) -> Optional[RoomConfig]:
        """Bind a room to a discord channel"""

        try:
            with self._conn() as connection:

                connection.execute("""
                    UPDATE room_configs
                    SET guild_id = ?, channel_id = ?
                    WHERE port = ?
                    """,
                    (guild_id, channel_id, port)
                )
                connection.commit()

            return self.get_by_port(port)

        except Exception as ex:
            logging.warning(f"Error in bind(): {ex}")
            return None
        
    def create(self, port: int, multidata: str, savedata: str, password: Optional[str] = None) -> Optional[RoomConfig]:
        """Create a room configuration."""

        try:
            with self._conn() as connection:

                connection.execute("""
                    INSERT INTO room_configs (port, multidata, savedata, password)
                    VALUES (?, ?, ?, ?)
                    """,
                    (port, multidata, savedata, password)
                )
                connection.commit()

            return self.get_by_port(port)
        
        except Exception as ex:
            return None
        
    def get_by_port(self, port: int) -> Optional[RoomConfig]:
        """Get a room configuration by the port"""

        try:
            with self._conn() as connection:

                config = connection.execute("""
                    SELECT port, password, multidata, savedata, guild_id, channel_id
                    FROM room_configs
                    WHERE port = ?
                    """,
                    (port,)
                ).fetchone()

            return RoomConfig(*config)

        except Exception as ex:
            return None
        
    def get_by_channel(self, guild_id: int, channel_id: int) -> Optional[RoomConfig]:
        """Get a room configuration by the guild and channel ID"""

        try:
            with self._conn() as connection:

                config = connection.execute("""
                    SELECT port, password, multidata, savedata, guild_id, channel_id
                    FROM room_configs
                    WHERE guild_id = ?
                        AND channel_id = ?
                    """,
                    (guild_id, channel_id)
                ).fetchone()

            return RoomConfig(*config)

        except Exception as ex:
            return None
        
    def get_all_active(self) -> List[RoomConfig]:
        """Get all room configurations"""

        try:
            with self._conn() as connection:

                configs = connection.execute("""
                    SELECT port, password, multidata, savedata, guild_id, channel_id
                    FROM room_configs
                    WHERE guild_id IS NOT NULL
                        AND channel_id IS NOT NULL
                """).fetchall()

            return [RoomConfig(*config) for config in configs]

        except Exception as ex:
            logging.warning(f"Error in get_all_active(): {ex}")
            return []
        
    def get_all_by_guild(self, guild_id: int) -> List[RoomConfig]:
        """Get a room configuration by the guild and channel ID"""

        try:
            with self._conn() as connection:

                configs = connection.execute("""
                    SELECT port, password, multidata, savedata, guild_id, channel_id
                    FROM room_configs
                    WHERE guild_id = ?
                    """,
                    (guild_id,)
                ).fetchall()

            return [RoomConfig(*config) for config in configs]

        except Exception as ex:
            return []
        
    def unbind(self, port: int) -> Optional[RoomConfig]:
        """Un-bind a room from a discord channel"""

        try:
            with self._conn() as connection:

                connection.execute("""
                    UPDATE room_configs
                    SET guild_id = NULL, channel_id = NULL
                    WHERE port = ?
                    """,
                    (port,)
                )
                connection.commit()

            return self.get_by_port(port)

        except Exception as ex:
            return None

class AgentRepo:

    def __init__(self, conn_factory):
        self._conn = conn_factory

    def delete(self, agent: Agent) -> bool:
        """Delete an agent from the store."""

        try:
            with self._conn() as connection:
                connection.execute("""
                    DELETE
                    FROM agents
                    WHERE guild_id = ?
                        AND channel_id = ?
                    """,
                    (agent.guild_id, agent.channel_id)
                )
                connection.commit()

        except Exception as ex:
            return False
        
        return True

    def exists(self, guild_id: int, channel_id: int) -> bool:
        """Check if an agent exists in the store."""

        with self._conn() as connection:
            agent = connection.execute("""
                SELECT 1
                FROM agents
                WHERE guild_id = ?
                    AND channel_id = ?
                """,
                (guild_id, channel_id)
            ).fetchone()

            return agent is not None

    def get(self, guild_id: int, channel_id: int) -> Optional[Agent]:
        """Get an agent from the store."""

        with self._conn() as connection:
            agent = connection.execute("""
                SELECT guild_id, channel_id, port, password
                FROM agents 
                WHERE guild_id = ?
                    AND channel_id = ?
                """,
                (guild_id, channel_id)
            ).fetchone()

        return Agent(*agent) if agent else None
    
    def get_many(self, guild_id: int) -> List[Agent]:
        """Get agents from the store for a guild."""

        with self._conn() as connection:
            agents = connection.execute("""
                SELECT guild_id, channel_id, port, password
                FROM agents
                WHERE guild_id = ?
                """,
                (guild_id,)
            ).fetchall()

            return [Agent(*agent) for agent in agents]
        
    def get_all(self) -> List[Agent]:
        """Get all agents from the store."""

        with self._conn() as connection:
            agents = connection.execute("""
                SELECT guild_id, channel_id, port, password
                FROM agents
            """).fetchall()

            return [Agent(*agent) for agent in agents]

    def upsert(self, agent: Agent) -> bool:
        """Add/Update an agent in the store."""

        try:
            with self._conn() as connection:

                connection.execute("""
                    INSERT INTO agents (guild_id, channel_id, port, password)
                    VALUES (?, ?, ?, ?)
                    """,
                    (agent.guild_id, agent.channel_id, agent.port, agent.password)
                )
                connection.commit()

        except Exception:
            return False
        
        return True
    
class RoomRepo:

    def __init__(self, conn_factory):
        self._conn = conn_factory

    def delete(self, agent: Room) -> bool:
        """Delete a room from the store."""

        try:
            with self._conn() as connection:
                connection.execute("""
                    DELETE
                    FROM rooms
                    WHERE port = ?
                    """,
                    (agent.port,)
                )
                connection.commit()

        except Exception as ex:
            return False
        
        return True

    def exists(self, port: int) -> bool:
        """Check if an agent exists in the store."""

        with self._conn() as connection:
            agent = connection.execute("""
                SELECT 1
                FROM rooms
                WHERE port = ?
                """,
                (port,)
            ).fetchone()

            return agent is not None

    def get(self, port: int) -> Optional[Room]:
        """Get an agent from the store."""

        with self._conn() as connection:
            room = connection.execute("""
                SELECT port, multidata, savedata
                FROM rooms 
                WHERE port = ?
                """,
                (port,)
            ).fetchone()

        return Room(*room) if room else None
        
    def get_all(self) -> List[Room]:
        """Get all rooms from the store."""

        with self._conn() as connection:
            rooms = connection.execute("""
                SELECT port, multidata, savedata
                FROM rooms
            """).fetchall()

            return [Room(*room) for room in rooms]

    def upsert(self, room: Room) -> bool:
        """Add/Update a room in the store."""

        try:
            with self._conn() as connection:

                connection.execute("""
                    INSERT INTO rooms (port, multidata, savedata)
                    VALUES (?, ?, ?)
                    """,
                    (room.port, room.multidata, room.savedata)
                )
                connection.commit()

        except Exception:
            return False
        
        return True