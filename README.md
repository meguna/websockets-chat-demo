# Chat Demo with Python Websockets and Web GUI

For CS21, Spring 2022, Tufts University.

### About this project

This project demonstrates a chat application service that uses a Python WebSockets backend and a very primitive HTML/Javascript frontend. It used [the official Python WebSockets tutorial](https://websockets.readthedocs.io/en/stable/intro/tutorial1.html) (which builds a Connect4 server instead) as a guide. 

### Run the project

Clone this repository and open two terminal windows from the project's root directory. 
- In one of the windows, run `python3 app.py`
- In the other window, run `python3 -m http.server`
- Then, you should be able to access the website at: `http://localhost:8000/`
- If you open the "join link" from a different browser (but within the same local network as the server), you should be able to use the application to communicate. 
- To be able to access this project from any network, you can publish it to the internet! See more [here](https://websockets.readthedocs.io/en/stable/intro/tutorial3.html). 

## Why WebSockets?

Websites by default use HTTP connections to communicate between a client and a server. This means that:
- a client requests some sort of information, a server returns it, and the communication ends.

What if the server realizes it has new information and wants to give it to the client?
- In traditional HTTP, we can't do this. 
- We can emulate thise behavior using "long polling" - essentially, manually choose to leave the connection open way longer after the first message was sent from the server to the client.
  - downsides: can be pretty burdensome on the server (one process per connection), tends to not scale well for bigger projects, consumes more resources, and can cause duplicate date on client-side.
- WebSockets was created as a way to directly respond to this situation, establishing real two-way communcation between clients and servers.
- Note that in web programming, the role of "client" and "server" are fixed - you always have a service that acts as the client, and a service that acts as the server, and that is how we communicate. 

## File Structure
- app.py: contains the server loop and server functions (functions that update the state of the server).
- main.js: contains the GUI, and the client functions that send requests to the server. We also receive responses from the server here, which update our GUI.
- index.html: basic HTML, which is manipulated by the Javascript. 
- style.css: styling for our website. Uses [Bulma](https://bulma.io/)

# Code Highlights (in class)

### App.py: main
```
async def main():
    async with websockets.serve(handler, "", 8001):       # start a websockets server. server listens on port 8001
        await asyncio.Future()                            # run forever
```
- We use the `websockets` library for this project
- `websockets` is based on the Python standard library `asyncio` 
- [`websockets.serve()` spec](https://websockets.readthedocs.io/en/stable/reference/server.html#starting-a-server)
- `handler`: name of function (described below)

Some key vocabulary terms here:
- `asyncio` is based on coroutines, which are basically like Python functions where you can choose to stop execution at certain checkpoints within the function, and resume execution from that stopped checkpoint later. 
- `async def ...` defines a coroutine.
- `await f()...` are statements that should only be used within coroutine functions, and will pause execution of the "caller" coroutine and waits for the execution of the `f()` to complete first before proceeding.

### App.py: handler function

```
async def handler(websocket):
    message = await websocket.recv()                    # Receive and parse the "init" event from the GUI.
    event = json.loads(message)                         # parse a string containing JSON and convert it to a dict (loads = load string)
    assert event["type"] == "init"

    if "joinKey" in event:                              # Second person joins an existing chat.
        await join(websocket, event["joinKey"])
    else:
        await start(websocket)                          # First person starts a new chat.
```
- `await websocket.recv()`: receive one message from the websocket. Since the GUI sends the first message with `{type: "init"}`, the assertion two lines below holds.
- depending on whether the user is starting a chatroom or joining one, handle the initialization request with either the `join()` or `start()` function (also in `app.py`).

### App.py start

```
JOIN = {}
...
async def start(websocket):
    chat = Chat()                                   # initialize a new Chat.
    connected = {websocket}                         # keep a list of connected users.

    join_key = secrets.token_urlsafe(12)            # make up a random token to identify the room.
    JOIN[join_key] = chat, connected                # keep information about our chat room in Python memory.
    userId = len(connected)

    event = {
        "type": "init",
        "joinKey": join_key,
        "userId": userId
    }
    await websocket.send(json.dumps(event))
    await send_chat(websocket, chat, userId, connected)
```
Things to note:
- this implementation maintains information about the chat (including chat history) in Python memory. You could easily persist the data by writing to a file, to a database, etc.
- [`websocket.send()` spec](https://websockets.readthedocs.io/en/stable/reference/common.html#websockets.legacy.protocol.WebSocketCommonProtocol.send)
- once we finish this initialization step, we'll move into `send_chat`, which will continuously listen for requests.

### App.py: send_chat (kind of like a server loop)

```
async def send_chat(websocket, chat, userId, connected):
    async for message in websocket:
        event = json.loads(message)
        if event["type"] == "talk":
          payload = event["payload"]
          userId = event["userId"]

          messageDetails = {"payload": payload, "userId": userId, "time": time()}
          chat.add_message(messageDetails)                                         # chat is a instance of Chat() class

          event = {"type": "talk", **messageDetails}
          websockets.broadcast(connected, json.dumps(event))
```
- similar to the server loop we saw earlier in Erlang - but for now we're only listening for one type of message
- `async for`: a for loop that allows you to call asynchronous code at each iteration. NOT concurrent - just lets the "caller" coroutine do other things while waiting for its asynchronous results. ie, it does not block the event loop.
- `chat.add_message` just adds messages to the in-memory Chat instance
- [`websockets.broadcast()` spec](https://websockets.readthedocs.io/en/stable/reference/utilities.html?highlight=broadcast#websockets.broadcast): send a message to a list of users
