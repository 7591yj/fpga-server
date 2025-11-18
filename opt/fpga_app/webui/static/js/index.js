document.addEventListener("DOMContentLoaded", () => {
  const dropdown = document.querySelector("#dropdown");
  const trigger = dropdown.querySelector("#dropdown-trigger");
  const logoutA = document.querySelector("#logout-a");
  const logoutModal = document.querySelector("#logout-modal");
  const logoutModalBackground = logoutModal.querySelector(".modal-background");
  const logoutModalClose = logoutModal.querySelector(".modal-close");
  const logoutModalCancelBtn = logoutModal.querySelector("button:nth-of-type(2)");
  const logoutModalConfirmBtn = logoutModal.querySelector("button:nth-of-type(1)");
  const jobCancelA = document.querySelector("#job-cancel-a");

  // JOB CANCEL MODAL
  const jobCancelModal = document.querySelector("#job-cancel-modal");
  const jobCancelModalBackground =
    jobCancelModal.querySelector(".modal-background");
  const jobCancelModalClose = jobCancelModal.querySelector(".modal-close");
  const jobCancelModalCancelBtn = jobCancelModal.querySelector(
    "button:nth-of-type(2)"
  );
  const jobCancelModalConfirmBtn = jobCancelModal.querySelector(
    "button:nth-of-type(1)"
  );

  // handle dropdown
  trigger.addEventListener("click", (event) => {
    event.stopPropagation();
    dropdown.classList.toggle("is-active");
  });

  document.addEventListener("click", (event) => {
    if (!dropdown.contains(event.target)) {
      dropdown.classList.remove("is-active");
    }
  });

  // LOGOUT MODAL
  logoutA.addEventListener("click", (event) => {
    event.preventDefault();
    logoutModal.classList.add("is-active");
  });

  [logoutModalBackground, logoutModalClose, logoutModalCancelBtn].forEach(
    (el) => {
      el.addEventListener("click", () => {
        logoutModal.classList.remove("is-active");
      });
    }
  );

  logoutModalConfirmBtn.addEventListener("click", () => {
    window.location.href = "/logout";
  });

  // JOB CANCEL MODAL
  jobCancelA.addEventListener("click", (event) => {
    event.preventDefault();
    jobCancelModal.classList.add("is-active");
  });

  [jobCancelModalBackground, jobCancelModalClose, jobCancelModalCancelBtn].forEach(
    (el) => {
      el.addEventListener("click", () => {
        jobCancelModal.classList.remove("is-active");
      });
    }
  );

  jobCancelModalConfirmBtn.addEventListener("click", () => {
    // TODO: implement logic
  });
});
