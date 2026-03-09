import logging
import os
from .BotUtils import Jsonable, NotifyFlags
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from pony.orm import(
    Database, Required, Optional, PrimaryKey, Set,
    ObjectNotFound,
    composite_key, delete, desc,
    db_session
)

store = Database()

_CURRENT_SCHEMA_VERSION = 1
_LEGACY_SCHEMA_VERSION = 0

def init_db(args):

    # Make directory if it doesn't exist
    path = Path(args["filename"]).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    # Does db already exist?
    new_db = not Path(path).exists()

    # Bind database
    store.bind(provider=args["provider"], filename=str(path), create_db=args["create_db"])

    # Apply migrations, if required
    _migrate(store, new_db)

    # Creaate mapping / schema
    store.generate_mapping(create_tables=True)

def column_exists(db: Database, table_name: str, column_name: str) -> bool:
    columns = db.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    return any(col[1] == column_name for col in columns)

@db_session
def _migrate(db: Database, new_db: bool):

    # Create migration table, if it doesn't exist - manual SQL here to create table as SchemaVersion needs to exist
    # BEFORE the mappings are created, if the DB file already exists but SchemaVersion table doesn't.
    db.execute("""
        CREATE TABLE IF NOT EXISTS SchemaVersion (
            id          INTEGER PRIMARY KEY,
            version     INTEGER NOT NULL,
            created_at  TEXT NOT NULL,
            modified_at TEXT
        )
    """)

    # Get version record, if exists
    row = db.execute("SELECT version FROM SchemaVersion WHERE id = 1").fetchone()
    if row is None:
        version = _CURRENT_SCHEMA_VERSION if new_db else _LEGACY_SCHEMA_VERSION
        created_at = datetime.utcnow().isoformat()

        db.execute("INSERT INTO SchemaVersion (id, version, created_at) VALUES (1, $version, $created_at)")
    else:
        version = row[0]
    
    # Apply migration(s) if lower than current schema version
    if version < _CURRENT_SCHEMA_VERSION:
        
        # Apply migration 1, if required
        if version < 1:
            if not column_exists(db, "Binding", "room_id"):
                db.execute("ALTER TABLE Binding ADD COLUMN room_id TEXT")

        # If adding/removing/modifying further columns in existing tables, do the following:
        # - Increment _CURRENT_SCHEMA_VERSION by 1
        # - Add new schema logic as current schema version. Example:
        #       if schema_version < 2:
        #           if not column_exists(db, "TableName", "ColumnName"):
        #               db.execute("ALTER TABLE TableName ADD COLUMN ColumnName INTEGER")

        version = _CURRENT_SCHEMA_VERSION
        modified_at = datetime.utcnow().isoformat()

        # Set to current version
        db.execute("""
            UPDATE SchemaVersion 
            SET version = $version, modified_at = $modified_at
            WHERE id = 1
            """
        )

#region Entities

class Binding(store.Entity):
    id = PrimaryKey(int, auto=True)
    guild_id = Required(int, size=64)
    channel_id = Required(int, size=64, unique=True)
    port = Required(int)
    slot_name = Required(str)
    password = Optional(str, nullable=True)
    room_id = Optional(str, nullable=True)
    enabled = Required(bool, default=True)
    created_at = Required(datetime, default=lambda: datetime.utcnow())
    modified_at = Optional(datetime, nullable=True)

    notifications = Set("NotificationSettings", cascade_delete=True)

    composite_key(port, slot_name)

    @db_session
    def set_state(self, enabled: bool):
        self.enabled = enabled

    @db_session
    def remove(self):
        self.delete()

    @classmethod
    @db_session
    def create(cls, guild_id: int, channel_id: int, port: int, slot_name: str, password: str | None = None, room_id: str | None = None):
        return cls(guild_id=guild_id, channel_id=channel_id, port=port, slot_name=slot_name, password=password, room_id=room_id)

    @classmethod
    @db_session
    def delete_for_channel(cls, channel_id: int):

        # Attempt to find binding
        if not (binding:= cls.get(channel_id=channel_id)):
            raise ObjectNotFound(Binding, channel_id)
        
        # Delete
        binding.delete()

    @classmethod
    @db_session
    def get_all(cls) -> list["Binding"]:
        return cls.select()[:]
    
    @classmethod
    @db_session
    def get_all_enabled(cls) -> list["Binding"]:
        return cls.select(lambda b: b.enabled is True)[:]

    @classmethod
    @db_session
    def get_for_guild(cls, guild_id: int) -> list["Binding"]:
        return cls.select(lambda b: b.guild_id == guild_id)[:]
    
    @classmethod
    @db_session
    def get_for_channel(cls, channel_id: int) -> "Binding":
        return cls.get(channel_id=channel_id)
    
    @classmethod
    @db_session
    def update(cls, channel_id: int, port: int) -> "Binding":

        # Attempt to find binding
        if not (binding:= cls.get(channel_id=channel_id)):
            raise ObjectNotFound(Binding, channel_id)
        
        # Update values
        binding.port = port

        return binding

class NotificationSettings(store.Entity):
    id = PrimaryKey(int, auto=True)
    binding = Required(Binding)
    user_id = Required(int, size=64)
    slot_id = Required(int)
    hint_flags = Required(int, default=0)
    item_flags = Required(int, default=0)
    enabled = Required(bool, default=True)
    created_at = Required(datetime, default=lambda: datetime.utcnow())
    modified_at = Optional(datetime)

    counts = Set("NotificationCount", cascade_delete=True)
    terms = Set("NotificationTerm", cascade_delete=True)

    composite_key(binding, user_id, slot_id)

    @classmethod
    @db_session
    def update(cls, notif_id: int, hint_flags: int = None, item_flags: int = None, terms: list[str] = None, counts: list[tuple[int, int, int]] = None) -> "NotificationSettings":
        
        # Get existing (to start new db session as previous is now detached)
        if not (notif:= cls.get(id=notif_id)):
            raise ObjectNotFound(NotificationSettings, notif_id)

        # Update flags if provided
        if hint_flags is not None: notif.hint_flags = hint_flags
        if item_flags is not None: notif.item_flags = item_flags

        # Update terms if provided
        if terms is not None:

            # Casefold all terms (and remove duplicates)
            casefold_terms = { term.casefold() for term in terms }

            # Create new terms
            for new_term in set(casefold_terms) - { t.term for t in notif.terms }:
                NotificationTerm(notification=notif, term=new_term)

            # Remove missing terms
            for missing_term in [t for t in notif.terms if t.term not in casefold_terms ]:
                missing_term.delete()

        # Update counts if provided
        if counts is not None:

            # Get new counts
            lookup = { (c.item_id, c.amount) for c in notif.counts }
            new_counts = [ (id, amt, end) for id, amt, end in counts if (id, amt) not in lookup ]
            for id, amt, end in new_counts:
                NotificationCount(notification=notif, item_id=id, amount=amt, end_amount=end)

            # Update existing counts
            lookup = { (id, amt): end for id, amt, end in counts }
            updated_counts = [ (c, lookup.get((c.item_id, c.amount))) for c in notif.counts if (c.item_id, c.amount) in lookup ]
            for existing, end_amount in updated_counts:
                existing.end_amount= end_amount

            # Remove missing counts
            lookup = { (id, amt) for id, amt, _ in counts }
            missing_counts = [ c for c in notif.counts if (c.item_id, c.amount) not in lookup ]
            for missing in missing_counts:
                missing.delete()

        notif.terms.load()
        notif.counts.load()

        return notif

    @classmethod
    @db_session
    def create(cls, binding: Binding, user_id: int, slot_id: int):
        return cls(binding=binding, user_id=user_id, slot_id=slot_id)

    @classmethod
    @db_session
    def get_for_user(cls, channel_id: int, user_id: int) -> list["NotificationSettings"]:
        return cls.select(
            n for n in NotificationSettings 
            if n.binding.channel_id == channel_id
            and n.user_id == user_id
        )
    
    @classmethod
    @db_session
    def get_users_for_hint_flags(cls, channel_id: int, slot_id: int, hint_flags: int) -> list[int]:
        """Get all notification settings for a channel where the slot's hint flags match."""
        
        # Bail if no hint flags
        if hint_flags == 0:
            return []
        
        # Get matching items
        matching_items = cls.select(
            lambda n:
            n.binding.channel_id == channel_id
            and n.slot_id == slot_id
        )[:]

        # Get with matching flags (as BITAND not supported)
        matching_flags = [
            n.user_id
            for n in matching_items
            if (n.hint_flags & hint_flags) != 0
        ]
        
        # Return unique user IDs
        return list({ id for id in matching_flags })

    @classmethod
    @db_session
    def get_users_for_item_flags(cls, channel_id: int, slot_id: int, item_flags: int) -> list[int]:
        """Get all notification settings for a channel where the slot's hint flags match."""
        
        # Bail if no item flags
        if item_flags == 0:
            return []
        
        # Get matching items
        matching_items = cls.select(
            lambda n:
            n.binding.channel_id == channel_id
            and n.slot_id == slot_id
        )[:]

        # Get with matching flags (as BITAND not supported)
        matching_flags = [
            n.user_id
            for n in matching_items
            if (n.item_flags & item_flags) != 0
        ]
        
        # Return unique user IDs
        return list({ id for id in matching_flags })

    @classmethod
    @db_session
    def get_for_user_slot(cls, channel_id: int, user_id: int, slot_id: int) -> "NotificationSettings":
        return cls.select(
            n for n in NotificationSettings
            if n.binding.channel_id == channel_id
            and n.user_id == user_id
            and n.slot_id == slot_id
        )
    
    @classmethod
    @db_session
    def get_or_create(cls, channel_id: int, user_id: int, slot_id: int) -> "NotificationSettings":

        # Get binding first
        if not (binding:= Binding.get(channel_id=channel_id)):
            raise ObjectNotFound(Binding, channel_id)

        # Attempt to get existing binding or create one if it doesn't exist
        notification = cls.get(binding=binding, user_id=user_id, slot_id=slot_id) \
            or cls(binding=binding, user_id=user_id, slot_id=slot_id)

        # Load terms and counts
        notification.terms.load()
        notification.counts.load()

        return notification

class NotificationCount(store.Entity):
    id = PrimaryKey(int, auto=True)
    notification = Required(NotificationSettings)
    item_id = Required(int)
    amount = Required(int)
    end_amount = Required(int)
    created_at = Required(datetime, default=lambda: datetime.utcnow())

    composite_key(notification, item_id, amount)

    @classmethod
    @db_session
    def get_for_channel(cls, channel_id: int) -> dict[int, list[int]]:
        "Get slots and their respective items to track counts for"

        if not channel_id:
            return {}
        
        # Get for matching channel
        matching_slots = cls.select(
            lambda nc:
            nc.notification.binding.channel_id == channel_id
        )

        # Extract slot IDs and all item IDs (unique)
        slot_items = defaultdict(set)
        for nc in matching_slots:
            slot_items[nc.notification.slot_id].add(nc.item_id)

        # Convert to dict with list and return
        return { k: list(v) for k, v in slot_items.items() }

    @classmethod
    @db_session
    def pop_users_for_counts(cls, channel_id: int, slot_id: int, to_match: dict[int, int]) -> list[int]:

        # If no terms, return nothing
        if not to_match:
            return []

        # Get item IDs
        item_ids = list(to_match.keys())

        # Get with matching items
        matching_items = cls.select(
            lambda nc:
            nc.notification.binding.channel_id == channel_id
            and nc.notification.slot_id == slot_id
            and nc.item_id in item_ids
        )

        # Get with matching thresholds
        matching_counts = [
            nc for nc in matching_items
            if to_match[nc.item_id] >= nc.end_amount
        ]

        # Compile unique user IDs
        user_ids = list({ nc.notification.user_id for nc in matching_counts })

        # Remove matches
        for nc in matching_counts:
            nc.delete()

        # return IDs
        return user_ids

class NotificationTerm(store.Entity):
    id = PrimaryKey(int, auto=True)
    notification = Required(NotificationSettings)
    term = Required(str)
    created_at = Required(datetime, default=lambda: datetime.utcnow())
    modified_at = Optional(datetime)

    composite_key(notification, term)

    @classmethod
    @db_session
    def get_users_for_terms(cls, channel_id: int, slot_id: int, to_match: list[str]) -> list[int]:

        # If no terms, return nothing
        if not to_match:
            return []

        # Casefold all matches
        casefold_to_match: list[str] = [m.casefold() for m in to_match]

        # Match by slot
        matching_slot = cls.select(
            lambda nt:
            nt.notification.binding.channel_id == channel_id
            and nt.notification.slot_id == slot_id
        )

        # Match by term 'LIKE' (wasn't supported as SQL)
        matching_terms = [
            nt.notification.user_id
            for nt in matching_slot
            if any(nt.term in term for term in casefold_to_match)
        ]

        # Compile unique IDs
        return list({ id for id in matching_terms })

class SchemaVersion(store.Entity):
    id = PrimaryKey(int, auto=True)
    version = Required(int, default=1)
    created_at = Required(datetime, default=lambda: datetime.utcnow())
    modified_at = Required(datetime, default=lambda: datetime.utcnow())

    def increment_version(self):
        self.version += 1
        self.modified_at = datetime.utcnow()

#endregion