function createAutocompleteState() {
  return {
    activeIndex: 0,
  };
}

function normalizeAutocompleteIndex(index, length) {
  if (!length) {
    return 0;
  }

  return ((index % length) + length) % length;
}

function getActiveAutocompleteItem(matches, state) {
  if (!matches.length) {
    return null;
  }

  state.activeIndex = normalizeAutocompleteIndex(state.activeIndex, matches.length);
  return matches[state.activeIndex] || null;
}

function moveAutocompleteIndex(state, delta, length) {
  state.activeIndex = normalizeAutocompleteIndex(state.activeIndex + delta, length);
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

window.createAutocompleteState = createAutocompleteState;
window.normalizeAutocompleteIndex = normalizeAutocompleteIndex;
window.getActiveAutocompleteItem = getActiveAutocompleteItem;
window.moveAutocompleteIndex = moveAutocompleteIndex;
window.showAutocompletePopup = showAutocompletePopup;
window.hideAutocompletePopup = hideAutocompletePopup;
window.handleAutocompleteKeydown = handleAutocompleteKeydown;
