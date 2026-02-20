import logging
import sqlite3
import bot.Utils as utils
from dataclasses import dataclass
from typing import ClassVar, Optional, List

@dataclass
class Agent:
    guild_id: int
    channel_id: int
    port: int
    password: Optional[str]

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
        self.configs = RoomConfigRepo(self._conn)
        self.notifications = NotificationRepo(self._conn)

    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

class NotificationRepo:

    table_name: ClassVar[str] = "notifications"

    def __init__(self, connection_factory: sqlite3.Connection):
        self._conn: sqlite3.Connection = connection_factory
        self._init()

    def _init(self):
        with self._conn() as connection:
            connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    port        INTEGER NOT NULL,
                    user_id     INTEGER NOT NULL,
                    slot_id     INTEGER NOT NULL,
                    hints       INTEGER NOT NULL,
                    types       INTEGER NOT NULL,
                    
                    UNIQUE(port, user_id, slot_id)
                )
            """)
            
            connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name}_terms (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    notification_id INTEGER NOT NULL,
                    term            TEXT NOT NULL,

                    FOREIGN KEY (notification_id)
                        REFERENCES notifications(id)
                        ON DELETE CASCADE,

                    UNIQUE(notification_id, term)
                )
            """)

            connection.commit()

    def __bind(self, row) -> Optional[utils.Notification]:
        """Bind a returned row as a Notification object."""
        if not row: return None
        else: return utils.Notification(
            id=row["id"],
            port=row["port"],
            user_id=row["user_id"],
            slot_id=row["slot_id"],
            hints=row["hints"],
            types=row["types"],
            terms=row["terms"].split(",") if row["terms"] else []
            # terms=self.__get_terms(row["id"])
        )

    def get_or_create(self, port: int, user_id: int, slot_id: int) -> Optional[utils.Notification]:
        """Get a notification item or create one if it doesn't exist."""

        try:
            if (notification:= self.get(port, user_id, slot_id)):
                return notification
            else:
                return self.upsert(utils.Notification(
                    port=port,
                    user_id=user_id,
                    slot_id=slot_id
                )) 

        except Exception as ex:
            logging.warning(f"Error in {self.table_name} get_or_create(): {ex}")
            return None
        
    def upsert(self, notif: utils.Notification) -> Optional[utils.Notification]:
        """Insert or update a notification."""

        try:
            with self._conn() as connection:
                connection.execute(f"""
                    INSERT INTO {self.table_name} (port, user_id, slot_id, hints, types)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(port, user_id, slot_id) DO UPDATE SET
                        hints = excluded.hints,
                        types = excluded.types
                    """,
                    (notif.port, notif.user_id, notif.slot_id, notif.hints, notif.types)
                )

                # Get the ID if it didn't already have one
                if not notif.id:
                    row = connection.execute(f"""
                        SELECT id
                        FROM {self.table_name}
                        WHERE port = ?
                            AND user_id = ?
                            AND slot_id = ?
                        """,
                        (notif.port, notif.user_id, notif.slot_id)
                    ).fetchone()

                    # Set the ID
                    notif.id = row[0]

                # Wipe all existing terms
                connection.execute(f"""
                    DELETE FROM {self.table_name}_terms
                    WHERE notification_id = ?
                    """,
                    (notif.id,)
                )

                # Insert terms
                connection.executemany(f"""
                    INSERT INTO {self.table_name}_terms (notification_id, term)
                    VALUES(?, ?)
                    """,
                    [(notif.id, term) for term in notif.terms]
                )

                connection.commit()

            # Return newly created
            return self.get(notif.port, notif.user_id, notif.slot_id)

        except Exception as ex:
            logging.warning(f"Error in {self.table_name} upsert: {ex}")
            return None

    def get(self, port: int, user_id: int, slot_id: int) -> Optional[utils.Notification]:
        """Get a notification."""

        try:
            with self._conn() as connection:
                row = connection.execute(f"""
                    SELECT n.id, n.port, n.user_id, n.slot_id, n.hints, n.types, GROUP_CONCAT(t.term) AS terms
                    FROM {self.table_name} n
                    LEFT JOIN {self.table_name}_terms t
                        ON t.notification_id = n.id
                    WHERE n.port = ?
                        AND n.user_id = ?
                        AND n.slot_id = ?
                    GROUP BY n.id
                    """,
                    (port, user_id, slot_id)
                ).fetchone()

                return self.__bind(row)
            
        except Exception as ex:
            logging.warning(f"Error in {self.table_name} get: {ex}")
            return None
    
    def get_for_hint_flags(self, port: int, slot_id: int, notify_flags: utils.NotifyFlags) -> List[int]:
        """Get user IDs subscribed to notifications for a slot with matching hint flags."""

        try:

            logging.info(f"Checking Port: {port} | Slot: {slot_id} | Flags: {notify_flags.value}")

            with self._conn() as connection:
                rows = connection.execute(f"""
                    SELECT DISTINCT n.user_id
                    FROM {self.table_name} n
                    WHERE n.port = ?
                        AND n.slot_id = ?
                        AND (n.hints & ?) != 0
                    """,
                    (port, slot_id, notify_flags.value)
                ).fetchall()

                logging.info(f"Found hint_flag user ids: {rows}")

                return [ row["user_id"] for row in rows ] if rows else []

        except Exception as ex:
            logging.warning(f"Error in {self.table_name} get_for_hint_flags(): {ex}")
            return []
        
    def get_for_item_flags(self, port: int, slot_id: int, notify_flags: utils.NotifyFlags) -> List[int]:
        """Get user IDs subscribed to notifications for a slot with matching item flags."""

        try:
            with self._conn() as connection:
                rows = connection.execute(f"""
                    SELECT DISTINCT n.user_id
                    FROM {self.table_name} n
                    WHERE n.port = ?
                        AND n.slot_id = ?
                        AND (n.types & ?) != 0
                    """,
                    (port, slot_id, notify_flags)
                ).fetchall()

                return [ row["user_id"] for row in rows ] if rows else []

        except Exception as ex:
            logging.warning(f"Error in {self.table_name} get_for_item_flags(): {ex}")
            return []
        
    def get_for_terms(self, port: int, slot_id: int, item_names: List[str]) -> List[int]:
        """Get user IDs subscribed to notifications for a slot with matching terms."""

        logging.info(f"Checking item name(s): {item_names}")

        try:
            temp_table_name: str = "tmp_item_names"

            with self._conn() as connection:
                # Create a temporary table and populate with all item names
                connection.execute(f"CREATE TEMP TABLE IF NOT EXISTS {temp_table_name} (name TEXT NOT NULL)")
                connection.execute(f"DELETE FROM {temp_table_name}")
                connection.executemany(f"""
                    INSERT INTO {temp_table_name}
                    VALUES (?)
                    """,
                    ([(item_name,) for item_name in item_names])
                )

                # Query matches against temporary table
                rows = connection.execute(f"""
                    SELECT DISTINCT n.user_id
                    FROM {self.table_name} n
                    JOIN {self.table_name}_terms t
                        ON t.notification_id = n.id
                    JOIN {temp_table_name} i
                    WHERE n.port = ?
                        AND n.slot_id = ?
                        AND LOWER(i.name) LIKE '%' || lower(t.term) || '%'
                """,
                (port, slot_id)
            ).fetchall()
                
            return [ row["user_id"] for row in rows ] if rows else []

        except Exception as ex:
            logging.warning(f"Error in {self.table_name} get_for_terms(): {ex}")
            return []

    def delete(self, notif: utils.Notification) -> bool:
        """Delete a notification"""

        try:
            with self._conn() as connection:
                notif = connection.execute(f"""
                    DELETE
                    FROM {self.table_name}
                    WHERE id = ?
                    """,
                    (notif.id,)
                )
                connection.commit()
                
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