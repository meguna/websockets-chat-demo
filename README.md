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

## File Structure
- app.py: contains the server loop and server functions (functions that update the state of the server).
- main.js: contains the GUI, and the client functions that send requests to the server. We also receive responses from the server here, which update our GUI.
- index.html: basic HTML, which is manipulated by the Javascript. 
- style.css: styling for our website. Uses [Bulma](https://bulma.io/)

# Code Highlights (in class)

### App.py: Server Loop
```
async def main():
    async with websockets.serve(handler, "", 8001):       # run the websockets 
        await asyncio.Future()                            # run forever
```
- We use the `websockets` library for this project
- `websockets` is based on the Python standard library `asyncio` 

Some key vocabulary terms here:
- `asyncio` is based on coroutines, which are basically like Python functions where you can choose to stop execution at certain checkpoints within the function, and resume execution from that stopped checkpoint later. 
- `async def ...` defines a coroutine.
- `await f()...` are statements that should only be used within coroutine functions, and will pause execution of the "caller" coroutine and waits for the execution of the `f()` to complete first before proceeding.

