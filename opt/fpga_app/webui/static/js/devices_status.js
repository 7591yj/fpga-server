let selectedDeviceId = null;

async function fetchDeviceStatuses() {
  try {
    const response = await fetch("/api/devices");
    if (!response.ok) return;
    const devices = await response.json();

    const container = document.getElementById("device-list");
    container.innerHTML = "";
    const activeDeviceName = document.getElementById("active-device-name");

    // Initialize selected device if not chosen yet
    if (!selectedDeviceId && devices.length > 0) {
      selectedDeviceId = devices[0].serial_number;
    }

    const selectedDevice =
      devices.find((d) => d.serial_number === selectedDeviceId) || devices[0];

    activeDeviceName.textContent = selectedDevice.device_name;

    devices.forEach((d) => {
      const isActive = d.serial_number === selectedDeviceId;
      const queued = d.queued_jobs || 0;
      const dotColor =
        queued > 0 ? "has-text-warning" : "has-text-success";

      const item = document.createElement("a");
      item.href = "#";
      item.className = `dropdown-item ${isActive ? "is-active" : ""}`;
      item.innerHTML = `
        <div class="is-flex is-justify-content-space-between is-align-items-center">
          <abbr title="${d.serial_number}">${d.device_name}</abbr>
          <div class="is-flex is-align-items-center">
            <span>${queued}</span>
            <span class="icon ${dotColor}">
              <i class="fas fa-circle"></i>
            </span>
          </div>
        </div>
      `;

      item.addEventListener("click", () => {
        selectedDeviceId = d.serial_number;
        // Immediately update displayed active device
        activeDeviceName.textContent = d.device_name;
        fetchDeviceStatuses();
      });

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
