#!/usr/bin/env python3

import argparse
import asyncio
import bot.Utils as utils
import discord
import json
import logging
import math
import sys
import uuid

from discord import app_commands
from discord.ext import commands
from bot.Store import Agent, Store
from typing import Dict, Optional

# Global variables
admin_only: bool = True
bot = commands.Bot(command_prefix='/', intents=discord.Intents.none())
store = Store()

class AgentProcess:

    on_discord_message_received = utils.Hookable()
    on_hint_received = utils.Hookable()
    on_item_received = utils.Hookable()
    on_status_received = utils.Hookable()
    on_stopped = utils.Hookable()

    def __init__(self, binding: utils.Binding):

        self.config: utils.RoomBinding = binding
        self.process: asyncio.subprocess.Process = None
        self.status: str = "Stopped"
        
        self.__player_lookup: dict[str, int] = {}               # Player Name-to-Id lookup
        self.__request_queue: dict[str, asyncio.Future] = {}    # Queue for requests awaiting a response

        self.rcv_queue: asyncio.Queue = asyncio.Queue()
        self.snd_queue: asyncio.Queue = asyncio.Queue()

    async def send(self, packet: utils.TrackerPacket):
        """Send a payload to the agent process."""
        logging.info(f"Sending {packet.cmd} to gateway...")
        await self.__send(packet.to_json())

    async def request(self, request: utils.IdentifiablePacket) -> utils.IdentifiablePacket:
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
            "--slot_name", self.config.slot_name,
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

    def stop(self):
        """Stop the agent process"""

        logging.info(f"Stopping agent process... | Port {self.config.port}")

        # Check process exists
        if not self.process:
            logging.warning(f"Agent process is not currently running | Port {self.config.port}")

        # Terminate process
        self.process.terminate()

    async def __handle_packet(self, packet: utils.TrackerPacket):
        """Handle a received packet from the agent process"""

        logging.info(f"Handling {packet.cmd} packet...")

        match packet.cmd:

            case utils.DiscordMessagePacket.cmd:
                await self.__handle_discordmessage_packet(packet)

            # case utils.StatusUpdatePacket.cmd:
            #     await self.__handle_statusupdate_packet(packet)

            case utils.ErrorPacket.cmd | utils.InvalidPacket.cmd:
                logging.warning(f"Received {packet.cmd} packet with message: '{packet.message}'")
                if packet.id:
                    await self.__handle_response_packet(packet)

            case utils.NotificationsResponsePacket.cmd | utils.StatisticsResponsePacket.cmd | utils.StatusResponsePacket.cmd:
                await self.__handle_response_packet(packet)

            # case utils.StoredStatsPacket.cmd:
            #     await self.__handle_storedstats_packet(packet)

            case utils.TrackerInfoPacket.cmd:
                await self.__handle_trackerinfo_packet(packet)

            case _:
                logging.warning(f"{packet.cmd} is an unhandled packet type.")

        # while True:
        #     if not (data:= await self.rcv_queue.get()):
        #         continue
            
        #     # Convert to appropriate packet type

        #     await utils.TrackerPacket.receive(data, self)

    async def __send(self, json: str):
        """Send data to the agent process."""
        self.process.stdin.write(f"{json}\n".encode("utf-8"))
        await self.process.stdin.drain()

    # @utils.DiscordMessagePacket.on_received
    async def __handle_discordmessage_packet(self, packet: utils.DiscordMessagePacket):
        """Handler for receiving a discord message packet."""

        logging.info(f"Received {packet.cmd} from :{self.config.port}")

        # Trigger event
        await self.on_discord_message_received.run(packet.message)

    # @utils.StatusUpdatePacket.on_received
    # async def __handle_statusupdate_packet(self, packet: utils.StatusUpdatePacket):
    #     """Handle receipt of a status packet"""
        
    #     logging.info(f"Received {packet.cmd} from :{self.config.port}")

    #     # Store status
    #     self.status = packet.status

    #     # Trigger event
    #     await self.on_status_received.run(packet.message)

    # @utils.StatisticsResponsePacket.on_received
    # @utils.StatusResponsePacket.on_received
    async def __handle_response_packet(self, packet: utils.IdentifiablePacket):
        """Handler for receiving a response packet"""

        logging.info(f"Received {packet.cmd} from :{self.config.port}")

        # If waiting for this response, set packet as result
        if (future:= self.__request_queue.get(packet.id)):
            future.set_result(packet)

    # @utils.StoredStatsPacket.on_received
    # async def __handle_storedstats_packet(self, packet: utils.StoredStatsPacket):
    #     """Handler for receiving stored stats."""

    #     # Update stored stats
    #     self.stats.update({ k: v for k, v in packet.stats.items() })

    async def __handle_trackerinfo_packet(self, packet: utils.TrackerInfoPacket):
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
                        utils.TrackerPacket.parse(data)
                    )

    async def __watch(self):
        """Watch the agent process and clean-up when terminated."""

        code = await self.process.wait()

        logging.warning(f"Agent process for port {self.config.port} exited with code {code}")

        # Clear process
        self.process = None
        self.status = "Stopped"

        # Trigger event
        await self.on_stopped.run(code)

    def get_player_count(self) -> int:
        """Get amount of players."""
        return len(self.__player_lookup.keys())

    def get_player_name(self, slot_id: int) -> str | None:
        """Get the name of a player by slot number"""
        return next((name for name, slot in self.__player_lookup.items() if slot == slot_id), None)

    def get_player_slot(self, player_name: str) -> int | None:
        """Get the slot number for a player by name (ignoring case)"""
        return next((slot for name, slot in self.__player_lookup.items() if player_name.casefold() == name.casefold()), None)

    def get_player_stats(self, player_name: str) -> utils.PlayerStats | None:
        """Get stats for a player."""
        return self.stats.get(player_name, None)

    def get_session_stats(self) -> utils.PlayerStats | None:
        """Returns stats for the entire session."""
        stats: utils.PlayerStats = utils.PlayerStats(
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

agents: Dict[int, AgentProcess] = {}

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

def get_agent(channel_id: int) -> Optional[AgentProcess]:
    """Get an agent process, if it exists."""
    global agents
    return agents.get(channel_id, None)

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
async def _on_agent_hint_received(agent: AgentProcess, recipient: int, item: utils.NetworkItem):
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

@AgentProcess.on_stopped
async def _on_agent_stopped(agent: AgentProcess, code: int):
    """Handler for when an agent process has stopped."""

    global agents

    # Remove agent from list
    agents[agent.config.channel_id] = None

    # Send message
    await post_message(agent.config.channel_id, f"The client at `:{agent.config.port}` has stopped.")

async def post_message(channel_id: int, message: str):
    """Post a message to a discord channel."""
    global bot

    if (channel:= await bot.fetch_channel(channel_id)):
        await channel.send(message)
    else:
        logging.warning(f"Discord channel with ID {channel_id} could not be found.")

async def create_agent(binding: utils.Binding) -> AgentProcess:
    """Create and start an agent process"""
    global agents

    logging.info(f"Creating agent... | Port: {binding.port}")

    agent = AgentProcess(binding)
    agents[binding.channel_id] = agent

    # Start agent process
    await agent.start()

def generate_player_stats_embed(agent: AgentProcess, slot_id: int, stats: utils.PlayerStats) -> discord.Embed:
    """Generate an embed for a stats command response."""

    embed = discord.Embed(
        color=discord.Color.red(),
        title=agent.get_player_name(slot_id),
        description=generate_player_stats_description(agent, stats)
    )
    
    # Add thumbnail as it can't be set in constructor
    embed.set_thumbnail(url="https://storage.ficsit.app/file/smr-prod-s3/images/mods/9mg7TSpp5gB6jU/logo.webp")

    return embed

def generate_player_stats_description(agent: AgentProcess, stats: utils.PlayerStats) -> str:
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

def generate_session_stats_embed(agent: AgentProcess, stats: utils.SessionStats) -> discord.Embed:
    """Generate an embed for a session stats command response"""

    embed = discord.Embed(
        color=discord.Color.red(),
        title="Session",
        description=generate_session_stats_description(agent, stats)
    )
    
    # Add thumbnail as it can't be set in constructor
    embed.set_thumbnail(url="https://storage.ficsit.app/file/smr-prod-s3/images/mods/9mg7TSpp5gB6jU/logo.webp")

    return embed

def generate_session_stats_description(agent: AgentProcess, stats: utils.SessionStats) -> str:
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

    # Sync the command tree
    await bot.tree.sync()

    # Create and start any existing, actively-bound agents
    if (active_bindings:= store.bindings.get_all()):
        logging.info(f"Starting {len(active_bindings)} bound agent(s)...")
        for binding in active_bindings:
            await create_agent(binding)

    logging.info(f"Ready!")

@bot.tree.command(name="bind", description="Bind this channel to an Archipelago room.")
@app_commands.describe(port="The port number of the local archipelago room.", password="(Optional) Room password")
async def bind(interaction: discord.Interaction, port: int, slot_name: str, password: str | None = None):
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
    
    # Check if an agent is already running for it
    if (agent:= get_agent(interaction.channel_id)) or (binding:= store.bindings.get_one(interaction.channel_id)):
        await interaction.followup.send(f"This channel is already bound to `:{agent.config.port}` - please use `/unbind` to unbind it first.", ephemeral=True)
        return

    # Attempt to create binding
    if not (new_binding:= store.bindings.upsert(utils.Binding(interaction.channel_id, interaction.guild_id, port, slot_name, password))):
        await interaction.followup.send(f"Unable to bind this channel to port `:{port}` - please wait a moment and try again.", ephemeral=True)
        return
    
    # Success response
    await interaction.followup.send(f"Successfully bound {interaction.channel.jump_url} to port `:{new_binding.port}` - please use `/connect` to connect a client.", ephemeral=True)

@bot.tree.command(name="connect", description="Connect to the archipelago session bound to this channel.")
async def connect(interaction: discord.Interaction):
    """Command to connect to archipelago session."""

    global store

    logging.info(f"Connect requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check if an agent is already running for it
    if (agent:= get_agent(interaction.channel_id)):

        # Get status
        response = await agent.request(utils.StatusRequestPacket(id=uuid.uuid4().hex))
        
        # Validate response
        if response.is_error():
            await interaction.followup.send(f"An unexpected error occurred: {response.message}", ephemeral=True)
        else:        
            await interaction.followup.send(f"The client for this channel is already running with status: `{response.status}`.", ephemeral=True)
        return

    # Check for existing binding
    if not (binding:= store.bindings.get_one(interaction.channel_id)):
        await interaction.followup.send(f"This channel is not currently bound to a port - please use `/bind` to bind it to a session.", ephemeral=True)
        return
    
    # Respond
    await interaction.followup.send(f"Starting client connection to `:{binding.port}` - this may take a moment.", ephemeral=True)
    
    # Create and start agent
    await create_agent(binding)

@bot.tree.command(name="disconnect", description="Disconnect from the archipelago session bound to this channel.")
async def disconnect(interaction: discord.Interaction):
    """Command to disconnect from the archipelago session."""

    global store

    logging.info(f"Disconnect requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check user is an admin, if required
    if admin_only and not await interaction_is_admin(interaction):
        await interaction.followup.send("Only administrators can disconnect clients.", ephemeral=True)
        return

    # Check if an agent is already running for it
    if not (agent:= get_agent(interaction.channel_id)):
        await interaction.followup.send(f"This channel does not currently have an active client.", ephemeral=True)
        return

    # Stop client
    agent.stop()

    # Respond
    await interaction.followup.send(f"Stopping the client at `:{agent.config.port}` - this may take a moment.", ephemeral=True)

@bot.tree.command(name="list", description="List all bound channels.")
async def _list(interaction: discord.Interaction):
    """Command to list all bound channels in the guild."""

    global store

    logging.info(f"List requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Get agent bindings for guild
    if not (room_configs:= store.bindings.get_all_for_guild(interaction.guild_id)):
        await interaction.followup.send(f"No channels are bound to any sessions - use the `/bind` command to bind one.", ephemeral=True)
        return
    
    # Compile response
    response: str = "This server has the following bindings:"
    for config in room_configs:
        response += f"\n- <#{config.channel_id}> is bound to `:{config.port}`\n"

    # Respond
    await interaction.followup.send(response, ephemeral=True)

@bot.tree.command(name="notify_hints", description="Notify on hints received")
@app_commands.describe(finder="The finding player name", action="Action to perform", item_type="Notify for item type")
@app_commands.choices(
    action=[
        app_commands.Choice(name="Add", value=utils.Action.ADD),
        app_commands.Choice(name="Remove", value=utils.Action.REMOVE),
    ],
    item_type=[
        app_commands.Choice(name="Progression", value=utils.NotifyFlags.PROGRESSION),
        app_commands.Choice(name="Useful", value=utils.NotifyFlags.USEFUL),
        app_commands.Choice(name="Both", value=utils.NotifyFlags.PROGRESSION | utils.NotifyFlags.USEFUL)
    ]
)
async def notify_hints(interaction: discord.Interaction, finder: str, action: int, item_type: int):
    """Command to modify notifications for targeted hints."""

    global store

    logging.info(f"Notify Hints requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check if binding exists
    if not (binding:= store.bindings.get_one(interaction.channel_id)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is not currently bound to a port.", ephemeral=True)
        return
    
    # Attempt to get process
    if not (agent:= get_agent(binding.channel_id)):
        await interaction.followup.send(f"{interaction.channel.jump_url} is bound to a port but its process is not running.", ephemeral=True)
        return

    # Request notification change and await response
    response: utils.NotificationsResponsePacket = await agent.request(utils.NotificationsRequestPacket(
        id=uuid.uuid4().hex,
        action=action,
        user_id=interaction.user.id,
        player=finder,
        hints=item_type,
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(f"Error setting hint preferences: '**_{response.message}_**'.", ephemeral=True)
        return
    
    # Respond with appropriate message
    if response.notification.hints == utils.NotifyFlags.NONE.value:
        await interaction.followup.send(f"You now have no hint notifications for `{finder}`.", ephemeral=True)
    else:
        await interaction.followup.send(f"You will now receive a {interaction.user.mention} when `{finder}` is the target of **{utils.NotifyFlags(response.notification.hints).to_text()}** item hints.", ephemeral=True)

@bot.tree.command(name="notify_terms", description="Notify on item terms received")
@app_commands.describe(recipient="Player receiving the item(s)", action="Action to perform", terms="E.g. Orb,Frame,Scraps etc.")
@app_commands.choices(
    action=[
        app_commands.Choice(name="Add", value=utils.Action.ADD),
        app_commands.Choice(name="Remove", value=utils.Action.REMOVE),
    ]
)
async def notify_terms(interaction: discord.Interaction, recipient: str, action: int, terms: str):
    """Command to modify notifications for received item terms."""

    logging.info(f"Notify Terms requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)
    
    # Validate arguments
    if not (term_list:= list(dict.fromkeys(term.strip() for term in terms.strip().split(",") if term and term.strip()))):
        await interaction.followup.send(f"Please provide a valid, comma-separated list of terms to {utils.Action(action).name.lower()}. _(E.g. `Frame,Orb,Scraps`)_ ", ephemeral=True)
        return

    # Attempt to get process
    if not (agent:= get_agent(interaction.channel_id)):
        await interaction.followup.send(f"No client is running for this channel - use `/connect` to start or `/bind` to bind it to a session.", ephemeral=True)
        return
    
    # Request notification change and await response
    response: utils.NotificationsResponsePacket = await agent.request(utils.NotificationsRequestPacket(
        id=uuid.uuid4().hex,
        action=action,
        user_id=interaction.user.id,
        player=recipient,
        terms=term_list
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(f"Error setting hint preferences: '**_{response.message}_**'.", ephemeral=True)
        return
    
    # Respond with appropriate message
    if not response.notification.terms:
        await interaction.followup.send(f"You now have no item term notifications for `{recipient}`.", ephemeral=True)
    else:
        await interaction.followup.send(f"You will now receive a {interaction.user.mention} when `{recipient}` receives items containing term(s): {", ".join([f"`{term}`" for term in response.notification.terms])}.", ephemeral=True)

@bot.tree.command(name="notify_types", description="Notify on item types received")
@app_commands.describe(recipient="Player receiving the item(s)", action="Action to perform", item_type="Type of item to notify")
@app_commands.choices(
    action=[
        app_commands.Choice(name="Add", value=utils.Action.ADD),
        app_commands.Choice(name="Remove", value=utils.Action.REMOVE),
    ],
    item_type=[
        app_commands.Choice(name="Progression", value=utils.NotifyFlags.PROGRESSION),
        app_commands.Choice(name="Useful", value=utils.NotifyFlags.USEFUL),
        app_commands.Choice(name="Trap", value=utils.NotifyFlags.TRAP),
        app_commands.Choice(name="Filler", value=utils.NotifyFlags.FILLER),
        app_commands.Choice(name="All", value=utils.NotifyFlags.PROGRESSION | utils.NotifyFlags.USEFUL | utils.NotifyFlags.TRAP | utils.NotifyFlags.FILLER)
    ]
)
async def notify_types(interaction: discord.Interaction, recipient: str, action: int, item_type: int):
    """Command to modify notifications for received item types."""

    logging.info(f"Notify Types requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Attempt to get process
    if not (agent:= get_agent(interaction.channel_id)):
        await interaction.followup.send(f"No client is running for this channel - use `/connect` to start or `/bind` to bind it to a session.", ephemeral=True)
        return
    
    # Request notification change and await response
    response: utils.NotificationsResponsePacket = await agent.request(utils.NotificationsRequestPacket(
        id=uuid.uuid4().hex,
        action=action,
        user_id=interaction.user.id,
        player=recipient,
        types=item_type
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(f"Error setting hint preferences: '**_{response.message}_**'.", ephemeral=True)
        return
    
    # Respond with appropriate message
    if response.notification.types == utils.NotifyFlags.NONE.value:
        await interaction.followup.send(f"You now have no item type notifications for `{recipient}`.", ephemeral=True)
    else:
        await interaction.followup.send(f"You will now receive a {interaction.user.mention} when `{recipient}` receives **{utils.NotifyFlags(response.notification.types).to_text()}** items.", ephemeral=True)

@bot.tree.command(name="stats_session", description="List of players. E.g. Player1,Player2 etc.")
async def stats_session(interaction: discord.Interaction):
    """Command to list stats for a player."""

    global store

    logging.info(f"Session Stats requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Attempt to get process
    if not (agent:= get_agent(interaction.channel_id)):
        await interaction.followup.send(f"No client is running for this channel - use `/connect` to start or `/bind` to bind it to a session.", ephemeral=True)
        return

    # Request stats
    response = await agent.request(utils.StatisticsRequestPacket(
        id=uuid.uuid4().hex,
        players=[],
        include_session=True
    ))

    # Validate stats
    if response.is_error() or not response.session:
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

    # Validate player input
    if not (names:= list(dict.fromkeys(player.strip() for player in players.strip().split(",") if player and player.strip()))):
        await interaction.followup.send(f"Please provide a list of comma-separated player names. _(E.g. `Player1,Player2,Player3`)_", ephemeral=True)
        return

    # Attempt to get process
    if not (agent:= get_agent(interaction.channel_id)):
        await interaction.followup.send(f"No client is running for this channel - use `/connect` to start or `/bind` to bind it to a session.", ephemeral=True)
        return
    
    # Request stats
    response = await agent.request(utils.StatisticsRequestPacket(
        id=uuid.uuid4().hex,
        players=names,
        include_session=False
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(f"Error retrieving player stats: '**_{response.message}_**'.", ephemeral=True)
        return
    elif not response.slots:
        await interaction.followup.send(f"Unable to retrieve player stats - please wait a moment and try again.", ephemeral=True)
        return

    # Respond with stats embed(s)   
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

    # Attempt to get process
    if not (agent:= get_agent(interaction.channel_id)):
        await interaction.followup.send(f"No client is running for this channel - use `/connect` to start or `/bind` to bind it to a session.", ephemeral=True)
        return
    
    # Request status from agent
    response = await agent.request(utils.StatusRequestPacket(
        id=uuid.uuid4().hex
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(f"Error retrieving current status: **_{response.message}_**", ephemeral=True)
        return

    # Respond with status
    await interaction.followup.send(f"The client bound to the session at `:{agent.config.port}` is currently `{response.status}`.", ephemeral=True)

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
    if not (binding:= store.bindings.get_one(interaction.channel_id)):
        await interaction.followup.send(f"This channel is not currently bound to a port.", ephemeral=True)
        return

    # Attempt to un-bind
    if not store.bindings.delete(binding):
        await interaction.followup.send(f"Unable to un-bind this channel from port `:{binding.port}` - please wait a moment and try again.", ephemeral=True)
        return
    
    # Stop the agent process, if running
    if (agent:= get_agent(binding.channel_id)):
        agent.stop()
    
    # Success response
    await interaction.followup.send(f"This channel has been successfully unbound from port `:{binding.port}`.", ephemeral=True)

#endregion

if __name__ == "__main__":
    asyncio.run(main())