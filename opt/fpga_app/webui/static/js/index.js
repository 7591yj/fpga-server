document.addEventListener("DOMContentLoaded", () => {
  const dropdown = document.querySelector("#dropdown");
  const trigger = dropdown.querySelector("#dropdown-trigger");
  const logoutA = document.querySelector("#logout-a");
  const logoutModal = document.querySelector("#logout-modal");
  const modalBackground = logoutModal.querySelector(".modal-background");
  const modalClose = logoutModal.querySelector(".modal-close");
  const cancelBtn = logoutModal.querySelector("button:nth-of-type(2)");
  const confirmBtn = logoutModal.querySelector("button:nth-of-type(1)");

  // handle toggle dropdown
  trigger.addEventListener("click", (event) => {
    event.stopPropagation();
    dropdown.classList.toggle("is-active");
  });

  // open modal when logout link clicked
  logoutA.addEventListener("click", (event) => {
    event.preventDefault();
    logoutModal.classList.add("is-active");
  });

  // close modal on background, close icon, or cancel button
  [modalBackground, modalClose, cancelBtn].forEach((el) => {
    el.addEventListener("click", () => {
      logoutModal.classList.remove("is-active");
    });
  });

  // handle confirm logout
  confirmBtn.addEventListener("click", () => {
    window.location.href = "/logout";
  });

  // handle cancel logout
  document.addEventListener("click", (event) => {
    if (!dropdown.contains(event.target)) {
      dropdown.classList.remove("is-active");
    }
  });
});
