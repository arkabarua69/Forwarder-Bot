const BASE_URL = "https://forwarder-bot-1.onrender.com"; // Flask backend URL

// Start the Telegram bot
async function startBot() {
  const source = document.getElementById("sourceId").value.trim();
  const target = document.getElementById("targetId").value.trim();

  if (!source || !target) {
    alert("Please enter both Source and Target Chat IDs!");
    return;
  }

  appendLog("Starting bot...");

  try {
    const res = await fetch(`${BASE_URL}/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source, target })
    });

    if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);

    const data = await res.json();
    appendLog(data.message);

  } catch (error) {
    console.error("Error starting bot:", error);
    appendLog(`Error: ${error.message}`);
  }
}

// Fetch logs from backend
async function fetchLogs() {
  try {
    const res = await fetch(`${BASE_URL}/logs`);
    if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
    const data = await res.json();

    const logsDiv = document.getElementById("logs");
    logsDiv.innerText = data.logs.join("\n"); // Replace old logs
    logsDiv.scrollTop = logsDiv.scrollHeight; // Scroll to bottom
  } catch (error) {
    console.error("Error fetching logs:", error);
    appendLog(`Error: ${error.message}`);
  }
}

// Append message to logs div
function appendLog(message) {
  const logsDiv = document.getElementById("logs");
  logsDiv.innerText += message + "\n";
  logsDiv.scrollTop = logsDiv.scrollHeight;
}

// Auto-refresh logs every 5 seconds
setInterval(fetchLogs, 5000);

// Optional: fetch logs immediately on page load
window.addEventListener("load", fetchLogs);
