document.addEventListener("DOMContentLoaded", () => {
  const dropdown = document.querySelector("#dropdown");
  const trigger = dropdown.querySelector("#dropdown-trigger");

  trigger.addEventListener("click", (event) => {
    event.stopPropagation();
    dropdown.classList.toggle("is-active");
  });

  document.addEventListener("click", (event) => {
    if (!dropdown.contains(event.target)) {
      dropdown.classList.remove("is-active");
    }
  });
});
