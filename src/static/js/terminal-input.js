const terminalInput = document.getElementById("terminal-command");

// Сопоставляет введённую команду с URL.
const COMMAND_HANDLERS = {
  help: () => "/help",
  new: () => "/new",
  random: () => "/random",
  tags: () => "/tags",
  tag: async (args) => {
    const tagName = args.trim().toUpperCase();
    if (!tagName) {
      return 'Введите название тега.';
    }

    const url = `/tags/${encodeURIComponent(tagName)}`;
    const response = await fetch(url, { method: "GET" });

    if (response.ok) {
      return url;
    }

    return `Тег "${tagName}" не найден.`;
  },
};

if (terminalInput) {
  // Срабатывает по Enter в терминальной строке.
  terminalInput.addEventListener("keydown", async (event) => {
    if (event.key !== "Enter") {
      return;
    }

    const raw = terminalInput.value.trim();
    if (!raw) {
      return;
    }

    const [command, ...args] = raw.split(/\s+/);
    const handler = COMMAND_HANDLERS[command.toLowerCase()];
    if (!handler) {
      return;
    }

    const result = await handler(args.join(" "));

    if (typeof result === "string" && result.startsWith("/")) {
      window.location.href = result;
      return;
    }

    if (typeof result === "string") {
      window.alert(result);
    }
  });
}
