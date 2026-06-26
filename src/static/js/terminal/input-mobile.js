const terminalInputMobile = document.getElementById("terminal-command");
const mobileViewport = window.matchMedia("(width <= 720px)");

if (terminalInputMobile) {
  // На мобильных экранах мягко прокручивает страницу к терминалу после фокуса.
  terminalInputMobile.addEventListener("focus", () => {
    if (!mobileViewport.matches) {
      return;
    }

    window.requestAnimationFrame(() => {
      window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: "smooth",
      });
    });
  });
}
