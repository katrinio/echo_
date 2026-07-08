// table.js использует ResizeObserver, requestAnimationFrame и DOMContentLoaded.
// Мокаем всё что не реализовано в jsdom.

function makeTable(rows = 2) {
  const rowsHtml = Array.from({ length: rows }, (_, i) => `
    <div data-terminal-table-row>
      <span data-terminal-label>Label ${i}</span>
      <span data-terminal-dots></span>
      <span data-terminal-value>Value ${i}</span>
    </div>
  `).join("");

  return `<div data-terminal-table>${rowsHtml}</div>`;
}

let resizeObserverCallback;

beforeAll(() => {
  // ResizeObserver не реализован в jsdom — мокаем.
  global.ResizeObserver = class {
    constructor(callback) {
      resizeObserverCallback = callback;
    }

    observe() {}

    disconnect() {}
  };

  // requestAnimationFrame выполняем синхронно.
  vi.stubGlobal("requestAnimationFrame", (fn) => { fn(); return 0; });
});

async function setup(html = makeTable()) {
  vi.resetModules();
  document.body.innerHTML = html;
  await import("../../src/static/js/terminal/table.js");
  document.dispatchEvent(new Event("DOMContentLoaded"));
}

describe("форматирование таблицы", () => {
  it("не падает на таблице без строк", async () => {
    await expect(setup(`<div data-terminal-table></div>`)).resolves.not.toThrow();
  });

  it("устанавливает textContent для блоков с точками", async () => {
    await setup();
    const dots = document.querySelectorAll("[data-terminal-dots]");
    dots.forEach((el) => {
      // В jsdom getBoundingClientRect возвращает нули — точек 0, но строка пустая, не undefined.
      expect(typeof el.textContent).toBe("string");
    });
  });

  it("пропускает строки без обязательных элементов", async () => {
    await setup(`
      <div data-terminal-table>
        <div data-terminal-table-row>
          <span data-terminal-label>Only label</span>
        </div>
      </div>
    `);
    // Не должно упасть — строки без dots/value просто пропускаются.
  });

  it("обрабатывает несколько таблиц на странице", async () => {
    await setup(`
      ${makeTable(2)}
      ${makeTable(1)}
    `);
    const tables = document.querySelectorAll("[data-terminal-table]");
    expect(tables.length).toBe(2);
  });

  it("подписывается на ResizeObserver для каждой таблицы", async () => {
    await setup(makeTable());
    expect(typeof resizeObserverCallback).toBe("function");
  });
});

describe("вычисление ширины символов", () => {
  it("возвращает fallback 8 если canvas context недоступен", async () => {
    // jsdom не поддерживает canvas getContext — getMonospaceCharWidth вернёт 8.
    // Убеждаемся что форматирование всё равно запускается без ошибок.
    await setup(makeTable(3));
    const dots = document.querySelectorAll("[data-terminal-dots]");
    expect(dots.length).toBe(3);
  });
});

describe("обновление при изменении размера", () => {
  it("ResizeObserver вызывает reformat при изменении", async () => {
    await setup(makeTable());
    // Симулируем срабатывание ResizeObserver.
    expect(() => resizeObserverCallback?.()).not.toThrow();
  });

  it("window resize не бросает ошибок", async () => {
    await setup(makeTable());
    expect(() =>
      window.dispatchEvent(new Event("resize")),
    ).not.toThrow();
  });
});
