function createAutocompleteState() {
  // -1 означает "ничего не выбрано".
  return {
    activeIndex: -1,
  };
}

function normalizeAutocompleteIndex(index, length) {
  if (!length) {
    return 0;
  }

  return ((index % length) + length) % length;
}

function getActiveAutocompleteItem(matches, state) {
  if (!matches.length || state.activeIndex === -1) {
    return null;
  }

  state.activeIndex = normalizeAutocompleteIndex(state.activeIndex, matches.length);
  return matches[state.activeIndex] || null;
}

function moveAutocompleteIndex(state, delta, length) {
  if (state.activeIndex === -1) {
    // Из состояния "ничего не выбрано" ArrowDown идёт к первому элементу,
    // ArrowUp остаётся на месте.
    state.activeIndex = delta > 0 ? 0 : -1;
  } else {
    state.activeIndex = normalizeAutocompleteIndex(state.activeIndex + delta, length);
  }
  return state.activeIndex;
}

function showAutocompletePopup(container) {
  if (!container) {
    return;
  }

  container.hidden = false;
}

function hideAutocompletePopup(container) {
  if (!container) {
    return;
  }

  container.hidden = true;
  container.innerHTML = "";
}

function handleAutocompleteKeydown(event, matches, state, options) {
  const { applySuggestion, renderSuggestions, hidePopup } = options;

  // Escape всегда закрывает список подсказок.
  if (event.key === "Escape") {
    event.preventDefault();
    hidePopup();
    return true;
  }

  if (!matches.length) {
    return false;
  }

  if (event.key === "ArrowDown") {
    event.preventDefault();
    moveAutocompleteIndex(state, 1, matches.length);
    renderSuggestions(matches);
    return true;
  }

  if (event.key === "ArrowUp") {
    event.preventDefault();
    moveAutocompleteIndex(state, -1, matches.length);
    renderSuggestions(matches);
    return true;
  }

  if (event.key === "Tab" || event.key === "Enter") {
    event.preventDefault();
    const selectedMatch = getActiveAutocompleteItem(matches, state);

    if (!selectedMatch) {
      return true;
    }

    applySuggestion(selectedMatch);
    return true;
  }

  return false;
}

function handleAutocompletePointerDown(event, options) {
  const { container, getSuggestionElement, applySuggestion } = options;

  if (!container) {
    return false;
  }

  // Клик по самой подсказке должен вести себя как выбор элемента.
  const suggestion = getSuggestionElement(event.target);

  if (!suggestion) {
    return false;
  }

  event.preventDefault();
  applySuggestion(suggestion, event);
  return true;
}

window.createAutocompleteState = createAutocompleteState;
window.normalizeAutocompleteIndex = normalizeAutocompleteIndex;
window.getActiveAutocompleteItem = getActiveAutocompleteItem;
window.moveAutocompleteIndex = moveAutocompleteIndex;
window.showAutocompletePopup = showAutocompletePopup;
window.hideAutocompletePopup = hideAutocompletePopup;
window.handleAutocompleteKeydown = handleAutocompleteKeydown;
window.handleAutocompletePointerDown = handleAutocompletePointerDown;
