import argparse
import asyncio
import json
import logging
import websockets
import sys
import threading

from settings import get_settings
from bot.Packets import TrackerPacket, ConnectPacket, ConnectedPacket, ConnectionRefusedPacket, HintMessagePacket, ItemMessagePacket, PrintJSONPacket, RoomInfoPacket, StatusPacket, NetworkItem, NetworkVersion
from bot.Utils import Hookable
from typing import List, Optional
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

class StdClient:

    def __init__(self):
        self.__attempt: int = 0
        self.__attempt_timeouts: List[int] = [ 5, 10, 15 ]
        self.__run: bool = False
        self.__send_queue: asyncio.Queue = asyncio.Queue()
        self.__tasks: List[asyncio.Task] = []

    def __can_retry(self) -> bool:
        """Can the client retry?"""
        return self.__attempt <= len(self.__attempt_timeouts)

    def __get_next_timeout(self) -> int:
        """Get the next timeout duration."""
        return self.__attempt_timeouts[self.__attempt - 1] if self.__attempt < len(self.__attempt_timeouts) else self.__attempt_timeouts[-1]

    async def __read_loop(self):
        """Read data from the stdin pipe."""
        loop = asyncio.get_running_loop()
        queue = asyncio.Queue()

        def reader():
            while True:
                line = sys.stdin.readline()
                loop.call_soon_threadsafe(queue.put_nowait, line)

        # Run reader() in daemon thread to prevent readline() from keeping the process alive on task cancel
        threading.Thread(target=reader, daemon=True).start()

        try:
            while self.__run:
                line = await queue.get()

                if line == "":
                    raise Exception("The stdin pipe has closed (EOF).")
                
                logging.info(f"Data received from stdin: {line.rstrip()}")
                
        except asyncio.CancelledError:
            logging.warning("The std client __read_loop() task has been cancelled.")
            raise

        except Exception as ex:
            logging.error(f"Unexpected error in std client __read_loop() task: '{ex}'")

    async def __stop_tasks(self):
        """Stop all running tasks"""
        logging.info("Stopping all std client tasks...")

        # Cancel all tasks
        for task in self.__tasks:
            task.cancel()

    async def __write_loop(self):
        """Write data to the stdout pipe."""

        try:
            while self.__run:

                packet: TrackerPacket = await self.__send_queue.get()

                # Skip if empty
                if not packet:
                    continue

                sys.stdout.write(f"{packet.to_json()}\n")
                sys.stdout.flush()

        except asyncio.CancelledError:
            logging.warning("The std client __write_loop() task has been cancelled.")
            raise

        except Exception as ex:
            logging.error(f"Unexpected error in std client __write_loop() task: '{ex}'")

    async def send(self, packet: TrackerPacket):
        """Send a packet to the stdout pipe"""
        await self.__send_queue.put(packet)

    async def start(self):
        """Start the std client connection"""

        logging.info("Starting std client...")

        # Exit if already running
        if self.__run:
            logging.info("The std client is already running.")
            return

        # Set starting variables
        self.__attempt = 0
        self.__run = True

        try:
            while self.__run:
                logging.info("Attempting to connect to stdin/stdoud...")

                # Gather and start asynchronous tasks, stopping when either of them finish
                self.__tasks = [
                    asyncio.create_task(self.__read_loop()),
                    asyncio.create_task(self.__write_loop()),
                ]
                complete, pending = await asyncio.wait(self.__tasks, return_when=asyncio.FIRST_COMPLETED)

                # Cancel any pending tasks
                for task in pending:
                    task.cancel()

                # Await cancel completion
                await asyncio.gather(*pending, return_exceptions=True)

                logging.info("Stdin/Stdout connections have closed.")

                # Prepare for retry
                self.__attempt += 1
                self.__tasks = []

                # Exit if retry limit exceeded
                if not self.__can_retry():
                    logging.warning(f"Std connection retry limit has been reached.")
                    return
                
                logging.info("Waiting to retry stdin/stdout connection...")
                
                # Wait before retry
                await asyncio.sleep(self.__get_next_timeout())

        except asyncio.CancelledError:
            logging.warning("The std client start() task has been cancelled.")
            raise

        except Exception as ex:
            logging.error(f"Unexpected error in std client start() task: '{ex}'")

        finally:
            # Task cleanup
            for task in self.__tasks:
                task.cancel()

            # Wait for task cancellation
            await asyncio.gather(*self.__tasks, return_exceptions=True)

            self.__tasks = []

    def stop(self):
        """Stop the std client connection"""
        logging.info("Stopping std client...")

        # Stop all running tasks
        self.__stop_tasks()

        # Prevent further re-runs
        self.__run = False

class TrackerClient:
    
    # Hookable methods
    on_connected = Hookable()
    on_connection_refused = Hookable()
    on_disconnected = Hookable()
    on_error = Hookable()
    on_hint_received = Hookable()
    on_item_received = Hookable()

    def __init__(self, args):

        self.__attempt: int = 0                                         # Current connection attempt
        self.__attempt_timeouts: List[int] = [ 5, 15, 30, 60, 300 ]     # Duration(s) to wait between connection attempts
        self.__running: bool = False                                    # Is currently running
        self.__status: str = "Disconnected"                             # Current status
        self.__tasks: List[asyncio.Task] = []                           # Asynchronous tasks
        self.__websocket: websockets.WebSocketClientProtocol = None     # Websocket client

        self.port: int = args.port
        self.multidata_path: str = args.multidata
        self.savedata_path: str = args.savedata
        self.password: Optional[str] = args.password

    def __can_retry(self) -> bool:
        """Check if the client can attempt a retry."""
        return self.__attempt <= len(self.__attempt_timeouts)

    def __get_next_timeout(self) -> int:
        """Get next attempt timeout duration (in seconds)"""
        return self.__attempt_timeouts[self.__attempt - 1] if self.__attempt < len(self.__attempt_timeouts) else self.__attempt_timeouts[-1]
    
    async def __handle_data(self, data: str):
        """Handle incoming data"""
        logging.info(f"Data received: '{data}'")

    async def __listen_loop(self):
        """Listen to the websocket for incoming data."""

        try:
            # Continue reading while
            while self.__running:
                payload = await self.__websocket.recv()

                logging.info(f"Payload received: {payload}")

                for packet in json.loads(payload):
                    await TrackerPacket.receive(packet, self)

        except asyncio.CancelledError:
            logging.warning(f"The tracker client __listen_loop() task has been cancelled.")
            raise

        except ConnectionClosed as ccex:
            logging.warning(f"The tracker client connection has been closed.")

        except Exception as ex:
            logging.error(f"Unexpected error in tracker client __listen_loop() task: '{ex}'")

    async def __send_packet(self, packet: TrackerPacket):
        """Send a packet to the websocket server"""
        json = packet.to_json()
        logging.info(f"Sending payload: {json}")
        await self.__websocket.send(json)

    def __stop_tasks(self):
        """Stop all running tasks"""

        logging.info("Attempting to cancel all tasks...")

        # Check if any tasks to cancel
        if len(self.__tasks) == 0:
            logging.warning("No current tasks to be cancelled.")
            return

        # Cancel all tasks
        for task in self.__tasks:
            task.cancel()

    async def get_status(self) -> str:
        """Get current status."""
        return self.__status

    @ConnectedPacket.on_received
    async def __on_connected_packet(self, packet: ConnectedPacket):
        """Handler for when a Connected packet is received."""
        logging.info(f"Connected packet received!")

        # Reset connect attempt count
        self.__attempt = 0

        # Trigger event
        await self.on_connected.run()

    @ConnectionRefusedPacket.on_received
    async def __on_connection_refused_packet(self, packet: ConnectionRefusedPacket):
        """Handler for when a ConnectionRefused packet is received."""
        logging.info(f"ConnectionRefused packet received!")

        # Trigger event
        await self.on_connection_refused.run(packet.errors)

        # Disconnect
        await self.__websocket.close(reason=f"Connection refused by server for reason(s): {", ".join(packet.errors)}")
    
    @PrintJSONPacket.on_received
    async def __on_printjson_packet(self, packet: PrintJSONPacket):
        """Handler for when a PrintJSON packet is received."""
        logging.info(f"PrintJSON ({packet.type}) packet received!")

        match packet.type:
            case "ItemSend":
                # Trigger item event
                await self.on_item_received.run(packet.receiving, packet.item)
            case "Hint":
                # Trigger hint event
                await self.on_hint_received.run(packet.receiving, packet.item)
            case _:
                logging.info(f"PrintJSON packet was a generic message type.")


    @RoomInfoPacket.on_received
    async def __on_room_info_packet(self, packet: RoomInfoPacket):
        """Handler for when a RoomInfo packet is received."""
        # Send connection packet
        connect_packet = ConnectPacket(
            game="",
            items_handling=0b0001,
            name="Botipelago",
            password=self.password,
            slot_data=False,
            tags=["Bot", "Deathlink", "Tracker"],
            uuid=f"botipelago_spectator",
            version=NetworkVersion(
                major=0,
                minor=6,
                build=4
            )
        )
        await self.__send_packet(connect_packet)

    async def start(self):
        """Start the tracker client connection"""

        logging.info(f"Starting tracker client... | Port: {self.port}")

        # Bail if already running
        if (self.__running):
            logging.info(f"Tracker Client is already running")
            return
        
        # Set as running
        self.__attempt = 0
        self.__running = True
        self.__status = "Connecting"

        try:

            while self.__running:

                # Attempt to connect
                try:
                    async with connect(f"ws://localhost:{self.port}") as self.__websocket:
                        logging.info(f"Connection to websocket established.")

                        # Set connected variables
                        # self.__attempt = 0
                        # self.__status = "Connected"

                        # Trigger event
                        # await self.on_connected.run(self)

                        # Create and run all asynchronous task(s), stopping when any of them complete
                        self.__tasks = [
                            asyncio.create_task(self.__listen_loop()),
                        ]
                        completed, pending = await asyncio.wait(self.__tasks, return_when=asyncio.FIRST_COMPLETED)

                        # Cancel pending tasks
                        for task in pending:
                            task.cancel()

                        # Await cancel completion
                        await asyncio.gather(*pending, return_exceptions=True)

                except ConnectionRefusedError as crex:
                    logging.warning(f"Connection to the tracker client websocket was refused.")

                except Exception as ex:
                    logging.error(f"Unexpected error occurred in tracker client start() task: {ex}")

                logging.warning("Tracker client task(s) have ended.")

                # Trigger event
                await self.on_disconnected.run()

                # Prepare for retry
                self.__attempt += 1
                self.__status = "Disconnected"
                self.__tasks = []
                self.__websocket = None

                # Exit if retry limit reached
                if not self.__can_retry():
                    logging.warning("Tracker client retry limit has been reached.")
                    return

                logging.warning("Waiting to retry tracker connection...")

                # Wait for timeout before retrying
                await asyncio.sleep(self.__get_next_timeout())

        except asyncio.CancelledError:
            logging.warning("The tracker client start() task has been cancelled.")
            raise

        except Exception as ex:
            logging.warning(f"Unexpected error in tracker client start() task: {ex}")


    def stop(self):
        """Stop the tracker client"""

        logging.info("Stopping tracker client...")

        # Abandon if already stopped
        if not self.__running:
            logging.warning("Tracker Client is already stopped.")
            return

        # Cancel all tasks
        self.__stop_tasks()

        # Stop from further running
        self.__running = False

handlers = {}
receive_queue: asyncio.Queue = asyncio.Queue()
send_queue: asyncio.Queue = asyncio.Queue()
websocket: websockets.WebSocketClientProtocol = None

# Retry timeouts
retry_attempt: int = 0
retry_timeouts: List[int] = [ 5, 15, 60, 300, 900 ]

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""

    defaults = get_settings().discord_agent_options.as_dict()

    parser = argparse.ArgumentParser(prog="Tracker Client.py", description="Archipelago Discord Tracker Client")
    parser.add_argument("--port", type=int, help="The full URL to the archipelago session.")
    parser.add_argument("--password", type=str, help="The password for the server or slot.")
    parser.add_argument("--multidata", type=str, help="The path to the multidata file.")
    parser.add_argument("--savedata", type=str, help="The path to the save data file.")
    parser.add_argument("--loglevel", default=defaults["loglevel"], type=str)
    parser.add_argument("--logtime", default=defaults["logtime"], type=bool)

    args = parser.parse_args()
    return args

async def update_status(status: str):
    """Send a status update to the gateway"""
    await send_packet_to_gateway(StatusPacket(status))

async def send_packet_to_gateway(packet: TrackerPacket):
    """Queue a packet for sending to the gateway."""
    global send_queue
    await send_queue.put(packet)

def get_retry_timeout():
    """Get the timeout duration"""
    global retry_attempt, retry_timeouts
    return retry_timeouts[retry_attempt] if retry_attempt < len(retry_timeouts) else retry_timeouts[-1]

@TrackerClient.on_connected
async def on_tracker_client_connected(client):
    """Handler for the tracker client connecting to the archipelago server."""

    logging.info("Connected event!")

    global __std_client

    # Create and send packet
    status_packet = StatusPacket(
        status="Connected"
    )
    await __std_client.send(status_packet)


@TrackerClient.on_disconnected
async def on_tracker_client_disconnected(client):
    """Handler for the tracker client disconnecting from the archipelago server."""

    logging.info("Disconnected event!")

    global __std_client

    # Create and send packet
    status_packet = StatusPacket(
        status="Disconnected"
    )
    await __std_client.send(status_packet)

@TrackerClient.on_error
async def on_tracker_client_error(client, msg: str):
    """Handler for the tracker client experiencing an error."""

    logging.info(f"Error event! Message: {msg}")

    # TODO: Forward status to the gateway?

@TrackerClient.on_hint_received
async def on_tracker_client_hint(client, receiver: int, item: NetworkItem):
    """"""

    logging.info(f"The player {item.player} needs {item.player} to complete {item.location} for their {item.item} (with flag(s) {item.flags}) ")

    # Create and send hint packet to gateway
    hint_packet = HintMessagePacket(
        recipient=receiver,
        item=item
    )
    await __std_client.send(hint_packet)

@TrackerClient.on_item_received
async def on_tracker_client_item_received(client, receiver: int, item: NetworkItem):
    """Handler for an item being received."""

    logging.info(f"The player {receiver} has received their {item.item} with flag(s) {item.flags}")

    # TODO: 'Combine' items as per previous bot before forwarding.

    # Create and send item packet to gateway
    item_packet = ItemMessagePacket(
        recipient=receiver,
        items={ item.item: 1 }
    )
    await __std_client.send(item_packet)

__std_client: StdClient = None
__tasks: List[asyncio.Task] = []
__tracker_client: TrackerClient = None

async def main() -> None:

    global __std_client
    global __tasks
    global __tracker_client

    args = parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.loglevel.upper(), logging.INFO),
        format=f"[AGENT]    {'%(asctime)s\t' if args.logtime else ''}%(levelname)s:\t%(message)s | Port: {args.port}",
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    # Just print the values
    logging.info(f"Starting tracker client process...")

    # Create new tracker client instance
    __std_client = StdClient()
    __tracker_client = TrackerClient(args)

    # Gather and start all asynchronous tasks, exiting when any task completes
    __tasks = [
        asyncio.create_task(__std_client.start()),
        asyncio.create_task(__tracker_client.start())
    ]
    complete, pending = await asyncio.wait(__tasks, return_when=asyncio.FIRST_COMPLETED)
    
    # Cancel any pending tasks
    for task in pending:
        task.cancel()

    await asyncio.gather(*pending, return_exceptions=True)

    logging.info(f"All running task(s) have ended.")

    # Exit
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
