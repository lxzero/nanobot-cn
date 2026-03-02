"""Mattermost channel implementation using WebSocket and REST API."""

import asyncio
import json
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
from loguru import logger
from websockets import connect as ws_connect
from websockets.exceptions import ConnectionClosed, InvalidStatus

from nanobot.bus.events import InboundMessage, OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.channels.base import BaseChannel
from nanobot.config.schema import MattermostConfig


class MattermostChannel(BaseChannel):
    """Mattermost channel using WebSocket for real-time messaging."""

    name = "mattermost"

    def __init__(self, config: MattermostConfig, bus: MessageBus):
        super().__init__(config, bus)
        self.config: MattermostConfig = config
        self._client: httpx.AsyncClient | None = None
        self._ws_connection: Any | None = None
        self._seq: int = 0
        self._bot_user_id: str | None = None
        self._bot_username: str | None = None
        self._team_ids: set[str] = set()
        self._receive_task: asyncio.Task | None = None
        self._http_timeout: float = 30.0

    async def start(self) -> None:
        """Start the Mattermost WebSocket connection."""
        if not self.config.url or not self.config.token:
            logger.error("Mattermost URL or token not configured")
            return

        self._running = True
        base_url = self.config.url.rstrip("/")

        # Initialize HTTP client
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
        }
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=self._http_timeout,
        )

        # Get bot user info
        try:
            me = await self._get("/api/v4/users/me")
            self._bot_user_id = me.get("id")
            self._bot_username = me.get("username", "")
            logger.info("Mattermost bot connected as @{} ({})", self._bot_username, self._bot_user_id)
        except Exception as e:
            logger.error("Failed to authenticate with Mattermost: {}", e)
            return

        # Resolve configured team names to IDs
        if self.config.teams:
            try:
                all_teams = await self._get("/api/v4/teams")
                name_to_id = {
                    t.get("name"): t.get("id")
                    for t in all_teams
                }
                display_to_id = {
                    t.get("display_name"): t.get("id")
                    for t in all_teams
                }
                for team_name in self.config.teams:
                    team_id = name_to_id.get(team_name) or display_to_id.get(team_name)
                    if team_id:
                        self._team_ids.add(team_id)
                        logger.info("Mattermost team allowed: {} ({})", team_name, team_id)
                    else:
                        logger.warning("Team '{}' not found, will be ignored", team_name)
            except Exception as e:
                logger.warning("Failed to resolve team info: {}", e)

        # Start the receive loop (single task, manages reconnection internally)
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def stop(self) -> None:
        """Stop the Mattermost connection."""
        self._running = False

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            self._receive_task = None

        if self._ws_connection:
            try:
                await self._ws_connection.close()
            except Exception as e:
                logger.debug("WebSocket close error: {}", e)
            self._ws_connection = None

        if self._client:
            await self._client.aclose()
            self._client = None

        logger.info("Mattermost channel stopped")

    async def send(self, msg: OutboundMessage) -> None:
        """Send a message through Mattermost."""
        if not self._client:
            logger.warning("Mattermost client not running")
            return

        channel_id = msg.chat_id
        thread_id = msg.metadata.get("mattermost", {}).get("thread_id") if msg.metadata else None

        # Send text message
        if msg.content:
            try:
                payload = {
                    "channel_id": channel_id,
                    "message": msg.content,
                }
                if thread_id:
                    payload["root_id"] = thread_id

                await self._post("/api/v4/posts", payload)
            except Exception as e:
                logger.error("Failed to send Mattermost message: {}", e)

        # Send media files
        for media_path in msg.media or []:
            try:
                await self._upload_file(channel_id, media_path, thread_id)
            except Exception as e:
                logger.error("Failed to upload file {}: {}", media_path, e)

    async def _get(self, path: str) -> Any:
        """Make a GET request to Mattermost API."""
        if not self._client:
            raise RuntimeError("HTTP client not initialized")
        response = await self._client.get(path)
        response.raise_for_status()
        return response.json()

    async def _post(self, path: str, data: dict) -> Any:
        """Make a POST request to Mattermost API."""
        if not self._client:
            raise RuntimeError("HTTP client not initialized")
        response = await self._client.post(path, json=data)
        response.raise_for_status()
        return response.json()

    async def _upload_file(self, channel_id: str, file_path: str, thread_id: str | None = None) -> None:
        """Upload a file to Mattermost."""
        if not self._client:
            return

        path = Path(file_path)
        if not path.exists():
            logger.warning("File not found: {}", file_path)
            return

        with open(path, "rb") as f:
            files = {"files": (path.name, f, "application/octet-stream")}
            data = {"channel_id": channel_id}
            if thread_id:
                data["root_id"] = thread_id

            # Need to use a new client without Content-Type header for multipart
            headers = {"Authorization": f"Bearer {self.config.token}"}
            async with httpx.AsyncClient(headers=headers, timeout=self._http_timeout) as client:
                response = await client.post(
                    urljoin(self.config.url.rstrip("/") + "/", "api/v4/files"),
                    data=data,
                    files=files,
                )
                response.raise_for_status()
                result = response.json()
                file_ids = result.get("file_infos", [])
                if file_ids:
                    logger.debug("Uploaded file: {} -> {}", file_path, file_ids[0].get("id"))

    async def _connect_websocket(self) -> None:
        """Establish WebSocket connection and send auth challenge. Does NOT spawn tasks."""
        base_url = self.config.url.rstrip("/")
        ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_url}/api/v4/websocket"

        self._ws_connection = await ws_connect(
            ws_url,
            additional_headers={"Authorization": f"Bearer {self.config.token}"},
        )
        logger.info("Mattermost WebSocket connected")

        auth_msg = {
            "seq": self._next_seq(),
            "action": "authentication_challenge",
            "data": {"token": self.config.token},
        }
        await self._ws_connection.send(json.dumps(auth_msg))

    async def _receive_loop(self) -> None:
        """Main WebSocket receive loop. Started once; manages all reconnection internally."""
        _BASE_DELAY = 5.0
        _MAX_DELAY = 60.0
        reconnect_delay = _BASE_DELAY

        # Initial connection attempt
        while self._running:
            try:
                await self._connect_websocket()
                break
            except asyncio.CancelledError:
                return
            except Exception as e:
                logger.error("Mattermost WebSocket initial connection failed: {}", e)
                logger.info("Retrying in {}s...", reconnect_delay)
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, _MAX_DELAY)

        reconnect_delay = _BASE_DELAY

        while self._running:
            try:
                message = await self._ws_connection.recv()
                reconnect_delay = _BASE_DELAY  # Reset backoff on successful receive
                data = json.loads(message)

                event_type = data.get("event")
                if event_type == "posted":
                    await self._handle_posted(data.get("data", {}))
                elif event_type == "hello":
                    logger.info("Mattermost server said hello")
                elif event_type == "status_change":
                    logger.debug("Mattermost status change: {}", data)

            except ConnectionClosed:
                logger.warning("Mattermost WebSocket closed, reconnecting in {}s...", reconnect_delay)
                self._ws_connection = None
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in Mattermost receive loop: {}", e)
                self._ws_connection = None

            if not self._running:
                break

            if self._ws_connection is None:
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, _MAX_DELAY)
                try:
                    logger.info("Reconnecting to Mattermost WebSocket...")
                    await self._connect_websocket()
                    reconnect_delay = _BASE_DELAY  # Reset on successful reconnect
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error("Mattermost reconnect failed: {}", e)

    async def _handle_posted(self, event_data: dict) -> None:
        """Handle a 'posted' event (new message)."""
        post_data_str = event_data.get("post", "{}")
        try:
            post = json.loads(post_data_str)
        except json.JSONDecodeError:
            logger.warning("Failed to parse post data: {}", post_data_str)
            return

        sender_id = post.get("user_id")
        channel_id = post.get("channel_id")
        message = post.get("message", "").strip()
        post_id = post.get("id")
        root_id = post.get("root_id")  # Thread ID

        # Ignore own messages
        if sender_id == self._bot_user_id:
            return

        # Ignore empty messages
        if not message:
            return

        # Check allow list
        if not self.is_allowed(sender_id):
            logger.warning("Access denied for sender {} on Mattermost", sender_id)
            return

        # Strip bot mention and normalize bot commands early, before respond checks.
        # Supported bot command prefixes:
        #   /cmd       — direct slash (only works in DMs; Mattermost intercepts in channels)
        #   !cmd       — exclamation prefix (bypasses Mattermost interception)
        #   " /cmd"    — leading-space slash (also bypasses Mattermost interception)
        _SLASH_COMMANDS = {"/new", "/stop", "/help", "/status", "/skills"}
        clean_message = self._strip_bot_mention(message)
        _cmd_candidate = clean_message.lstrip()
        if _cmd_candidate.startswith("!"):
            _slash = "/" + _cmd_candidate[1:]
            if _slash.lower() in _SLASH_COMMANDS:
                clean_message = _slash
        elif _cmd_candidate.startswith("/") and _cmd_candidate.lower() in _SLASH_COMMANDS:
            clean_message = _cmd_candidate

        # Bot commands always bypass mention/channel policy checks.
        is_bot_command = clean_message.lower() in _SLASH_COMMANDS

        # Get channel info for metadata
        channel_type = "direct"
        channel_team_id = None
        try:
            channel_info = await self._get(f"/api/v4/channels/{channel_id}")
            channel_type = channel_info.get("type", "unknown")  # D=direct, O=open, P=private
            channel_team_id = channel_info.get("team_id")
        except Exception as e:
            logger.debug("Failed to get channel info: {}", e)

        # Team filter: if configured, only process messages from allowed teams.
        # DMs have no team_id (""), so they always pass through.
        if self._team_ids and channel_team_id and channel_team_id not in self._team_ids:
            return

        # Parse mentions from event_data (Mattermost sends a JSON-encoded list of user IDs)
        mentions_raw = event_data.get("mentions", "[]")
        try:
            mentions: list[str] = json.loads(mentions_raw) if isinstance(mentions_raw, str) else (mentions_raw or [])
        except (json.JSONDecodeError, TypeError):
            mentions = []

        # Determine if we should respond (bot commands always pass through)
        if not is_bot_command and not self._should_respond(channel_type, channel_id, message, mentions):
            return

        # Acknowledge the message with a reaction so the user knows it was received
        await self._add_reaction(post_id, "eyes")

        # Download attachments if present
        media_paths = []
        file_ids = post.get("file_ids", [])
        for file_id in file_ids:
            try:
                file_path = await self._download_file(file_id)
                if file_path:
                    media_paths.append(file_path)
                    clean_message += f"\n[attachment: {file_path}]"
            except Exception as e:
                logger.warning("Failed to download file {}: {}", file_id, e)

        logger.debug("Mattermost message from {} in {}: {}", sender_id, channel_id, clean_message[:50])

        # Forward to message bus
        await self._handle_message(
            sender_id=sender_id,
            chat_id=channel_id,
            content=clean_message,
            media=media_paths,
            metadata={
                "post_id": post_id,
                "root_id": root_id,
                "channel_type": channel_type,
                "mattermost": {
                    "thread_id": root_id or post_id,  # For reply threading
                },
            },
            session_key=f"mattermost:{channel_id}:{root_id or post_id}" if root_id else None,
        )

    def _should_respond(self, channel_type: str, channel_id: str, message: str, mentions: list[str]) -> bool:
        """Determine if bot should respond to this message.

        Rules:
        - Direct messages (type "D"): always respond, ignore allow_channels.
        - allow_channels: if non-empty, only process messages from those channel IDs.
        - mention_policy:
            "always" (default) — only respond when @mentioned in channels.
            "never"            — respond to all messages in channels.
        """
        # Direct messages: controlled by allow_direct_messages (default True)
        if channel_type == "D":
            return self.config.allow_direct_messages

        # Channel allowlist: if configured, silently ignore channels not in the list
        if self.config.allow_channels and channel_id not in self.config.allow_channels:
            return False

        # "never" = no mention required, respond to everything in allowed channels
        if self.config.mention_policy == "never":
            return True

        # "always" (default) = require @mention in channels
        if self._bot_user_id and self._bot_user_id in mentions:
            return True
        if self._bot_username and f"@{self._bot_username}" in message.lower():
            return True
        return False

    def _strip_bot_mention(self, message: str) -> str:
        """Remove @botname mention from message text."""
        import re
        if not self._bot_username:
            return message
        return re.sub(rf"@{re.escape(self._bot_username)}\b\s*", "", message, flags=re.IGNORECASE).strip()

    async def _add_reaction(self, post_id: str, emoji_name: str) -> None:
        """Add an emoji reaction to a post."""
        if not self._client or not self._bot_user_id or not post_id:
            return
        try:
            await self._post("/api/v4/reactions", {
                "user_id": self._bot_user_id,
                "post_id": post_id,
                "emoji_name": emoji_name,
            })
        except Exception as e:
            logger.debug("Failed to add reaction to post {}: {}", post_id, e)

    async def _download_file(self, file_id: str) -> str | None:
        """Download a file from Mattermost."""
        if not self._client:
            return None

        try:
            # Get file metadata (info endpoint returns JSON, not binary)
            file_info = await self._get(f"/api/v4/files/{file_id}/info")
            file_name = file_info.get("name", f"file_{file_id}")

            # Download file content
            response = await self._client.get(f"/api/v4/files/{file_id}")
            response.raise_for_status()

            # Save to media directory
            media_dir = Path.home() / ".nanobot" / "media"
            media_dir.mkdir(parents=True, exist_ok=True)

            file_path = media_dir / f"{file_id}_{file_name}"
            with open(file_path, "wb") as f:
                f.write(response.content)

            return str(file_path)
        except Exception as e:
            logger.error("Failed to download file {}: {}", file_id, e)
            return None

    def _next_seq(self) -> int:
        """Get next sequence number for WebSocket messages."""
        self._seq += 1
        return self._seq
