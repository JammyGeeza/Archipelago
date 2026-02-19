#!/usr/bin/env python3

import argparse
import asyncio
import bot.Packets as pkts
import discord
import json
import logging
import math
import sys
import uuid

from discord import app_commands
from discord.ext import commands
from bot.Store import Agent, Notification, Store, RoomConfig
from bot.Utils import Action, Hookable, ItemFlags
from typing import Dict, Literal, List, Optional, Tuple

# Global variables
admin_only: bool = True
bot = commands.Bot(command_prefix='/', intents=discord.Intents.none())
store = Store()

class AgentProcess:

    on_discord_message_received = Hookable()
    on_hint_received = Hookable()
    on_item_received = Hookable()
    on_status_received = Hookable()

    def __init__(self, config: RoomConfig):

        self.config: RoomConfig = config
        self.process: asyncio.subprocess.Process = None
        # self.stats: Dict[str, pkts.PlayerStats] = {}
        self.status: str = "Stopped"
        
        self.__player_lookup: dict[str, int] = {}               # Player Name-to-Id lookup
        self.__request_queue: dict[str, asyncio.Future] = {}    # Queue for requests awaiting a response

        self.rcv_queue: asyncio.Queue = asyncio.Queue()
        self.snd_queue: asyncio.Queue = asyncio.Queue()

    async def send(self, packet: pkts.TrackerPacket):
        """Send a payload to the agent process."""
        logging.info(f"Sending {packet.cmd} to gateway...")
        await self.__send(packet.to_json())

    async def request(self, request: pkts.IdentifiablePacket) -> pkts.IdentifiablePacket:
        """Request an action and await a response."""

        logging.info(f"Sending request... | Type: {request.cmd} | ID: {request.id}")

        response: asyncio.Future = asyncio.get_running_loop().create_future()
        self.__request_queue[request.id] = response

        # Send packet
        await self.send(request)

        # Wait for response
        return await response

    async def start(self):
        """Start the agent process"""

        logging.info(f"Starting agent process... | Port: {self.config.port}")

        if self.process:
            logging.warning(f"Agent process is already running | Port: {self.config.port}")
            return

        # Create command-line arguments
        args = [
            sys.executable,
            "-m", "bot.Agent",
            "--port", str(self.config.port),
            "--multidata", self.config.multidata,
            "--savedata", self.config.savedata
        ]

        # Add password arg if provided
        if self.config.password:
            args += ["--password", self.config.password]

        # Create agent process
        self.process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )

        # Start watchers/readers
        asyncio.create_task(self.__watch())
        asyncio.create_task(self.__read_stdout())
        # asyncio.create_task(self._handle_packet())

    def stop(self):
        """Stop the agent process"""

        logging.info(f"Stopping agent process... | Port {self.config.port}")

        # Check process exists
        if not self.process:
            logging.warning(f"Agent process is not currently running | Port {self.config.port}")

        # Terminate process
        self.process.terminate()

    async def __handle_packet(self, packet: pkts.TrackerPacket):
        """Handle a received packet from the agent process"""

        logging.info(f"Handling {packet.cmd} packet...")

        match packet.cmd:

            case pkts.DiscordMessagePacket.cmd:
                await self.__handle_discordmessage_packet(packet)

            # case pkts.StatusUpdatePacket.cmd:
            #     await self.__handle_statusupdate_packet(packet)

            case pkts.StatisticsResponsePacket.cmd | pkts.StatusResponsePacket.cmd:
                await self.__handle_response_packet(packet)

            # case pkts.StoredStatsPacket.cmd:
            #     await self.__handle_storedstats_packet(packet)

            case pkts.TrackerInfoPacket.cmd:
                await self.__handle_trackerinfo_packet(packet)

            case _:
                logging.warning(f"{packet.cmd} is an unhandled packet type.")

        # while True:
        #     if not (data:= await self.rcv_queue.get()):
        #         continue
            
        #     # Convert to appropriate packet type

        #     await pkts.TrackerPacket.receive(data, self)

    async def __send(self, json: str):
        """Send data to the agent process."""
        self.process.stdin.write(f"{json}\n".encode("utf-8"))
        await self.process.stdin.drain()

    # @pkts.DiscordMessagePacket.on_received
    async def __handle_discordmessage_packet(self, packet: pkts.DiscordMessagePacket):
        """Handler for receiving a discord message packet."""

        logging.info(f"Received {packet.cmd} from :{self.config.port}")

        # Trigger event
        await self.on_discord_message_received.run(packet.message)

    # @pkts.StatusUpdatePacket.on_received
    # async def __handle_statusupdate_packet(self, packet: pkts.StatusUpdatePacket):
    #     """Handle receipt of a status packet"""
        
    #     logging.info(f"Received {packet.cmd} from :{self.config.port}")

    #     # Store status
    #     self.status = packet.status

    #     # Trigger event
    #     await self.on_status_received.run(packet.message)

    # @pkts.StatisticsResponsePacket.on_received
    # @pkts.StatusResponsePacket.on_received
    async def __handle_response_packet(self, packet: pkts.IdentifiablePacket):
        """Handler for receiving a response packet"""

        logging.info(f"Received {packet.cmd} from :{self.config.port}")

        # If waiting for this response, set packet as result
        if (future:= self.__request_queue.get(packet.id)):
            future.set_result(packet)

    # @pkts.StoredStatsPacket.on_received
    # async def __handle_storedstats_packet(self, packet: pkts.StoredStatsPacket):
    #     """Handler for receiving stored stats."""

    #     # Update stored stats
    #     self.stats.update({ k: v for k, v in packet.stats.items() })

    async def __handle_trackerinfo_packet(self, packet: pkts.TrackerInfoPacket):
        """Handle an incoming TrackerInfo packet"""

        # Update player lookup (and reverse to name-to-id)
        self.__player_lookup.update({ v: k for k, v in packet.players.items() })

    async def __read_stdout(self):
        """Listen for data received from the agent process."""

        if self.process.stdout is not None:
            async for line in self.process.stdout:
                payload = line.decode("utf-8", errors="replace").rstrip()

                # Convert from json and handle
                for data in json.loads(payload):
                    await self.__handle_packet(
                        pkts.TrackerPacket.parse(data)
                    )

    async def __watch(self):
        """Watch the agent process and clean-up when terminated."""

        code = await self.process.wait()

        logging.warning(f"Agent process for port {self.config.port} exited with code {code}")

        # Clear process
        self.process = None
        self.status = "Stopped"

    def get_player_count(self) -> int:
        """Get amount of players."""
        return len(self.__player_lookup.keys())

    def get_player_name(self, slot_id: int) -> str | None:
        """Get the name of a player by slot number"""
        return next((name for name, slot in self.__player_lookup.items() if slot == slot_id), None)

    def get_player_slot(self, player_name: str) -> int | None:
        """Get the slot number for a player by name (ignoring case)"""
        return next((slot for name, slot in self.__player_lookup.items() if player_name.casefold() == name.casefold()), None)

    def get_player_stats(self, player_name: str) -> pkts.PlayerStats | None:
        """Get stats for a player."""
        return self.stats.get(player_name, None)

    def get_session_stats(self) -> pkts.PlayerStats | None:
        """Returns stats for the entire session."""
        stats: pkts.PlayerStats = pkts.PlayerStats(
            checked=sum(stats.checked for stats in self.stats.values()),
            goal=sum(1 for stats in self.stats.values() if stats.goal), # HACK
            remaining=sum(stats.remaining for stats in self.stats.values()),
            received=sum(stats.received for stats in self.stats.values())
        )

        return stats

    def get_status(self) -> str:
        """Get current status."""
        return self.status
    
    def player_exists(self, player: str) -> bool:
        """Check if a player name exists."""
        return any(True for key in self.stats.keys() if key.casefold() == player.casefold())

agents: Dict[Tuple[int, int], AgentProcess] = {}

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments, providing defaults from host.yaml file if argument not provided."""
    from settings import get_settings

    parser = argparse.ArgumentParser()
    defaults = get_settings().discord_gateway_options.as_dict()

    parser.add_argument("--token", default=defaults["token"], type=str,
                        help="The discord bot auth token, generated from the discord developer portal.")
    parser.add_argument("--admin-only", default=defaults["admin_only"], type=bool)
    parser.add_argument("--loglevel", default=defaults["loglevel"], type=str, choices=["debug", "info", "warning", "error", "critical"])
    parser.add_argument("--logtime", default=defaults["logtime"], type=bool)
    
    args = parser.parse_args()
    return args

def get_agent(guild_id: int, channel_id: int) -> Optional[AgentProcess]:
    """Get an agent process, if it exists."""
    global agents
    return agents.get((guild_id, channel_id), None)

async def interaction_is_admin(interaction: discord.Interaction) -> bool:
    """Check if user is owner or administrator."""

    # Fetch guild information
    guild = await interaction.client.fetch_guild(interaction.guild_id)

    # Is user owner or administrator of the guild?
    return bool(
        guild.owner_id == interaction.user.id
        or interaction.user.guild_permissions.administrator
    )

@AgentProcess.on_discord_message_received
async def _on_agent_discord_message_received(agent: AgentProcess, message: str):
    """Handler for when a discord message is received from an agent."""
    await post_message(agent.config.channel_id, message)

@AgentProcess.on_hint_received
async def _on_agent_hint_received(agent: AgentProcess, recipient: int, item: pkts.NetworkItem):
    """Handler for when a hint is received from an agent."""
    await post_message(agent.config.channel_id, f"**[HINT]**: `{recipient}'s` **{item.item}** **_({item.flags})_** can be found at `{item.player}'s` **{item.location}** :eyes:")

@AgentProcess.on_item_received
async def _on_agent_item_received(agent: AgentProcess, recipient: int, items: Dict[int, int]):
    """Handler for when item(s) are received from an agent."""

    # Combine items and their counts
    item_string: str = ", ".join([ f"**{item} {f"_(x{count})_" if count > 1 else ""}**" for item, count in items.items() ])
    await post_message(agent.config.channel_id, f"`{recipient}` has just received their {item_string}")

@AgentProcess.on_status_received
async def _on_agent_status_received(agent: AgentProcess, message: str):
    """Handler for when the status is received from an agent."""
    await post_message(agent.config.channel_id, message)

async def post_message(channel_id: int, message: str):
    """Post a message to a discord channel."""
    global bot

    if (channel:= await bot.fetch_channel(channel_id)):
        await channel.send(message)
    else:
        logging.warning(f"Discord channel with ID {channel_id} could not be found.")

async def create_agent(config: RoomConfig) -> AgentProcess:
    """Create and start an agent process"""
    global agents

    logging.info(f"Creating agent... | Port {config.port}")

    agent = AgentProcess(config)
    agents[(config.guild_id, config.channel_id)] = agent

    # Start agent process
    await agent.start()

def generate_player_stats_embed(agent: AgentProcess, slot_id: int, stats: pkts.PlayerStats) -> discord.Embed:
    """Generate an embed for a stats command response."""

    embed = discord.Embed(
        color=discord.Color.red(),
        title=agent.get_player_name(slot_id),
        description=generate_player_stats_description(agent, stats)
    )
    
    # Add thumbnail as it can't be set in constructor
    embed.set_thumbnail(url="https://storage.ficsit.app/file/smr-prod-s3/images/mods/9mg7TSpp5gB6jU/logo.webp")

    return embed

def generate_player_stats_description(agent: AgentProcess, stats: pkts.PlayerStats) -> str:
    """Generate the description string for a player stats embed."""

    # Calculate totals and percentages
    total: int = stats.checked + stats.remaining
    itm_perc: int = math.floor((stats.received / total) * 100)
    loc_perc: int = math.floor((stats.checked / total) * 100)
    
    return (
        f"**Items**: {stats.received}/{total} _({itm_perc}%)_\n"
        f"**Locations**: {stats.checked}/{total} _({loc_perc}%)_\n"
        f"**Goaled**: {"Yes" if stats.goal else "No"}"
    )

def generate_session_stats_embed(agent: AgentProcess, stats: pkts.SessionStats) -> discord.Embed:
    """Generate an embed for a session stats command response"""

    embed = discord.Embed(
        color=discord.Color.red(),
        title="Session",
        description=generate_session_stats_description(agent, stats)
    )
    
    # Add thumbnail as it can't be set in constructor
    embed.set_thumbnail(url="https://storage.ficsit.app/file/smr-prod-s3/images/mods/9mg7TSpp5gB6jU/logo.webp")

    return embed

def generate_session_stats_description(agent: AgentProcess, stats: pkts.SessionStats) -> str:
    """Generate the description string for a session stats embed."""

    # Calculate totals and percentages
    players: int = agent.get_player_count()
    total: int = stats.checked + stats.remaining
    goal_perc: int = math.floor((stats.goals / players) * 100)
    loc_perc: int = math.floor((stats.checked / total) * 100)
    
    return (
        f"**Locations**: {stats.checked}/{total} _({loc_perc}%)_\n"
        f"**Goals**: {stats.goals}/{players} _({goal_perc}%)_"
    )

def get_agent(config: RoomConfig) -> Optional[AgentProcess]:
    """Get an agent process"""
    global agents
    return agents.get((config.guild_id, config.channel_id), None)

async def message_agent(agent: Agent, payload: str) -> bool:
    """Send a message to an agent process"""

    global agents

    logging.info(f"Attempting to send payload to Agent Process... | Guild ID: {agent.guild_id} | Channel ID: {agent.channel_id} | Port: {agent.port}")

    try:
        # Attempt to get agent process
        if not (process:= agents.get((agent.guild_id, agent.channel_id), None)):
            logging.warning(f"No agent process found for port {agent.port}")
            return

        # Send message
        process.stdin.write(f"{payload}\n".encode("utf-8"))
        await process.stdin.drain()

    except Exception as ex:
        logging.error(f"Error in message_agent(): {ex}")
        return False

    return True 


async def main() -> None:
    args = parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.loglevel.upper(), logging.INFO),
        format=f"[GATEWAY]  {'%(asctime)s\t' if args.logtime else ''}%(levelname)s:\t%(message)s",
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    # If no token provided
    if not args.token:
        raise SystemExit("No discord bot token provided. Set discord_gateway_options.token in host.yaml or pass --token command-line argument.")
    
    global admin_only
    
    # Set variables
    admin_only = args.admin_only

    # Connect to discord with token
    await bot.start(args.token)

#region Discord Bot Event Handlers

@bot.event
async def on_ready():
    """Event handler for when discord client has connected and is ready."""
    
    global agents
    
    logging.info(f"Connected to discord as {bot.user.name} ({bot.user.id})")
    logging.info(f"Syncing command tree...")

    await bot.tree.sync()

    logging.info("Starting agent(s)...")

    # Create agents for existing room configurations
    for config in store.configs.get_all_active():
        await create_agent(config)

@bot.tree.command(name="bind", description="Bind this channel to an Archipelago room.")
@app_commands.describe(port="The port number of the local archipelago room.", password="(Optional) Room password")
async def bind(interaction: discord.Interaction, port: int, password: str | None = None):
    """Command to bind a channel to a room."""

    global admin_only
    global agents
    global store

    logging.info(f"Binding requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id} | Port: {port}")
    
    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check user is an admin, if required
    if admin_only and not await interaction_is_admin(interaction):
        await interaction.followup.send("Only administrators can bind channels to rooms.", ephemeral=True)
        return
    
    # Check for existing binding
    if (room_config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is already bound to port `:{room_config.port}` - please unbind it first.", ephemeral=True)
        return

    # Attempt to create binding
    if not (room_config:= store.configs.bind(port, interaction.guild_id, interaction.channel_id)):
        await interaction.followup.send(f"Unable to bind {interaction.channel.jump_url} to port `:{port}` - please check that the port exists or wait a moment and try again.", ephemeral=True)
        return
    
    # Success response
    await interaction.followup.send(f"Successfully bound {interaction.channel.jump_url} to port `:{port}`!", ephemeral=True)
    
    # Start agent
    await create_agent(room_config)

@bot.tree.command(name="unbind", description="Unbind this channel from its Archipelago room.")
async def unbind(interaction: discord.Interaction):
    """Command to unbind a channel from a room."""

    global admin_only
    global store

    logging.info(f"Unbind requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")
    
    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check user is an admin, if required
    if admin_only and not await interaction_is_admin(interaction):
        await interaction.followup.send("Only administrators can unbind channels from rooms.", ephemeral=True)
        return
    
    # Check for existing binding
    if not (room_config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is not currently bound to a port.", ephemeral=True)
        return

    # Attempt to un-bind
    if not (room_config:= store.configs.unbind(room_config.port)):
        await interaction.followup.send(f"Unable to un-bind {interaction.channel.jump_url} from port `:{room_config.port}` - please wait a moment and try again.", ephemeral=True)
        return
    
    # Stop the process, if running
    if (agent:= get_agent(room_config)):
        agent.stop()
    
    # Success response
    await interaction.followup.send(f"The channel {interaction.channel.jump_url} has been successfully unbound from port `:{agent.port}`.", ephemeral=True)

@bot.tree.command(name="list", description="List all bound channels.")
async def _list(interaction: discord.Interaction):
    """Command to list all bound channels in the guild."""

    global store

    logging.info(f"List requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Get agent bindings for guild
    if not (room_configs:= store.configs.get_all_by_guild(interaction.guild_id)):
        await interaction.followup.send(f"No channels bound to ports could be found.", ephemeral=True)
        return
    
    # Compile response
    response: str = "This server has the following bound channel(s):"
    for config in room_configs:
        response += f"\n- <#{config.channel_id}> is bound to `{config.url}`\n"

    await interaction.followup.send(response, ephemeral=True)

@bot.tree.command(name="stats_session", description="List of players. E.g. Player1,Player2 etc.")
async def stats_session(interaction: discord.Interaction):
    """Command to list stats for a player."""

    global store

    logging.info(f"Session Stats requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check if binding exists
    if not (config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is not currently bound to a port.", ephemeral=True)
        return
    
    # Attempt to get process
    if not (agent:= get_agent(config)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is bound to a port but its process is not running.", ephemeral=True)
        return

    # Request stats
    response = await agent.request(pkts.StatisticsRequestPacket(
        id=uuid.uuid4().hex,
        slots=[],
        session=True
    ))

    # Validate stats
    if not response or not response.session:
        await interaction.followup.send("Failed to retrieve stats - please wait a moment and try again.", ephemeral=True)
        return

    # Respond with stats embeds
    await interaction.followup.send(
        embed=generate_session_stats_embed(agent, response.session),
        ephemeral=True
    )

@bot.tree.command(name="stats_players", description="Get statistics for a player or session.")
@app_commands.describe(players="List of players. E.g. Player1,Player2 etc.")
async def stats_players(interaction: discord.Interaction, players: str):
    """Command to list stats for a player."""

    global store

    logging.info(f"Player Stats requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check if binding exists
    if not (config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is not currently bound to a port.", ephemeral=True)
        return
    
    # Attempt to get process
    if not (agent:= get_agent(config)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is bound to a port but its process is not running.", ephemeral=True)
        return

    # Validate player names
    if not (names:= list(dict.fromkeys(player for player in players.strip().split(",") if player))):
        await interaction.followup.send(f"Please provide a list of comma-separated player names. _(E.g. `Player1,Player2,Player3`)_", ephemeral=True)
        return
    
    # Validate slots
    slots: Dict[str, int] = { name: agent.get_player_slot(name) for name in names }
    if (invalid_names:= [ name for name, id in slots.items() if not id ]):
        await interaction.followup.send(f"Could not find player(s) with name(s) {", ".join([f"`{inv_name}`" for inv_name in invalid_names])} - please check the names and try again.", ephemeral=True)
        return
    
    # Request stats
    response = await agent.request(pkts.StatisticsRequestPacket(
        id=uuid.uuid4().hex,
        slots=[slot_id for slot_id in slots.values()],
        session=False
    ))

    # Validate stats
    if not response or not response.slots:
        await interaction.followup.send("Failed to retrieve stats - please wait a moment and try again.", ephemeral=True)
        return

    # Respond with stats embeds
    await interaction.followup.send(
        embeds=[ generate_player_stats_embed(agent, slot, stats) for slot, stats in response.slots.items() ],
        ephemeral=True
    )

@bot.tree.command(name="status", description="Get the status of this channel, if bound to a room.")
async def status(interaction: discord.Interaction):
    """Command to check the status of a bound channel in the guild."""

    logging.info(f"Status requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    global store

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check if binding exists
    if not (config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is not currently bound to a port.", ephemeral=True)
        return

    # Attempt to get process
    if not (agent:= get_agent(config)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is bound to `:{config.port}` but its process is not running.", ephemeral=True)
        return
    
    # Request status from agent
    await agent.request(pkts.StatusRequestPacket(
        id=uuid.uuid4().hex
    ))

    # Respond with status
    await interaction.followup.send(f"{interaction.channel.jump_url} is currently `{agent.get_status()}`", ephemeral=True)

@bot.tree.command(name="notify_hints", description="Notify on hints received")
@app_commands.describe(finder="The finding player name", action="Action to perform", item_type="Notify for item type")
@app_commands.choices(
    action=[
        app_commands.Choice(name="Add", value=Action.ADD),
        app_commands.Choice(name="Remove", value=Action.REMOVE),
    ],
    item_type=[
        app_commands.Choice(name="Progression", value=ItemFlags.PROGRESSION),
        app_commands.Choice(name="Useful", value=ItemFlags.USEFUL),
        app_commands.Choice(name="Both", value=ItemFlags.PROGRESSION | ItemFlags.USEFUL)
    ]
)
async def notify_hints(interaction: discord.Interaction, finder: str, action: int, item_type: int):
    """Command to modify notifications for targeted hints."""

    global store

    logging.info(f"Notify Hints requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check if binding exists
    if not (config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is not currently bound to a port.", ephemeral=True)
        return
    
    # Attempt to get process
    if not (agent:= get_agent(config)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is bound to a port but its process is not running.", ephemeral=True)
        return
    
    # Check if player exists
    if not (slot_id:= agent.get_player_slot(finder)):
        await interaction.followup.send(f"No player found with name `{finder}` - please check the name and try again.", ephemeral=True)
        return

    # Request notification change and await response
    response: pkts.NotificationsResponsePacket = await agent.request(pkts.NotificationsRequestPacket(
        id=uuid.uuid4().hex,
        action=action,
        user_id=interaction.user.id,
        channel_id=interaction.channel_id,
        slot_id=slot_id,
        hints=item_type,
    ))

    # Validate response
    if not response or not response.success:
        await interaction.followup.send(f"Unable to set hint notification preferences - please wait a moment and try again.", ephemeral=True)
        return

    match action:
        case Action.ADD:
            await interaction.followup.send(f"You will now receive a {interaction.user.mention} when `{finder}` is the target of **Progression** hints.", ephemeral=True)

        case Action.REMOVE:
            await interaction.followup.send(f"You will no longer be mentioned when `{finder}` is the target for hints.", ephemeral=True)

@bot.tree.command(name="notify_items_terms", description="Notify on item terms received")
@app_commands.describe(recipient="Player receiving the item(s)", action="Action to perform", terms="E.g. Orb,Frame,Scraps etc.")
async def notify_items_terms(interaction: discord.Interaction, recipient: str, action: Literal["Add", "Remove", "Clear"], terms: Optional[str] = ""):
    """Command to modify notifications for received item terms."""

    logging.info(f"Notify Item Terms requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check if binding exists
    if not (config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is not currently bound to a port.", ephemeral=True)
        return
    
    # Attempt to get process
    if not (agent:= get_agent(config)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is bound to a port but its process is not running.", ephemeral=True)
        return
    
    # Check if player exists
    if not agent.player_exists(recipient):
        await interaction.followup.send(f"No player found with name `{recipient}` - please check the name and try again.", ephemeral=True)
        return
    
    # Split terms by ',' delimiter
    term_list: List[str] = [term.strip() for term in terms.split(",") if term]

    # Validate params
    if action in [ "Add", "Remove" ] and not terms or not term_list:
        await interaction.followup.send(f"Please provide a valid, comma-separated list of terms to {action.lower()}. _(E.g. `Frame,Orb,Scraps`)_ ", ephemeral=True)
        return
    
    match action:
        case "Add":
            # TODO: Actually implement this
            await interaction.followup.send(f"You will now receive a {interaction.user.mention} when `{recipient}` receives items containing the term(s) {", ".join([f"`{term}`" for term in term_list])}", ephemeral=True)

        case "Remove": 
            # TODO: Actually implement this
            await interaction.followup.send(f"You will no longer be mentioned when `{recipient}` receives items containing the term(s) `{", ".join([f"`{term}`" for term in term_list])}`.", ephemeral=True)

        case "Clear":
            # TODO: Actually implement this
            await interaction.followup.send(f"You will no longer be mentioned for any item terms for `{recipient}`.", ephemeral=True)

@bot.tree.command(name="notify_items_types", description="Notify on item types received")
@app_commands.describe(recipient="Player receiving the item(s)", action="Action to perform", type="Item type")
async def notify_items_types(interaction: discord.Interaction, recipient: str, action: Literal["Add", "Remove", "Clear"], type: Optional[Literal["Progression", "Useful", "Filler", "All"]] = ""):
    """Command to modify notifications for received item types."""

    logging.info(f"Notify Item Types requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check if binding exists
    if not (config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is not currently bound to a port.", ephemeral=True)
        return
    
    # Attempt to get process
    if not (agent:= get_agent(config)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is bound to a port but its process is not running.", ephemeral=True)
        return
    
    # Check if player exists
    if not agent.player_exists(recipient):
        await interaction.followup.send(f"No player found with name `{recipient}` - please check the name and try again.", ephemeral=True)
        return
    
    # Validate params
    if action in [ "Add", "Remove" ] and not type:
        await interaction.followup.send(f"Please provide an item type to {action.lower()}. _(E.g. `Useful`)_", ephemeral=True)
        return
    
    match action:
        case "Add":
            # TODO: Actually implement this
            await interaction.followup.send(f"You will now receive a {interaction.user.mention} when `{recipient}` receives '{type}' items.", ephemeral=True)

        case "Remove": 
            # TODO: Actually implement this
            await interaction.followup.send(f"You will no longer be mentioned when `{recipient}` receives `{type}` items.", ephemeral=True)

        case "Clear":
            # TODO: Actually implement this
            await interaction.followup.send(f"You will no longer be mentioned for any item types for `{recipient}`.", ephemeral=True)

#endregion

if __name__ == "__main__":
    asyncio.run(main())