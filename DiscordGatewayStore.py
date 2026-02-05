import sqlite3
from dataclasses import dataclass
from typing import Optional, List

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

class Store:

    def __init__(self, path: str = "discord_gateway.db"):
        self.path = path
        self._init()

        self.agents = AgentRepo(self._conn)
        self.rooms = RoomRepo(self._conn)

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

    # def add_agent(self, agent: Agent) -> bool:
    #     """Add an agent binding to the store."""

    #     try:
    #         with self._conn() as connection:
    #             connection.execute("""
    #                 INSERT INTO agents (guild_id, channel_id, url, password)
    #                 VALUES (?, ?, ?, ?)
    #                 """,
    #                 (agent.guild_id, agent.channel_id, agent.url, agent.password)
    #             )
    #             connection.commit()

    #     except Exception as ex:
    #         return False
        
    #     return True

    # def exists_agent(self, guild_id: int, channel_id: int) -> bool:
    #     """Check if an agent binding exists in the store by its guild and channel ids."""

    #     with self._conn() as connection:
    #         agent = connection.execute("""
    #             SELECT 1
    #             FROM agents
    #             WHERE guild_id = ?
    #                 AND channel_id = ?
    #             """,
    #             (guild_id, channel_id)
    #         ).fetchone()

    #         return agent is not None

    # def get_agent(self, guild_id: int, channel_id: int) -> Optional[Agent]:
    #     """Get an agent binding from the store by its guild and channel ids."""

    #     with self._conn() as connection:
    #         agent = connection.execute("""
    #             SELECT guild_id, channel_id, url, password
    #             FROM agents 
    #             WHERE guild_id = ?
    #                 AND channel_id = ?
    #             """,
    #             (guild_id, channel_id)
    #         ).fetchone()

    #     return Agent(*agent) if agent else None
    
    # def get_all_agents(self) -> List[Agent]:
    #     """Get all agent bindings from the store."""

    #     with self._conn() as connection:
    #         agents = connection.execute("""
    #             SELECT guild_id, channel_id, url, password
    #             FROM agents
    #         """).fetchall()

    #         return [Agent(*agent) for agent in agents]
        
    # def get_all_guild_agents(self, guild_id: int) -> List[Agent]:
    #     """Get all agent bindings from the store for a specified guild."""

    #     with self._conn() as connection:
    #         agents = connection.execute("""
    #             SELECT guild_id, channel_id, url, password
    #             FROM agents
    #             WHERE guild_id = ?
    #             """,
    #             (guild_id,)
    #         ).fetchall()

    #         return [Agent(*agent) for agent in agents]
    
    # def delete_agent(self, guild_id: int, channel_id: int) -> bool:
    #     """Delete an agent binding from the store by its guild and channel ids."""

    #     try:
    #         with self._conn() as connection:
    #             connection.execute("""
    #                 DELETE
    #                 FROM agents
    #                 WHERE guild_id = ?
    #                     AND channel_id = ?
    #                 """,
    #                 (guild_id, channel_id)
    #             )
    #             connection.commit()

    #     except Exception as ex:
    #         return False
        
    #     return True


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