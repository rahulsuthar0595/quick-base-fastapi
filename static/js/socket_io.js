const socket = io("http://localhost:8000");

socket.on('return_chat', function(data) {
    addMessage(data.message);
});

document.getElementById("sendButton").addEventListener("click", () => {
    const message = document.getElementById("messageInput").value;
    if (message) {
        socket.emit("room_chat", message);
        addMessage(`You: ${message}`);
        document.getElementById("messageInput").value = "";
    }
});

function addMessage(text) {
    const messagesDiv = document.getElementById("messages");
    const messageDiv = document.createElement("div");
    messageDiv.className = "message";
    messageDiv.textContent = text;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}