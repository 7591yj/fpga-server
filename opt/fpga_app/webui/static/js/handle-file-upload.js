document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.querySelector(".file-input");
  const fileName = document.querySelector(".file-name");
  const programBtn = document.getElementById("program-btn");
  const progressBar = document.querySelector("progress");

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    fileName.textContent = file ? file.name : "Choose a file…";
  });

  programBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/fpga/upload", true);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        progressBar.value = (e.loaded / e.total) * 100;
      }
    };

    xhr.onload = async () => {
      if (xhr.status !== 200) {
        console.error("Upload failed:", xhr.responseText);
        return;
      }

      let resp;
      try {
        resp = JSON.parse(xhr.responseText);
      } catch {
        console.error("Upload returned invalid JSON");
        return;
      }

      if (!resp.path) {
        console.error("Upload response missing path");
        return;
      }

      const params = new URLSearchParams(window.location.search);
      const deviceSn = params.get("device");

      // Automatically program after uploading
      const programResp = await fetch("/api/fpga/program", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        }, body: JSON.stringify({ path: resp.path, device_sn: deviceSn }),
      });
      const programResult = await programResp.json();

      if (programResult.status !== "queued") {
        console.error("Programming failed:", programResult.error);
        return;
      }
    };

    xhr.onerror = () => console.error("Upload request error");
    xhr.send(formData);
  });
});
