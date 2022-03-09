# Chat Demo with Python Websockets and Web GUI

For CS21, Spring 2022, Tufts University.

### About this project

This project demonstrates a chat application service that uses a Python WebSockets backend and a very primitive HTML/Javascript frontend. It used [the official Python WebSockets tutorial](https://websockets.readthedocs.io/en/stable/intro/tutorial1.html) (which builds a Connect4 server instead) as a guide. 

### Run the project

Clone this repository and open two terminal windows from the project's root directory. 
- In one of the windows, run `python3 app.py`
- In the other window, run python3 -m http.server
- Then, you should be able to access the website at: `http://localhost:8000/`
- If you open the "join link" from a different browser (but within the same local network as the server), you should be able to use the application to communicate. 
- To be able to access this project from any network, you can publish it to the internet! See more [here](https://websockets.readthedocs.io/en/stable/intro/tutorial3.html). 

