#!/usr/bin/env python3

import argparse
import asyncio
import discord
import logging
import sys

from discord import app_commands
from discord.ext import commands
from DiscordGatewayStore import AgentBinding, Store
from typing import Dict, List, Tuple

# Global variables
admin_only: bool = True
agents: Dict[Tuple[int,int], asyncio.subprocess.Process]
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

async def interaction_is_admin(interaction: discord.Interaction) -> bool:
    """Check if user is owner or administrator."""

    # Fetch guild information
    guild = await interaction.client.fetch_guild(interaction.guild_id)

    # Is user owner or administrator of the guild?
    return bool(
        guild.owner_id == interaction.user.id
        or interaction.user.guild_permissions.administrator
    )

async def main() -> None:
    args = parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.loglevel.upper(), logging.INFO),
        format="[GATEWAY]\t%(levelname)s:\t%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
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
    
    await bot.tree.sync()
    logging.info(f"Command tree synced.")

@bot.tree.command(name="bind", description="Bind this channel to an Archipelago room.")
@app_commands.describe(url="Full url to the archipelago session.", password="(Optional) Room password")
async def bind(interaction: discord.Interaction, url: str, password: str | None = None):
    """Command to bind a channel to a room."""

    global admin_only
    global store

    logging.info(f"Binding requested for Guild: {interaction.guild.name} ({interaction.guild_id}) | Channel: {interaction.channel.name} ({interaction.channel_id}) | Url: {url}")
    
    # Check user is an admin, if required
    if admin_only and not await interaction_is_admin(interaction):
        await interaction.response.send_message("Only administrators can bind channels to rooms.", ephemeral=True)
        return
    
    # Check if binding already exists
    if store.exists_agent_binding(interaction.guild_id, interaction.channel_id):
        await interaction.response.send_message(f"The channel {interaction.channel.jump_url} is already bound to a room - please unbind it first.", ephemeral=True)
        return
    
    # Create and add binding
    binding = AgentBinding(
        guild_id=interaction.guild_id,
        channel_id=interaction.channel_id,
        url=url,
        password=password
    )

    # Creation of binding failed 
    if not store.add_agent_binding(binding):
        await interaction.response.send_message(f"An error occurred when attempting to create a new binding - please wait a moment and try again.", ephemeral=True)
        return
    
    # TODO: Perform binding activities here
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "DiscordAgent.py",
        "--url", binding.url,
        "--password", password if password else "",
        "--save-dir", 
    )
    
    # Success response
    await interaction.response.send_message(f"Binding channel {interaction.channel.jump_url} to port `{url}`...", ephemeral=True)

@bot.tree.command(name="unbind", description="Unbind this channel from an Archipelago room.")
async def unbind(interaction: discord.Interaction):
    """Command to unbind a channel from a room."""

    global admin_only
    global store

    logging.info(f"Unbind requested for Guild: {interaction.guild.name} ({interaction.guild_id}) | Channel: {interaction.channel.name} ({interaction.channel_id})")
    
    # Check user is an admin, if required
    if admin_only and not await interaction_is_admin(interaction):
        await interaction.response.send_message("Only administrators can unbind channels from rooms.", ephemeral=True)
        return
    
    # Attempt to get existing binding
    agent_binding: AgentBinding = store.get_agent_binding(interaction.guild_id, interaction.channel_id)
    if not agent_binding:
        await interaction.response.send_message(f"The channel {interaction.channel.jump_url} is not currently bound to a room.", ephemeral=True)
        return

    # Attempt to delete binding
    if not store.delete_agent_binding(agent_binding.guild_id, agent_binding.channel_id):
        await interaction.response.send_message(f"An error occurred when attempting to remove the binding - please wait a moment and try again.", ephemeral=True)
        return
    
    # TODO: Perform un-binding activities here

    # Success response
    await interaction.response.send_message(f"The channel {interaction.channel.jump_url} has been successfully unbound from `{agent_binding.url}`.", ephemeral=True)

@bot.tree.command(name="list", description="List all bound channels.")
async def list(interaction: discord.Interaction):
    """Command to list all bound channels in the guild."""

    global store

    logging.info(f"List requested for Guild: {interaction.guild.name} ({interaction.guild_id}) | Channel: {interaction.channel.name} ({interaction.channel_id})")

    # Get agent bindings for guild
    agent_bindings: List[AgentBinding] = store.get_all_guild_agent_bindings(interaction.guild_id)
    if not agent_bindings or len(agent_bindings) == 0:
        await interaction.response.send_message(f"No channels bound to rooms could be found for this server.", ephemeral=True)
        return
    
    # Compile response
    response: str = "This server has the following bound channel(s):"
    for binding in agent_bindings:
        response += f"\n- <#{binding.channel_id}> is bound to `{binding.url}`\n"

    await interaction.response.send_message(response, ephemeral=True)

if __name__ == "__main__":
    asyncio.run(main())

