import "../../src/static/js/terminal/history.js";

const { saveToHistory, createHistoryState, navigateHistory, resetHistoryCursor } = window;

beforeEach(() => {
  localStorage.clear();
});

describe("saveToHistory", () => {
  it("saves a command", () => {
    saveToHistory("help");
    const history = JSON.parse(localStorage.getItem("echo_terminal_history"));
    expect(history).toEqual(["help"]);
  });

  it("does not save empty string", () => {
    saveToHistory("");
    expect(localStorage.getItem("echo_terminal_history")).toBeNull();
  });

  it("does not save consecutive duplicate", () => {
    saveToHistory("help");
    saveToHistory("help");
    const history = JSON.parse(localStorage.getItem("echo_terminal_history"));
    expect(history).toHaveLength(1);
  });

  it("saves non-consecutive duplicates", () => {
    saveToHistory("help");
    saveToHistory("new");
    saveToHistory("help");
    const history = JSON.parse(localStorage.getItem("echo_terminal_history"));
    expect(history).toHaveLength(3);
  });

  it("keeps max 50 commands", () => {
    for (let i = 0; i < 55; i++) {
      saveToHistory(`cmd${i}`);
    }
    const history = JSON.parse(localStorage.getItem("echo_terminal_history"));
    expect(history).toHaveLength(50);
    expect(history[0]).toBe("cmd5");
    expect(history[49]).toBe("cmd54");
  });
});

describe("navigateHistory", () => {
  beforeEach(() => {
    saveToHistory("first");
    saveToHistory("second");
    saveToHistory("third");
  });

  it("ArrowDown when not navigating returns null", () => {
    const state = createHistoryState();
    expect(navigateHistory(state, "down")).toBeNull();
  });

  it("ArrowUp shows last command", () => {
    const state = createHistoryState();
    expect(navigateHistory(state, "up")).toBe("third");
  });

  it("ArrowUp navigates backwards", () => {
    const state = createHistoryState();
    navigateHistory(state, "up");
    expect(navigateHistory(state, "up")).toBe("second");
  });

  it("ArrowUp stops at oldest command", () => {
    const state = createHistoryState();
    navigateHistory(state, "up");
    navigateHistory(state, "up");
    navigateHistory(state, "up");
    navigateHistory(state, "up"); // уже на первом элементе
    expect(navigateHistory(state, "up")).toBe("first");
  });

  it("ArrowDown after ArrowUp goes forward", () => {
    const state = createHistoryState();
    navigateHistory(state, "up"); // third
    navigateHistory(state, "up"); // second → теперь cursor на second
    expect(navigateHistory(state, "down")).toBe("third");
  });

  it("ArrowDown past end returns empty string", () => {
    const state = createHistoryState();
    navigateHistory(state, "up"); // перемещаемся на последний
    expect(navigateHistory(state, "down")).toBe("");
  });

  it("resetHistoryCursor resets navigation", () => {
    const state = createHistoryState();
    navigateHistory(state, "up");
    resetHistoryCursor(state);
    expect(state.cursor).toBe(-1);
  });

  it("empty history returns null for ArrowUp", () => {
    localStorage.clear();
    const state = createHistoryState();
    expect(navigateHistory(state, "up")).toBeNull();
  });
});
