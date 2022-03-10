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
    Send all the previous messages from the chat, so that new
    members to the chat room can see what was said before.
    """
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
    Receive and process chat messages from a user.

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
    Handle a connection: start a new chat.

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
        await send_chat(websocket, chat, userId, connected)
    finally:
        del JOIN[join_key]


async def join(websocket, join_key):
    """
    Handle a connection: join an existing chatroom

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
    Handle a connection and dispatch it according to who is connecting
    (either join a chatroom or start one).
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
    """
    Start a WebSockets server.
    """
    async with websockets.serve(handler, "", 8001): 
        await asyncio.Future()  # run forever

# entry point
if __name__ == "__main__":
    asyncio.run(main())