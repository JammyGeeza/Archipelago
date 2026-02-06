import argparse
import asyncio
import logging
import websockets
import sys

from settings import get_settings

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
    while True:
        line = await asyncio.to_thread(sys.stdin.readline)

        if line == "":
            logging.info("stdin closed (EOF)")
            return
        
        logging.info(f"Received: {line.rstrip()}")

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
    await asyncio.create_task(read_stdin())

    # TODO: Also make this a task?
    async with websockets.connect(f"ws://localhost:{args.port}") as ws:
        async for msg in ws:
            logging.info(f"Received: {msg}")

if __name__ == "__main__":
    asyncio.run(main())
