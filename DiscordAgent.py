import argparse
import asyncio
import json
import logging
import websockets
import sys

from settings import get_settings
from DiscordPackets import AgentPacket, StatusPacket
from typing import List

handlers = {}

receive_queue: asyncio.Queue = asyncio.Queue()
send_queue: asyncio.Queue = asyncio.Queue()

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""

    defaults = get_settings().discord_agent_options.as_dict()

    parser = argparse.ArgumentParser(prog="Agent.py", description="Archipelago Discord Agent")
    parser.add_argument("--port", type=int, help="The full URL to the archipelago session.")
    parser.add_argument("--password", type=str, help="The password for the server or slot.")
    parser.add_argument("--multidata", type=str, help="The path to the multidata file.")
    parser.add_argument("--savedata", type=str, help="The path to the save data file.")
    parser.add_argument("--loglevel", default=defaults["loglevel"], type=str)
    parser.add_argument("--logtime", default=defaults["logtime"], type=bool)

    args = parser.parse_args()
    return args

async def read_stdin():
    """Read data from the input."""

    global receive_queue

    while True:
        line = await asyncio.to_thread(sys.stdin.readline)

        if line == "":
            logging.info("stdin closed (EOF)")
            return
        
        await receive_queue.put(line.rstrip())

async def write_stdout():
    """Write data to the output."""

    global send_queue

    while True:

        packet: AgentPacket = await send_queue.get()

        if not packet:
            continue

        sys.stdout.write(f"{packet.to_json()}\n")
        sys.stdout.flush()

async def handle_packet():
    """Handle a received packet from the gateway"""

    global receive_queue

    while True:
        payload = await receive_queue.get()

        logging.info(f"Received payload from gateway")
        logging.info(f"Payload: {payload}")

        if not payload:
            continue
        
        await AgentPacket.receive(payload)

async def send_packet(packet: AgentPacket):
    """Queue a packet for sending to the gateway."""
    global send_queue
    await send_queue.put(packet)

@StatusPacket.on_received
async def handle_status_request(_ctx, status: StatusPacket):
    """Handle receiving a status request packet"""

    logging.info("Received status request packet")

    # TODO: Infer actual status
    await send_packet(
        StatusPacket("I'm all gucci, baby!")
    )

async def main() -> None:
    args = parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.loglevel.upper(), logging.INFO),
        format=f"[AGENT]    {'%(asctime)s\t' if args.logtime else ''}%(levelname)s:\t%(message)s",
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    # Just print the values
    logging.info(f"Agent Started | Port: {args.port} | Password: {args.password} | Multidata: {args.multidata} | Save Data: {args.savedata}")

    # Initiate stdin read loop
    asyncio.create_task(read_stdin())
    asyncio.create_task(write_stdout())
    asyncio.create_task(handle_packet())

    # TODO: Also make this a task?
    async with websockets.connect(f"ws://localhost:{args.port}") as ws:
        async for msg in ws:
            logging.info(f"Received: {msg}")

if __name__ == "__main__":
    asyncio.run(main())
