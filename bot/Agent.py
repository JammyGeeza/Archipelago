import argparse
import asyncio
import bot.Utils as utils
import json
import logging
import math
import sys
import threading
import websockets

from settings import get_settings
from bot.Store import Store
from datetime import datetime
from typing import Dict, List, Optional
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

class StdClient:

    # Events
    on_error = utils.Hookable()
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

        logging.info(f"Received {packet.cmd} from gateway.")

        try:
            match packet.cmd:
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
                message=f"{ex}"
            ))

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
    on_error = utils.Hookable() # TODO: Actually trigger this when things go wrong.
    on_goal = utils.Hookable()
    on_hint = utils.Hookable()
    on_item = utils.Hookable()
    on_release = utils.Hookable()

    #region Private Methods

    def __init__(self, args):

        self.__attempt: int = 0                                         # Current connection attempt
        self.__attempt_timeouts: List[int] = [ 5, 15, 30, 60, 300 ]     # Duration(s) to wait between connection attempts
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

        logging.info(f"Handling {packet.cmd} packet...")

        try:
            match packet.cmd:

                case utils.ConnectedPacket.cmd:
                    await self.__handle_connected_packet(packet)

                case utils.ConnectionRefusedPacket.cmd:
                    await self.__handle_connection_refused_packet(packet)

                case utils.DataPackagePacket.cmd:
                    await self.__handle_datapackage_packet(packet)

                case utils.PrintJSONPacket.cmd:
                    await self.__handle_printjson_packet(packet)

                case utils.RetrievedPacket.cmd:
                    await self.__handle_retrieved_packet(packet)

                case utils.RoomInfoPacket.cmd:
                    await self.__handle_roominfo_packet(packet)

                case utils.StatsPacket.cmd:
                    await self.__handle_stats_packet(packet)

                case _:
                    logging.warning(f"{packet.cmd} is an unhandled packet type.")

        except Exception as ex:
            logging.error(f"Unexpected error handling {packet.cmd} packet: {ex}")
            # TODO: Respond with InvalidPacket instead
            await self.on_error.run(ex)

    async def __handle_connected_packet(self, packet: utils.ConnectedPacket):
        """Handle an incoming Connected packet."""

        # Store player lookup
        self.__player_lookup.update({ slot: data for slot, data in packet.slot_info.items() if data.name != self.slot_name })

        # Request data packet for each unique game (could do this all in one request, but I think some games can be HUGE)
        for game in set([player.game for slot, player in self.__player_lookup.items() if player.game != "Archipelago" ]):
            await self.__send_packet(utils.GetDataPackagePacket(games=[game]))

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
                if (stats:= self.get_player_stats(packet.item.player)):
                    stats.checked += 1
                    stats.remaining -= 1
                else:
                    # Request stats if they don't exist
                    await self.__send_packet(utils.GetStatsPacket(slots=[packet.item.player]))

                # Trigger item event
                await self.on_item.run(packet.receiving, packet.item)

            case "Release":
                # Trigger release event
                await self.on_release.run(packet.slot)
            
            case _:
                logging.info(f"PrintJSON ({packet.type}) are not currently handled.")

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
            tags=["Bot", "Deathlink", "Tracker"],
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

    def get_item_name(self, slot_id: int, item_id: int) -> str | None:
        """Get the name of an item."""
        game: str = self.get_game_name(slot_id)
        return self.__item_lookup.get(game, {}).get(item_id, None)

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
            goals=sum(1 for stats in self.__stats_lookup.values() if stats.goal),
            # players=self.get_player_count(),
            remaining=sum(stats.remaining for stats in self.__stats_lookup.values()),
        )

    def get_status(self) -> str:
        """Get the current status."""
        return self.__state

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
                # Attempt to connect
                try:
                    async with connect(f"ws://localhost:{self.port}") as self.__websocket:
                        logging.info(f"Connection to websocket established.")

                        # Trigger connected event if first attempt
                        if self.__attempt == 0:
                            await self.__set_connection_state("Connected")

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

# Store
__store: Store

# Variables
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

def split_at_separator(text: str, limit: int = 2000, separator: str = ", ") -> List[str]:
    """Split a string into chunks no longer than <limit> by <separator>"""

    # If not longer than the limit, return it
    if len(text) <= limit:
        return [ text ]

    parts = text.split(separator)
    chunks = []
    current_chunk = ""

    # Cycle through split parts
    for part in parts:
        # Include separator if current chunk is not empty
        test_chunk = current_chunk + separator + part if current_chunk else part

        if len(test_chunk) > limit:
            # Next chunk is too long, append what we have
            chunks.append(current_chunk)
            current_chunk = part
        else:
            current_chunk = test_chunk

    # Add any remaining chunks
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

async def send(packet: utils.TrackerPacket):
    """Send a packet to the gateway"""
    global __std_client
    await __std_client.send(packet)

def append_mentions(text: str, user_ids: List[int]) -> str:
    """Append notification mentions to a string."""

    # Append mentions if provided
    if not user_ids: return text
    else: return text + f" -> ({", ".join(f"<@{user_id}>" for user_id in user_ids)})"

def generate_hint_text(recipient: int, item: utils.NetworkItem) -> str:
    """Generate the text for a hint message."""

    # Generate hint text with mentions, if applicable
    return append_mentions(
        f"**[HINT]**: `{get_player(recipient)}`'s item **{get_item(recipient, item.item)} _({utils.NotifyFlags.item_to_notify_flags(item.flags).to_text()})_** is at `{get_player(item.player)}`'s location **{get_location(item.player, item.location)}** check.",
        get_hint_flag_notifications(item.player, item.flags),
    )

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
        list(set(get_item_flag_notifications(recipient, combined_flags)) | set(get_item_term_notifications(recipient, [ name for name in item_counts.keys() ])))
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
    
    msg: str = ""
    match state:

        case "Connected":   # TODO: Is this misleading? Maybe re-word?
            # msg = f"Client has successfully connected to `:{client.port}`"
            return

        case "Connecting":
            msg = f"Client is attempting to connect to `:{client.port}`..."

        case "Disconnected":
            msg = f"Client has disconnected from `:{client.port}` - please use the `/connect` command to retry."

        case "Failed": 
            msg = f"Client has failed to connect to `:{client.port}`. Error(s): {", ".join(errors)}"

        case "Reconnecting":
            msg = f"Client connection has failed, attempting to retry connection to `:{client.port}` - this may take a few minutes."

        case "Tracking":
            msg = f"Client is now tracking the session at `:{client.port}`"

            # Send tracker info
            await send(utils.TrackerInfoPacket(
                players={ k: v.name for k, v in client.get_players().items() }
            ))

        case _:
            return
    
    # Send status update
    await send(utils.DiscordMessagePacket(message=msg))

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

    # Add to item queue
    queue_item(receiver, item)

@TrackerClient.on_release
async def __on_release(client, slot_id: int):
    """Handler for items being released from a slot."""

    # Send release message
    msg: str = f"`{get_player(slot_id)}` has released all of their remaining items from **{get_game(slot_id)}**."
    await send(utils.DiscordMessagePacket(message=msg))

#endregion

#region StdClient Event Handlers

@StdClient.on_error
async def __on_std_error(client: StdClient, msg: str):
    """Handle an error from the std client."""

    # TODO: Figure out if this is the right thing to do...
    await send(utils.DiscordMessagePacket(message=f"Client encountered an unexpected error: '{msg}'."))

@StdClient.on_notifications_request
async def __on_notifications_request(client: StdClient, packet: utils.NotificationsRequestPacket):
    """Handle an incoming notifications request."""

    global __store
    global __tracker_client

    # Validate the player name
    if not (slot_id:= __tracker_client.get_slot(packet.player)):
        await send(utils.InvalidPacket(
            id=packet.id,
            original_cmd=packet.cmd,
            message=f"Player with name `{packet.player}` could not be found."
        ))
        return
    
    # TODO: Validate the flags??
    #       I could probably do this in __post_init__()...
    
    # Check if notification exists, create if it doesn't
    if not (notif:= __store.notifications.get_or_create(__tracker_client.port, packet.user_id, slot_id)):
        await send(utils.ErrorPacket(
            id=packet.id,
            original_cmd=packet.cmd,
            message="An error occurred while attempting to get or create notification preferences."
        ))
        return
    
    match packet.action:
        case utils.Action.ADD:
            notif.hints = ((notif.hints or utils.NotifyFlags.NONE) | (packet.hints or utils.NotifyFlags.NONE))
            notif.types = ((notif.types or utils.NotifyFlags.NONE) | (packet.types or utils.NotifyFlags.NONE))
            notif.terms = list(set(notif.terms or []) | set(packet.terms or []))

        case utils.Action.REMOVE:
            notif.hints = ((notif.hints or utils.NotifyFlags.NONE) & ~(packet.hints or utils.NotifyFlags.NONE))
            notif.types = ((notif.types or utils.NotifyFlags.NONE) & ~(packet.types or utils.NotifyFlags.NONE))
            notif.terms = list(set(notif.terms or []) - set(packet.terms or []))
        
        case utils.Action.CLEAR:
            notif.hints = utils.NotifyFlags.NONE
            notif.types = utils.NotifyFlags.NONE
            notif.terms = []

        case _:
            await send(utils.InvalidPacket(
                id=packet.id,
                original_cmd=packet.cmd,
                message=f"Invalid action type '{packet.action}'"
            ))
            return

    # Save changes
    if not (notif:= __store.notifications.upsert(notif)):
        await send(utils.ErrorPacket(
            id=packet.id,
            message="An error occurred while attempting to store the notification preferences."
        ))
        return
    
    # Respond
    await send(utils.NotificationsResponsePacket(
        id=packet.id,
        notification=notif
    ))

@StdClient.on_statistics_request
async def __on_statistics_request(client: StdClient, packet: utils.StatisticsRequestPacket):
    """Handle an incoming statistics request."""

    global __tracker_client

    # Validate player names
    slot_ids = { name: __tracker_client.get_slot(name) for name in packet.players }
    if (invalid_names:= [ name for name, slot_id in slot_ids.items() if not slot_id ]):
        await send(utils.InvalidPacket(
            id=packet.id,
            message=f"No player(s) found with name(s) {", ".join([f"`{invalid}`" for invalid in invalid_names ])}"
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

def get_location(slot_id: int, location_id: int) -> str | None:
    """Get the name of an item."""
    global __tracker_client
    return __tracker_client.get_location_name(slot_id, location_id)

def get_hint_flag_notifications(slot_id: int, item_flags: int) -> List[int]:
    """Get user IDs subscribed to 'hinted item' notifications with these flags."""

    global __store
    global __tracker_client

    # Get notifications from store
    return __store.notifications.get_for_hint_flags(
        __tracker_client.port,
        slot_id,
        utils.NotifyFlags.item_to_notify_flags(item_flags)
    )

def get_item_flag_notifications(slot_id: int, item_flags: int) -> List[int]:
    """Get user IDs subscribed to 'item received' notifications with these flags."""

    global __store
    global __tracker_client

    # Get notifications from store
    return __store.notifications.get_for_item_flags(
        __tracker_client.port,
        slot_id,
        utils.NotifyFlags.item_to_notify_flags(item_flags)
    )

def get_item_term_notifications(slot_id: int, item_names: List[str]) -> List[int]:
    """Get user IDs subscribed to 'item received' notifications with terms within these item names."""

    global __store
    global __tracker_client

    # Get notifications from store
    return __store.notifications.get_for_terms(
       __tracker_client.port,
       slot_id,
       item_names
    )

async def main() -> None:

    global __args
    global __store
    global __std_client
    global __tasks
    global __tracker_client

    # Parse commandline args
    __args = parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, __args.loglevel.upper(), logging.INFO),
        format=f"[AGENT]    {'%(asctime)s\t' if __args.logtime else ''}%(levelname)s:\t%(message)s | Port: {__args.port}",
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    # Instantiate store
    __store = Store()

    # Instantiate clients
    __std_client = StdClient()
    __tracker_client = TrackerClient(__args)

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

    defaults = get_settings().discord_agent_options.as_dict()

    parser = argparse.ArgumentParser(prog="Agent.py", description="Archipelago Discord Tracker Client")
    parser.add_argument("--port", type=int, help="The port of the local archipelago session.")
    parser.add_argument("--slot_name", type=str, help="The slot name to connect to.")
    parser.add_argument("--password", type=str, help="The password for the server or slot.")
    parser.add_argument("--loglevel", default=defaults["loglevel"], type=str)
    parser.add_argument("--logtime", default=defaults["logtime"], type=bool)

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    asyncio.run(main())
