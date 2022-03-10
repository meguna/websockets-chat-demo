/**
 * send a request to join or start a chatroom.
 */
function initChat(websocket) {
  websocket.addEventListener("open", () => {
    const params = new URLSearchParams(window.location.search);
    let event = { type: "init" };
    if (params.has("join")) {
      event.joinKey = params.get("join");
    }
    websocket.send(JSON.stringify(event));
  });
}

/**
 * Display text in the main dialog box of the webpage.
 * Optionally, pass a userId integer.
 */
function displayText(message, userId="") {
  const timestamp = Date.now();
  const messageElement = document.createElement("p");
  messageElement.innerHTML = userId !== "" ? `User ${userId}: ${message}` : message;
  messageElement.dataset.time = timestamp;
  messageElement.id = `${timestamp}-message`;
  document.querySelector("#message-wrapper").append(messageElement);
}

/**
 * Receive a response from the server, and update the GUI based on 
 * that response.
 */
function receiveWebsocketMessage(websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "init":
        const params = new URLSearchParams(window.location.search);
        let joinLink = document.location + "?join=" + event.joinKey;
        if (params.has("join")) {
          joinLink = params.get("join");
        }
        document.getElementById('name-span').innerHTML = event.userId;
        displayText(`chat started; join: ${joinLink}`);
        break;
      case "talk":
        displayText(event.payload, event.userId);
        break;
      case "quit":
        displayText(event.player + "has left the chat.");
        websocket.close(1000);
        break;
      case "error":
        displayText(event.payload);
        break;
      default:
        throw new Error(`Unsupported event type: ${event.type}.`);
    }
  });
}

/**
 * Send a message to the chatroom based on the content of the input form.
 */
function sendTalk(websocket) {
  const inputForm = document.querySelector('form');
  inputForm.addEventListener('submit', event => {
    const message = document.getElementById('message-input').value;
    const userId = document.getElementById('name-span').innerHTML;
    event.preventDefault();
    const req = {
      type: "talk",
      payload: message,
      userId: userId,
    };
    websocket.send(JSON.stringify(req));
    document.getElementById('message-input').value = "";
  });

}

/**
 * Start a connection with the chat server.
 */
window.addEventListener("DOMContentLoaded", () => {
  // Open the WebSocket connection and register event handlers.
  const websocket = new WebSocket("ws://localhost:8001/");
  initChat(websocket);
  receiveWebsocketMessage(websocket);
  sendTalk(websocket);
});