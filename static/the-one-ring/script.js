const messages = document.getElementById("messages");
const input = document.getElementById("userInput");

function appendMessage(sender, text, className) {
  const msg = document.createElement("div");
  msg.classList.add("message", className);
  msg.textContent = `${sender}: ${text}`;
  messages.appendChild(msg);
}

input.addEventListener("keydown", async (e) => {
  if (e.key === "Enter" && input.value.trim()) {
    const userMessage = input.value.trim();
    appendMessage("You", userMessage, "user");
    input.value = "";

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
      });

      if (!response.ok) {
        const text = await response.text();
        appendMessage("Error", `Server error ${response.status}: ${text}` , "assistant");
        return;
      }

      const data = await response.json();
      appendMessage("Demerzel", data.response, "assistant");
    } catch (error) {
      appendMessage("Error", "There was a problem contacting the server.", "assistant");
    }

    messages.scrollTop = messages.scrollHeight;
  }
});
