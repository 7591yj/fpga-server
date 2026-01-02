document.addEventListener("DOMContentLoaded", () => {
  const cancelLinks = document.querySelectorAll(".job-cancel-a");

  cancelLinks.forEach((link) => {
    const modal = link.closest("td").querySelector(".job-cancel-modal");
    const background = modal.querySelector(".modal-background");
    const close = modal.querySelector(".modal-close");
    const cancelBtn = modal.querySelector("button:nth-of-type(2)");
    const confirmBtn = modal.querySelector("button:nth-of-type(1)");

    link.addEventListener("click", (e) => {
      e.preventDefault();
      modal.classList.add("is-active");
    });

    [background, close, cancelBtn].forEach((el) => {
      el.addEventListener("click", () => modal.classList.remove("is-active"));
    });

    confirmBtn.addEventListener("click", async () => {
      const jobRow = link.closest("tr");
      // job_id is in the 4th td
      const jobId = jobRow.children[3].textContent;

      try {
        const response = await fetch(`/api/jobs/cancel/${jobId}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({}),
          credentials: "same-origin",
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        // Reload the page to reflect the cancelled job status
        window.location.reload();

      } catch (error) {
        console.error("Error cancelling job:", error);
        alert("Failed to cancel job: " + error.message);
      } finally {
        modal.classList.remove("is-active");
      }
    });
  });
});
