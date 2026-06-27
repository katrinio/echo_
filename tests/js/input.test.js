// input.js ищет #terminal-command в момент загрузки модуля.
// DOM должен существовать до импорта — используем динамические импорты в beforeAll.

let HANDLERS;

beforeAll(async () => {
  document.body.innerHTML = '<input id="terminal-command">';
  await import("../../src/static/js/terminal/history.js");
  await import("../../src/static/js/terminal/input.js");
  HANDLERS = window.TERMINAL_COMMAND_HANDLERS;
});

describe("TERMINAL_COMMAND_HANDLERS routing", () => {
  it("help returns /help", () => {
    expect(HANDLERS.help()).toBe("/help");
  });

  it("new returns /new", () => {
    expect(HANDLERS.new()).toBe("/new");
  });

  it("tags returns /tags", () => {
    expect(HANDLERS.tags()).toBe("/tags");
  });

  it("random returns /random", () => {
    expect(HANDLERS.random()).toBe("/random");
  });

  it("search returns /search with encoded query", () => {
    expect(HANDLERS.search("my dog")).toBe("/search?q=my%20dog");
  });

  it("search with empty args returns error string (not a URL)", () => {
    const result = HANDLERS.search("  ");
    expect(typeof result).toBe("string");
    expect(result.startsWith("/")).toBe(false);
  });

  it("tag with empty args returns error string", async () => {
    const result = await HANDLERS.tag("   ");
    expect(result.startsWith("/")).toBe(false);
  });

  it("tag with valid name fetches and returns URL on success", async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: true });
    const result = await HANDLERS.tag("WORK");
    expect(result).toBe("/tags/WORK");
    expect(fetch).toHaveBeenCalledWith("/tags/WORK", { method: "GET" });
  });

  it("tag returns error string when fetch fails", async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false });
    const result = await HANDLERS.tag("UNKNOWN");
    expect(result.startsWith("/")).toBe(false);
  });
});

describe("terminal Enter handler", () => {
  let input;

  beforeEach(() => {
    input = document.getElementById("terminal-command");
    input.value = "";
    global.fetch = vi.fn().mockResolvedValue({ ok: true });
    localStorage.clear();
    vi.restoreAllMocks();
  });

  function enter(value) {
    input.value = value;
    input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
  }

  it("empty value does not invoke any handler", () => {
    const spy = vi.spyOn(HANDLERS, "help");
    enter("");
    expect(spy).not.toHaveBeenCalled();
  });

  it("unknown command does not invoke any handler", () => {
    const spy = vi.spyOn(HANDLERS, "help");
    enter("unknowncmd");
    expect(spy).not.toHaveBeenCalled();
  });

  it("help command invokes help handler", async () => {
    const spy = vi.spyOn(HANDLERS, "help");
    enter("help");
    await vi.waitFor(() => expect(spy).toHaveBeenCalledOnce());
  });

  it("successful command is saved to history", async () => {
    const saveSpy = vi.spyOn(window, "saveToHistory");
    enter("help");
    await vi.waitFor(() => expect(saveSpy).toHaveBeenCalledWith("help"));
  });
});
