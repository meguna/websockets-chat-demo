function initChat(websocket) {
  websocket.addEventListener("open", () => {
    // Send an "init" event according to who is connecting.
    const params = new URLSearchParams(window.location.search);
    let event = { type: "init" };
    if (params.has("join")) {
      event.joinKey = params.get("join");
    }
    websocket.send(JSON.stringify(event));
  });
}

function showMessage(message, userId="") {
  const timestamp = Date.now();
  const messageElement = document.createElement("p");
  messageElement.innerHTML = userId !== "" ? `User ${userId}: ${message}` : message;
  messageElement.dataset.time = timestamp;
  messageElement.id = `${timestamp}-message`;
  document.querySelector("#message-wrapper").append(messageElement);
}

function removeMessage(messageId) {
  const messageElement = document.getElementById(`${messageId}-message`);
  messageElement.remove();
}

function receiveRequest(websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "init":
        console.log(event);
        // Create links for inviting others
        const joinLink = document.location + "?join=" + event.joinKey;
        document.getElementById('name-span').innerHTML = event.userId;
        showMessage(`chat started; join: ${joinLink}`);
        break;
      case "talk":
        showMessage(event.payload, event.userId);
        console.log(event.payload);
        break;
      case "quit":
        showMessage(event.player + "has left the chat.");
        websocket.close(1000);
        break;
      case "error":
        showMessage(event.payload);
        break;
      default:
        throw new Error(`Unsupported event type: ${event.type}.`);
    }
  });
}

function sendDelete(websocket) {
  // const chatWindow = document.getElementById('message-wrapper');
  // // When clicking a column, send a "play" event for a move in that column.
  // chatWindow.addEventListener("click", ({ target }) => {
  //   const timestamp = target.dataset.time;
  //   // Ignore clicks outside a time.
  //   if (timestamp === undefined) {
  //     return;
  //   }
  //   const event = {
  //     type: "delete",
  //     messageId: `${timestamp}-message`,
  //   };
  //   websocket.send(JSON.stringify(event));
  // });
}

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

window.addEventListener("DOMContentLoaded", () => {
  // Open the WebSocket connection and register event handlers.
  const websocket = new WebSocket("ws://localhost:8001/");
  initChat(websocket);
  receiveRequest(websocket);
  sendDelete(websocket);
  sendTalk(websocket);
});