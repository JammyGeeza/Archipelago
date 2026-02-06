#!/usr/bin/env python3

import argparse
import asyncio
import discord
import logging
import sys

from discord import app_commands
from discord.ext import commands
from DiscordGatewayStore import Agent, Store, Room
from typing import Dict, List, Optional, Tuple

# Global variables
admin_only: bool = True
agents: Dict[Tuple[int,int], asyncio.subprocess.Process] = {}
bot = commands.Bot(command_prefix='/', intents=discord.Intents.none())
store = Store()

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

def delete_agent(agent: Agent) -> bool:
    global store
    return store.agents.delete(agent)

def get_agent(guild_id: int, channel_id: int) -> Optional[Agent]:
    global store
    return store.agents.get(guild_id, channel_id)

async def _listen_agent_process(key: tuple[int, int], process: asyncio.subprocess.Process):
    """Read the stdout of an agent process and handle incoming data."""
    if process.stdout is not None:
        async for line in process.stdout:
            payload = line.decode("utf-8", errors="replace").rstrip()
            logging.info(f"Received from Agent Process {key}: {payload}")

async def _watch_agent_process(key: tuple[int, int], process: asyncio.subprocess.Process):
    """Watch an agent and clean-up when it terminates."""
    global agents
    
    # Wait for process to finish
    code = await process.wait()
    logging.warning(f"Agent process {key} exited with code {code}")

    # Remove
    agents.pop(key)

def get_agent_process(agent: Agent) -> Optional[asyncio.subprocess.Process]:
    global agents
    return agents.get((agent.guild_id, agent.channel_id), None)

async def start_agent_process(agent: Agent, room: Room):
    """Create and start an agent"""

    global agents

    logging.info(f"Starting Agent... | Port: {agent.port} | Password: {agent.password} | Multidata: {room.multidata} | Save Data: {room.savedata}")

    # Create command-line arguments
    args = [
        sys.executable,
        "DiscordAgent.py",
        "--port", str(agent.port),
        "--multidata", room.multidata,
        "--savedata", room.savedata
    ]

    # Add password arg if provided
    if agent.password:
        args += ["--password", agent.password]

    # Create agent process
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )

    # Add process to agents list
    key = (agent.guild_id, agent.channel_id)
    agents[key] = process

    # Start watchers/readers
    asyncio.create_task(_watch_agent_process(key, process))
    asyncio.create_task(_listen_agent_process(key, process))

def stop_agent_process(agent: Agent):
    global agents

    # Get agent process
    if not (process:= get_agent_process(agent)):
        logging.warn(f"No Agent Process found | Guild ID: {agent.guild_id} | Channel ID: {agent.channel_id}")
        return False

    # Terminate the process
    process.terminate()
    
    return True

async def interaction_is_admin(interaction: discord.Interaction) -> bool:
    """Check if user is owner or administrator."""

    # Fetch guild information
    guild = await interaction.client.fetch_guild(interaction.guild_id)

    # Is user owner or administrator of the guild?
    return bool(
        guild.owner_id == interaction.user.id
        or interaction.user.guild_permissions.administrator
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

@bot.event
async def on_ready():
    """Event handler for when discord client has connected and is ready."""
    logging.info(f"Connected to discord as {bot.user.name} ({bot.user.id})")
    logging.info(f"Syncing command tree...")

    await bot.tree.sync()

    agent_list: List[Agent] = store.agents.get_all()
    logging.info(f"Starting {len(agent_list)} agent(s)...")

    for agent in agent_list:

        # Find room data for port
        if not (room:= store.rooms.get(agent.port)):
            logging.warning(f"Room data could not be found | Port: {agent.port}")
            continue

        # Start agent process
        asyncio.create_task(start_agent_process(agent, room))

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
    
    # Check if binding already exists
    if store.agents.exists(interaction.guild_id, interaction.channel_id):
        await interaction.response.send_message(f"The channel {interaction.channel.jump_url} is already bound to a room - please unbind it first.", ephemeral=True)
        return
    
    # Create and add binding
    agent = Agent(
        guild_id=interaction.guild_id,
        channel_id=interaction.channel_id,
        port=port,
        password=password
    )

    # Creation of binding failed 
    if not store.agents.upsert(agent):
        await interaction.response.send_message(f"An error occurred when attempting to create a new binding - please wait a moment and try again.", ephemeral=True)
        return
    
    # Get room data
    if not (room_data:= store.rooms.get(agent.port)):
        await interaction.response.send_message(f"Unable to find local room data for port `:{agent.port}`", ephemeral=True)
        return
    
    # Start agent
    asyncio.create_task(start_agent_process(agent, room_data))

    # Success response
    await interaction.response.send_message(f"Binding channel {interaction.channel.jump_url} to port `:{port}`...", ephemeral=True)

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
    
    # Attempt to get existing binding
    if not (agent:= get_agent(interaction.guild_id, interaction.channel_id)):
        await interaction.response.send_message(f"The channel {interaction.channel.jump_url} is not currently bound to a room.", ephemeral=True)
        return

    # Attempt to delete binding
    if not delete_agent(agent):
        await interaction.response.send_message(f"An error occurred when attempting to remove the binding - please wait a moment and try again.", ephemeral=True)
        return
    
    # Attempt to stop the process
    if not stop_agent_process(agent):
        await interaction.response.send_message(f"An error occurred when attempting to stop the tracker process.", ephemeral=True)
        return
    
    # Success response
    await interaction.response.send_message(f"The channel {interaction.channel.jump_url} has been successfully unbound from port `:{agent.port}`.", ephemeral=True)

@bot.tree.command(name="list", description="List all bound channels.")
async def list(interaction: discord.Interaction):
    """Command to list all bound channels in the guild."""

    global store

    logging.info(f"List requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    # Get agent bindings for guild
    agent_bindings: List[Agent] = store.agents.get_many(interaction.guild_id)
    if not agent_bindings or len(agent_bindings) == 0:
        await interaction.response.send_message(f"No channels bound to rooms could be found for this server.", ephemeral=True)
        return
    
    # Compile response
    response: str = "This server has the following bound channel(s):"
    for binding in agent_bindings:
        response += f"\n- <#{binding.channel_id}> is bound to `{binding.url}`\n"

    await interaction.response.send_message(response, ephemeral=True)

@bot.tree.command(name="status", description="Get the status of this channel, if bound to a room.")
async def status(interaction: discord.Interaction):
    """Command to check the status of a bound channel in the guild."""

    logging.info(f"Status requested... | Guild ID: {interaction.guild_id} | Channel ID: {interaction.channel_id}")

    global store

    # Check if binding exists
    if not (agent:= store.agents.get(interaction.guild_id, interaction.channel_id)):
        await interaction.response.send_message(f"The channel {interaction.channel.jump_url} has not been bound to a room.", ephemeral=True)
        return
    
    # TODO: Request status from agent process
    # Sending a message for now, just to test
    if not await message_agent(agent, "Status, please!"):
        await interaction.response.send_message(f"An error occurred when attempting to get the status - please wait a moment and try again.", ephemeral=True)
        return
    
    await interaction.response.send_message(f"Status for `:{agent.port}` is currently `[Connected/Disconnected]`", ephemeral=True)

if __name__ == "__main__":
    asyncio.run(main())