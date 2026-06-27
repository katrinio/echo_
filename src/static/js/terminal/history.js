const HISTORY_KEY = "echo_terminal_history";
const HISTORY_MAX = 50;

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveToHistory(command) {
  if (!command) return;

  const history = loadHistory();

  if (history[history.length - 1] === command) return;

  history.push(command);

  if (history.length > HISTORY_MAX) {
    history.shift();
  }

  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function createHistoryState() {
  // cursor === -1 означает "не в режиме навигации по истории".
  return { cursor: -1 };
}

function navigateHistory(state, direction) {
  const history = loadHistory();

  if (!history.length) return null;

  if (state.cursor === -1) {
    if (direction === "up") {
      state.cursor = history.length - 1;
    } else {
      return null;
    }
  } else if (direction === "up") {
    state.cursor = Math.max(0, state.cursor - 1);
  } else {
    state.cursor += 1;
    if (state.cursor >= history.length) {
      state.cursor = -1;
      return "";
    }
  }

  return state.cursor === -1 ? "" : history[state.cursor];
}

function resetHistoryCursor(state) {
  state.cursor = -1;
}

window.saveToHistory = saveToHistory;
window.createHistoryState = createHistoryState;
window.navigateHistory = navigateHistory;
window.resetHistoryCursor = resetHistoryCursor;
