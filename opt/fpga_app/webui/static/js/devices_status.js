async function fetchDeviceStatuses() {
  try {
    const response = await fetch("/api/devices");
    if (!response.ok) return;
    const devices = await response.json();

    const container = document.getElementById("device-list");
    container.innerHTML = "";

    devices.forEach((d) => {
      const active = d.current_job_id ? "is-active" : "";
      const queued = d.queued_jobs || 0;
      const dotColor = queued > 0 ? "has-text-warning" : "has-text-success";

      const item = document.createElement("a");
      item.href = "#";
      item.className = `dropdown-item ${active}`;
      item.innerHTML = `
        <div class="is-flex is-justify-content-space-between is-align-items-center">
          ${d.device_name}
          <div class="is-flex is-align-items-center">
            <span>${queued}</span>
            <span class="icon ${dotColor}">
              <i class="fas fa-circle"></i>
            </span>
          </div>
        </div>
      `;
      container.appendChild(item);
    });
  } catch (err) {
    console.error("Failed to fetch device statuses", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fetchDeviceStatuses();
  setInterval(fetchDeviceStatuses, 60000);
});
