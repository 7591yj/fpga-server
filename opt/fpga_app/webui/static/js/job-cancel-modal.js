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

    confirmBtn.addEventListener("click", () => {
      // TODO: API call
      modal.classList.remove("is-active");
    });
  });
});
