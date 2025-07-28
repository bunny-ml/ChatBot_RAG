/* Particle.js initialization */
particlesJS('particles-js', {
    "particles": {
        "number": {
            "value": 100,
            "density": {
                "enable": true,
                "value_area": 800
            }
        },
        "color": {
            "value": "#77B254"
        },
        "shape": {
            "type": "circle",
            "stroke": {
                "width": 0,
                "color": "#77B254"
            }
        },
        "opacity": {
            "value": 1,
            "random": true,
            "anim": {
                "enable": true,
                "speed": 0,
                "opacity_min": 0.1
            }
        },
        "size": {
            "value": 3,
            "random": true,
            "anim": {
                "enable": true,
                "speed": 100,
                "size_min": 0.1
            }
        },
        "line_linked": {
            "enable": true,
            "distance": 150,
            "color": "#77B254",
            "opacity": 0.4,
            "width": 1
        },
        "move": {
            "enable": true,
            "speed": 3,
            "direction": "none",
            "random": true,
            "straight": false,
            "out_mode": "out",
            "bounce": false,
            "attract": {
                "enable": false,
                "rotateX": 600,
                "rotateY": 1200
            }
        }
    },
    "interactivity": {
        "detect_on": "window",
        "events": {
            "onhover": {
                "enable": true,
                "mode": "grab"
            },
            "onclick": {
                "enable": true,
                "mode": "push"
            },
            "resize": true
        }
    },
    "retina_detect": true
});


const chatInput = document.getElementById("messageInput");
const sendChatBtn = document.getElementById("sendBTN");
const chatbox = document.getElementById("chatbox");
const fileInput = document.getElementById("fileUpload");

// Create message element
const createMessageDiv = (message, type = "incoming") => {
  const messageDiv = document.createElement("div");
  messageDiv.className = `chat-message ${type}`;
  messageDiv.innerHTML = `<p>${message}</p>`;
  return messageDiv;
};

// Stream response from Flask backend
const streamFlaskResponse = async (userMessage, placeholderDiv) => {
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_query: userMessage })
    });

    if (!response.ok) {
      throw new Error("Failed to fetch response from backend.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let fullResponse = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      fullResponse += chunk;
      placeholderDiv.querySelector("p").textContent = fullResponse;
    }
  } catch (error) {
    console.error("Chat fetch error:", error);
    placeholderDiv.querySelector("p").textContent = "⚠️ Error fetching response.";
  } finally {
    chatbox.scrollTop = chatbox.scrollHeight;
  }
};

// Send message logic
const handleChat = () => {
  const userMessage = chatInput.value.trim();
  if (!userMessage) return;

  // Show user message
  const userDiv = createMessageDiv(userMessage, "outgoing");
  chatbox.appendChild(userDiv);

  // Clear input
  chatInput.value = "";
  chatInput.focus();

  // Add placeholder for bot reply
  const placeholder = createMessageDiv("Typing...", "incoming");
  chatbox.appendChild(placeholder);
  chatbox.scrollTop = chatbox.scrollHeight;

  // Fetch response from backend
  streamFlaskResponse(userMessage, placeholder);
};

// Event listeners
sendChatBtn.addEventListener("click", handleChat);

chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleChat();
  }
});

// Optional: Handle file upload (if you have /upload implemented)
fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;

  const fileMsg = createMessageDiv(`📎 Uploading "${file.name}"...`, "outgoing");
  chatbox.appendChild(fileMsg);
  chatbox.scrollTop = chatbox.scrollHeight;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    const confirmation = data?.message || "File uploaded successfully.";
    const botResponse = createMessageDiv(confirmation, "incoming");
    chatbox.appendChild(botResponse);
  } catch (error) {
    console.error("Upload failed:", error);
    const errorMsg = createMessageDiv("❌ File upload failed.", "incoming");
    chatbox.appendChild(errorMsg);
  } finally {
    chatbox.scrollTop = chatbox.scrollHeight;
    fileInput.value = "";
  }
});
