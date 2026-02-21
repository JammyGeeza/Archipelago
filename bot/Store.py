import logging
import sqlite3
import bot.Utils as utils
from typing import ClassVar, Optional, List

class Store:
    def __init__(self, path: str = "bot.db"):
        self.path = path
        self.bindings = BindingRepo(self._conn)
        self.notifications = NotificationRepo(self._conn)

    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

class RepoBase:
    table_name: ClassVar[str]

    def __init__(self, connection_factory: sqlite3.Connection):
        self._conn = connection_factory
        self._create()

    def _create(self):
        """Create the repo to store this data type."""
        raise NotImplementedError(f"The _create() method for {self.__class__.__name__} has not been overridden.")

class BindingRepo(RepoBase):
    table_name: ClassVar[str] = "bindings"

    def _create(self):
        """Create the repo to store binding data."""

        try:

            with self._conn() as conn:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        channel_id      INTEGER PRIMARY KEY NOT NULL,
                        guild_id        INTEGER NOT NULL,
                        port            INTEGER NOT NULL,
                        slot_name       TEXT NOT NULL,
                        password        TEXT,
                        last_modified   INTEGER NOT NULL DEFAULT (unixepoch())
                    )
                """)

                conn.commit()

        except Exception as ex:
            logging.error(f"Error in {self.__class__.__name__}._create(): {ex}")

    def delete(self, binding: utils.Binding) -> bool:
        """Delete a room binding."""

        try:
            with self._conn() as conn:
                conn.execute(f"""
                    DELETE FROM {self.table_name}
                    WHERE channel_id = ?
                    """,
                    (binding.channel_id,)
                )
                conn.commit()

                return True

        except Exception as ex:
            logging.error(f"ERROR in {self.__class__.__name__}.delete(): {ex}")
            return False

    def get_all(self) -> List[utils.Binding]:
        """Get all room bindings."""

        try:
            with self._conn() as conn:
                rows = conn.execute(f"""
                    SELECT *
                    FROM {self.table_name}
                """).fetchall()

                return [ utils.Binding.from_row(row) for row in rows] if rows else []
            
        except Exception as ex:
            logging.error(f"ERROR in {self.__class__.__name__}.get_all_for_guild(): {ex}")
            return []

    def get_all_for_guild(self, guild_id: int) -> List[utils.Binding]:
        """Get all room bindings for a specified guild."""

        try:
            with self._conn() as conn:
                rows = conn.execute(f"""
                    SELECT *
                    FROM {self.table_name}
                    WHERE guild_id = ?
                    """,
                    (guild_id,)
                ).fetchall()

                return [ utils.Binding.from_row(row) for row in rows] if rows else []
            
        except Exception as ex:
            logging.error(f"ERROR in {self.__class__.__name__}.get_all_for_guild(): {ex}")
            return []

    def get_one(self, channel_id: int) -> Optional[utils.Binding]:
        """Get an existing room binding."""

        try:
            with self._conn() as conn:
                row = conn.execute(f"""
                    SELECT *
                    FROM {self.table_name}
                    WHERE channel_id = ?
                    """,
                    (channel_id,)
                ).fetchone()

                return utils.Binding.from_row(row) if row else None
            
        except Exception as ex:
            logging.error(f"ERROR in {self.__class__.__name__}.get_one(): {ex}")
            return None

    def upsert(self, binding: utils.Binding) -> Optional[utils.Binding]:
        """Insert or update a room binding"""

        try:
            with self._conn() as conn:
                conn.execute(f"""
                    INSERT INTO {self.table_name} (channel_id, guild_id, port, slot_name, password, last_modified)
                    VALUES (?, ?, ?, ?, ?, unixepoch())
                    ON CONFLICT(channel_id) DO UPDATE SET
                        guild_id = excluded.guild_id,
                        port = excluded.port,
                        slot_name = excluded.slot_name,
                        password = excluded.password,
                        last_modified = unixepoch()
                    """,
                    (binding.channel_id, binding.guild_id, binding.port, binding.slot_name, binding.password)
                )
                
                conn.commit()

                return self.get_one(binding.channel_id)
            
        except Exception as ex:
            logging.error(f"ERROR in {self.__class__.__name__}.upsert(): {ex}")
            return None

class NotificationRepo(RepoBase):
    table_name: ClassVar[str] = "notifications"

    def _create(self):

        try:
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

                connection.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name}_counts (
                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                        notification_id INTEGER NOT NULL,
                        item_id         INTEGER NOT NULL,
                        target          INTEGER NOT NULL,
                        last_count      INTEGER NOT NULL,

                        FOREIGN KEY (notification_id)
                            REFERENCES notifications(id)
                            ON DELETE CASCADE,

                        UNIQUE(notification_id, item_id)
                    )
                """)

                connection.commit()

        except Exception as ex:
            logging.error(f"ERROR in {self.__class__.__name__}._init(): {ex}")

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

                # Wipe all existing counts
                connection.execute(f"""
                    DELETE FROM {self.table_name}_counts
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

                # Insert counts
                connection.executemany(f"""
                    INSERT INTO {self.table_name}_counts (notification_id, item_id, target, last_count)
                    VALUES(?, ?, ?, ?)
                    """,
                    [(notif.id, count.item_id, count.target, count.last_count) for count in notif.counts]
                )

                connection.commit()

            # Return newly created
            return self.get(notif.port, notif.user_id, notif.slot_id)

        except Exception as ex:
            logging.warning(f"Error in {self.__class__.__name__}.upsert(): {ex}")
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

                notif = utils.Notification.from_row(row)

                children = connection.execute(f"""
                    SELECT *
                    FROM {self.table_name}_counts
                    WHERE notification_id = ?
                    """,
                    (notif.id,)
                ).fetchall()

                notif.counts = [ utils.NotificationCount.from_row(child) for child in children ] if children else []
                
                return notif
            
        except Exception as ex:
            logging.warning(f"Error in {self.__class__.__name__}.get(): {ex}")
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
            logging.warning(f"Error in {self.__class__.__name__}.get_for_hint_flags(): {ex}")
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
            logging.warning(f"Error in {self.__class__.__name__}.get_for_item_flags(): {ex}")
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
            logging.warning(f"Error in {self.__class__.__name__}.get_for_terms(): {ex}")
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
            logging.warning(f"Error in {self.__class__.__name__}.delete(): {ex}")
            return False