beforeEach(() => {
  document.body.innerHTML = `
    <input id="terminal-command">
    <div id="terminal-suggestions" hidden></div>
  `;
  // Перерегистрируем обработчики через свежий импорт модуля.
  vi.resetModules();
});

async function setup() {
  await import("../../src/static/js/keyboard/global.js");
}

function press(key, target = document.body) {
  target.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true }));
}

describe("/ shortcut", () => {
  it("focuses terminal input", async () => {
    await setup();
    press("/");
    expect(document.activeElement.id).toBe("terminal-command");
  });

  it("does not focus terminal when inside an input", async () => {
    await setup();
    const other = document.createElement("input");
    document.body.appendChild(other);
    other.focus();
    press("/", other);
    expect(document.activeElement).toBe(other);
  });

  it("does not focus terminal when inside a textarea", async () => {
    await setup();
    const ta = document.createElement("textarea");
    document.body.appendChild(ta);
    ta.focus();
    press("/", ta);
    expect(document.activeElement).toBe(ta);
  });

  it("does not focus terminal from select", async () => {
    await setup();
    const sel = document.createElement("select");
    document.body.appendChild(sel);
    sel.focus();
    press("/", sel);
    expect(document.activeElement).toBe(sel);
  });
});

describe("Escape shortcut", () => {
  it("removes focus from terminal input", async () => {
    await setup();
    const input = document.getElementById("terminal-command");
    input.focus();
    expect(document.activeElement).toBe(input);
    press("Escape", input);
    expect(document.activeElement).not.toBe(input);
  });

  it("hides terminal suggestions", async () => {
    await setup();
    const container = document.getElementById("terminal-suggestions");
    container.hidden = false;
    press("Escape");
    expect(container.hidden).toBe(true);
  });
});
