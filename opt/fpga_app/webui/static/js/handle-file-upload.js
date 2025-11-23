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

      // Automatically program after uploading
      const programResp = await fetch("/api/fpga/program", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: resp.path }),
      });
      const programResult = await programResp.json();

      if (programResult.status !== "success") {
        console.error("Programming failed:", programResult.error);
        return;
      }

      // Automatically submit a job after programming
      const submitResp = await fetch("/api/jobs/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: CURRENT_USER_ID, // TODO: replace with real user id
          device_id: CURRENT_DEVICE_ID, // TODO: replace with device id
          job: {
            bitfile: resp.path,
            log: programResult.output,
          },
        }),
      });

      const submitResult = await submitResp.json();
      if (submitResp.ok) {
        console.log("Job submitted:", submitResult.job_id);
      } else {
        console.error("Job submission failed:", submitResult.error);
      }
    };

    xhr.onerror = () => console.error("Upload request error");
    xhr.send(formData);
  });
});
