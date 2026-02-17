#!/usr/bin/env python3

import argparse
import asyncio
import discord
import json
import logging
import sys

from discord import app_commands
from discord.ext import commands
from bot.Packets import DiscordMessagePacket, NetworkItem, TrackerPacket, StatusPacket
from bot.Store import Agent, Store, Room, RoomConfig
from bot.Utils import Hookable
from typing import Dict, List, Optional, Tuple

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
        self.status: str = "Stopped"

        self.rcv_queue: asyncio.Queue = asyncio.Queue()
        self.snd_queue: asyncio.Queue = asyncio.Queue()

    async def send(self, payload: str):
        """Send a payload to the agent process."""

        logging.info(f"Sending payload to agent process... | Port: {self.config.port}")
        logging.info(f"Payload: {payload}")

        self.process.stdin.write(f"{payload}\n".encode("utf-8"))
        await self.process.stdin.drain()

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
            # sys.executable,
            # "Agent.py",
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
        asyncio.create_task(self._watch())
        asyncio.create_task(self._read_stdout())
        asyncio.create_task(self._handle_packet())

    def stop(self):
        """Stop the agent process"""

        logging.info(f"Stopping agent process... | Port {self.config.port}")

        # Check process exists
        if not self.process:
            logging.warning(f"Agent process is not currently running | Port {self.config.port}")

        # Terminate process
        self.process.terminate()

    async def _handle_packet(self):
        """Handle a received packet from the agent process"""

        while True:
            if not (data:= await self.rcv_queue.get()):
                continue
            
            logging.info(f"Received payload from agent process | Port: {self.config.port} | Payload: {data}")

            # Convert to appropriate packet type
            await TrackerPacket.receive(data, self)

    # @HintMessagePacket.on_received
    # async def _on_hint_received(self, packet: HintMessagePacket):
    #     """Handler for receiving a hint message packet."""

    #     # Trigger event
    #     await self.on_hint_received.run(packet.recipient, packet.item)

    @DiscordMessagePacket.on_received
    async def _on_discord_message_received(self, packet: DiscordMessagePacket):
        """Handler for receiving a discord message packet."""

        # Trigger event
        await self.on_discord_message_received.run(packet.message)

    # @ItemMessagePacket.on_received
    # async def _on_item_received(self, packet: ItemMessagePacket):
    #     """Handler for receiving an item message packet."""

    #     # Trigger event
    #     await self.on_item_received.run(packet.recipient, packet.items)

    @StatusPacket.on_received
    async def _handle_status_packet(self, packet: StatusPacket):
        """Handle receipt of a status packet"""

        # Store status
        self.status = packet.status

        # Trigger event
        await self.on_status_received.run(packet.status)

    async def _read_stdout(self):
        """Listen for data received from the agent process."""

        if self.process.stdout is not None:
            async for line in self.process.stdout:
                payload = line.decode("utf-8", errors="replace").rstrip()

                # Convert from json
                for data in json.loads(payload):
                    await self.rcv_queue.put(data)


    async def _watch(self):
        """Watch the agent process and clean-up when terminated."""

        code = await self.process.wait()

        logging.warning(f"Agent process for port {self.config.port} exited with code {code}")

        # Clear process
        self.process = None
        self.status = "Stopped"

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

# async def _listen_agent_process(key: tuple[int, int], process: asyncio.subprocess.Process):
#     """Read the stdout of an agent process and handle incoming data."""
#     if process.stdout is not None:
#         async for line in process.stdout:
#             payload = line.decode("utf-8", errors="replace").rstrip()
#             logging.info(f"Received from Agent Process {key}: {payload}")

# async def _watch_agent_process(key: tuple[int, int], process: asyncio.subprocess.Process):
#     """Watch an agent and clean-up when it terminates."""
#     global agents
    
#     # Wait for process to finish
#     code = await process.wait()
#     logging.warning(f"Agent process {key} exited with code {code}")

#     # Remove
#     agents.pop(key)

def get_agent(guild_id: int, channel_id: int) -> Optional[AgentProcess]:
    """Get an agent process, if it exists."""
    global agents
    return agents.get((guild_id, channel_id), None)

# async def start_agent_process(agent: Agent, room: Room):
#     """Create and start an agent"""

#     global agents

#     logging.info(f"Starting Agent... | Port: {agent.port} | Password: {agent.password} | Multidata: {room.multidata} | Save Data: {room.savedata}")

#     # Create command-line arguments
#     args = [
#         sys.executable,
#         "DiscordAgent.py",
#         "--port", str(agent.port),
#         "--multidata", room.multidata,
#         "--savedata", room.savedata
#     ]

#     # Add password arg if provided
#     if agent.password:
#         args += ["--password", agent.password]

#     # Create agent process
#     process = await asyncio.create_subprocess_exec(
#         *args,
#         stdout=asyncio.subprocess.PIPE,
#         stdin=asyncio.subprocess.PIPE,
#     )

#     # Add process to agents list
#     key = (agent.guild_id, agent.channel_id)
#     agents[key] = process

#     # Start watchers/readers
#     asyncio.create_task(_watch_agent_process(key, process))
#     asyncio.create_task(_listen_agent_process(key, process))

# def stop_agent_process(agent: Agent):
#     global agents

#     # Get agent process
#     if not (process:= get_agent_process(agent)):
#         logging.warn(f"No Agent Process found | Guild ID: {agent.guild_id} | Channel ID: {agent.channel_id}")
#         return False

#     # Terminate the process
#     process.terminate()
    
#     return True

async def interaction_is_admin(interaction: discord.Interaction) -> bool:
    """Check if user is owner or administrator."""

    # Fetch guild information
    guild = await interaction.client.fetch_guild(interaction.guild_id)

    # Is user owner or administrator of the guild?
    return bool(
        guild.owner_id == interaction.user.id
        or interaction.user.guild_permissions.administrator
    )

# async def send_packet(agent: Agent, packet: TrackerPacket):
#     """Send a packet to an agent"""

#     global send_queue
#     await send_queue.put(())

@AgentProcess.on_discord_message_received
async def _on_agent_discord_message_received(agent: AgentProcess, message: str):
    """Handler for when a discord message is received from an agent."""
    await post_message(agent.config.channel_id, message)

@AgentProcess.on_hint_received
async def _on_agent_hint_received(agent: AgentProcess, recipient: int, item: NetworkItem):
    """Handler for when a hint is received from an agent."""
    await post_message(agent.config.channel_id, f"**[HINT]**: `{recipient}'s` **{item.item}** **_({item.flags})_** can be found at `{item.player}'s` **{item.location}** :eyes:")

@AgentProcess.on_item_received
async def _on_agent_item_received(agent: AgentProcess, recipient: int, items: Dict[int, int]):
    """Handler for when item(s) are received from an agent."""

    # Combine items and their counts
    item_string: str = ", ".join([ f"**{item} {f"_(x{count})_" if count > 1 else ""}**" for item, count in items.items() ])
    await post_message(agent.config.channel_id, f"`{recipient}` has just received their {item_string}")

@AgentProcess.on_status_received
async def _on_agent_status_received(agent: AgentProcess, status: str):
    """Handler for when the status is received from an agent."""
    await post_message(agent.config.channel_id, f"Client at Port `{agent.config.port}` has **{status.lower()}**.")

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
    
    # Check user is an admin, if required
    if admin_only and not await interaction_is_admin(interaction):
        await interaction.response.send_message("Only administrators can bind channels to rooms.", ephemeral=True)
        return
    
    # Check for existing binding
    if (room_config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.response.send_message(f"{interaction.channel.jump_url} is already bound to port `:{room_config.port}` - please unbind it first.", ephemeral=True)
        return

    # Attempt to create binding
    if not (room_config:= store.configs.bind(port, interaction.guild_id, interaction.channel_id)):
        await interaction.response.send_message(f"Unable to bind {interaction.channel.jump_url} to port `:{port}` - please check that the port exists or wait a moment and try again.", ephemeral=True)
        return
    
    # Success response
    await interaction.response.send_message(f"Successfully bound {interaction.channel.jump_url} to port `:{port}`!", ephemeral=True)
    
    # Start agent
    await create_agent(room_config)

@bot.tree.command(name="unbind", description="Unbind this channel from its Archipelago room.")
async def unbind(interaction: discord.Interaction):
    """Command to unbind a channel from a room."""

    global admin_only
    global store

    logging.info(f"Unbind requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")
    
    # Check user is an admin, if required
    if admin_only and not await interaction_is_admin(interaction):
        await interaction.response.send_message("Only administrators can unbind channels from rooms.", ephemeral=True)
        return
    
    # Check for existing binding
    if not (room_config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.response.send_message(f"{interaction.channel.jump_url} is not currently bound to a port.", ephemeral=True)
        return

    # Attempt to un-bind
    if not (room_config:= store.configs.unbind(room_config.port)):
        await interaction.response.send_message(f"Unable to un-bind {interaction.channel.jump_url} from port `:{room_config.port}` - please wait a moment and try again.", ephemeral=True)
        return
    
    # Stop the process, if running
    if (agent:= get_agent(room_config)):
        agent.stop()
    
    # Success response
    await interaction.response.send_message(f"The channel {interaction.channel.jump_url} has been successfully unbound from port `:{agent.port}`.", ephemeral=True)

@bot.tree.command(name="list", description="List all bound channels.")
async def list(interaction: discord.Interaction):
    """Command to list all bound channels in the guild."""

    global store

    logging.info(f"List requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Get agent bindings for guild
    if not (room_configs:= store.configs.get_all_by_guild(interaction.guild_id)):
        await interaction.response.send_message(f"No channels bound to ports could be found.", ephemeral=True)
        return
    
    # Compile response
    response: str = "This server has the following bound channel(s):"
    for config in room_configs:
        response += f"\n- <#{config.channel_id}> is bound to `{config.url}`\n"

    await interaction.response.send_message(response, ephemeral=True)

@bot.tree.command(name="status", description="Get the status of this channel, if bound to a room.")
async def status(interaction: discord.Interaction):
    """Command to check the status of a bound channel in the guild."""

    logging.info(f"Status requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    global store

    # Check if binding exists
    if not (config:= store.configs.get_by_channel(interaction.guild_id, interaction.channel_id)):
        await interaction.response.send_message(f"{interaction.channel.jump_url} is not currently bound to a port.", ephemeral=True)
        return

    # Attempt to get process
    if not (agent:= get_agent(config)):
        await interaction.response.send_message(f"{interaction.channel.jump_url} is bound to a port but its process is not running.", ephemeral=True)
        return
    
    # Send
    # TODO: Add to a sending queue
    await agent.send(StatusPacket("Gimme status pls").to_json())

    # Respond
    # TODO: Work out how to get the response before responding
    await interaction.response.send_message(f"Requesting status for {interaction.channel.jump_url} bound to port `:{agent.config.port}`...", ephemeral=True)

if __name__ == "__main__":
    asyncio.run(main())