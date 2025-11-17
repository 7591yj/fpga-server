const prefersDark =
  window.matchMedia('(prefers-color-scheme: dark)').matches;

document.querySelectorAll('#queue-dot-unknown').forEach((el) => {
  if (!prefersDark) {
    el.classList.add('has-text-black');
    el.classList.remove('has-text-white');
  } else {
    el.classList.add('has-text-white');
    el.classList.remove('has-text-black');
  }
});
