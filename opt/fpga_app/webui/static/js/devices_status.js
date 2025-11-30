let selectedDeviceId = null;

async function fetchDeviceStatuses() {
  try {
    const response = await fetch("/api/devices", { credentials: "same-origin" });
    if (!response.ok) return;
    const devices = await response.json();

    const container = document.getElementById("device-list");
    container.innerHTML = "";
    const activeDeviceName = document.getElementById("active-device-name");

    const params = new URLSearchParams(window.location.search);
    selectedDeviceId = params.get("device");

    if (
      !selectedDeviceId ||
      !devices.some((d) => d.serial_number === selectedDeviceId)
    ) {
      selectedDeviceId = devices[0]?.serial_number || null;
    }

    const selectedDevice = devices.find(
      (d) => d.serial_number === selectedDeviceId
    );
    activeDeviceName.textContent = selectedDevice
      ? selectedDevice.device_name
      : "(No active device)";

    devices.forEach((d) => {
      const isActive = d.serial_number === selectedDeviceId;
      const queued = d.queued_jobs || 0;
      const dotColor = queued > 0 ? "has-text-warning" : "has-text-success";

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
        setActiveDevice(d.serial_number);
      });

      container.appendChild(item);
    });
  } catch (err) {
    console.error("Failed to fetch device statuses:", err);
  }
}

function setActiveDevice(serial) {
  const current = new URL(window.location.href);
  current.searchParams.set("device", serial);
  // preserve pathname
  window.location.href = `${current.pathname}?${current.searchParams.toString()}`;
}

document.addEventListener("DOMContentLoaded", () => {
  fetchDeviceStatuses();
});
