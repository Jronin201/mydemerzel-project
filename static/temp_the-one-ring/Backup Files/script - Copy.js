const messages = document.getElementById("messages");
const input = document.getElementById("userInput");
const pdfFrame = document.getElementById("pdfFrame");

// === Save character sheet field data from PDF.js viewer ===
async function saveCharacterSheet(name) {
  const iframe = document.getElementById("pdfFrame");
  const viewerWindow = iframe.contentWindow;

  if (!viewerWindow || !viewerWindow.PDFViewerApplication) {
    appendMessage("System", "PDF viewer is not ready.", "assistant");
    return;
  }

  try {
    const pdfDoc = viewerWindow.PDFViewerApplication.pdfDocument;
    const fields = await pdfDoc.getFieldObjects();

    const formData = {};
    for (const [key, entries] of Object.entries(fields)) {
      const field = entries[0];
      const val = field.V || field.DV || "";
      formData[key] = val;
    }

    const res = await fetch("https://mydemerzel.onrender.com/save-character", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, fieldData: formData })
    });

    const result = await res.json();
    appendMessage("System", result.message || result.error || "Unknown response.", "assistant");
  } catch (err) {
    appendMessage("System", "Failed to save character: " + err.message, "assistant");
  }
}

// === Load character sheet ===
async function loadCharacterSheet(name) {
  const safeName = name.toLowerCase().trim().replace(/\s+/g, "_");
  try {
    const response = await fetch(`https://mydemerzel.onrender.com/load-character/${safeName}`);
    if (!response.ok) {
      appendMessage("System", "Character not found.", "assistant");
      return;
    }

    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(blob);
    pdfFrame.src = blobUrl;

    appendMessage("System", `Character sheet '${name}' loaded successfully.`, "assistant");
  } catch (err) {
    appendMessage("System", "Failed to load character: " + err.message, "assistant");
  }
}

// === Race-based command interpretation ===
function interpretCommand(text) {
  const lowered = text.toLowerCase();
  if (lowered.includes("show") && lowered.includes("elf")) return "pdfs/elf.pdf";
  if (lowered.includes("show") && lowered.includes("dwarf")) return "pdfs/dwarf.pdf";
  if (lowered.includes("show") && lowered.includes("hobbit")) return "pdfs/hobbit.pdf";
  if (lowered.includes("show") && (lowered.includes("man") || lowered.includes("men"))) return "pdfs/men.pdf";
  if (lowered.includes("remove") || lowered.includes("hide")) return "remove";
  return null;
}

// === Main input handler ===
input.addEventListener("keydown", async (e) => {
  if (e.key === "Enter" && input.value.trim()) {
    const userMessage = input.value.trim();
    appendMessage("You", userMessage, "user");
    input.value = "";

    const lowered = userMessage.toLowerCase();
    let systemResponded = false;

    if (lowered === "?") {
      appendMessage("System", `
Available commands:
- save character as [name]
- load character [name]
- show elf / dwarf / hobbit / man
- remove character sheet`, "assistant");
      systemResponded = true;
    } else if (lowered.startsWith("save character as ")) {
      const name = userMessage.slice(17).trim();
      await saveCharacterSheet(name);
      systemResponded = true;
    } else if (lowered.startsWith("load character ") || lowered.startsWith("load ")) {
      const name = userMessage.replace(/^(load character |load )/, "").trim();
      await loadCharacterSheet(name);
      systemResponded = true;
    } else {
      const command = interpretCommand(userMessage);

      if (command === "remove") {
        pdfFrame.src = "";
        appendMessage("System", "The character sheet has been removed from view.", "assistant");
        systemResponded = true;
      } else if (command) {
        pdfFrame.src = command;
        const race = command.includes("elf") ? "Elf"
                   : command.includes("dwarf") ? "Dwarf"
                   : command.includes("hobbit") ? "Hobbit"
                   : "Man";
        appendMessage("System", `The ${race} character sheet is now visible on the left panel.`, "assistant");
        systemResponded = true;
      }
    }

    if (!systemResponded) {
      try {
        const response = await fetch("https://mydemerzel.onrender.com/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();
        appendMessage("Demerzel", data.response, "assistant");
      } catch (error) {
        appendMessage("Error", "There was a problem contacting the server.", "assistant");
      }
    }

    messages.scrollTop = messages.scrollHeight;
  }
});

function appendMessage(sender, text, className) {
  const msg = document.createElement("div");
  msg.classList.add("message", className);
  msg.textContent = `${sender}: ${text}`;
  messages.appendChild(msg);
}
