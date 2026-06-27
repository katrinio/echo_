// navigation.js регистрирует глобальные слушатели на уровне модуля.
// Импортируем один раз — все тесты используют один и тот же обработчик.
import "../../src/static/js/terminal/navigation.js";

// jsdom не реализует scrollIntoView — мокаем.
Element.prototype.scrollIntoView = vi.fn();

function setupRows(n = 3) {
  document.body.innerHTML = Array.from(
    { length: n },
    (_, i) => `<a data-keyboard-row href="/${i + 1}">Row ${i + 1}</a>`,
  ).join("");
}

function press(key, target = document.body) {
  target.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true }));
}

function selectedRows() {
  return [...document.querySelectorAll("[data-keyboard-row].is-selected")];
}

beforeEach(() => {
  setupRows(3);
  press("Escape"); // сбрасываем выделение перед каждым тестом
});

describe("keyboard navigation", () => {
  it("ArrowDown selects first row", () => {
    press("ArrowDown");
    const rows = [...document.querySelectorAll("[data-keyboard-row]")];
    expect(rows[0].classList.contains("is-selected")).toBe(true);
    expect(rows[1].classList.contains("is-selected")).toBe(false);
  });

  it("ArrowDown moves selection down", () => {
    press("ArrowDown");
    press("ArrowDown");
    const rows = [...document.querySelectorAll("[data-keyboard-row]")];
    expect(rows[1].classList.contains("is-selected")).toBe(true);
  });

  it("ArrowUp moves selection up", () => {
    press("ArrowDown");
    press("ArrowDown");
    press("ArrowUp");
    const rows = [...document.querySelectorAll("[data-keyboard-row]")];
    expect(rows[0].classList.contains("is-selected")).toBe(true);
  });

  it("Escape clears selection", () => {
    press("ArrowDown");
    press("Escape");
    expect(selectedRows()).toHaveLength(0);
  });

  it("no rows — ArrowDown does nothing", () => {
    document.body.innerHTML = "";
    expect(() => press("ArrowDown")).not.toThrow();
  });
});

describe("terminal input blocks page navigation", () => {
  it("ArrowDown does not select rows when terminal is focused", () => {
    document.body.innerHTML += '<input id="terminal-command">';
    const input = document.getElementById("terminal-command");
    press("ArrowDown", input);
    expect(selectedRows()).toHaveLength(0);
  });

  it("focusing terminal clears existing selection", () => {
    press("ArrowDown"); // выбираем строку
    expect(selectedRows()).toHaveLength(1);

    const input = document.createElement("input");
    input.id = "terminal-command";
    document.body.appendChild(input);
    input.dispatchEvent(new FocusEvent("focusin", { bubbles: true }));
    expect(selectedRows()).toHaveLength(0);
  });
});
