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

let userMessage = "";


// Create a message element
const createMessageDiv = (message, type = "incoming") => {
  const messageDiv = document.createElement("div");
  messageDiv.className = `chat-message ${type}`;
  messageDiv.innerHTML = `<p>${message}</p>`;
  return messageDiv;
};

// Fetch response
const generateResponse = async (placeholderDiv) => {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: userMessage }]
      })
    });

    const data = await response.json();
    const reply = data.choices?.[0]?.message?.content || "No response.";
    placeholderDiv.querySelector("p").textContent = reply;
  } catch (error) {
    placeholderDiv.querySelector("p").textContent = "⚠️ Error fetching response.";
    placeholderDiv.querySelector("p").classList.add("error");
    console.error("Fetch error:", error);
  } finally {
    chatbox.scrollTop = chatbox.scrollHeight;
  }
};

// Handle sending a message
const handleChat = () => {
  userMessage = chatInput.value.trim();
  if (!userMessage) return;

  // Display user message
  const outgoingMsg = createMessageDiv(userMessage, "outgoing");
  chatbox.appendChild(outgoingMsg);
  chatInput.value = "";
  chatbox.scrollTop = chatbox.scrollHeight;

  // Add placeholder bot message
  const placeholder = createMessageDiv("Typing...", "incoming");
  chatbox.appendChild(placeholder);
  chatbox.scrollTop = chatbox.scrollHeight;

  generateResponse(placeholder);
};

// Send on button click
sendChatBtn.addEventListener("click", handleChat);

// Optional: Send on "Enter" press
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleChat();
  }
});


const fileInput = document.getElementById("fileUpload");

// Handle file selection
fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;

  // Show file name as outgoing message
  const fileMessage = createMessageDiv(`📎 Uploading "${file.name}"...`, "outgoing");
  chatbox.appendChild(fileMessage);
  chatbox.scrollTop = chatbox.scrollHeight;

  // Create FormData to send to backend
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
    fileInput.value = ""; // Reset file input
  }
});
