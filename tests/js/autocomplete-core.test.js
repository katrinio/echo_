import "../../src/static/js/autocomplete/core.js";

const {
  createAutocompleteState,
  moveAutocompleteIndex,
  getActiveAutocompleteItem,
  handleAutocompleteKeydown,
} = window;

const MATCHES = [
  { command: "help", description: "Show help" },
  { command: "new", description: "Create milestone" },
  { command: "tags", description: "List tags" },
];

function fakeEvent(key) {
  return { key, preventDefault: vi.fn() };
}

function fakeHandlers(overrides = {}) {
  return {
    applySuggestion: vi.fn(),
    renderSuggestions: vi.fn(),
    hidePopup: vi.fn(),
    ...overrides,
  };
}

describe("createAutocompleteState", () => {
  it("starts with activeIndex -1 (nothing selected)", () => {
    expect(createAutocompleteState().activeIndex).toBe(-1);
  });
});

describe("moveAutocompleteIndex", () => {
  it("ArrowDown from -1 selects first item", () => {
    const state = createAutocompleteState();
    moveAutocompleteIndex(state, 1, 3);
    expect(state.activeIndex).toBe(0);
  });

  it("ArrowUp from -1 stays at -1", () => {
    const state = createAutocompleteState();
    moveAutocompleteIndex(state, -1, 3);
    expect(state.activeIndex).toBe(-1);
  });

  it("ArrowDown advances normally when already selected", () => {
    const state = { activeIndex: 0 };
    moveAutocompleteIndex(state, 1, 3);
    expect(state.activeIndex).toBe(1);
  });

  it("ArrowDown wraps from last to first", () => {
    const state = { activeIndex: 2 };
    moveAutocompleteIndex(state, 1, 3);
    expect(state.activeIndex).toBe(0);
  });

  it("ArrowUp wraps from first to last", () => {
    const state = { activeIndex: 0 };
    moveAutocompleteIndex(state, -1, 3);
    expect(state.activeIndex).toBe(2);
  });
});

describe("getActiveAutocompleteItem", () => {
  it("returns null when nothing selected", () => {
    const state = createAutocompleteState();
    expect(getActiveAutocompleteItem(MATCHES, state)).toBeNull();
  });

  it("returns null for empty matches", () => {
    const state = { activeIndex: 0 };
    expect(getActiveAutocompleteItem([], state)).toBeNull();
  });

  it("returns correct item when selected", () => {
    const state = { activeIndex: 1 };
    expect(getActiveAutocompleteItem(MATCHES, state)).toEqual(MATCHES[1]);
  });
});

describe("handleAutocompleteKeydown", () => {
  it("Escape calls hidePopup regardless of matches", () => {
    const handlers = fakeHandlers();
    handleAutocompleteKeydown(fakeEvent("Escape"), [], createAutocompleteState(), handlers);
    expect(handlers.hidePopup).toHaveBeenCalledOnce();
  });

  it("Tab with nothing selected does not call applySuggestion", () => {
    const handlers = fakeHandlers();
    const state = createAutocompleteState();
    handleAutocompleteKeydown(fakeEvent("Tab"), MATCHES, state, handlers);
    expect(handlers.applySuggestion).not.toHaveBeenCalled();
  });

  it("Tab with item selected calls applySuggestion", () => {
    const handlers = fakeHandlers();
    const state = { activeIndex: 0 };
    handleAutocompleteKeydown(fakeEvent("Tab"), MATCHES, state, handlers);
    expect(handlers.applySuggestion).toHaveBeenCalledWith(MATCHES[0]);
  });

  it("Enter with nothing selected does not call applySuggestion", () => {
    const handlers = fakeHandlers();
    handleAutocompleteKeydown(fakeEvent("Enter"), MATCHES, createAutocompleteState(), handlers);
    expect(handlers.applySuggestion).not.toHaveBeenCalled();
  });

  it("ArrowDown calls renderSuggestions", () => {
    const handlers = fakeHandlers();
    const state = createAutocompleteState();
    handleAutocompleteKeydown(fakeEvent("ArrowDown"), MATCHES, state, handlers);
    expect(handlers.renderSuggestions).toHaveBeenCalledWith(MATCHES);
  });
});
