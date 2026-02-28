#!/usr/bin/env python3

import argparse
import asyncio
from . import BotUtils as utils
import discord
import json
import logging
import math
import sys
import uuid

from .BotUtils import format_error, format_port, format_port_slot, format_slot, split_at_separator
from .BotStore import init_db, Binding
from discord import app_commands
from discord.ext import commands
from pony.orm import IntegrityError, ObjectNotFound, TransactionIntegrityError
from typing import Dict, Optional

# Global variables
admin_only: bool = True
bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())

class AgentProcess:

    on_error = utils.Hookable()
    on_discord_message_received = utils.Hookable()
    on_hint_received = utils.Hookable()
    on_item_received = utils.Hookable()
    on_status_received = utils.Hookable()
    on_stopped = utils.Hookable()

    def __init__(self, binding: Binding):

        self.config: Binding = binding
        self.process: asyncio.subprocess.Process = None
        self.status: str = "Stopped"
        
        self.__player_lookup: dict[str, int] = {}               # Player Name-to-Id lookup
        self.__request_queue: dict[str, asyncio.Future] = {}    # Queue for requests awaiting a response

        self.rcv_queue: asyncio.Queue = asyncio.Queue()
        self.snd_queue: asyncio.Queue = asyncio.Queue()

    async def send(self, packet: utils.TrackerPacket):
        """Send a payload to the agent process."""
        logging.info(f"Sending {packet.cmd} to agent...")
        await self.__send(packet.to_json())

    async def request(self, request: utils.IdentifiablePacket) -> utils.IdentifiablePacket:
        """Request an action and await a response."""

        logging.info(f"Sending request... | Type: {request.cmd} | ID: {request.id}")

        future: asyncio.Future = asyncio.get_running_loop().create_future()
        self.__request_queue[request.id] = future

        # Send packet
        await self.send(request)

        # Wait for response, bail after 6 seconds
        result: utils.IdentifiablePacket = None
        try:
            async with asyncio.timeout(7):
                result = await future
        except TimeoutError:
            logging.warning(f"Request '{request.id}' timed out.")
            result = utils.ErrorPacket(
                id=request.id,
                original_cmd=request.cmd,
                text=f"Request to the tracker client timed out."
            )
        except Exception as ex:
            logging.error(f"Request '{request.id}' suffered an unexpected error: {ex}")
            result = utils.ErrorPacket(
                id=request.id,
                original_cmd=request.cmd,
                text=f"Request suffered an unexpected error: {ex}"
            )

        # Pop request from queue and return
        self.__request_queue.pop(request.id)
        return result

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
            "--channel_id", str(self.config.channel_id),
            "--port", str(self.config.port),
            "--slot_name", str(self.config.slot_name)
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

        try:
            if not packet or not hasattr(packet, "cmd"):
                logging.error(f"Unknown packet received, handling has been abandoned.")
                return

            logging.info(f"Handling {packet.cmd} packet...")

            match packet.cmd:

                case utils.DiscordMessagePacket.cmd:
                    await self.__handle_discordmessage_packet(packet)

                case utils.TrackerInfoPacket.cmd:
                    await self.__handle_trackerinfo_packet(packet)

                case _:
                    logging.warning(f"{packet.cmd} is an unhandled packet type.")

            # If it's a response packet, pass it through
            if hasattr(packet, "id"):
                await self.__handle_response_packet(packet)

        except Exception as ex:
            logging.error(f"Unexpected error handling {packet.cmd} packet: {ex}")
            await self.on_error.run(ex)

    async def __send(self, json: str):
        """Send data to the agent process."""
        self.process.stdin.write(f"{json}\n".encode("utf-8"))
        await self.process.stdin.drain()

    async def __handle_discordmessage_packet(self, packet: utils.DiscordMessagePacket):
        """Handler for receiving a discord message packet."""

        logging.info(f"Received {packet.cmd} from :{self.config.port}")

        # Trigger event
        await self.on_discord_message_received.run(packet.message)

    async def __handle_response_packet(self, packet: utils.IdentifiablePacket):
        """Handler for receiving a response packet"""

        logging.info(f"Received {packet.cmd} response from :{self.config.port} | ID: {packet.id}")

        # If waiting for this response, set packet as result
        if (future:= self.__request_queue.get(packet.id)):
            future.set_result(packet)

    async def __handle_trackerinfo_packet(self, packet: utils.TrackerInfoPacket):
        """Handle an incoming TrackerInfo packet"""

        # Update player lookup (and reverse to name-to-id)
        self.__player_lookup.update({ v: k for k, v in packet.players.items() })

    async def __read_stdout(self):
        """Listen for data received from the agent process."""

        try:
            # If none, bail out
            if self.process.stdout is None:
                raise Exception(f"stdout is 'None'")

            async for line in self.process.stdout:
                payload = line.decode("utf-8", errors="replace").rstrip()
                if not payload:
                    logging.warning("Payload was empty")
                    continue

                # Convert from json and handle
                for data in json.loads(payload):
                    await self.__handle_packet(
                        utils.TrackerPacket.parse(data)
                    )

        except asyncio.CancelledError:
            logging.warning("The std client __read_stdout() task has been cancelled.")
            raise

        except Exception as ex:
            logging.error(f"Unexpected error in std client __read_stdout() task: '{ex}'")

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
    from settings import get_bot_settings

    parser = argparse.ArgumentParser()
    defaults = get_bot_settings().gateway.as_dict()

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

@AgentProcess.on_error
async def _on_agent_error(agent: AgentProcess, message: str):
    """Handler for when the agent suffers an error"""
    await post_message(agent.config.channel_id, f"The client at `:{agent.config.port}` suffered an unexpected error: **_{message}_**")

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

async def create_agent(binding: Binding) -> AgentProcess:
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
        f"**Deaths**: {stats.deaths}\n"
        f"**Items**: {stats.received}/{total} _({itm_perc}%)_\n"
        f"**Locations**: {stats.checked}/{total} _({loc_perc}%)_\n"
        f"**Goaled**: {"Yes" if stats.goal else "No"}"
    )

def generate_notifications_text(agent: AgentProcess, notif: utils.Notification) -> str:
    """Generate a notifications view command response"""

    lines = [
        f"## Notifications for {format_slot(notif.slot_name)}",
        f"{generate_notifications_hint_text(agent, notif)}",
        f"{generate_notifications_type_text(agent, notif)}",
        f"{generate_notifications_term_text(agent, notif)}",
        f"{generate_notifications_count_text(agent, notif)}",
    ]

    return "\n\n".join(lines)

def generate_notifications_count_text(agent: AgentProcess, notif: utils.NotificationSettingsDTO):
    """Generate an item count notifications command response"""
    
    if not notif.counts:
        return f"You will not receive item count notifications for {format_slot(notif.slot_name)}"
    
    # Sort the list
    notif.counts.sort()
    
    lines = [ f"You will receive a mention when {format_slot(notif.slot_name)} receives:" ]
    lines += [ f"- **{amt}** of the **{name}** item" for name, amt in notif.counts ]
    return "\n".join(lines)

def generate_notifications_hint_text(agent: AgentProcess, notif: utils.NotificationSettingsDTO):
    """Generate a hint notifications command response"""

    if not notif.hint_flags:
        return f"You will not receive hint notifications for {format_slot(notif.slot_name)}"
    
    return f"You will receive a mention when a hint reveals **{utils.NotifyFlags(notif.hint_flags).to_text()}** items are in {format_slot(notif.slot_name)}'s world" \

def generate_notifications_term_text(agent: AgentProcess, notif: utils.NotificationSettingsDTO):
    """Generate an item term notifications command response"""
    
    if not notif.terms:
        return f"You will not receive item term notifications for {format_slot(notif.slot_name)}"

    # Sort the list
    notif.terms.sort()

    lines = [ f"You will receive a mention when {format_slot(notif.slot_name)} receives an item containing any of the terms:" ]
    lines += [f"- `{term}`" for term in notif.terms]
    return "\n".join(lines)
        

def generate_notifications_type_text(agent: AgentProcess, notif: utils.NotificationSettingsDTO):
    """Generate a item type notifications command response"""

    if not notif.item_flags:
        return f"You will not receive item type notifications for {format_slot(notif.slot_name)}"

    return f"You will receive a mention when {format_slot(notif.slot_name)} receives **{utils.NotifyFlags(notif.item_flags).to_text()}** items" \

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
        f"**Deaths**: {stats.deaths}\n"
        f"**Locations**: {stats.checked}/{total} _({loc_perc}%)_\n"
        f"**Goals**: {stats.goals}/{players} _({goal_perc}%)_"
    )

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

#region Discord Bot Commands / Events

async def validate_agent(interaction: discord.Interaction) -> AgentProcess:
    """Validate that a channel has an active agent."""

    if not (agent:= get_agent(interaction.channel_id)):
        await interaction.followup.send(f"This channel is currently `disconnected` - please `/connect` it first.", ephemeral=True)

    return agent

async def validate_binding(interaction: discord.Interaction) -> Binding | None:
    """Validate that a channel has an active binding."""

    if not (binding:= Binding.get_for_channel(interaction.channel_id)):
        await interaction.followup.send(f"This channel is not bound - please `/bind` it first.", ephemeral=True)

    return binding

#region 'Notify' group

notify_group = app_commands.Group(name="notify", description="Manage your notifications", guild_only=True)

@app_commands.describe(slot_name="The slot name")
@notify_group.command(name="clear", description="Clear your notifications for a slot")
async def notify_clear(interaction: discord.Interaction, slot_name: app_commands.Range[str, 1, 16]):
    """Command to clear notifications for a slot"""

    logging.info(f"Notify Clear requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Validate binding and agent exist
    if not (binding:= await validate_binding(interaction)) or not (agent:= await validate_agent(interaction)):
        return

    # Request notification change and await response
    response: utils.NotificationsResponsePacket = await agent.request(utils.NotificationsRequestPacket(
        id=uuid.uuid4().hex,
        action=utils.Action.CLEAR,
        user_id=interaction.user.id,
        player=slot_name
    ))

    # Respond appropriately
    if response.is_error():
        await interaction.followup.send(format_error("clearing notifications", response.text), ephemeral=True)
    else:    
        await interaction.followup.send(f"You have cleared all of your notifications for {format_slot(slot_name)}", ephemeral=True)

@app_commands.describe(action="Action to perform", slot_name="Slot name receiving the item", item_name="Full item name", times="Notify when received X times from now")
@app_commands.choices(
    action=[
        app_commands.Choice(name="Add", value=utils.Action.ADD),
        app_commands.Choice(name="Remove", value=utils.Action.REMOVE),
    ]
)
@notify_group.command(name="count", description="Notify on X of an item received")
async def notify_count(interaction: discord.Interaction, action: int, slot_name: app_commands.Range[str, 1, 16], item_name: app_commands.Range[str, 1, 100], times: app_commands.Range[int, 1, 2000]):
    """Command to modify notifications for received item counts."""

    logging.info(f"Notify Count requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Validate binding and agent exist
    if not (binding:= await validate_binding(interaction)) or not (agent:= await validate_agent(interaction)):
        return
    
    # Request notification change and await response
    response: utils.NotificationsResponsePacket = await agent.request(utils.NotificationsRequestPacket(
        id=uuid.uuid4().hex,
        action=action,
        user_id=interaction.user.id,
        player=slot_name,
        counts={ item_name: times }
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(format_error("setting count notification", response.text), ephemeral=True)
    else:
        for chunk in split_at_separator(generate_notifications_count_text(agent, response.notification), separator="\n"):
            await interaction.followup.send(chunk, ephemeral=True)

@app_commands.describe(action="Action to perform", slot_name="Slot name finding the item(s)", item_type="Notify when item type is hinted")
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
@notify_group.command(name="hints", description="Notify you for hinted items")
async def notify_hints(interaction: discord.Interaction, action: int, slot_name: app_commands.Range[str, 1, 16], item_type: int):
    """Command to modify notifications for targeted hints."""

    logging.info(f"Notify Hints requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Validate binding and agent exist
    if not (binding:= await validate_binding(interaction)) or not (agent:= await validate_agent(interaction)):
        return

    # Request notification change and await response
    response: utils.NotificationsResponsePacket = await agent.request(utils.NotificationsRequestPacket(
        id=uuid.uuid4().hex,
        action=action,
        user_id=interaction.user.id,
        player=slot_name,
        hints=item_type,
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(format_error("setting hint notifications", response.text), ephemeral=True)
    else:
        await interaction.followup.send(generate_notifications_hint_text(agent, response.notification), ephemeral=True)

@app_commands.describe(action="Action to perform", slot_name="Slot name receiving the item(s)", terms="Notify when item name contains term(s) E.g. Orb,Frame,Scraps")
@app_commands.choices(
    action=[
        app_commands.Choice(name="Add", value=utils.Action.ADD),
        app_commands.Choice(name="Remove", value=utils.Action.REMOVE),
    ]
)
@notify_group.command(name="terms", description="Notify you for items containing words")
async def notify_terms(interaction: discord.Interaction, action: int, slot_name: app_commands.Range[str, 1, 16], terms: str):
    """Command to modify notifications for received item terms."""

    logging.info(f"Notify Terms requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Validate binding and agent exist
    if not (binding:= await validate_binding(interaction)) or not (agent:= await validate_agent(interaction)):
        return
    
    # Validate arguments
    if not (term_list:= list(dict.fromkeys(term.strip() for term in terms.strip().split(",") if term and term.strip()))):
        await interaction.followup.send(f"Please provide a valid, comma-separated list of terms to {utils.Action(action).name.lower()}. _(E.g. `Frame,Orb,Scraps`)_ ", ephemeral=True)
        return
    
    # Request notification change and await response
    response: utils.NotificationsResponsePacket = await agent.request(utils.NotificationsRequestPacket(
        id=uuid.uuid4().hex,
        action=action,
        user_id=interaction.user.id,
        player=slot_name,
        terms=term_list
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(format_error("setting term notifications", response.text), ephemeral=True)
    else:
        for chunk in split_at_separator(generate_notifications_term_text(agent, response.notification), separator="\n"):
            await interaction.followup.send(chunk, ephemeral=True)

@app_commands.describe(action="Action to perform", slot_name="Slot name receiving the item(s)", item_type="Notify when item type is received")
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
@notify_group.command(name="types", description="Notify you for item types")
async def notify_types(interaction: discord.Interaction, action: int, slot_name: app_commands.Range[str, 1, 16], item_type: int):
    """Command to modify notifications for received item types."""

    logging.info(f"Notify Types requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Validate binding and agent exist
    if not (binding:= await validate_binding(interaction)) or not (agent:= await validate_agent(interaction)):
        return
    
    # Request notification change and await response
    response: utils.NotificationsResponsePacket = await agent.request(utils.NotificationsRequestPacket(
        id=uuid.uuid4().hex,
        action=action,
        user_id=interaction.user.id,
        player=slot_name,
        types=item_type
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(format_error("setting type notifications", response.text), ephemeral=True)
    else:
        await interaction.followup.send(generate_notifications_type_text(agent, response.notification), ephemeral=True)

@app_commands.describe(slot_name="Slot name for your notifications")
@notify_group.command(name="list", description="List your notifications for a slot")
async def notify_list(interaction: discord.Interaction, slot_name: app_commands.Range[str, 1, 16]):
    """Command to view notifications for a slot"""

    logging.info(f"Notify View requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Validate binding and agent exist
    if not (binding:= await validate_binding(interaction)) or not (agent:= await validate_agent(interaction)):
        return

    # Request notifications and await response
    response = await agent.request(utils.NotificationsRequestPacket(
        id=uuid.uuid4().hex,
        action=utils.Action.VIEW,
        user_id=interaction.user.id,
        player=slot_name
    ))

    # Respond appropriately
    if response.is_error() or not response.notification:
        await interaction.followup.send(format_error("retrieving notifications", response.text), ephemeral=True)
    else:
        for chunk in split_at_separator(generate_notifications_text(agent, response.notification), separator="\n"):
            await interaction.followup.send(chunk, ephemeral=True)

#endregion

#region 'Stats' group

stats_group = app_commands.Group(name="stats", description="See player and session statistics", guild_only=True)

@stats_group.command(name="session", description="See stats for the session")
async def view_session(interaction: discord.Interaction):
    """Command to list stats for a player."""

    logging.info(f"Session Stats requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Validate binding and agent exist
    if not (binding:= await validate_binding(interaction)) or not (agent:= await validate_agent(interaction)):
        return

    # Request stats
    response = await agent.request(utils.StatisticsRequestPacket(
        id=uuid.uuid4().hex,
        players=[],
        include_session=True
    ))

    # Validate stats
    if response.is_error() or not response.session:
        await interaction.followup.send(format_error("retrieving session stats", response.text), ephemeral=True)
    else:
        await interaction.followup.send(embed=generate_session_stats_embed(agent, response.session), ephemeral=True)

@app_commands.describe(slot_names="List of slot names - E.g. Player1,Player2 etc.")
@stats_group.command(name="players", description="See stats for specific players")
async def view_players(interaction: discord.Interaction, slot_names: str):
    """Command to list stats for a player."""

    logging.info(f"Player Stats requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Validate binding and agent exist
    if not (binding:= await validate_binding(interaction)) or not (agent:= await validate_agent(interaction)):
        return

    # Validate player input
    if not (names:= list(dict.fromkeys(player.strip() for player in slot_names.strip().split(",") if player and player.strip()))):
        await interaction.followup.send(f"Please provide a list of comma-separated player names. *(E.g. `Player1,Player2,Player3`)*", ephemeral=True)
        return
    
    # Request stats
    response = await agent.request(utils.StatisticsRequestPacket(
        id=uuid.uuid4().hex,
        players=names,
        include_session=False
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(format_error("retrieving player stats", response.text), ephemeral=True)
    elif not response.slots:
        await interaction.followup.send(f"Unable to retrieve player stats - please wait a moment and try again.", ephemeral=True)
    else:
        await interaction.followup.send(
            embeds=[ generate_player_stats_embed(agent, slot, stats) for slot, stats in response.slots.items() ],
            ephemeral=True
        )

#endregion

#region 'Other' commands

@app_commands.describe(port="The room's port number", slot_name="Slot name to connect as")
@bot.tree.command(name="bind", description="Bind this channel to a room")
async def bind(interaction: discord.Interaction, port: app_commands.Range[int, 1, 65535], slot_name: app_commands.Range[str, 1, 16], password: str | None = None):
    """Command to bind a channel to a room."""

    logging.info(f"Binding requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id} | Port: {port}")
    
    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check for existing binding
    if (binding:= Binding.get_for_channel(interaction.channel_id)):
        await interaction.followup.send(f"This channel is already bound to {format_port_slot(binding.port, binding.slot_name)} - please `/rebind` or `/unbind` it.", ephemeral=True)
        return
    
    # Attempt to create binding
    try:
        binding = Binding.create(interaction.guild_id, interaction.channel_id, port, slot_name, password)
    except (TransactionIntegrityError, IntegrityError):
        await interaction.followup.send(f"The {format_port_slot(port, slot_name)} combination is already bound to another channel - please `/rebind` or `/unbind` it first.", ephemeral=True)
    except Exception as ex:
        await interaction.followup.send(format_error("creating binding", ex), ephemeral=True)
    else:
        await interaction.followup.send(f"Successfully bound {interaction.channel.jump_url} to {format_port_slot(binding.port, binding.slot_name)} - use `/connect` to attempt connection.", ephemeral=True)

@app_commands.describe(command="Full command. E.g. /option hint_cost 10")
@bot.tree.command(name="cmd", description="Perform an admin server command")
async def cmd(interaction: discord.Interaction, command: str):
    """Command to perform a server command"""

    logging.info(f"Command requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")
    
    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Validate binding and agent exist
    if not (binding:= await validate_binding(interaction)) or not (agent:= await validate_agent(interaction)):
        return
    
    # Request command via agent
    response = await agent.request(utils.CommandRequestPacket(
        id=uuid.uuid4().hex,
        command=command
    ))
    
    # Validate response
    if response.is_error():
        await interaction.followup.send(format_error("performing command", response.text), ephemeral=True)
    elif not response.success:
        await interaction.followup.send(f"Command `{command}` failed - please see the server log for more information.", ephemeral=True)
    else:
        await interaction.followup.send(f"Command `{command}` was performed successfully.", ephemeral=True)

@app_commands.describe(port="The port number of the local archipelago room", slot_name="The name of the slot to connect to")
@bot.tree.command(name="rebind", description="Update this channel's current room binding")
async def rebind(interaction: discord.Interaction, port: app_commands.Range[int, 1, 65535], slot_name: app_commands.Range[str, 1, 16], password: str | None = None):
    """Command to re-bind a channel."""

    logging.info(f"Rebinding requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id} | Port: {port}")
    
    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    try:
        binding = Binding.update(interaction.channel_id, port, slot_name, password)
    except ObjectNotFound:
        await interaction.followup.send(f"This channel is not bound - please `/bind` it first.", ephemeral=True)
    except (TransactionIntegrityError, IntegrityError):
        await interaction.followup.send(f"The {format_port_slot(port, slot_name)} combination is already bound by another channel - please `/unbind` it first.", ephemeral=True)
    except Exception as ex:
        await interaction.followup.send(format_error("rebinding channel", ex), ephemeral=True)
    else:
        # Stop the agent process, if running
        if (agent:= get_agent(binding.channel_id)):
            agent.stop()
        
        # Success response
        await interaction.followup.send(f"Successfully re-bound {interaction.channel.jump_url} to {format_port_slot(binding.port, binding.slot_name)} - use `/connect` to re-connect the client.", ephemeral=True)

@bot.tree.command(name="unbind", description="Unbind this channel from a room")
async def unbind(interaction: discord.Interaction):
    """Command to unbind a channel from a room."""

    logging.info(f"Unbind requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")
    
    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Try to delete binding
    try:
        Binding.delete_for_channel(interaction.channel_id)
    except ObjectNotFound as ex:
        await interaction.followup.send(f"This channel is not currently bound.", ephemeral=True)
    except Exception as ex:
        logging.error(format_error(f"unbinding channel {interaction.channel_id}", ex))
        await interaction.followup.send(format_error("unbinding channel", ex), ephemeral=True)
    else:
        await interaction.followup.send(f"Successfully un-bound {interaction.channel.jump_url}", ephemeral=True)

@bot.tree.command(name="connect", description="Connect to the bound room")
async def connect(interaction: discord.Interaction):
    """Command to connect to archipelago session."""

    logging.info(f"Connect requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check for existing binding
    if not (binding:= Binding.get_for_channel(interaction.channel_id)):
        await interaction.followup.send(f"This channel is not bound - please `/bind` it first.", ephemeral=True)
        return

    # Check if an agent is already running for this channel
    if (agent:= get_agent(interaction.channel_id)):

        # Get status
        response = await agent.request(utils.StatusRequestPacket(id=uuid.uuid4().hex))
        
        # Validate response
        if response.is_error():
            await interaction.followup.send(format_error("connecting", response.text), ephemeral=True)
        else:
            await interaction.followup.send(f"This channel is already `{response.status}` to/from {format_port_slot(binding.port, binding.slot_name)}.", ephemeral=True)
        return

    # Respond
    await interaction.followup.send(f"Starting connection to {format_port_slot(binding.port, binding.slot_name)} - this may take a few moments.", ephemeral=True)
    
    # Create and start agent
    await create_agent(binding)

@bot.tree.command(name="disconnect", description="Disconnect from the bound room")
async def disconnect(interaction: discord.Interaction):
    """Command to disconnect from the archipelago session."""

    logging.info(f"Disconnect requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check for binding
    if not (binding:= Binding.get_for_channel(interaction.channel_id)):
        await interaction.followup.send(f"This channel is not currently bound - please `/bind` and `/connect` it first.", ephemeral=True)
        return

    # Check if an agent is already running for it
    if not (agent:= get_agent(interaction.channel_id)):
        await interaction.followup.send(f"This channel is already `disconnected` from {format_port_slot(binding.port, binding.slot_name)}.", ephemeral=True)
        return

    # Stop client
    agent.stop()

    # Respond
    await interaction.followup.send(f"Disconnecting from {format_port(agent.config.port)} / {format_port(agent.config.slot_name)} - this may take a few moments.", ephemeral=True)

@bot.tree.command(name="status", description="Check the status if this channel's room binding")
async def status(interaction: discord.Interaction):
    """Command to check the status of a bound channel in the guild."""

    logging.info(f"Status requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Check for binding
    if not (binding:= Binding.get_for_channel(interaction.channel_id)):
        await interaction.followup.send(f"This channel is not currently bound - please `/bind` it first.", ephemeral=True)
        return

    # Attempt to get process
    if not (agent:= get_agent(interaction.channel_id)):
        await interaction.followup.send(f"This channel is currently `disconnected` from {format_port_slot(binding.port, binding.slot_name)}.", ephemeral=True)
        return
    
    # Request status from agent
    response = await agent.request(utils.StatusRequestPacket(
        id=uuid.uuid4().hex
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(format_error("retrieving status", response.text), ephemeral=True)
        return

    # Respond with status
    await interaction.followup.send(f"This channel is currently `{response.status}` to/from {format_port(binding.port)} / {format_slot(binding.slot_name)}.", ephemeral=True)

@bot.tree.command(name="list", description="List all room bindings in this server")
async def list_all(interaction: discord.Interaction):
    """Command to list all bound channels in the guild."""

    logging.info(f"List requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Get bindings for guild
    bindings_text: str = "This server has the following bindings:\n"
    for binding in Binding.get_for_guild(interaction.guild_id):
        bindings_text += f"- <#{binding.channel_id}> is bound to {format_port_slot(binding.port, binding.slot_name)}\n"

    # Respond
    for chunk in split_at_separator(bindings_text, separator="\n"):
        await interaction.followup.send(chunk, ephemeral=True)

@app_commands.describe(slot_name="Slot name to hint for", item_name="Item to hint for", password="Password for slot")
@bot.tree.command(name="hint", description="Request a hint for an item")
async def hint(interaction: discord.Interaction, slot_name: app_commands.Range[str, 1, 16], item_name: str, password: Optional[str] = None):
    """Command to request a hint for a player."""

    logging.info(f"Hint requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Defer response
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Attempt to get process
    if not (agent:= get_agent(interaction.channel_id)):
        await interaction.followup.send(f"No client is running for this channel - use `/connect` to start or `/bind` to bind it to a session.", ephemeral=True)
        return
    
    # Request status from agent
    response = await agent.request(utils.HintRequestPacket(
        id=uuid.uuid4().hex,
        slot_name=slot_name,
        item_name=item_name,
        password=password
    ))

    # Validate response
    if response.is_error():
        await interaction.followup.send(f"Error requesting hint: **_{response.text}_**", ephemeral=True)
        return
    elif not response.success or not response.hints:
        await interaction.followup.send(f"Hint request responded with: **_{response.comment}_**.", ephemeral=True)
        return
    
    # Respond
    for chunk in split_at_separator(response.comment, separator="\n"):
        await interaction.followup.send(chunk, ephemeral=True)

async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle command errors."""

    logging.error(f"Unexpected command error: {error}")

    try:
        try:
            # Try normal response first
            await interaction.response.send_message(f"An unexpected error occurred - please wait a moment and try again.", ephemeral=True)

        except discord.InteractionResponded:
        
            # Then try as follow-up
            await interaction.followup.send(f"An unexpected error occurred - please wait a moment and try again.", ephemeral=True)
    
    except Exception as ex:
        logging.error(format_error("handling command error", ex))

#endregion

@bot.event
async def on_guild_channel_update(before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):

    # Ignore for any non-text channels
    if not isinstance(after, discord.TextChannel):
        return
    
    # Get permission changes
    before_perms = before.permissions_for(before.guild.default_role).send_messages
    after_perms = after.permissions_for(after.guild.default_role).send_messages

    # If permissions for @everyone send_messages changes to False, wipe binding
    if before_perms and not after_perms:

        # Get agent if running and stop it
        if (agent:= get_agent(before.id)):
            agent.stop()

        # Delete binding
        Binding.delete_for_channel(before.id)

@bot.event
async def on_thread_update(before: discord.Thread, after: discord.Thread):
    """Handle thread configuration updates"""

    logging.info(f"Thread {before.id} has changed.")

    # If thread becomes locked, wipe binding
    if not before.locked and after.locked:
        logging.info(f"Thread {before.id} has been locked.")

        # Get agent if running and stop it
        if (agent:= get_agent(before.id)):
            agent.stop()

        # Delete binding
        Binding.delete_for_channel(before.id)

@bot.event
async def on_ready():
    """Event handler for when discord client has connected and is ready."""
    
    global agents
    
    logging.info(f"Connected to discord as {bot.user.name} ({bot.user.id})")
    logging.info(f"Syncing command tree...")

    # Add command error event handler
    bot.tree.on_error = on_command_error

    # Add groups to tree and sync
    bot.tree.add_command(notify_group)
    bot.tree.add_command(stats_group)
    await bot.tree.sync()

    # Initialize db
    init_db()

    # Start existing agents from enabled bindings
    for binding in Binding.get_all_enabled():
        await create_agent(binding)

    logging.info(f"Ready!")

#endregion

if __name__ == "__main__":
    asyncio.run(main())