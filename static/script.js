document.addEventListener("DOMContentLoaded", () => {
  // 🟢 1. Particle.js Initialization
  
  const particlesContainer = document.getElementById("particles-js");
  if (particlesContainer) {
    particlesJS('particles-js', {
      particles: {
        number: { value: 100, density: { enable: true, value_area: 800 } },
        color: { value: "#77B254" },
        shape: { type: "circle", stroke: { width: 0, color: "#77B254" } },
        opacity: { value: 1, random: true, anim: { enable: true, speed: 0, opacity_min: 0.1 } },
        size: { value: 3, random: true, anim: { enable: true, speed: 100, size_min: 0.1 } },
        line_linked: { enable: true, distance: 150, color: "#77B254", opacity: 0.4, width: 1 },
        move: {
          enable: true,
          speed: 3,
          direction: "none",
          random: true,
          straight: false,
          out_mode: "out",
          attract: { enable: false, rotateX: 600, rotateY: 1200 }
        }
      },
      interactivity: {
        detect_on: "window",
        events: {
          onhover: { enable: true, mode: "grab" },
          onclick: { enable: true, mode: "push" },
          resize: true
        }
      },
      retina_detect: true
    });
  }

  // Detect if running locally or on production
const BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:5000"
    : window.location.origin;

  const MAX_HISTORY = 10; 
  const HISTORY_KEY = "chat_history";

  // 🟢 Load history from localStorage
  const getChatHistory = () => {
    try {
      return JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
    } catch {
      return [];
    }
  };

  const saveChatHistory = (history) => {
    if (history.length > MAX_HISTORY) {
      history.splice(0, history.length - MAX_HISTORY);
    }
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  };

  // 🟢 2. DOM Elements
  const chatInput = document.getElementById("messageInput");
  const sendChatBtn = document.getElementById("sendBTN");
  const chatbox = document.getElementById("chatbox");
  const fileInput = document.getElementById("fileUpload");
  
  

  // 🟢 3. Utility: Create Message Div
  const createMessageDiv = (markdown, type = "incoming") => {
    const div = document.createElement("div");
    div.className = `chat-message ${type}`;
    const rawHtml = marked.parse(markdown);
    const safeHtml = DOMPurify.sanitize(rawHtml);
    div.innerHTML = safeHtml;
    Prism.highlightAllUnder(div);
    return div;
  };

  // 🟢 4. Streaming Flask Response
const streamFlaskResponse = async (userMessage, placeholderDiv) => {
    try {
      const history = getChatHistory();
      history.push({ role: "user", content: userMessage });

      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
                               user_query: userMessage,
                               messages: history })
      });

      if (!response.ok) throw new Error("Failed to fetch response from backend.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let fullResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        fullResponse += chunk;
        placeholderDiv.textContent = fullResponse;
        chatbox?.scrollTo({ top: chatbox.scrollHeight, behavior: "smooth" });
      }

      const html = marked.parse(fullResponse);
      placeholderDiv.innerHTML = DOMPurify.sanitize(html);
      Prism.highlightAllUnder(placeholderDiv);

      // 🟢 Save assistant reply to history
      history.push({ role: "assistant", content: fullResponse });
      saveChatHistory(history);

      chatbox?.scrollTo({ top: chatbox.scrollHeight, behavior: "smooth" });
    } catch (err) {
      console.error("Chat error:", err);
      placeholderDiv.textContent = "⚠️ Error fetching response. Please check that you are logged in.";
    }
  };

  // 🟢 5. Chat Send Handler
  const handleChat = () => {
    const userMessage = chatInput?.value.trim();
    if (!userMessage) return;

    const userDiv = createMessageDiv(userMessage, "outgoing");
    chatbox?.appendChild(userDiv);

    chatInput.value = "";
    chatInput.focus();

    const placeholder = createMessageDiv("Typing...", "incoming");
    chatbox?.appendChild(placeholder);
    chatbox?.scrollTo({ top: chatbox.scrollHeight, behavior: "smooth" });

    streamFlaskResponse(userMessage, placeholder);
  };
  

  // 🟢 6. Add Event Listeners Safely
  if (sendChatBtn) {
    sendChatBtn.addEventListener("click", handleChat);
  }

  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleChat();
      }
    });
  }
// file upload

  if (fileInput) {
    fileInput.addEventListener("change", async () => {
      const file = fileInput.files[0];
      if (!file) return;

      const uploadingDiv = createMessageDiv(`📎 Uploading "${file.name}"...`, "outgoing");
      chatbox?.appendChild(uploadingDiv);

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch("/upload", { method: "POST", body: formData });
        const data = await response.json();

        const msg = data.message || data.error || "Upload complete.";
        const msgDiv = createMessageDiv(msg, "incoming");
        chatbox?.appendChild(msgDiv);
      } catch (err) {
        console.error("Upload error:", err);
        chatbox?.appendChild(createMessageDiv("❌ Upload failed.", "incoming"));
      } finally {
        chatbox?.scrollTo({ top: chatbox.scrollHeight, behavior: "smooth" });
        fileInput.value = "";
      }
    });
  }


  // 🟢 7. Supabase Auth
  const sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

  // 🔐 Register
  window.registerUser = async function(email, password) {
    const msgDiv = document.getElementById("register_message");
    const submitBtn = document.querySelector("button[type='submit']");
    if (submitBtn) submitBtn.disabled = true;

    const { data, error } = await sb.auth.signUp({ email, password });

    if (error) {
      msgDiv.textContent = "❌ " + error.message;
      msgDiv.style.color = "red";
      if (submitBtn) submitBtn.disabled = false;
    } else {
      msgDiv.textContent = "✅ Registration successful! Please check your email.";
      msgDiv.style.color = "green";
      document.getElementById("reg_email").value = "";
      document.getElementById("reg_password").value = "";
    }
  };

  // 🔑 Login
window.handleLogin = async function() {
    const email = document.getElementById("login_email").value.trim();
    const password = document.getElementById("login_password").value.trim();
    const errorDiv = document.getElementById("errorMsg");
    const loadingDiv = document.getElementById("loadingMsg");

    errorDiv.textContent = "";
    loadingDiv.textContent = "Checking credentials...";

    const { data, error } = await sb.auth.signInWithPassword({ email, password });

    if (error) {
      loadingDiv.textContent = "";
      errorDiv.textContent = "❌ " + error.message;
      return;
    }

    const session = data.session;
    if (!session) {
      loadingDiv.textContent = "";
      errorDiv.textContent = "❌ Login failed.";
      return;
    }

    // Await the response from your /set-session endpoint
    // This is the key step to ensure the cookie is set.
    const response = await fetch(`${BASE_URL}/set-session`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        access_token: session.access_token,
        refresh_token: session.refresh_token,
      }),
      redirect: 'follow'
    });
    
    // Check if the server successfully set the cookie before redirecting
    if (response.ok) {
        // Now it's safe to redirect, as the browser has received and stored the cookie.
        // window.location.href = "http://127.0.0.1:5000/api/profile";
        loadingDiv.textContent= 'Session set! Redirecting...';
        window.location.href = `redirecting`;
    } else {
        loadingDiv.textContent = "";
        errorDiv.textContent = "❌ Failed to set session cookies.";
    }
};

// logout


  window.logoutUser = async function() {
    try {
      const { error } = await sb.auth.signOut();
      if (error) console.error("Logout error:", error);
      window.location.href = "/login";
    } catch (err) {
      console.error("Unexpected error:", err);
      window.location.href = "/login";
    }
  }

});
