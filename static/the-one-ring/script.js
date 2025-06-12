const messages = document.getElementById("messages");
const input = document.getElementById("userInput");
const pdfFrame = document.getElementById("pdfFrame");

// Path to the PDF.js viewer. Using an absolute path ensures the viewer and
// referenced PDF files are correctly resolved regardless of the current page
// location.
const PDF_VIEWER_PATH = "/static/pdfjs/web/viewer.html";

// Store currently used template (race PDF), to pass to backend on save
let currentTemplatePdfPath = null;

function appendMessage(sender, text, className) {
  const msg = document.createElement("div");
  msg.classList.add("message", className);
  msg.textContent = `${sender}: ${text}`;
  messages.appendChild(msg);
}

function normalizeName(name) {
  return name.toLowerCase().trim().replace(/\s+/g, "_");
}

let pdfReady = false;

// Listen for PDF.js load completion
window.addEventListener("message", (event) => {
  if (event.data?.type === "documentloaded") {
    pdfReady = true;
  }
});

// === Extract all AcroForm field values from the iframe ===
async function extractPdfFields() {
  return new Promise((resolve, reject) => {
    try {
      const viewer = pdfFrame.contentWindow.PDFViewerApplication;
      const fields = {};

      const annotations = viewer._annotationStorage._storage;
      for (const [key, value] of Object.entries(annotations)) {
        if (value && value.value !== undefined) {
          fields[key] = value.value;
        }
      }

      resolve(fields);
    } catch (err) {
      reject(err);
    }
  });
}

// === Save current character sheet fields ===
async function saveCharacterSheet(name) {
  try {
    if (!pdfReady) {
      appendMessage("System", "PDF viewer is not ready.", "assistant");
      return;
    }
    if (!currentTemplatePdfPath) {
      appendMessage("System", "You must load a character sheet template before saving.", "assistant");
      return;
    }

    const fields = await extractPdfFields();

    const res = await fetch("/save-character", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name,
        template: currentTemplatePdfPath, // <--- Correct key
        fieldData: fields,                // <--- Correct key
      })
    });

    const result = await res.json();
    appendMessage("System", result.message || result.error || "Unknown response.", "assistant");
  } catch (err) {
    appendMessage("System", "Failed to save character: " + err.message, "assistant");
  }
}

// === Load saved character sheet ===
async function loadCharacterSheet(name) {
  const safeName = normalizeName(name);
  try {
    // Use the direct endpoint; PDF.js can fetch directly.
    const pdfUrl = `/load-character/${safeName}`;
    pdfFrame.src = `${PDF_VIEWER_PATH}?file=${encodeURIComponent(pdfUrl)}`;
    appendMessage("System", `Character sheet '${name}' loaded successfully.`, "assistant");
    // Optionally, clear currentTemplatePdfPath here because we loaded a saved character
    currentTemplatePdfPath = null;
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
  if (lowered.includes("show") && (lowered.includes("man") || lowered.includes("men"))) return "pdfs/man.pdf";
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
        // If showing a built-in template, use static path (adjust if necessary)
        const encodedUrl = encodeURIComponent(command);
        pdfFrame.src = `${PDF_VIEWER_PATH}?file=${encodedUrl}`;

        // Track the template for future reference (e.g., on save)
        currentTemplatePdfPath = command;

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
        const response = await fetch("/chat", {
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