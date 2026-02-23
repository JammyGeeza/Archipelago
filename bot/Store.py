import logging
import sqlite3
import bot.Utils as utils
from typing import ClassVar, Dict, Optional, List

class Store:
    def __init__(self, path: str = "data/bot.db"):
        self.path = path

        # Create repos
        self.bindings = BindingRepo(self._conn)
        self.notifications = NotificationRepo(self._conn)
        self.notification_counts = NotificationCountRepo(self._conn)

        # Inject dependency repos
        self.notifications._inject(self.notification_counts)

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
        raise NotImplementedError(f"The _create() method for {self.__class__.__name__} has been called but not overridden.")
    
    def _inject(self, *args, **kwargs):
        """Inject dependency repos."""
        raise NotImplementedError(f"The inject() method for {self.__class__.__name__} has been called but not overridden.")

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
            raise

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
            with self._conn() as conn:
                conn.execute(f"""
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
                
                conn.execute(f"""
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

                conn.commit()

        except Exception as ex:
            logging.error(f"ERROR in {self.__class__.__name__}._create(): {ex}")
            raise

    def _inject(self, notif_counts_repo: "NotificationCountRepo"):
        """Inject the notification counts repo."""
        self.notification_counts = notif_counts_repo

    def delete(self, notif: utils.Notification) -> bool:
        """Delete a notification"""

        try:
            with self._conn() as conn:
                notif = conn.execute(f"""
                    DELETE
                    FROM {self.table_name}
                    WHERE id = ?
                    """,
                    (notif.id,)
                )

                conn.commit()
                
                return True
            
        except Exception as ex:
            logging.warning(f"Error in {self.__class__.__name__}.delete(): {ex}")
            return False

    def get(self, port: int, user_id: int, slot_id: int) -> Optional[utils.Notification]:
        """Get a notification."""

        try:
            with self._conn() as conn:
                row = conn.execute(f"""
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
            notif.counts = self.notification_counts.get_for_notification(notif)
                
            return notif
            
        except Exception as ex:
            logging.warning(f"Error in {self.__class__.__name__}.get(): {ex}")
            return None

    def get_count_items_for_port(self, port: int) -> Dict[int, List[int]]:
        """Get slot/item IDs for count notifications"""

        try:
            with self._conn() as conn:
                rows = conn.execute(f"""
                    SELECT DISTINCT n.slot_id, c.item_id
                    FROM {self.table_name}_counts c
                    JOIN {self.table_name} n
                        ON n.id = c.notification_id
                    WHERE n.port = ?
                    """,
                    (port,)
                ).fetchall()

            result = {}
            for slot_id, item_id in rows:
                result.setdefault(slot_id, []).append(item_id)

            return result
            
        except Exception as ex:
            logging.warning(f"Error in {self.__class__.__name__}.get_count_items_for_port(): {ex}")
            return {}

    def get_for_hint_flags(self, port: int, slot_id: int, notify_flags: utils.NotifyFlags) -> List[int]:
        """Get user IDs subscribed to notifications for a slot with matching hint flags."""

        try:

            with self._conn() as conn:
                rows = conn.execute(f"""
                    SELECT DISTINCT n.user_id
                    FROM {self.table_name} n
                    WHERE n.port = ?
                        AND n.slot_id = ?
                        AND (n.hints & ?) != 0
                    """,
                    (port, slot_id, notify_flags.value)
                ).fetchall()

            return [ row["user_id"] for row in rows ] if rows else []

        except Exception as ex:
            logging.warning(f"Error in {self.__class__.__name__}.get_for_hint_flags(): {ex}")
            return []

    def get_for_item_flags(self, port: int, slot_id: int, notify_flags: utils.NotifyFlags) -> List[int]:
        """Get user IDs subscribed to notifications for a slot with matching item flags."""

        try:
            with self._conn() as conn:
                rows = conn.execute(f"""
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

            with self._conn() as conn:
                # Create a temporary table and populate with all item names
                conn.execute(f"CREATE TEMP TABLE IF NOT EXISTS {temp_table_name} (name TEXT NOT NULL)")
                conn.execute(f"DELETE FROM {temp_table_name}")
                conn.executemany(f"""
                    INSERT INTO {temp_table_name}
                    VALUES (?)
                    """,
                    ([(item_name,) for item_name in item_names])
                )

                # Query matches against temporary table
                rows = conn.execute(f"""
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
            with self._conn() as conn:
                conn.execute(f"""
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
                    row = conn.execute(f"""
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
                conn.execute(f"""
                    DELETE FROM {self.table_name}_terms
                    WHERE notification_id = ?
                    """,
                    (notif.id,)
                )

                # Insert terms
                conn.executemany(f"""
                    INSERT INTO {self.table_name}_terms (notification_id, term)
                    VALUES(?, ?)
                    """,
                    [(notif.id, term) for term in notif.terms]
                )

                conn.commit()

            # Sync counts
            self.notification_counts.sync(notif)

            # Return newly created
            return self.get(notif.port, notif.user_id, notif.slot_id)

        except Exception as ex:
            logging.warning(f"Error in {self.__class__.__name__}.upsert(): {ex}")
            return None
        
class NotificationCountRepo(RepoBase):

    table_name: ClassVar[str] = f"{NotificationRepo.table_name}_counts"

    def _create(self):
        try:
            with self._conn() as conn:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                        notification_id INTEGER NOT NULL,
                        item_id         INTEGER NOT NULL,
                        count           INTEGER NOT NULL,
                        end_at          INTEGER NOT NULL,

                        FOREIGN KEY (notification_id)
                            REFERENCES notifications(id)
                            ON DELETE CASCADE,

                        UNIQUE(notification_id, item_id, count)
                    )
                """)

                conn.commit()
                    
        except Exception as ex:
            logging.error(f"ERROR in {self.__class__.__name__}._create(): {ex}")
            raise

    def pop_for_item_counts(self, port: int, slot_id: int, item_counts: Dict[int, int]) -> List[int]:
        """Get user IDs subscribed to notifications for a slot with matching item counts and pop (auto-delete) the notification counts."""

        try:
            with self._conn() as conn:
                temp_table_name = f"tmp_{self.table_name}"
                conn.execute(f"CREATE TEMP TABLE IF NOT EXISTS {temp_table_name} (item_id INTEGER NOT NULL, target INTEGER NOT NULL)")
                conn.execute(f"DELETE FROM {temp_table_name}")
                conn.executemany(f"""
                    INSERT INTO {temp_table_name}
                    VALUES (?,?)
                    """,
                    ([(item_id, count) for item_id, count in item_counts.items()])
                )

                # Query matches against temporary table
                rows = conn.execute(f"""
                    SELECT DISTINCT n.user_id
                    FROM {NotificationRepo.table_name} n
                    JOIN {self.table_name} c
                        ON c.notification_id = n.id
                    JOIN {temp_table_name} i
                        ON i.item_id = c.item_id
                    WHERE n.port = ?
                        AND n.slot_id = ?
                        AND i.target >= c.end_at
                    """,
                    (port, slot_id)
                ).fetchall()

                # Auto-remove found entries
                conn.execute(f"""
                    DELETE FROM {self.table_name}
                    WHERE rowid IN (
                        SELECT c.rowid
                        FROM {self.table_name} c
                        JOIN {NotificationRepo.table_name} n
                            ON c.notification_id = n.id
                        JOIN {temp_table_name} i
                            ON i.item_id = c.item_id
                        WHERE n.port = ?
                            AND n.slot_id = ?
                            AND i.target >= c.end_at
                    )
                """, (port, slot_id))

                conn.commit()

            return [ row["user_id"] for row in rows ] if rows else []

        except Exception as ex:
            logging.warning(f"Error in {self.__class__.__name__}.get_for_item_counts(): {ex}")
            return []

    def get_for_notification(self, notif: utils.Notification) -> List[utils.NotificationCount]:
        """Get all notification counts for a notification.""" 

        try:
            with self._conn() as conn:
                rows = conn.execute(f"""
                    SELECT *
                    FROM {self.table_name}
                    WHERE notification_id = ?
                    """,
                    (notif.id,)
                ).fetchall()

            return [ utils.NotificationCount.from_row(row) for row in rows ] if rows else []

        except Exception as ex:
            logging.error(f"ERROR in {self.__class__.__name__}.get_for_notification(): {ex}")
            return []
        
    def sync(self, notif: utils.Notification):
        """Add new and remove missing notification counts for a notification."""

        try:
            with self._conn() as conn:

                # If no counts, delete all
                if not notif.counts:
                    conn.execute(f"""
                        DELETE FROM {self.table_name}
                        WHERE notification_id = ?
                        """,
                        (notif.id,)
                    )

                    conn.commit()
                    return

                # Add new / Update existing items
                conn.executemany(f"""
                    INSERT INTO {self.table_name} (notification_id, item_id, count, end_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(notification_id, item_id, count) DO UPDATE SET
                        end_at = excluded.end_at
                    """,
                    [(notif.id, nc.item_id, nc.count, nc.end_at) for nc in notif.counts ]
                )

                # Create temporary table
                temp_table_name = f"tmp_{self.table_name}"
                conn.execute(f"""
                    CREATE TEMP TABLE IF NOT EXISTS {temp_table_name} (
                        item_id     INTEGER NOT NULL,
                        count       INTEGER NOT NULL
                    )"""
                )
                conn.execute(f"DELETE FROM {temp_table_name}")
                conn.executemany(f"""
                    INSERT OR IGNORE INTO {temp_table_name} (item_id, count)
                    VALUES (?, ?)""",
                    [(nc.item_id, nc.count) for nc in notif.counts]
                )

                # Delete missing items
                conn.execute(f"""
                    DELETE FROM {self.table_name}
                    WHERE notification_id = ?
                        AND (item_id, count) NOT IN (
                            SELECT item_id, count
                            FROM {temp_table_name}
                        )""",
                    (notif.id,)
                )

                conn.commit()

        except Exception as ex:
            logging.error(f"ERROR in {self.__class__.__name__}.sync(): {ex}")
            raise