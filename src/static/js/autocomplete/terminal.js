let terminalCommands = [];
const terminalAutocompleteState = createAutocompleteState();
const terminalHistoryState = createHistoryState();

async function loadTerminalCommands() {
  const response = await fetch("/terminal/commands");

  if (!response.ok) {
    console.warn("Failed to load terminal commands");
    return [];
  }

  return response.json();
}

function getTerminalInput() {
  return document.getElementById("terminal-command");
}

function getSuggestionsContainer() {
  return document.getElementById("terminal-suggestions");
}

function getMatchingCommands(value) {
  const query = value.trim().toLowerCase();

  if (!query) {
    return [];
  }

  return terminalCommands
    .filter((item) => item.command.startsWith(query))
    .slice(0, 5);
}

function renderSuggestions(matches) {
  const container = getSuggestionsContainer();

  if (!container) {
    return;
  }

  if (!matches.length) {
    container.hidden = true;
    container.innerHTML = "";
    return;
  }

  container.hidden = false;
  // Рисуем не только текст команд, но и короткое описание справа.
  container.innerHTML = matches
    .map((item, index) => {
      const activeClass = index === terminalAutocompleteState.activeIndex ? " is-active" : "";

      return `
        <div class="terminal-suggestion${activeClass}" data-command="${item.command}">
          <span class="terminal-suggestion-command">${item.command}</span>
          <span class="terminal-suggestion-description">${item.description}</span>
        </div>
      `;
    })
    .join("");
}

function getCurrentMatches() {
  const input = getTerminalInput();

  if (!input) {
    return [];
  }

  return getMatchingCommands(input.value);
}

function applySuggestion(command) {
  const input = getTerminalInput();
  const container = getSuggestionsContainer();

  if (!input) {
    return;
  }

  input.value = command;
  input.focus();

  if (container) {
    container.hidden = true;
    container.innerHTML = "";
  }
}

function updateSuggestions() {
  const input = getTerminalInput();

  if (!input) {
    return;
  }

  terminalAutocompleteState.activeIndex = -1;
  renderSuggestions(getMatchingCommands(input.value));
}
document.addEventListener("DOMContentLoaded", async () => {
  const input = getTerminalInput();
  const container = getSuggestionsContainer();

  if (!input || !container) {
    return;
  }

  input.addEventListener("input", () => {
    resetHistoryCursor(terminalHistoryState);
    updateSuggestions();
  });

  input.addEventListener("keydown", (event) => {
    const matches = getCurrentMatches();
    const suggestionsVisible = !container.hidden && matches.length > 0;

    if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      // Стрелки всегда останавливаются здесь — страница не должна двигаться.
      event.preventDefault();
      event.stopPropagation();

      if (!suggestionsVisible) {
        // Подсказок нет — переключаем историю.
        const direction = event.key === "ArrowUp" ? "up" : "down";
        const value = navigateHistory(terminalHistoryState, direction);
        if (value !== null) {
          input.value = value;
        }
        return;
      }
    }

    handleAutocompleteKeydown(event, matches, terminalAutocompleteState, {
      applySuggestion: (selectedMatch) => applySuggestion(selectedMatch.command),
      renderSuggestions,
      hidePopup: () => renderSuggestions([]),
    });
  });

  container.addEventListener("pointerdown", (event) => {
    handleAutocompletePointerDown(event, {
      container,
      getSuggestionElement: (target) => target.closest(".terminal-suggestion"),
      applySuggestion: (suggestion) => {
        const command = suggestion.dataset.command;

        if (!command) {
          return;
        }

        applySuggestion(command);
      },
    });
  });

  try {
    terminalCommands = await loadTerminalCommands();
  } catch (error) {
    console.warn("Failed to initialize terminal autocomplete", error);
    terminalCommands = [];
  }
});
