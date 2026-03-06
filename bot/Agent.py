import argparse
import asyncio
from . import BotUtils as utils
import json
import logging
import math
import sys
import threading
import uuid
import websockets

from .BotStore import (
    NotificationSettings, NotificationCount, NotificationTerm,
    init_db,
)
from .BotUtils import format_host_port_slot, split_at_separator
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

class StdClient:

    # Events
    on_cmd_request = utils.Hookable()
    on_error = utils.Hookable()
    on_hint_request = utils.Hookable()
    on_notifications_request = utils.Hookable()
    on_statistics_request = utils.Hookable()
    on_status_request = utils.Hookable()

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

    async def __handle_packet(self, packet: utils.TrackerPacket):
        """Handle an incoming packet"""
        
        try:
            # Bail if blank / unknown packet
            if not packet or not hasattr(packet, "cmd"):
                logging.error(f"Unknown packet received, handling has been abandoned.")
                return
            
            logging.info(f"Received {packet.cmd} from gateway.")

            match packet.cmd:

                case utils.CommandRequestPacket.cmd:
                    await self.on_cmd_request.run(packet)

                case utils.HintRequestPacket.cmd:
                    await self.on_hint_request.run(packet)

                case utils.NotificationsRequestPacket.cmd:
                    await self.on_notifications_request.run(packet)

                case utils.StatisticsRequestPacket.cmd:
                    await self.on_statistics_request.run(packet)

                case utils.StatusRequestPacket.cmd:
                    await self.on_status_request.run(packet)
                    
                case _:
                    logging.warning(f"{packet.cmd} is an unhandled packet type.")
        
        except Exception as ex:
            logging.error(f"Unexpected error handling {packet.cmd} packet: {ex}")

            await self.send(utils.ErrorPacket(
                id=packet.id or "",
                original_cmd=packet.cmd or "",
                text=f"{ex}"
            ))

        logging.info(f"Packet handling loop ended.")

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
                
                # Convert from json
                for data in json.loads(line):
                    await self.__handle_packet(
                        utils.TrackerPacket.parse(data)
                    )
                
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

                packet: utils.TrackerPacket = await self.__send_queue.get()

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

    async def send(self, packet: utils.TrackerPacket):
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
    on_collect = utils.Hookable()
    on_connection_state_changed = utils.Hookable()
    on_deathlink = utils.Hookable()
    on_error = utils.Hookable()
    on_goal = utils.Hookable()
    on_hint = utils.Hookable()
    on_item = utils.Hookable()
    on_received_counts = utils.Hookable()
    on_release = utils.Hookable()

    #region Private Methods

    def __init__(self, args):

        self.__attempt: int = 0                                         # Current connection attempt
        self.__attempt_timeouts: List[int] = [ 5, 15, 30, 60, 300 ]     # Duration(s) to wait between connection attempts
        self.__request_queue: dict[str, asyncio.Future] = {}            # Queue for requests awaiting a response
        self.__running: bool = False                                    # Is currently running
        self.__state: str = "Disconnected"                              # Current state
        self.__tasks: List[asyncio.Task] = []                           # Asynchronous tasks
        self.__websocket: websockets.WebSocketClientProtocol = None     # Websocket client

        # Lookups
        self.__goal_lookup: Dict[int, bool] = {}
        self.__item_lookup: Dict[str, Dict[int, str]] = {}
        self.__location_lookup: Dict[str, Dict[int, str]] = {}
        self.__player_lookup: Dict[int, utils.NetworkSlot] = {}
        self.__stats_lookup: Dict[int, utils.PlayerStats] = {}

        self.channel_id: str = args.channel_id
        self.host: str = args.host
        self.port: int = args.port
        self.slot_name: str = args.slot_name
        self.password: Optional[str] = args.password

    def __can_retry(self) -> bool:
        """Check if the client can attempt a retry."""
        return self.__attempt <= len(self.__attempt_timeouts)

    def __get_next_timeout(self) -> int:
        """Get next attempt timeout duration (in seconds)"""
        return self.__attempt_timeouts[self.__attempt - 1] if self.__attempt < len(self.__attempt_timeouts) else self.__attempt_timeouts[-1]

    async def __handle_packet(self, packet: utils.TrackerPacket):
        """Handle an incoming packet."""

        try:
            # Bail if blank / unknown packet
            if not packet or not hasattr(packet, "cmd"):
                logging.warning(f"Unknown packet received, unable to handle.")
                return

            logging.info(f"Handling {packet.cmd} packet...")

            match packet.cmd:

                case utils.BouncedPacket.cmd:
                    await self.__handle_bounced_packet(packet)

                case utils.ConnectedPacket.cmd:
                    await self.__handle_connected_packet(packet)

                case utils.ConnectionRefusedPacket.cmd:
                    await self.__handle_connection_refused_packet(packet)

                case utils.DataPackagePacket.cmd:
                    await self.__handle_datapackage_packet(packet)

                case utils.InvalidPacket.cmd:
                    await self.__handle_invalid_packet(packet)

                case utils.PrintJSONPacket.cmd:
                    await self.__handle_printjson_packet(packet)

                case utils.ReceivedCountResponsePacket.cmd:
                    if not packet.is_error():
                        await self.__handle_receivedcount_packet(packet)

                case utils.RetrievedPacket.cmd:
                    await self.__handle_retrieved_packet(packet)

                case utils.RoomInfoPacket.cmd:
                    await self.__handle_roominfo_packet(packet)

                case utils.StatsPacket.cmd:
                    await self.__handle_stats_packet(packet)

                case _:
                    logging.warning(f"{packet.cmd} is an unhandled packet type.")

            # If this packet is a response, pass it through
            if hasattr(packet, "id"):
                await self.__handle_response_packet(packet)

        except Exception as ex:
            logging.error(f"Unexpected error handling {packet or 'unknown'} packet: {ex}")
            await self.on_error.run(ex)

    async def __handle_bounced_packet(self, packet: utils.BouncedPacket):
        """Handle an incoming Bounce packet."""

        # Handle deathlink
        if "DeathLink" in packet.tags:

            # Increment death count
            if (slot_id:= packet.data.get("slot_id", None)) is not None:
                if (player_stats:= self.__stats_lookup.get(slot_id, None)) is not None:
                    player_stats.deaths += 1

            # Trigger deathlink event
            await self.on_deathlink.run(packet.data.get("source", ""), packet.data.get("cause", ""))

    async def __handle_connected_packet(self, packet: utils.ConnectedPacket):
        """Handle an incoming Connected packet."""

        # Store player lookup
        self.__player_lookup.update({ slot: data for slot, data in packet.slot_info.items() if data.name != self.slot_name })

        # Request data packet for each unique game (could do this all in one request, but I think some games can be HUGE)
        for game in set([player.game for slot, player in self.__player_lookup.items() if player.game != "Archipelago" ]):
            await self.__send_packet(utils.GetDataPackagePacket(games=[game]))

        # Request item counts (for notifications)
        if (items_to_count:= NotificationCount.get_for_channel(self.channel_id)):
            logging.info(f"Requesting item counts for: {items_to_count}")
            await self.__send_packet(utils.ReceivedCountRequestPacket(id="",slot_items=items_to_count))

        # Request stats
        await self.__send_packet(utils.GetStatsPacket(slots=[slot for slot in self.__player_lookup.keys()]))

    async def __handle_connection_refused_packet(self, packet: utils.ConnectionRefusedPacket):
        """Handle an incoming ConnectionRefused packet."""

        # Trigger event
        await self.__set_connection_state("Failed", packet.errors)

        # Don't retry
        self.__attempt = len(self.__attempt_timeouts)

        # Disconnect
        await self.__websocket.close(reason=f"Connection refused by server for reason(s): {", ".join(packet.errors)}")

    async def __handle_datapackage_packet(self, packet: utils.DataPackagePacket):
        """Handle an incoming DataPackage packet."""

        # Store game lookups (and reverse to ID: Name)
        self.__item_lookup.update({ game: { id: name for name, id in data.item_name_to_id.items() } for game, data in packet.data.games.items() })
        self.__location_lookup.update({ game: { id: name for name, id in data.location_name_to_id.items() } for game, data in packet.data.games.items() })

    async def __handle_invalid_packet(self, packet: utils.InvalidPacket):
        """Handle an incoming Invalid packet."""

        logging.error(f"Invalid packet received for '{packet.original_cmd}' with error(s): {packet.text or packet.errors}")

        match packet.original_cmd:

            case utils.ConnectPacket.cmd | utils.GetDataPackagePacket.cmd:
                self.stop()

            case utils.GetStatsPacket.cmd:
                await self.on_error.run(f"Failed to get stats, `/stats` command(s) may not function correctly.")
                return
            
            case utils.ReceivedCountRequestPacket.cmd:
                await self.on_error.run(f"Failed to get received item counts, `/notify count` notifications may not function correctly.")
                return
        
        # Pass on error if no ID
        if not packet.id:
            await self.on_error.run(packet.text)
        

    async def __handle_printjson_packet(self, packet: utils.PrintJSONPacket):
        """Handle an incoming PrintJSON packet"""

        match packet.type:

            case "Collect":
                # Trigger goal event
                await self.on_collect.run(packet.slot)
            
            case "Goal":
                # Update player goal in stats
                if (stats:= self.get_player_stats(packet.slot)):
                    stats.goal = True
                else:
                    # Request stats if they don't exist
                    await self.__send_packet(utils.GetStatsPacket(slots=[packet.slot]))

                # Trigger goal event
                await self.on_goal.run(packet.slot)

            case "Hint":
                # Trigger hint event
                await self.on_hint.run(packet.receiving, packet.item, packet.found)

            case "ItemSend":
                # Update SENDING player's location checks in stats
                if (send_stats:= self.get_player_stats(packet.item.player)):
                    send_stats.checked += 1
                    send_stats.remaining -= 1
                
                # Update RECEIVING player's received items in stats
                if (rcv_stats:= self.get_player_stats(packet.receiving)):
                    rcv_stats.received += 1

                # Trigger item event
                await self.on_item.run(packet.receiving, packet.item)

            case "Release":
                # Trigger release event
                await self.on_release.run(packet.slot)
            
            case _:
                logging.info(f"PrintJSON ({packet.type}) are not currently handled.")

    async def __handle_receivedcount_packet(self, packet: utils.IdentifiablePacket):
        """Handle a received count packet"""

        # Trigger event
        await self.on_received_counts.run(packet.counts)

    async def __handle_response_packet(self, packet: utils.IdentifiablePacket):
        """Handle an incoming response packet"""

        logging.info(f"Received {packet.cmd} response | ID: {packet.id}")

        # If waiting for this response, set packet as result
        if (future:= self.__request_queue.get(packet.id)):
            future.set_result(packet)

    async def __handle_retrieved_packet(self, packet: utils.RetrievedPacket):
        """Handle an incoming Retrieved packet."""

        # Cycle through key/values
        for key, value in packet.keys.items():

            # Update goal statuses
            if key.startswith("_read_client_status_"):
                self.__goal_lookup.update({ int(key[-1]) : int(value) == utils.ClientStatus.GOAL.value })

    async def __handle_roominfo_packet(self, packet: utils.RoomInfoPacket):
        """Handle an incoming RoomInfo packet."""

        # Send connection packet
        connect_packet = utils.ConnectPacket(
            game="",
            items_handling=0b0001,
            name=self.slot_name,
            password=self.password,
            slot_data=False,
            tags=["Bot", "DeathLink", "Tracker"],
            uuid=f"bot_spectator_{self.slot_name}",
            version=utils.NetworkVersion(
                major=0,
                minor=6,
                build=4
            )
        )
        await self.__send_packet(connect_packet)

    async def __handle_stats_packet(self, packet: utils.StatsPacket):
        """Handler for when a Stats packet is received."""

        # Update stats lookup
        self.__stats_lookup.update({k: v for k, v in packet.stats.items()})

        # Consider this as "properly connected" as agent should now have everything it needs
        self.__attempt = 0
        await self.__set_connection_state("Tracking")

    async def __listen_loop(self):
        """Listen to the websocket for incoming data."""

        try:
            # Continue reading while
            while self.__running:
                payload = await self.__websocket.recv()

                for packet in json.loads(payload):
                    await self.__handle_packet(
                        utils.TrackerPacket.parse(packet)
                    )

        except asyncio.CancelledError:
            logging.warning(f"The tracker client __listen_loop() task has been cancelled.")
            raise

        except ConnectionClosed as ccex:
            logging.warning(f"The tracker client connection has been closed.")

        except Exception as ex:
            logging.error(f"Unexpected error in tracker client __listen_loop() task: '{ex}'")

    async def __send_packet(self, packet: utils.TrackerPacket):
        """Send a packet to the websocket server"""

        logging.info(f"Sending {packet.cmd} packet...")

        json = packet.to_json()
        await self.__websocket.send(json)

    async def __set_connection_state(self, new_state: str, errors: List[str] = []):
        """Set the current state of the tracker."""
        self.__state = new_state

        # Trigger event
        await self.on_connection_state_changed.run(new_state, errors)

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

    #endregion

    #region Public Methods

    def get_all_player_stats(self) -> Dict[int, utils.PlayerStats]:
        """Get stats for all players."""
        return self.__player_lookup

    def get_game_name(self, slot_id: int) -> str | None:
        """Get the name of a player's game."""
        return self.__player_lookup.get(slot_id, utils.NetworkSlot()).game

    def get_goal_count(self) -> int:
        """Get the current amount of goals reached."""
        return sum(1 for stat in self.__stats_lookup.values() if stat.goal)

    def get_item_id(self, slot_id: int, item_name: str) -> int | None:
        """Get the ID of an item."""
        game: str = self.get_game_name(slot_id)
        return next((id for id, name in self.__item_lookup.get(game, {}).items() if name.casefold() == item_name.casefold()), None)

    def get_item_name(self, slot_id: int, item_id: int) -> str | None:
        """Get the name of an item."""
        game: str = self.get_game_name(slot_id)
        return self.__item_lookup.get(game, {}).get(item_id, None)

    def get_location_id(self, slot_id: int, location_name: str) -> int | None:
        """Get the ID of a location."""
        game: str = self.get_game_name(slot_id)
        return next((id for id, name in self.__location_lookup.get(game, {}).items() if name.casefold() == location_name.casefold()), None)

    def get_location_name(self, slot_id: int, location_id: int) -> str | None:
        """Get the name of a location."""
        game: str = self.get_game_name(slot_id)
        return self.__location_lookup.get(game, {}).get(location_id, None)
    
    def get_players(self) -> Dict[int, str]:
        """Get all players."""
        return self.__player_lookup

    def get_player_count(self) -> int:
        """Get the amount of players."""
        return len(self.__player_lookup)

    def get_player_name(self, slot_id: int) -> str | None:
        """Get the name of a player."""
        return self.__player_lookup.get(slot_id, utils.NetworkSlot).name
    
    def get_player_stats(self, slot_id: int) -> utils.PlayerStats | None:
        """Get the stats for a player."""
        return self.__stats_lookup.get(slot_id, None)

    def get_slot(self, name: str) -> int | None:
        """Get the slot id for a player by name."""
        return next((slot for slot, player in self.__player_lookup.items() if name.casefold() == player.name.casefold()), None)

    def get_session_stats(self) -> utils.SessionStats:
        """Get the stats for the session."""
        return utils.SessionStats(
            checked=sum(stats.checked for stats in self.__stats_lookup.values()),
            deaths=sum(stats.deaths for stats in self.__stats_lookup.values()),
            goals=sum(1 for stats in self.__stats_lookup.values() if stats.goal),
            remaining=sum(stats.remaining for stats in self.__stats_lookup.values()),
        )

    def get_status(self) -> str:
        """Get the current status."""
        return self.__state

    async def request(self, request: utils.IdentifiablePacket) -> utils.IdentifiablePacket:

        logging.info(f"Sending request... | Type: {request.cmd} | ID: {request.id}")

        future: asyncio.Future = asyncio.get_running_loop().create_future()
        self.__request_queue[request.id] = future

        # Send packet
        await self.__send_packet(request)

        # Wait for response, bail after 5 seconds
        result: utils.IdentifiablePacket = None
        try:
            async with asyncio.timeout(5):
                result = await future
        except TimeoutError:
            logging.warning(f"Request {request.id} timed out.")
            result = utils.ErrorPacket(
                id=request.id,
                original_cmd=request.cmd,
                text=f"Request to the archipelago server timed out."
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
    
    async def send(self, packet: utils.TrackerPacket):
        """Send a packet to the archipelago server"""
        await self.__send_packet(packet)

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

        # Trigger connection state change
        await self.__set_connection_state("Connecting")

        try:
            while self.__running:
                # Try both schemas
                for scheme in [ "wss", "ws" ]:
                    try:
                        async with connect(f"{scheme}://{self.host}:{self.port}") as self.__websocket:
                            logging.info(f"Connection to websocket established via {scheme}://.")

                            # Trigger connected event if first attempt
                            if self.__attempt == 0:
                                await self.__set_connection_state("Connected")

                            # Create and run all asynchronous task(s), stopping when any of them complete
                            self.__tasks = [
                                asyncio.create_task(self.__listen_loop()),
                            ]
                            completed, pending = await asyncio.wait(self.__tasks, return_when=asyncio.FIRST_COMPLETED)

                            logging.info(f"Resolving pending requests...")

                            # Resolve request queue
                            for id, req in self.__request_queue.items():
                                logging.info(f"Resolving request: {id}")
                                req.set_result(utils.ErrorPacket(
                                    id=id,
                                    text="Client disconnected from the archipelago server before receiving a response."
                                ))

                            # Cancel pending tasks
                            for task in pending:
                                task.cancel()

                            # Await cancel completion
                            await asyncio.gather(*pending, return_exceptions=True)

                            # Break to prevent second schema retry
                            break

                    except ConnectionRefusedError as crex:
                        logging.warning(f"Connection to the tracker client websocket was refused via {scheme}://.")

                    except Exception as ex:
                        logging.error(f"Unexpected error occurred in tracker client start() task: {ex}")

                    # Wait before trying again
                    await asyncio.sleep(1)

                logging.warning("Tracker client task(s) have ended.")

                # Prepare for retry
                self.__attempt += 1
                self.__tasks = []
                self.__websocket = None

                # If first retry, trigger event. If last retry, exit
                if self.__attempt == 1:
                    await self.__set_connection_state("Reconnecting")
                elif not self.__can_retry():
                    logging.warning("Tracker client retry limit has been reached.")
                    await self.__set_connection_state("Disconnected")
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

    #endregion

# Arguments
__args: argparse.Namespace

# Variables
__item_counts: Dict[Tuple[int, int], int] = {}
__item_queue: Dict[int, utils.ItemQueue] = {}
__tasks: List[asyncio.Task] = []

# Clients
__std_client: StdClient
__tracker_client: TrackerClient

def queue_item(slot_id: int, item: utils.NetworkItem):
    """Add an item to the item queue."""

    global __item_queue

    # Get/Create queue for recipient
    queue: utils.ItemQueue = __item_queue.get(slot_id, utils.ItemQueue())
    queue.add(item)

    # Update recipient's queue
    __item_queue[slot_id] = queue

async def send(packet: utils.TrackerPacket):
    """Send a packet to the gateway"""
    global __std_client
    await __std_client.send(packet)

async def send_invalid(packet, text: str):
    """Send an invalid packet to the gateway"""
    await send(utils.InvalidPacket(
        id=packet.id,
        original_cmd=packet.cmd,
        text=text
    ))

async def validate_item_counts(packet, action: int, slot_id: int, counts: dict[str, int]) -> Tuple[int, int, int] | None:
    """Validate that item counts exist"""

    # Map item ID/Name/Count
    item_count_lookup = { (get_item_id(slot_id, name), name, count) for name, count in counts.items() }
    
    # Check if any of these names don't exist
    if item_count_lookup and (invalid_names:= [ nm for id, nm, ct in item_count_lookup if id is None ]):
        await send(utils.InvalidPacket(id=packet.id, original_cmd=packet.cmd, text=f"Could not find matching item(s) for {", ".join([f"`{inv}`" for inv in invalid_names])}"))
        return None
    
    # Check if we are missing counts for any of these
    if action == utils.Action.ADD and (unknown_counts:= [ id for id, nm, ct in item_count_lookup if (slot_id, id) not in __item_counts ]):

        # Request item counts from server
        response = await __tracker_client.request(utils.ReceivedCountRequestPacket(
            id=uuid.uuid4().hex,
            slot_items={ slot_id: unknown_counts }
        ))

        # NOTE: Update to __item_counts is handled BEFORE the response is passed back to here

        # Validate response
        if response.is_error():
            await send(utils.ErrorPacket(id=packet.id, original_cmd=packet.cmd, text="Failed to retrieve item data from server."))
            return
    
    # Map counts by ID / Amount / End Amount
    return { (id, amt, __item_counts.get((slot_id, id), 0) + amt ) for id, nm, amt in item_count_lookup } 

async def validate_notification(packet, user_id: int, slot_id: int) -> NotificationSettings | None:
    """Validate that"""

    global __tracker_client
    try:
        notif = NotificationSettings.get_or_create(__tracker_client.channel_id, user_id, slot_id)
    except Exception as ex:
        await send_invalid(packet, f"{ex}")

    return notif

async def validate_slot_name(packet, slot_name: str) -> int | None:
    global __tracker_client

    if not (slot_id:= __tracker_client.get_slot(slot_name)):
        await send_invalid(packet, f"Could not find player with name `{packet.player}`")

    return slot_id

def append_mentions(text: str, user_ids: List[int]) -> str:
    """Append notification mentions to a string."""

    # Append mentions if provided
    if not user_ids: return text
    else: return text + f" -> ({", ".join(f"<@{user_id}>" for user_id in user_ids)})"

def generate_hint_text(recipient: int, item: utils.NetworkItem) -> str:
    """Generate the text for a hint message."""

    # Generate hint text with mentions, if applicable
    return append_mentions(
        f"**[HINT]**: `{get_player(recipient)}`'s item **{get_item(recipient, item.item)} _({utils.NotifyFlags.item_to_notify_flags(item.flags).to_text()})_**" \
            f" is at `{get_player(item.player)}`'s location **{get_location(item.player, item.location)}**",
        get_users_for_hint_flag_notifications(item.player, item.flags),
    )

def generate_networkhint_text(hint: utils.Hint):
    """Generate the text for a hint message"""

    # Generate hint text
    return f"**[HINT]**: `{get_player(hint.receiving_player)}`'s item **{get_item(hint.receiving_player, hint.item)} _({utils.NotifyFlags.item_to_notify_flags(hint.item_flags).to_text()})_**" \
        f" is at `{get_player(hint.finding_player)}`'s location **{get_location(hint.finding_player, hint.location)}**"

def generate_items_text(recipient: int, items: Dict[int, utils.QueuedItemData]) -> str:
    """Generate the text for an item received message."""

    # Convert item IDs to names and counts
    item_counts: Dict[str, int] = { get_item(recipient, item_id): item_data.count for item_id, item_data in items.items() }
    
    # Combine all item flags for notifications
    combined_flags: int = 0
    for flag in [ item_data.flags for item_data in items.values() ]:
        combined_flags |= flag

    # Generate item text with mentions, if applicable
    return append_mentions(
        f"`{get_player(recipient)}` received their " + ", ".join([f"**{item_name}**" + (f" **_(x{count})_**" if count > 1 else "") for item_name, count in item_counts.items()]),
        list(
            set(get_users_for_item_flag_notifications(recipient, combined_flags)) | 
            set(get_users_for_item_term_notifications(recipient, [ name for name in item_counts.keys() ])) |
            set(get_users_for_item_count_notifications(recipient, { tup[1]: rcv_count for tup, rcv_count in __item_counts.items() if tup[0] == recipient and tup[1] in items.keys() }))
        )
    )

#region Tracker Event Handlers

@TrackerClient.on_collect
async def __on_collect(client, slot_id: int):
    """Handler for a slot collecting their remaining items."""
    msg: str = f"`{get_player(slot_id)}` has collected all of their items for **{get_game(slot_id)}** from other worlds."
    await send(utils.DiscordMessagePacket(message=msg))

@TrackerClient.on_connection_state_changed
async def __on_connection_state_changed(client, state: str, errors: List[str] = []):
    """Handler for the tracker's connection state changing."""
    
    global __tracker_client

    msg: str = ""
    match state:

        case "Connected":   # TODO: Is this misleading? Maybe re-word?
            # msg = f"Client has successfully connected to `{client.host}:{client.port}`"
            return

        case "Connecting":
            msg = f"Client is attempting to connect to {format_host_port_slot(client.host, client.port, client.slot_name)} ..."

        case "Disconnected":
            msg = f"Client has disconnected from {format_host_port_slot(client.host, client.port, client.slot_name)} - please use the `/connect` command to retry."

        case "Failed": 
            msg = f"Client has failed to connect to {format_host_port_slot(client.host, client.port, client.slot_name)}. Error(s): {", ".join(errors)}"

        case "Reconnecting":
            msg = f"Client connection has failed, attempting to retry connection to {format_host_port_slot(client.host, client.port, client.slot_name)} - this may take a few minutes."

        case "Tracking":
            msg = f"Client is now tracking the session at {format_host_port_slot(client.host, client.port, client.slot_name)}"

            # Send tracker info
            await send(utils.TrackerInfoPacket(
                players={ k: v.name for k, v in client.get_players().items() }
            ))

        case _:
            return
    
    # Send status update
    await send(utils.DiscordMessagePacket(message=msg))

@TrackerClient.on_deathlink
async def __on_deathlink(client, source: str, cause: str):
    """Handler for the tracker receiving a deathlink"""

    # TODO: Optional whether or not deaths are posted as messages?

@TrackerClient.on_error
async def __on_error(client, msg: str):
    """Handler for the tracker client experiencing an error."""
    await send(utils.DiscordMessagePacket(message=f"Client encountered an unexpected error: '{msg}'."))

@TrackerClient.on_goal
async def __on_goal(client, slot_id: int):
    """Handler for a slot achieving its goal."""

    goals: int = client.get_goal_count()
    players: int = client.get_player_count()
    percentage: int = math.floor((goals / players) * 100)

    # Construct message line(s)
    lines: List[str] = [
        f"## :tada: `{get_player(slot_id)}` has just completed their goal for {get_game(slot_id)} :tada:",
        f"**{goals}/{players} _({percentage}%)_** goals have " + "been reached so far!" if goals < players else "now been reached!"
    ]
    
    await send(utils.DiscordMessagePacket(message="\n".join(lines)))

@TrackerClient.on_hint
async def __on_hint(client, recipient: int, item: utils.NetworkItem, found: bool):
    """Handler for a slot receiving a hint."""

    # Check if item is progression/useful and not already found
    if item.flags & (utils.ItemFlags.PROGRESSION | utils.ItemFlags.USEFUL) and not found:
        msg: str = generate_hint_text(recipient, item)
        await send(utils.DiscordMessagePacket(message=msg))

@TrackerClient.on_item
async def __on_item(client, receiver: int, item: utils.NetworkItem):
    """Handler for an item being received."""

    global __item_counts

    # Increment item count, if tracked
    if (receiver, item.item) in __item_counts:
       __item_counts[(receiver, item.item)] = __item_counts.get((receiver, item.item), 0) + 1

    # Add to item queue
    queue_item(receiver, item)

@TrackerClient.on_received_counts
async def __on_received_counts(client, counts: Dict[int, Dict[int, int]]):
    """Handler for item counts being received"""

    global __item_counts

    # Update item counts
    __item_counts.update({
        (slot_id, item_id) : item_count
        for slot_id, item_counts in counts.items()
        for item_id, item_count in item_counts.items()
    })

@TrackerClient.on_release
async def __on_release(client, slot_id: int):
    """Handler for items being released from a slot."""

    # Send release message
    msg: str = f"`{get_player(slot_id)}` has released all of their remaining items from **{get_game(slot_id)}**."
    await send(utils.DiscordMessagePacket(message=msg))

#endregion

#region StdClient Event Handlers

@StdClient.on_cmd_request
async def __on_cmd_request(client: StdClient, packet: utils.CommandRequestPacket):
    """Handle an incoming cmd request packet"""

    global __tracker_client

    # Send it (this is just forwarding, really.)
    response = await __tracker_client.request(packet)

    # Return the response
    await send(response)

@StdClient.on_error
async def __on_std_error(client: StdClient, msg: str):
    """Handle an error from the std client."""

    # TODO: Figure out if this is the right thing to do...
    await send(utils.DiscordMessagePacket(message=f"Client encountered an unexpected error: '{msg}'."))

@StdClient.on_hint_request
async def __on_hint_request(client: StdClient, packet: utils.HintRequestPacket):
    """Handle an incoming hint request."""

    global __tracker_client

    # Forward to archipelago server
    response = await __tracker_client.request(packet)

    logging.info(f"Response: {response}")

    # Format hints if success
    if not response.is_error() and response.success and response.hints:
        response.comment += ("\n\n" if response.comment else "") + "\n".join([f"- {generate_networkhint_text(hint)}" for hint in response.hints])

    # Return response
    await send(response)

@StdClient.on_notifications_request
async def __on_notifications_request_v2(client: StdClient, packet: utils.NotificationsRequestPacket):
    """Handle an incoming notifications request"""

    # Validate packet data
    if not (slot_id:= await validate_slot_name(packet, packet.player)) or not (notif:= await validate_notification(packet, packet.user_id, slot_id)):
        return
    elif packet.action < utils.Action.ADD or packet.action > utils.Action.VIEW:
        await send_invalid(packet, f"Unknown notifications action requested")
        return

    try:
        global __tracker_client

        # Bail early if just viewing
        if packet.action == utils.Action.VIEW:
            await send(utils.NotificationsResponsePacket(
                id=packet.id,
                notification=utils.NotificationSettingsDTO.from_entity(__tracker_client, notif)
            ))
            return

        # Validate and map item counts
        item_counts = []
        if packet.action != utils.Action.CLEAR and packet.counts:
            if (item_counts:= await validate_item_counts(packet, packet.action, slot_id, packet.counts)) is None:
                return
            
        # Adjust values depending on action
        match packet.action:

            case utils.Action.ADD:
                hint_flags = (notif.hint_flags or utils.NotifyFlags.NONE) | (packet.hints or utils.NotifyFlags.NONE)
                item_flags = (notif.item_flags or utils.NotifyFlags.NONE) | (packet.types or utils.NotifyFlags.NONE)
                terms = set([t.term for t in notif.terms or []]) | { t.casefold() for t in (packet.terms or []) }

                # Merge existing with inbound counts, taking the "end_count" from the inbound list
                merged_counts = { (c.item_id, c.amount): (c.item_id, c.amount, c.end_amount) for c in notif.counts }
                for id, amt, end in item_counts:
                    merged_counts[(id, amt)] = (id, amt, end)
                counts = list(merged_counts.values())

                notif = notif.update(notif.id, hint_flags, item_flags, terms, counts)

            case utils.Action.REMOVE:
                hint_flags = (notif.hint_flags or utils.NotifyFlags.NONE) & ~(packet.hints or utils.NotifyFlags.NONE)
                item_flags = (notif.item_flags or utils.NotifyFlags.NONE) & ~(packet.types or utils.NotifyFlags.NONE)
                terms = { t.term for t in (notif.terms or []) } - { t.casefold() for t in (packet.terms or []) }

                # Remove inbound counts that match exsting
                merged_counts = { (id, amt) for id, amt, _ in item_counts }
                counts = [ (c.item_id, c.amount, c.end_amount) for c in notif.counts if (c.item_id, c.amount) not in merged_counts ]
                
                notif = notif.update(notif.id, hint_flags, item_flags, terms, counts)

            case utils.Action.CLEAR:
                notif = notif.update(notif.id, utils.NotifyFlags.NONE, utils.NotifyFlags.NONE, [], {})

        # Return the notif settings
        await send(utils.NotificationsResponsePacket(
            id=packet.id,
            notification=utils.NotificationSettingsDTO.from_entity(__tracker_client, notif)
        ))

    except Exception as ex:
        await send_invalid(packet, f"{ex}")

@StdClient.on_statistics_request
async def __on_statistics_request(client: StdClient, packet: utils.StatisticsRequestPacket):
    """Handle an incoming statistics request."""

    global __tracker_client

    # Validate player names
    slot_ids = { name: __tracker_client.get_slot(name) for name in packet.players }
    if (invalid_names:= [ name for name, slot_id in slot_ids.items() if not slot_id ]):
        await send(utils.InvalidPacket(
            id=packet.id,
            text=f"No player(s) found with name(s) {", ".join([f"`{invalid}`" for invalid in invalid_names ])}"
        ))
        return
    
    # Add stats for each valid slot requested
    player_stats: Dict[int, utils.PlayerStats] = {}
    for slot in slot_ids.values():
        if (stat:= __tracker_client.get_player_stats(slot)):
            player_stats.update({ slot: stat })

    # Respond with stats for player
    await client.send(utils.StatisticsResponsePacket(
        id=packet.id,
        slots=player_stats,
        session=__tracker_client.get_session_stats() if packet.include_session else None
    ))

@StdClient.on_status_request
async def __on_status_request(client: StdClient, packet: utils.StatusRequestPacket):
    """Handle an incoming status request."""

    global __tracker_client

    # Respond with current status
    await client.send(utils.StatusResponsePacket(
        id=packet.id,
        status=__tracker_client.get_status()
    ))

#endregion

async def __item_loop():
    """Combine mass-received items."""

    global __item_queue

    try:
        while True:
            # Get all item queues that have expired
            now: datetime = datetime.now()
            expired: List[int] = [key for key, val in __item_queue.items() if val.expires and len(val.items) > 0 and val.expires < now]

            # Send message(s) for each expired queue
            for recipient in expired:
                queue: utils.ItemQueue = __item_queue.pop(recipient, utils.ItemQueue())
                msg: str = generate_items_text(recipient, queue.items)

                # Split at "," separator to fit messages within message limit and send to gateway
                for chunk in split_at_separator(msg):
                    await send(utils.DiscordMessagePacket(message=chunk))
            
            # Brief timeout
            await asyncio.sleep(2)

    except asyncio.CancelledError:
        logging.warning("The agent __item_loop() task has been cancelled.")
        raise

    except Exception as ex:
        logging.error(f"Unexpected error in agent __item_loop() task: '{ex}'")

def get_all_stats() -> Dict[int, utils.PlayerStats]:
    """Get stats for all players"""
    global __tracker_client
    return __tracker_client.get_all_player_stats()

def get_game(slot_id: int) -> str | None:
    """Get the name of a game."""
    global __tracker_client
    return __tracker_client.get_game_name(slot_id)

def get_player(slot_id: int) -> str | None:
    """Get the name of a player."""
    global __tracker_client
    return __tracker_client.get_player_name(slot_id)

def get_item(slot_id: int, item_id: int) -> str | None:
    """Get the name of an item."""
    global __tracker_client
    return __tracker_client.get_item_name(slot_id, item_id)

def get_item_id(slot_id: int, item_name: str) -> int | None:
    """Get the ID of an item by its name."""
    global __tracker_client
    return __tracker_client.get_item_id(slot_id, item_name)

def get_location(slot_id: int, location_id: int) -> str | None:
    """Get the name of an item."""
    global __tracker_client
    return __tracker_client.get_location_name(slot_id, location_id)

def get_users_for_hint_flag_notifications(slot_id: int, hint_flags: int) -> List[int]:
    """Get user IDs subscribed to 'hinted item' notifications with these flags."""
    global __tracker_client

    if not (converted_flags:= utils.NotifyFlags.item_to_notify_flags(hint_flags).value):
        return []  

    return NotificationSettings.get_users_for_hint_flags(
        __tracker_client.channel_id,
        slot_id,
        hint_flags
    )

def get_users_for_item_count_notifications(slot_id: int, item_counts: Dict[int, int]) -> List[int]:
    """Get user IDs subscribed to 'item count' notifications for these item counts."""
    global __tracker_client

    if not item_counts:
        return []

    return NotificationCount.pop_users_for_counts(
        __tracker_client.channel_id,
        slot_id,
        item_counts
    )

def get_users_for_item_flag_notifications(slot_id: int, item_flags: int) -> List[int]:
    """Get user IDs subscribed to 'item received' notifications with these flags."""
    global __tracker_client

    if not (converted_flags:= utils.NotifyFlags.item_to_notify_flags(item_flags).value):
        return []  
    
    return NotificationSettings.get_users_for_item_flags(
        __tracker_client.channel_id,
        slot_id,
        converted_flags
    )

def get_users_for_item_term_notifications(slot_id: int, item_names: List[str]) -> List[int]:
    """Get user IDs subscribed to 'item received' notifications with terms within these item names."""
    global __tracker_client

    if not item_names:
        return []
    
    return NotificationTerm.get_users_for_terms(
        __tracker_client.channel_id,
        slot_id,
        item_names
    )

async def main() -> None:

    global __std_client
    global __tasks
    global __tracker_client

    # Parse commandline args
    args = parse_args()

    utils.setup_logging(
        service=f"Agent_{args.port}",
        logtime=args.logtime,
        level=args.loglevel.upper()
    )

    # Instantiate clients
    __std_client = StdClient()
    __tracker_client = TrackerClient(args)

    # Initialise store
    init_db(args.pony)

    # Gather and start all asynchronous tasks, exiting when any task completes
    __tasks = [
        asyncio.create_task(__std_client.start()),
        asyncio.create_task(__tracker_client.start()),
        asyncio.create_task(__item_loop()),
    ]
    complete, pending = await asyncio.wait(__tasks, return_when=asyncio.FIRST_COMPLETED)
    
    # Cancel any pending tasks
    for task in pending:
        task.cancel()

    await asyncio.gather(*pending, return_exceptions=True)

    logging.info(f"All running task(s) have ended.")

    # Exit
    sys.exit()

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    from settings import get_bot_settings

    defaults = get_bot_settings().agent.as_dict()

    parser = argparse.ArgumentParser(prog="Agent.py", description="Archipelago Discord Tracker Client")
    parser.add_argument("--channel_id", type=str, help="The hostname of the archipelago server")
    parser.add_argument("--host", type=str, default=defaults["host"], help="The hostname of the archipelago server")
    parser.add_argument("--port", type=int, help="The port of the archipelago session.")
    parser.add_argument("--slot_name", type=str, help="The slot name to connect to.")
    parser.add_argument("--password", type=str, help="The password for the server or slot.")
    parser.add_argument("--loglevel", default=defaults["loglevel"], type=str)
    parser.add_argument("--logtime", default=defaults["logtime"], type=bool)

    args = parser.parse_args()
    args.pony = get_bot_settings().pony.as_dict()

    return args

if __name__ == "__main__":
    asyncio.run(main())
