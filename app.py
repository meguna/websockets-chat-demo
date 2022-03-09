#!/usr/bin/env python

import asyncio
import json
import secrets

import websockets
from time import time

JOIN = {}

class Chat():
  def __init__(self):
    self.messages = []
    self.users = []
  
  def add_message(self, message):
    self.messages.append(message)


async def error(websocket, message):
    """
    Send an error message.

    """
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def replay(websocket, chat):
    """
    Send previous messages.

    """
    # Make a copy to avoid an exception if chat.moves changes while iteration
    # is in progress. If a move is played while replay is running, moves will
    # be sent out of order but each move will be sent once and eventually the
    # UI will be consistent.
    for message in chat.messages.copy():
        event = {
            "type": "talk",
            "payload": message['payload'],
            "userId": message['userId'],
            "time": message['time'],
        }
        await websocket.send(json.dumps(event))


async def send_chat(websocket, chat, userId, connected):
    """
    Receive and process moves from a player.

    """
    async for message in websocket:
        # Parse a "talk" event from the UI.
        event = json.loads(message)
        if event["type"] == "talk":
          payload = event["payload"]
          userId = event["userId"]

          messageDetails = {"payload": payload, "userId": userId, "time": time()}
          try:
              # Send the chat message.
              chat.add_message(messageDetails)
          except RuntimeError as exc:
              # Send an "error" event if something goes wrong. 
              await error(websocket, str(exc))
              continue

          # Send a "talk" event to update the UI.
          event = {"type": "talk", **messageDetails}
          websockets.broadcast(connected, json.dumps(event))


async def start(websocket):
    """
    Handle a connection from the first person: start a new chat.

    """
    # Initialize a Chat, the set of WebSocket connections
    # receiving moves from this chat, and secret access tokens.
    chat = Chat()
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = chat, connected
    userId = len(connected)

    try:
        # Send the secret access tokens to the browser of the first person,
        # where they'll be used for building "join" links.
        event = {
            "type": "init",
            "joinKey": join_key,
            "userId": userId
        }
        await websocket.send(json.dumps(event))
        # Receive and process moves from the first player.
        await send_chat(websocket, chat, userId, connected)
    finally:
        del JOIN[join_key]


async def join(websocket, join_key):
    """
    Handle a connection from new chat members - join a chatroom

    """
    # find the chat in Python memory.
    try:
        chat, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "chat not found.")
        return

    # Register to receive moves from this chat.
    connected.add(websocket)
    userId = len(connected)
    try:
       # Send the secret access tokens to the browser of the first person,
        # where they'll be used for building "join" links.
        event = {
            "type": "init",
            "joinKey": join_key,
            "userId": len(connected)
        }
        await websocket.send(json.dumps(event))

        # Send messages so far (update new participants).
        await replay(websocket, chat)

        await send_chat(websocket, chat, userId, connected)
    finally:
        connected.remove(websocket)


async def handler(websocket):
    """
    Handle a connection and dispatch it according to who is connecting.

    """
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "joinKey" in event:
        # Second person joins an existing chat.
        await join(websocket, event["joinKey"])
    else:
        # First person starts a new chat.
        await start(websocket)


async def main():
    async with websockets.serve(handler, "", 8001): 
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())