document.addEventListener("DOMContentLoaded", () => {
  const commandForm = document.getElementById("commandForm");
  const commandInput = document.getElementById("commandInput");
  const submitBtn = document.getElementById("submitBtn");
  const jsonOutput = document.getElementById("jsonOutput");
  const resultMessage = document.getElementById("resultMessage");
  const statusBadge = document.getElementById("statusBadge");
  const devicesContainer = document.getElementById("devicesContainer");
  const rulesTableBody = document.getElementById("rulesTableBody");
  const refreshRulesBtn = document.getElementById("refreshRulesBtn");
  const refreshDevicesBtn = document.getElementById("refreshDevicesBtn");

  // Preset buttons handler
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const text = btn.getAttribute("data-text");
      commandInput.value = text;
      executeCommand(text);
    });
  });

  // Form submit handler
  commandForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = commandInput.value.trim();
    if (text) {
      executeCommand(text);
    }
  });

  refreshRulesBtn.addEventListener("click", fetchRules);
  refreshDevicesBtn.addEventListener("click", fetchDevices);

  async function executeCommand(text) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = "<span>Processing...</span>";
    statusBadge.className = "status-badge idle";
    statusBadge.textContent = "Processing";
    resultMessage.textContent = "Sending instruction to /command endpoint...";

    try {
      const response = await fetch("/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
      });

      const data = await response.json();
      renderResponse(data);
      fetchRules();
    } catch (err) {
      statusBadge.className = "status-badge unsupported";
      statusBadge.textContent = "Error";
      resultMessage.textContent = "Failed to communicate with backend API.";
      jsonOutput.textContent = JSON.stringify({ error: err.message }, null, 2);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span>Execute Action</span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`;
    }
  }

  function renderResponse(res) {
    statusBadge.className = `status-badge ${res.status}`;
    statusBadge.textContent = res.status.toUpperCase().replace("_", " ");
    resultMessage.textContent = res.message;
    jsonOutput.textContent = JSON.stringify(res, null, 2);
  }

  async function fetchDevices() {
    try {
      const res = await fetch("/devices");
      const devices = await res.json();
      devicesContainer.innerHTML = "";
      for (const [id, dev] of Object.entries(devices)) {
        const item = document.createElement("div");
        item.className = "device-card-item";
        const metricsHtml = dev.metrics.map(m => `<span class="metric-tag">${m}</span>`).join("");
        item.innerHTML = `
          <h4>${id}</h4>
          <p style="font-size:0.75rem; color:var(--text-muted); margin-bottom:4px;">${dev.name}</p>
          <div>${metricsHtml}</div>
        `;
        devicesContainer.appendChild(item);
      }
    } catch (e) {
      devicesContainer.innerHTML = `<p class="empty-state">Error loading devices.</p>`;
    }
  }

  async function fetchRules() {
    try {
      const res = await fetch("/rules");
      const data = await res.json();
      if (!data.rules || data.rules.length === 0) {
        rulesTableBody.innerHTML = `<tr><td colspan="7" class="empty-state">No rules created yet in memory.</td></tr>`;
        return;
      }
      rulesTableBody.innerHTML = "";
      data.rules.forEach(rule => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="font-family:'JetBrains Mono',monospace; font-size:0.75rem;">${rule.id}</td>
          <td><strong>${rule.device_id}</strong></td>
          <td>${rule.metric}</td>
          <td><span class="tag">${rule.condition}</span></td>
          <td>${rule.threshold}</td>
          <td>${rule.duration_minutes}m</td>
          <td>${rule.notify_via.join(", ")}</td>
        `;
        rulesTableBody.appendChild(tr);
      });
    } catch (e) {
      rulesTableBody.innerHTML = `<tr><td colspan="7" class="empty-state">Error fetching rules.</td></tr>`;
    }
  }

  // Initial load
  fetchDevices();
  fetchRules();
});
